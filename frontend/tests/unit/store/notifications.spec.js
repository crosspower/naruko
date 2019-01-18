import store from '@/store'

describe('store/modules/notifications', () => {

  it('mutations.destinations', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const state = {
      destinations: []
    }

    const data = [
      {dest_name: 'test_dest1'},
      {dest_name: 'test_dest2'}
    ]

    notifications.mutations.destinations(state, data)

    expect(state['destinations']).toBe(data)
    done()
  })

  it('mutations.groups', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const state = {
      groups: []
    }

    const data = [
      {group_name: 'test_group1'},
      {group_name: 'test_group2'}
    ]

    notifications.mutations.groups(state, data)

    expect(state['groups']).toBe(data)
    done()
  })

  it('actions.fetchDestinations', (done) => {
    const notifications = require('@/store/modules/notifications').default
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const responseData = [
      {
        id: 1,
        name: 'name',
        tenant: {},
        type: 'email',
        address: 'test@test.com',
        created_at: '2018-12-03T20:23:22.576000+09:00',
        updated_at: '2018-12-03T20:23:25.577000+09:00'
      },
      {
        id: 2,
        name: 'name2',
        tenant: {},
        type: 'telephone',
        phone_number: '03-1234-5678',
        created_at: '2018-12-03T20:23:22.576000+09:00',
        updated_at: '2018-12-03T20:23:25.577000+09:00'
      },
    ]

    const expectedData = [
      {
        id: 1,
        name: 'name',
        tenant: {},
        type: {
          id: 'email',
          name: 'メール'
        },
        value: "test@test.com",
        address: 'test@test.com',
        created_at: '2018-12-03T20:23:22.576000+09:00',
        updated_at: '2018-12-03T20:23:25.577000+09:00'
      },
      {
        id: 2,
        name: 'name2',
        tenant: {},
        type: {
          id: 'telephone',
          name: '電話'
        },
        value: "03-1234-5678",
        phone_number: '03-1234-5678',
        created_at: '2018-12-03T20:23:22.576000+09:00',
        updated_at: '2018-12-03T20:23:25.577000+09:00'
      }
    ]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getNotificationDestinations = jest.fn().mockImplementation((cid) => {
      expect(cid).toBe(userData.tenant.id)
      return Promise.resolve({data: responseData})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    notifications.actions.fetchDestinations({commit, rootGetters}).then((res) => {
      expect(res.data).toEqual(expectedData)
      done()
    })
  })

  it('actions.addDestinations', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const data = {
      name: 'name',
      type: 'email',
      address: 'test@test.com'
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addNotificationDestination = jest.fn().mockImplementation((cid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    notifications.actions.addDestination({rootGetters, dispatch}, data).then(() => {
      expect(httpClient.tenant.addNotificationDestination).toHaveBeenCalledWith(userData.tenant.id, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `通知先 name を登録しました。`, {root: true})
      done()
    })
  })

  it('actions.addDestinations', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const data = {
      name: 'name',
      type: 'telephone',
      phone_number: '03-1234-5678'
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addNotificationDestination = jest.fn().mockImplementation((cid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    notifications.actions.addDestination({rootGetters, dispatch}, data).then(() => {
      expect(httpClient.tenant.addNotificationDestination).toHaveBeenCalledWith(userData.tenant.id, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `通知先 name を登録しました。`, {root: true})
      done()
    })
  })

  it('actions.deleteDestinations', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }
    const destinationId = 1

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.deleteNotificationDestination = jest.fn().mockImplementation((cid, did) => {
      expect(cid).toBe(userData.tenant.id)
      expect(did).toBe(destinationId)
      return Promise.resolve()
    })

    const state = {
      destinations: [
        {id: 1, name: 'name'}
      ]
    }
    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    notifications.actions.deleteDestination({state, rootGetters, dispatch}, destinationId).then(() => {
      expect(httpClient.tenant.deleteNotificationDestination).toHaveBeenCalledWith(userData.tenant.id, destinationId)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `通知先 name を削除しました。`, {root: true})
      done()
    })
  })

  it('actions.fetchNotificationGroup', (done) => {
    const notifications = require('@/store/modules/notifications').default
    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const responseData = [
      {
        id: 1,
        name: 'name',
        tenant: {},
        destinations: [],
        aws_environments: [],
        created_at: '2018-12-03T20:23:22.576000+09:00',
        updated_at: '2018-12-03T20:23:25.577000+09:00'
      }
    ]

    const expectedData = [
      {
        id: 1,
        name: 'name',
        tenant: {},
        destinations: [],
        aws_environments: [],
        created_at: '2018-12-03T20:23:22.576000+09:00',
        updated_at: '2018-12-03T20:23:25.577000+09:00'
      }
    ]

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.getNotificationGroups = jest.fn().mockImplementation((cid) => {
      expect(cid).toBe(userData.tenant.id)
      return Promise.resolve({data: responseData})
    })

    const commit = jest.fn();
    const rootGetters = {
      'user/userData': userData
    }
    notifications.actions.fetchNotificationGroup({commit, rootGetters}).then((res) => {
      expect(res.data).toEqual(expectedData)
      expect(commit).toHaveBeenCalledWith('groups', expectedData)
      done()
    })
  })

  it('actions.addNotificationGroup', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }

    const data = {
      name: 'name',
      aws_environments: [1, 2, 3],
      destinations: [1, 2, 3]
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.addNotificationGroup = jest.fn().mockImplementation((cid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    notifications.actions.addNotificationGroup({rootGetters, dispatch}, data).then(() => {
      expect(httpClient.tenant.addNotificationGroup).toHaveBeenCalledWith(userData.tenant.id, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `通知グループ name を登録しました。`, {root: true})
      done()
    })
  })

  it('actions.editNotificationGroup', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }
    const groupId = 12
    const data = {
      name: 'name',
      aws_environments: [1, 2, 3],
      destinations: [1, 2, 3]
    }

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.editNotificationGroup = jest.fn().mockImplementation((cid, gid, d) => {
      expect(cid).toBe(userData.tenant.id)
      expect(gid).toBe(groupId)
      expect(d).toBe(data)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const dispatch = jest.fn()
    notifications.actions.editNotificationGroup({rootGetters, dispatch}, [groupId, data]).then(() => {
      expect(httpClient.tenant.editNotificationGroup).toHaveBeenCalledWith(userData.tenant.id, groupId, data)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `通知グループ name を編集しました。`, {root: true})
      done()
    })
  })

  it('actions.deleteNotificationGroup', (done) => {
    const notifications = require('@/store/modules/notifications').default

    const userData = {
      tenant: {
        id: 1,
        name: 'test_tenant'
      }
    }
    const groupId = 1

    const httpClient = require('@/lib/httpClient').default
    httpClient.tenant.deleteNotificationGroup = jest.fn().mockImplementation((cid, gid) => {
      expect(cid).toBe(userData.tenant.id)
      expect(gid).toBe(groupId)
      return Promise.resolve()
    })

    const rootGetters = {
      'user/userData': userData
    }
    const state = {
      groups: [{id: 1, name: 'name'}]
    }
    const dispatch = jest.fn()
    notifications.actions.deleteNotificationGroup({state, rootGetters, dispatch}, groupId).then(() => {
      expect(httpClient.tenant.deleteNotificationGroup).toHaveBeenCalledWith(userData.tenant.id, groupId)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `通知グループ name を削除しました。`, {root: true})
      done()
    })
  })
})
