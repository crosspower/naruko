import store from '@/store'

describe('store/modules/resources', () => {
  it('mutations.resources', (done) => {
    const tenants = require('@/store/modules/tenants').default

    const state = {
      tenants: []
    }

    const data = [{
      id: 'id1',
      tenant_name: 'tenant_name1',
      email: 'email1@email.com',
      tel: '03-1234-5678',
      aws_environment: [{}, {}]
    }, {
      id: 'id2',
      tenant_name: 'tenant_name2',
      email: 'email2@email.com',
      tel: '03-1234-5678',
      aws_environment: [{}, {}]
    }]

    tenants.mutations.tenants(state, data)

    expect(state['tenants']).toBe(data)
    done()
  })

  it('actions.fetchTenants', (done) => {
    const tenants = require('@/store/modules/tenants').default
    const data = {
      tenants: [
        {
          id: 'id1',
          tenant_name: 'tenant_name1',
          email: 'email1@email.com',
          tel: '03-1234-5678',
          aws_environment: [{}, {}]
        }, {
          id: 'id2',
          tenant_name: 'tenant_name2',
          email: 'email2@email.com',
          tel: '03-1234-5678',
          aws_environment: [{}, {}]
        }
      ]
    }

    const expectData = [
      {
        id: 'id1',
        tenant_name: 'tenant_name1',
        email: 'email1@email.com',
        tel: '03-1234-5678',
        aws_environment: [{}, {}]
      }, {
        id: 'id2',
        tenant_name: 'tenant_name2',
        email: 'email2@email.com',
        tel: '03-1234-5678',
        aws_environment: [{}, {}]
      }
    ]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getTenants = jest.fn().mockImplementation(() => {
      return Promise.resolve({data: data})
    })

    const commit = jest.fn();

    tenants.actions.fetchTenants({commit}).then(() => {
      expect(commit).toHaveBeenCalledWith('tenants', expectData)
      done()
    })
  })

  it('actions.addTenant', (done) => {
    const tenants = require('@/store/modules/tenants').default

    const tenant_name = 'test tenant'
    const email = 'test@test.com'
    const tel = '03-1234-1234'
    const username = 'testuser'
    const userEmail = 'userEmail@test.com'
    const data = {
      tenant: {
        tenant_name,
        email,
        tel
      },
      user: {
        name: username,
        email: userEmail
      }
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addTenant = jest.fn().mockImplementation((d) => {
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const dispatch = jest.fn();
    tenants.actions.addTenant({dispatch}, data).then(() => {
      expect(httpClient.tenant.addTenant).toHaveBeenCalledWith(data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `test tenant を登録しました。`, {root: true})
      done()
    })
  })

  it('actions.editTenant', (done) => {
    const tenants = require('@/store/modules/tenants').default

    const tenantId = 1
    const tenant_name = 'test tenant'
    const email = 'test@test.com'
    const tel = '03-1234-1234'

    const data = {
      tenant_name,
      email,
      tel
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.editTenant = jest.fn().mockImplementation((id, d) => {
      expect(id).toBe(tenantId)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const dispatch = jest.fn();
    tenants.actions.editTenant({dispatch}, [tenantId, data]).then(() => {
      expect(httpClient.tenant.editTenant).toHaveBeenCalledWith(tenantId, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `test tenant を編集しました。`, {root: true})
      done()
    })
  })

  it('actions.deleteTenant', (done) => {
    const tenants = require('@/store/modules/tenants').default

    const tenantId = 1

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.deleteTenant = jest.fn().mockImplementation((id) => {
      expect(id).toBe(tenantId)
      return Promise.resolve()
    })
    const state = {
      tenants: [
        {
          id: 1,
          tenant_name: 'test tenant'
        }
      ]
    }
    const dispatch = jest.fn();
    tenants.actions.deleteTenant({state, dispatch}, tenantId).then(() => {
      expect(httpClient.tenant.deleteTenant).toHaveBeenCalledWith(tenantId)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `test tenant を削除しました。`, {root: true})
      done()
    })
  })
})