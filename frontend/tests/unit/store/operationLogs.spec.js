import store from '@/store'

describe('store/modules/operationLogs', () => {
  it('mutations.operationLogs', (done) => {
    const operationLogs = require('@/store/modules/operationLogs').default

    const state = {
      operationLogs: []
    }

    const data = [{
      id: 'id1',
      operation: 'operation_id1'
    }, {
      id: 'id2',
      operation: 'operation_id2'
    }]

    operationLogs.mutations.operationLogs(state, data)

    expect(state['operationLogs']).toBe(data)
    done()
  })

  it('actions.fetchOperationLogs', (done) => {
    const operationLogs = require('@/store/modules/operationLogs').default
    const tenantId = 'test tenant id'
    const data = [{
      id: 'id1',
      operation: 'operation_id1'
    }, {
      id: 'id2',
      operation: 'operation_id2'
    }]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getOperationLog = jest.fn().mockImplementation((c) => {
      expect(c).toBe(tenantId)
      return Promise.resolve({data: data})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': {
        tenant: {
          id: tenantId
        }
      }
    }

    operationLogs.actions.fetchOperationLogs({commit, rootGetters}).then(() => {
      expect(commit).toHaveBeenCalledWith('operationLogs', data)
      done()
    })
  })
})