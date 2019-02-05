import store from '@/store'

describe('store/modules/resourceDetail', () => {
  it('mutations.metrics', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const state = {
      resource: {},
      metrics: []
    }

    const data = [
      {metric_name: 'test_metric1'},
      {metric_name: 'test_metric2'}
    ]

    resourceDetail.mutations.metrics(state, data)

    expect(state['metrics']).toBe(data)
    done()
  })

  it('mutations.resource', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const state = {
      resource: {},
      metrics: []
    }

    const data = {
      awsAccount: 'test aws account',
      region: 'test region',
      service: 'test service',
      id: 'test id',
      name: 'test name'
    }

    resourceDetail.mutations.resource(state, data)

    expect(state['resource']).toBe(data)
    done()
  })

  it('actions.fetchMonitors', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const awsAccount = 'test account'
    const region = 'test reigon'
    const service = 'EC2'
    const resourceId = 'test id'

    const responseData = [
      {
        metric_name: 'StatusCheckFailed',
        values: {'caution': 1, 'danger': 1},
        enabled: true,
        period: 300,
        evaluation_period: 1,
        statistic: 'Maximum',
        comparison_operator: 'GreaterThanOrEqualToThreshold',
        status: 'OK'
      }
    ]

    const expectData = [
      {
        metric_name: 'StatusCheckFailed',
        name: '死活監視',
        unit: "",
        values: {'caution': 1, 'danger': 1},
        enabled: {value: true, name: '有効'},
        period: 300,
        evaluation_period: 1,
        statistic: 'Maximum',
        comparison_operator: 'GreaterThanOrEqualToThreshold',
        status: {
          id: 'OK',
          name: '正常',
          sortText: '1',
          icon: 'mdi-checkbox-marked-circle',
          color: 'green'
        }
      }
    ]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getMonitors = jest.fn().mockImplementation((cid, a, r, s, rid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(awsAccount)
      expect(r).toBe(region)
      expect(s).toBe(service)
      expect(rid).toBe(resourceId)

      return Promise.resolve({data: responseData})
    })


    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    const state = {
      resource: {},
      metrics: []
    }
    resourceDetail.actions.fetchMonitors({
      commit,
      state,
      rootGetters
    }, [awsAccount, region, service, resourceId]).then((res) => {
      expect(res.data).toEqual(expectData)
      expect(commit).toHaveBeenCalledWith('metrics', expectData)
      done()
    })
  })

  it('actions.addMonitor', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const resource = {
      aws_environment: 'test aws account',
      region: 'test_region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const data = {
      metric_name: 'CPUUtilization',
      values: {
        caution: 70,
        danger: 80
      },
      enabled: true,
      period: 300,
      evaluation_period: 1,
      statistic: 'GreaterThanOrEqualToThreshold'
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addMonitor = jest.fn().mockImplementation((cid, a, r, s, rid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const state = {
      resource: resource,
      metrics: []
    }
    const dispatch = jest.fn()
    resourceDetail.actions.addMonitor({state, rootGetters, dispatch}, data).then(() => {
      expect(httpClient.tenant.addMonitor).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `CPU使用率 の監視を設定しました。`, {root: true})
      done()
    })
  })

  it('actions.applyProfiles', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const resource = {
      aws_environment: 'test aws account',
      region: 'test region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }
    const profiles = [
      {
        metric_name: 'CPUUtilization',
        values: {
          caution: 72,
          danger: 90
        },
        period: 300,
        evaluation_period: 3,
        statistic: 'Average',
        enabled: true
      }
    ]

    const data = {
      metric_name: profiles[0].metric_name,
      values: profiles[0].values,
      enabled: profiles[0].enabled,
      period: profiles[0].period,
      evaluation_period: profiles[0].evaluation_period,
      statistic: profiles[0].statistic
    }
    const expectData = [{success: true, data: data}]


    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addMonitor = jest.fn().mockImplementation((cid, a, r, s, rid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      expect(d).toEqual(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const state = {
      resource: resource,
      metrics: []
    }
    const dispatch = jest.fn()
    resourceDetail.actions.applyProfiles({state, rootGetters, dispatch}, profiles).then((res) => {
      expect(httpClient.tenant.addMonitor).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `CPU使用率 の監視を設定しました。`, {root: true})
      expect(res).toEqual(expectData)
      done()
    })
  })

  it('actions.fetchResource', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const awsAccount = 'test account'
    const region = 'test reigon'
    const service = 'EC2'
    const resourceId = 'test id'

    const responseData = {
      id: 'i-123412512341',
      name: 'test name',
      status: null,
      service: 'EC2',
      aws_environment: awsAccount,
      region: region,
      state: 'stopped'
    }


    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getResourceDetail = jest.fn().mockImplementation((cid, a, r, s, rid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(awsAccount)
      expect(r).toBe(region)
      expect(s).toBe(service)
      expect(rid).toBe(resourceId)

      return Promise.resolve({data: responseData})
    })


    const commit = jest.fn()
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.fetchResource({
      commit, rootGetters, dispatch
    }, [awsAccount, region, service, resourceId]).then((res) => {
      expect(res.data).toEqual(responseData)
      expect(commit).toHaveBeenCalledWith('resource', responseData)
      done()
    })
  })

  it('actions.startEc2Instance', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const resource = {
      aws_environment: 'test aws account',
      region: 'test region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.startEc2Instance = jest.fn().mockImplementation((cid, a, r, s, rid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)

      return Promise.resolve()
    })

    const state = {
      resource
    }
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.startEc2Instance({state, rootGetters, dispatch}).then(() => {
      expect(httpClient.tenant.startEc2Instance).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id)
      done()
    })
  })

  it('actions.stopEc2Instance', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const resource = {
      aws_environment: 'test aws account',
      region: 'test region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.stopEc2Instance = jest.fn().mockImplementation((cid, a, r, s, rid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      return Promise.resolve()
    })

    const state = {
      resource
    }
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.stopEc2Instance({state, rootGetters, dispatch}).then(() => {
      expect(httpClient.tenant.stopEc2Instance).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id)
      done()
    })
  })

  it('actions.rebootEc2Instance', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const resource = {
      aws_environment: 'test aws account',
      region: 'test region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.rebootEc2Instance = jest.fn().mockImplementation((cid, a, r, s, rid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      return Promise.resolve()
    })
    const state = {resource}
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.rebootEc2Instance({state, rootGetters, dispatch}).then(() => {
      expect(httpClient.tenant.rebootEc2Instance).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id)
      done()
    })
  })

  it('actions.createResourceBackup', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const resource = {
      aws_environment: 'test aws account',
      region: 'test region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }

    const data = {
      no_reboot: false
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.createResourceBackup = jest.fn().mockImplementation((cid, a, r, s, rid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      expect(d).toBe(data)
      return Promise.resolve()
    })
    const state = {resource}
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.createResourceBackup({state, rootGetters, dispatch}, data).then(() => {
      expect(httpClient.tenant.createResourceBackup).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `インスタンスのバックアップを作成しました。`, {root: true})
      done()
    })
  })

  it('actions.fetchSchedules', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default
    const Cron = require('@/lib/cron').default

    Cron.next = jest.fn().mockImplementation(() => {
      return 'next date'
    })

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const awsAccount = 543
    const region = 'test reigon'
    const service = 'EC2'
    const resourceId = 'test id'

    const responseData = [{
      id: 38,
      is_active: true,
      schedule_expression: "cron(0 18 27 * ? *)",
      created_at: "2018-12-20T06:39:18.197261Z",
      updated_at: "2018-12-20T06:39:18.197261Z",
      name: "testname",
      action: "BACKUP",
      notification: true,
      params: {"noReboot": true},
      resource: "i-1123456789",
      service: service,
      region: region
    }]

    const expectData = [{
      id: 38,
      is_active: {
        text: '有効',
        value: true
      },
      schedule_expression: "cron(0 18 27 * ? *)",
      next: 'next date',
      created_at: "2018-12-20T06:39:18.197261Z",
      updated_at: "2018-12-20T06:39:18.197261Z",
      name: "testname",
      action: {
        id: 'BACKUP',
        name: 'バックアップ'
      },
      notification: {
        text: '有効',
        value: true
      },
      params: {"noReboot": true},
      resource: "i-1123456789",
      service: service,
      region: region
    }]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getSchedules = jest.fn().mockImplementation((cid, a, r, s, rid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(awsAccount)
      expect(r).toBe(region)
      expect(s).toBe(service)
      expect(rid).toBe(resourceId)
      return Promise.resolve({data: responseData})
    })

    const commit = jest.fn()
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.fetchSchedules({
      commit, rootGetters, dispatch
    }, [awsAccount, region, service, resourceId]).then((res) => {
      expect(res.data).toEqual(expectData)
      expect(commit).toHaveBeenCalledWith('schedules', [])
      expect(commit).toHaveBeenCalledWith('schedules', expectData)
      done()
    })
  })

  it('actions.addSchedule', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const resource = {
      aws_environment: 'test aws account',
      region: 'test_region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const data = {
      name: "test",
      is_active: true,
      action: "START",
      schedule_expression: "cron(0 15 L * ? *)",
      params: {},
      notification: true
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addSchedule = jest.fn().mockImplementation((cid, a, r, s, rid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const state = {
      resource: resource,
      metrics: []
    }
    const dispatch = jest.fn()
    resourceDetail.actions.addSchedule({state, rootGetters, dispatch}, data).then(() => {
      expect(httpClient.tenant.addSchedule).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `スケジュール ${data.name} を作成しました。`, {root: true})
      done()
    })
  })

  it('actions.editSchedule', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const scheduleId = 123
    const resource = {
      aws_environment: 'test aws account',
      region: 'test_region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const data = {
      name: "test",
      is_active: true,
      action: "START",
      schedule_expression: "cron(0 15 L * ? *)",
      params: {},
      notification: true
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.editSchedule = jest.fn().mockImplementation((cid, a, r, s, rid, sid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      expect(sid).toBe(scheduleId)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const state = {
      resource: resource,
      metrics: []
    }
    const dispatch = jest.fn()
    resourceDetail.actions.editSchedule({state, rootGetters, dispatch}, [scheduleId, data]).then(() => {
      expect(httpClient.tenant.editSchedule).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id, scheduleId, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `スケジュール ${data.name} を編集しました。`, {root: true})
      done()
    })
  })

  it('actions.deleteSchedule', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const scheduleId = 38
    const resource = {
      aws_environment: 'test aws account',
      region: 'test_region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const target = {
      id: scheduleId,
      is_active: {
        text: '有効',
        value: true
      },
      schedule_expression: "cron(0 18 27 * ? *)",
      next: 'next date',
      created_at: "2018-12-20T06:39:18.197261Z",
      updated_at: "2018-12-20T06:39:18.197261Z",
      name: "testname",
      action: {
        id: 'BACKUP',
        name: 'バックアップ'
      },
      notification: {
        text: '有効',
        value: true
      },
      params: {"noReboot": true},
      resource: "i-1123456789",
      service: 'EC2',
      region: 'test_region'
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.deleteSchedule = jest.fn().mockImplementation((cid, a, r, s, rid, sid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      expect(sid).toBe(scheduleId)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const state = {
      resource: resource,
      schedules: [target],
      metrics: []
    }
    const dispatch = jest.fn()
    resourceDetail.actions.deleteSchedule({state, rootGetters, dispatch}, scheduleId).then(() => {
      expect(httpClient.tenant.deleteSchedule).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id, scheduleId)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `スケジュール ${target.name} を削除しました。`, {root: true})
      done()
    })
  })

  it('actions.fetchMonitorGraph', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const awsAccount = 'test account'
    const region = 'test reigon'
    const service = 'EC2'
    const resourceId = 'test id'
    const metricName = 'CPUUtilization'
    const data = {
      start_time: "2018-12-14T14:07:28+09:00",
      end_time: "2018-12-21T14:07:28+09:00",
      period: 300,
      stat: "Average"
    }

    const responseData = {"timestamps": ["2018-12-14T07:32:00Z", "2018-12-19T11:02:00Z"], "values": [50.0, 100.0]}
    const expectData = {
      labels: ['2018/12/14 16:32', '2018/12/19 20:02'],
      datasets: [{
        data: responseData.values,
        backgroundColor: 'rgba(0, 119, 204, 0.8)',
        borderColor: 'rgba(0, 119, 204, 0.3)',
        borderWidth: 1,
        fill: false,
        pointRadius: 2
      }],
      yHighlightRanges: {
        danger: {
          begin: 90,
          end: 100 + 100000,
          color: 'rgba(255,138, 128, 0.4)'
        },
        caution: {
          begin: 70,
          end: 90,
          color: 'rgba(255,213, 79, 0.4)'
        }
      }
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getMonitorGraph = jest.fn().mockImplementation((cid, a, r, s, rid, m, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(awsAccount)
      expect(r).toBe(region)
      expect(s).toBe(service)
      expect(rid).toBe(resourceId)
      expect(m).toBe(metricName)
      expect(d).toBe(data)
      return Promise.resolve({data: responseData})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    const state = {
      metrics: [{
        metric_name: "CPUUtilization",
        values: {caution: 70, danger: 90},
        enabled: {value: true, name: "有効"},
        period: 300,
        evaluation_period: 1,
        statistic: "Average",
        comparison_operator: "GreaterThanOrEqualToThreshold",
        status: {id: "OK", name: "正常", sortText: "1", icon: "mdi-checkbox-marked-circle", color: "green"},
        name: "CPU使用率",
        unit: "%"
      }]
    }
    resourceDetail.actions.fetchMonitorGraph({
      state, commit, rootGetters, dispatch
    }, [awsAccount, region, service, resourceId, metricName, data]).then((res) => {
      expect(res.data).toEqual(responseData)
      expect(commit).toHaveBeenCalledWith('monitorGraph', {"datasets": [], "labels": []})
      expect(commit).toHaveBeenCalledWith('monitorGraph', expectData)
      done()
    })
  })

  it('actions.fetchDocuments', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const awsAccount = 'test account'
    const region = 'test reigon'

    const responseData = [{name: "AWS-RunShellScript", parameters: []}]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getDocuments = jest.fn().mockImplementation((cid, a, r) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(awsAccount)
      expect(r).toBe(region)
      return Promise.resolve({data: responseData})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.fetchDocuments({
      commit, rootGetters, dispatch
    }, [awsAccount, region]).then((res) => {
      expect(res.data).toEqual(responseData)
      expect(httpClient.tenant.getDocuments).toHaveBeenCalledWith(userData.tenant.id, awsAccount, region)
      done()
    })
  })

  it('actions.fetchDocument', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const awsAccount = 'test account'
    const region = 'test reigon'
    const documentName = 'test documentName'

    const responseData = [{name: "AWS-RunShellScript", parameters: [
      {key: "commands", value: null, description: "test"}]}]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getDocumentDetail = jest.fn().mockImplementation((cid, a, r, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(awsAccount)
      expect(r).toBe(region)
      expect(d).toBe(documentName)
      return Promise.resolve({data: responseData})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.fetchDocument({
      commit, rootGetters, dispatch
    }, [awsAccount, region, documentName]).then((res) => {
      expect(res.data).toEqual(responseData)
      expect(httpClient.tenant.getDocumentDetail).toHaveBeenCalledWith(userData.tenant.id, awsAccount, region, documentName)
      done()
    })
  })

  it('actions.runCommand', (done) => {
    const resourceDetail = require('@/store/modules/resourceDetail').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }
    const resource = {
      aws_environment: 'test aws account',
      region: 'test region',
      service: 'EC2',
      id: 'test id',
      name: 'test name'
    }
    const data = {

    }
    const responseData = [{name: "AWS-RunShellScript", parameters: [
      {key: "commands", value: null, description: "test"}]}]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.runCommand = jest.fn().mockImplementation((cid, a, r, s, rid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(a).toBe(resource.aws_environment)
      expect(r).toBe(resource.region)
      expect(s).toBe(resource.service)
      expect(rid).toBe(resource.id)
      expect(d).toBe(data)
      return Promise.resolve({data: responseData})
    })

    const state = {
      resource: resource
    }
    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    resourceDetail.actions.runCommand({
      state, commit, rootGetters, dispatch
    }, data).then((res) => {
      expect(res.data).toEqual(responseData)
      expect(httpClient.tenant.runCommand).toHaveBeenCalledWith(userData.tenant.id, resource.aws_environment, resource.region, resource.service, resource.id, data)
      done()
    })
  })
})