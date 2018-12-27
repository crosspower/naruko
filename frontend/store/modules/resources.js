import httpClient from '@/lib/httpClient'
import STATUS from '@/lib/definition/monitorStatus'
import REGIONS from '@/lib/definition/regions'
import axios from 'axios'

// state
const state = {
  resources: [],
  cancelToken: null,
  pushAlertRef: null
}

// getters
const getters = {
  resources: state => state.resources
}

// mutations
const mutations = {
  resources(state, data) {
    state.resources = data
  },
  pushResources(state, data) {
    state.resources.push(data)
  },
  cancelToken(state, data) {
    state.cancelToken = data
  }
}

// actions
const actions = {
  fetch({commit, state, rootGetters, dispatch}) {
    // リクエストが存在する場合キャンセルしておく
    if (state.cancelToken) {
      state.cancelToken.cancel()
    }
    const source = axios.CancelToken.source()
    commit('cancelToken', source)
    commit('resources', [])

    const requestArray = []
    const tenantId = rootGetters['user/userData'].tenant.id
    for (const awsEnv of rootGetters['user/userData'].aws_environments) {
      REGIONS.forEach((region) => {
        const request = httpClient.tenant.getResources(source.token, tenantId, awsEnv.id, region.id).then((resp) => {
          for (const instance of resp.data) {
            // ステータスの設定
            if (instance.status === STATUS.OK.id) {
              instance.status = STATUS.OK
            } else if (instance.status === STATUS.CAUTION.id) {
              instance.status = STATUS.CAUTION
            } else if (instance.status === STATUS.DANGER.id) {
              instance.status = STATUS.DANGER
            } else {
              instance.status = STATUS.UNSET
            }
            instance.aws_environment = awsEnv
            commit('pushResources', instance)
          }
          return Promise.resolve(resp)
        }).catch((error) => {
          return Promise.reject({error, data: {awsEnv: awsEnv, region: region}})
        })
        requestArray.push(request)
      })
    }

    const toResultObject = (promise) => {
      return promise
          .then((res) => {
            return {success: true, data: res}
          }).catch((res) => {
            const isCancel = axios.isCancel(res.error)
            if (!isCancel) {
              dispatch('alert/pushErrorAlert', `${res.data.awsEnv.name}: ${res.data.region.name}のインスタンス一覧の取得に失敗しました。`, {root: true})
            }
            return {success: false, data: res.data, isCancel: isCancel}
          })
    }

    return Promise.all(requestArray.map(toResultObject)).then(() => {
      return Promise.resolve()
    })
  },
  cancelFetch({state}) {
    // リクエストをキャンセルする
    if (state.cancelToken) {
      state.cancelToken.cancel()
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}