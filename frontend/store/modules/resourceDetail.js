import httpClient from '@/lib/httpClient'
import STATUS from '@/lib/definition/monitorStatus'
import METRICS from '@/lib/definition/metrics'
import RESOURCES from '@/lib/definition/resources'
import moment from 'moment-timezone'
import Cron from '@/lib/cron'

// state
const state = {
  resource: {},
  metrics: [],
  backups: [],
  schedules: [],
  monitorGraph: [],
  documents: [],
  document: {},
  command: {}
}

// getters
const getters = {
  metrics: state => state.metrics,
  resource: state => state.resource,
  backups: state => state.backups,
  schedules: state => state.schedules,
  monitorGraph: state => state.monitorGraph,
  documents: state => state.documents,
  document: state => state.document,
  command: state => state.command
}

// mutations
const mutations = {
  metrics(state, data) {
    state.metrics = data
  },
  resource(state, data) {
    state.resource = data
  },
  backups(state, data) {
    state.backups = data
  },
  schedules(state, data) {
    state.schedules = data
  },
  monitorGraph(state, data) {
    state.monitorGraph = data
  },
  documents(state, data) {
    state.documents = data
  },
  document(state, data) {
    state.document = data
  },
  command(state, data) {
    state.command = data
  }
}

// actions
const actions = {
  fetchResource({commit, rootGetters, dispatch}, [awsAccount, region, service, resourceId]) {
    return httpClient.tenant.getResourceDetail(rootGetters['user/userData'].tenant.id, awsAccount, region, service, resourceId).then((res) => {
      commit('resource', res.data)
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `リソースの情報の取得に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  fetchMonitors({commit, rootGetters, dispatch}, [awsAccount, region, service, resourceId]) {
    return httpClient.tenant.getMonitors(rootGetters['user/userData'].tenant.id, awsAccount, region, service, resourceId).then((res) => {
      const metrics = res.data
      for (const metric of metrics) {
        // メトリクスのステータス取得

        metric.status = STATUS[metric.status]
        if (!metric.status) {
          metric.status = STATUS.UNSET
        }
        // メトリクスの名前取得
        let name = metric.metric_name
        let unit = ''
        if (METRICS[service.toUpperCase()] && METRICS[service.toUpperCase()][metric.metric_name]) {
          name = METRICS[service.toUpperCase()][metric.metric_name].name
          unit = METRICS[service.toUpperCase()][metric.metric_name].unit
        }
        metric.name = name
        metric.unit = unit

        if (metric.enabled === true) {
          metric.enabled = {value: true, name: '有効'}
        } else {
          metric.enabled = {value: false, name: '無効'}
        }
      }
      commit('metrics', metrics)
      return Promise.resolve(res)
    }).catch((err) => {
      commit('metrics', [])
      dispatch('alert/pushErrorAlert', `監視項目の取得に失敗しました。`, {root: true})
      return Promise.reject(err)
    })
  },
  fetchBackups({commit, rootGetters, dispatch}, [awsAccount, region, service, resourceId]) {
    commit('backups', [])
    return httpClient.tenant.getResourceBackups(
        rootGetters['user/userData'].tenant.id,
        awsAccount,
        region,
        service,
        resourceId).then((res) => {
      for (const backup of res.data) {
        backup.created_at = moment(new Date(backup.created_at)).format("YYYY/MM/DD HH:mm:ss")
      }
      commit('backups', res.data)
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `バックアップの情報の取得に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  fetchSchedules({commit, rootGetters, dispatch}, [awsAccount, region, service, resourceId]) {
    commit('schedules', [])
    return httpClient.tenant.getSchedules(
        rootGetters['user/userData'].tenant.id,
        awsAccount,
        region,
        service,
        resourceId).then((res) => {
      for (const schedule of res.data) {
        schedule.is_active = {
          value: schedule.is_active,
          text: schedule.is_active ? '有効' : '無効'
        }
        schedule.notification = {
          value: schedule.notification,
          text: schedule.notification ? '有効' : '無効'
        }
        schedule.action = RESOURCES[service.toUpperCase()].scheduleActions[schedule.action]
        try {
          schedule.next = Cron.next(schedule.schedule_expression, 'Asia/Tokyo', "YYYY/MM/DD HH:mm")
        } catch {
          schedule.next = '-'
        }
      }
      commit('schedules', res.data)
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `スケジュールの情報の取得に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  fetchMonitorGraph({state, commit, rootGetters, dispatch}, [awsAccount, region, service, resourceId, metricName, data]) {
    commit('monitorGraph', {labels: [], datasets: []})
    const metric = state.metrics.find(m => m.metric_name === metricName)
    return httpClient.tenant.getMonitorGraph(
        rootGetters['user/userData'].tenant.id,
        awsAccount,
        region,
        service,
        resourceId,
        metricName,
        data).then((res) => {
      const max = Math.max(...res.data.values.length > 0 ? res.data.values : [0])
      const data = {
        labels: res.data.timestamps.map(t => moment(t).tz('Asia/Tokyo').format("YYYY/MM/DD HH:mm")),
        datasets: [{
          data: res.data.values,
          backgroundColor: 'rgba(0, 119, 204, 0.8)',
          borderColor: 'rgba(0, 119, 204, 0.3)',
          borderWidth: 1,
          fill: false,
          pointRadius: 2
        }],
        yHighlightRanges: {
          danger: {
            begin: metric.values.danger || 0,
            end: metric.values.danger > 0 ? max + 100000 : 0,
            color: 'rgba(255,138, 128, 0.4)'
          },
          caution: {
            begin: metric.values.caution || 0,
            end: metric.values.danger || 0,
            color: 'rgba(255,213, 79, 0.4)'
          }
        }
      }
      commit('monitorGraph', data)
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `グラフの情報の取得に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  addMonitor({state, rootGetters, dispatch}, data) {
    return httpClient.tenant.addMonitor(
        rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id,
        data).then((res) => {
      dispatch('alert/pushSuccessAlert', `${METRICS[state.resource.service][data.metric_name].name} の監視を設定しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `${METRICS[state.resource.service][data.metric_name].name} の監視の設定に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  applyProfiles({state, rootGetters, dispatch}, profiles) {
    const requestArray = []
    for (const profile of profiles) {
      const request = httpClient.tenant.addMonitor(
          rootGetters['user/userData'].tenant.id,
          state.resource.aws_environment,
          state.resource.region,
          state.resource.service,
          state.resource.id,
          profile).then((res) => {
        return Promise.resolve({result: res, data: profile})
      }).catch((error) => {
        return Promise.reject({result: error, data: profile})
      })
      requestArray.push(request)
    }

    const toResultObject = (promise) => {
      return promise
          .then((res) => {
            dispatch('alert/pushSuccessAlert', `${METRICS[state.resource.service][res.data.metric_name].name} の監視を設定しました。`, {root: true})
            return {success: true, data: res.data}
          }).catch((res) => {
            dispatch('alert/pushErrorAlert', `${METRICS[state.resource.service][res.data.metric_name].name} の監視の設定に失敗しました。`, {root: true})
            return {success: false, data: res.data}
          })
    }

    return Promise.all(requestArray.map(toResultObject))
  },
  startEc2Instance({state, rootGetters, dispatch}) {
    return httpClient.tenant.startEc2Instance(
        rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id).then((res) => {
      dispatch('alert/pushSuccessAlert', `インスタンスを起動しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `インスタンスの起動に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  stopEc2Instance({state, rootGetters, dispatch}) {
    return httpClient.tenant.stopEc2Instance(
        rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id).then((res) => {
      dispatch('alert/pushSuccessAlert', `インスタンスを停止しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `インスタンスの停止に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  rebootEc2Instance({state, rootGetters, dispatch}) {
    return httpClient.tenant.rebootEc2Instance(
        rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id).then((res) => {
      dispatch('alert/pushSuccessAlert', `インスタンスを再起動しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `インスタンスの再起動に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  createResourceBackup({state, rootGetters, dispatch}, data) {
    return httpClient.tenant.createResourceBackup(
        rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id,
        data).then((res) => {
      dispatch('alert/pushSuccessAlert', `インスタンスのバックアップを作成しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `インスタンスのバックアップの作成に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  addSchedule({state, rootGetters, dispatch}, data) {
    return httpClient.tenant.addSchedule(
        rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id,
        data).then((res) => {
      dispatch('alert/pushSuccessAlert', `スケジュール ${data.name} を作成しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `スケジュール ${data.name} の作成に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  editSchedule({state, rootGetters, dispatch}, [scheduleId, data]) {
    return httpClient.tenant.editSchedule(
        rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id,
        scheduleId,
        data).then((res) => {
      dispatch('alert/pushSuccessAlert', `スケジュール ${data.name} を編集しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `スケジュール ${data.name} の編集に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  deleteSchedule({state, rootGetters, dispatch}, scheduleId) {
    const target = state.schedules.find(v => v.id === scheduleId)
    if (!target) {
      return Promise.reject()
    }
    return httpClient.tenant.deleteSchedule(rootGetters['user/userData'].tenant.id,
        state.resource.aws_environment,
        state.resource.region,
        state.resource.service,
        state.resource.id,
        scheduleId).then((res) => {
      dispatch('alert/pushSuccessAlert', `スケジュール ${target.name} を削除しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `スケジュール ${target.name} の削除に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  fetchDocuments({commit, rootGetters, dispatch}, [awsAccount, region]) {
    return httpClient.tenant.getDocuments(
        rootGetters['user/userData'].tenant.id,
        awsAccount,
        region).then((res) => {
          commit('documents', res.data)
          return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `ドキュメントの取得に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  fetchDocument({commit, rootGetters, dispatch}, [awsAccount, region, documentName]) {
    return httpClient.tenant.getDocumentDetail(
        rootGetters['user/userData'].tenant.id,
        awsAccount,
        region,
        documentName
      ).then((res) => {
        commit('document', res.data)
        return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `ドキュメントの取得に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  runCommand({state, commit, rootGetters}, data) {
    return httpClient.tenant.runCommand(
      rootGetters['user/userData'].tenant.id,
      state.resource.aws_environment,
      state.resource.region,
      state.resource.service,
      state.resource.id,
      data).then((res) => {
        commit('command', res.data)
        return Promise.resolve(res)
    }).catch((res) => {
      commit('command', {out_put: `コマンドの実行に失敗しました。`})
      return Promise.reject(res)
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}