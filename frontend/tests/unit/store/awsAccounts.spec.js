import store from '@/store'

describe('store/modules/awsAccounts', () => {
  it('mutations.awsAccounts', (done) => {
    const awsAccounts = require('@/store/modules/awsAccounts').default

    const state = {
      awsAccounts: []
    }

    const data = [{
      id: 'id1',
      aws_account_id: 'aws_account_id1',
      aws_role: 'aws_role1',
      aws_external_id: 'aws_external_id1'
    }, {
      id: 'id2',
      aws_account_id: 'aws_account_id2',
      aws_role: 'aws_role2',
      aws_external_id: 'aws_external_id2'
    }]

    awsAccounts.mutations.awsAccounts(state, data)

    expect(state['awsAccounts']).toBe(data)
    done()
  })

  it('actions.fetchAwsAccounts', (done) => {
    const awsAccounts = require('@/store/modules/awsAccounts').default
    const tenantId = 'test tenant id'
    const data = [{
      id: 'id1',
      aws_account_id: 'aws_account_id1',
      aws_role: 'aws_role1',
      aws_external_id: 'aws_external_id1'
    }, {
      id: 'id2',
      aws_account_id: 'aws_account_id2',
      aws_role: 'aws_role2',
      aws_external_id: 'aws_external_id2'
    }]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getAwsAccount = jest.fn().mockImplementation((c) => {
      expect(c).toBe(tenantId)
      return Promise.resolve({data: {aws_environments: data}})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': {
        tenant: {
          id: tenantId
        }
      }
    }

    awsAccounts.actions.fetchAwsAccounts({commit, rootGetters}).then(() => {
      expect(commit).toHaveBeenCalledWith('awsAccounts', data)
      done()
    })
  })

  it('actions.addAwsAccount', (done) => {
    const awsAccounts = require('@/store/modules/awsAccounts').default
    const tenantId = 'test tenant id'
    const name = 'test name'
    const aws_account_id = 'test id'
    const aws_role = 'test role'
    const aws_external_id = 'test external id'

    const data = {
      name,
      aws_account_id,
      aws_role,
      aws_external_id
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addAwsAccount = jest.fn().mockImplementation((c, d) => {
      expect(c).toBe(tenantId)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': {
        tenant: {
          id: tenantId
        }
      }
    }
    const dispatch = jest.fn()
    awsAccounts.actions.addAwsAccount({rootGetters, dispatch}, data).then(() => {
      expect(httpClient.tenant.addAwsAccount).toHaveBeenCalledWith(tenantId, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `test name を登録しました。`, {root: true})
      done()
    })
  })

  it('actions.editAwsAccount', (done) => {
    const awsAccounts = require('@/store/modules/awsAccounts').default
    const tenantId = 'test tenant id'
    const awsAccountId = 'test aws account id'
    const name = 'test name'
    const data = {
      name
    }


    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.editAwsAccount = jest.fn().mockImplementation((c, a, d) => {
      expect(c).toBe(tenantId)
      expect(a).toBe(awsAccountId)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': {
        tenant: {
          id: tenantId
        }
      }
    }
    const dispatch = jest.fn()
    awsAccounts.actions.editAwsAccount({rootGetters, dispatch}, [awsAccountId, data]).then(() => {
      expect(httpClient.tenant.editAwsAccount).toHaveBeenCalledWith(tenantId, awsAccountId, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `test name を編集しました。`, {root: true})
      done()
    })
  })

  it('actions.deleteAwsAccount', (done) => {
    const awsAccounts = require('@/store/modules/awsAccounts').default

    const tenantId = 1
    const awsAccountId = 1

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.deleteAwsAccount = jest.fn().mockImplementation((c, a) => {
      expect(c).toBe(tenantId)
      expect(a).toBe(awsAccountId)
      return Promise.resolve()
    })

    const state = {
      awsAccounts: [{id: 1, name: 'test name'}]
    }
    const rootGetters = {
      'user/userData': {
        tenant: {
          id: tenantId
        }
      }
    }
    const dispatch = jest.fn()
    awsAccounts.actions.deleteAwsAccount({state, rootGetters, dispatch}, awsAccountId).then(() => {
      expect(httpClient.tenant.deleteAwsAccount).toHaveBeenCalledWith(tenantId, awsAccountId)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `test name を削除しました。`, {root: true})
      done()
    })
  })
})