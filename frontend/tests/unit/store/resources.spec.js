import store from '@/store'

describe('store/modules/resources', () => {
  it('mutations.resources', (done) => {
    const resources = require('@/store/modules/resources').default

    const state = {
      resources: [],
      okCount: 0,
      cautionCount: 0,
      dangerCount: 0,
      awsEnvFilter: []
    }

    const data = [{
      id: 'id',
      name: 'name',
      service: 'service',
      status: 'OK',
      aws_environment: 1
    }]

    resources.mutations.resources(state, data)

    expect(state['resources']).toBe(data)
    done()
  })

  it('actions.fetch', (done) => {
    const Enum = require('@/lib/definition/enum').default
    const regions = require('@/lib/definition/regions')
    regions.default = new Enum({
      'ap-northeast-1': {
        id: 'ap-northeast-1',
        name: 'アジアパシフィック (東京)'
      }
    })

    const axios = require('axios').default
    axios.CancelToken = {
      cancel: jest.fn(),
      source: jest.fn().mockImplementation(() => {
        return {token: 'token'}
      })
    }

    const resources = require('@/store/modules/resources').default
    const tenantId = 1
    const awsEnv = 1
    const token = 'token'
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      },
      aws_environments: [
        {
          id: 1,
          name: 'testaws'
        }
      ]
    }
    const region = 'ap-northeast-1'
    const data = [
      {
        id: 'id1',
        name: 'name1',
        service: 'EC2',
        status: 'OK',
        aws_environment: 1
      },
      {
        id: 'id2',
        name: 'name2',
        service: 'EC2',
        status: 'CAUTION',
        aws_environment: 1
      },
      {
        id: 'id3',
        name: 'name3',
        service: 'EC2',
        status: 'DANGER',
        aws_environment: 1
      },
      {
        id: 'id4',
        name: 'name4',
        service: 'EC2',
        status: 'UNSET',
        aws_environment: 1
      }
    ]

    const expectData = [
      {
        id: 'id1',
        name: 'name1',
        service: 'EC2',
        status: {
          id: 'OK',
          name: '正常',
          sortText: '1',
          icon: 'mdi-checkbox-marked-circle',
          color: 'green'
        },
        aws_environment: {
          id: 1,
          name: 'testaws'
        }
      },
      {
        id: 'id2',
        name: 'name2',
        service: 'EC2',
        status: {
          id: 'CAUTION',
          name: '警告',
          sortText: '2',
          icon: 'mdi-alert',
          color: 'amber'
        },
        aws_environment: {
          id: 1,
          name: 'testaws'
        }
      },
      {
        id: 'id3',
        name: 'name3',
        service: 'EC2',
        status: {
          id: 'DANGER',
          name: '危険',
          sortText: '3',
          icon: 'mdi-alert-circle',
          color: 'deep-orange'
        },
        aws_environment: {
          id: 1,
          name: 'testaws'
        }
      },
      {
        id: 'id4',
        name: 'name4',
        service: 'EC2',
        status: {
          id: 'UNSET',
          name: '未設定',
          sortText: '4',
          icon: 'mdi-alert-circle-outline',
          color: 'blue-grey'
        },
        aws_environment: {
          id: 1,
          name: 'testaws'
        }
      }
    ]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getResources = jest.fn().mockImplementation((t, c, a, r) => {
      expect(t).toBe(token)
      expect(c).toBe(tenantId)
      expect(a).toBe(awsEnv)
      expect(r).toBe(region)
      return Promise.resolve({data: data})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    const state = {}
    resources.actions.fetch({commit, state, rootGetters}).then(() => {
      expect(commit).toHaveBeenCalledWith('cancelToken', {token: 'token'})
      expect(commit).toHaveBeenCalledWith('resources', [])
      expect(commit).toHaveBeenCalledWith('pushResources', expectData[0])
      expect(commit).toHaveBeenCalledWith('pushResources', expectData[1])
      expect(commit).toHaveBeenCalledWith('pushResources', expectData[2])
      done()
    })
  })
})