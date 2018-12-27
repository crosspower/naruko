import store from '@/store'

describe('store/modules/user', () => {
  it('mutations.loggedIn', (done) => {
    const user = require('@/store/modules/user').default

    const state = {
      isLoggedIn: false,
      token: null,
      userData: null
    }

    const data = {token: 'test_token', user: 'userData'}

    user.mutations.loggedIn(state, data)

    expect(state['token']).toBe(data.token)
    expect(state['userData']).toBe(data.user)
    expect(state['isLoggedIn']).toBe(true)
    done()
  })

  it('mutations.loggedOut', (done) => {
    const user = require('@/store/modules/user').default
    const state = {
      isLoggedIn: true,
      token: 'test_token',
      userData: 'userData'
    }

    user.mutations.loggedOut(state)

    expect(state['token']).toBe(null)
    expect(state['userData']).toBe(null)
    expect(state['isLoggedIn']).toBe(false)
    done()
  })

  it('actions.login', (done) => {
    const user = require('@/store/modules/user').default

    const data = {token: 'test_token', user: 'userData'}
    const email = 'test@test.com'
    const password = 'pass123'


    const httpClient = require('@/lib/httpClient').default
    httpClient.auth.login = jest.fn().mockImplementation((email, password) => {
      expect(email).toBe(email)
      expect(password).toBe(password)
      return Promise.resolve({data: data})
    })

    const commit = jest.fn();

    user.actions.login({commit}, [email, password]).then(() => {
      expect(commit).toHaveBeenCalledWith('loggedIn', data)
      expect(httpClient.defaults.headers.common['Authorization']).toBe(`JWT ${data.token}`)
      expect(localStorage.setItem).toHaveBeenCalledWith('token', data.token)
      done()
    })
  })

  it('actions.logout', (done) => {
    const user = require('@/store/modules/user').default
    const token = 'test_token'


    const httpClient = require('@/lib/httpClient').default
    httpClient.defaults.headers.common['Authorization'] = `JWT ${token}`

    const commit = jest.fn();

    user.actions.logout({commit})
    expect(commit).toHaveBeenCalledWith('loggedOut')
    expect(httpClient.defaults.headers.common['Authorization']).toBe(undefined)
    expect(localStorage.clear).toHaveBeenCalled()
    done()
  })

  it('actions.verifyToken', (done) => {
    const user = require('@/store/modules/user').default

    const data = {token: 'test_token', user: 'userData'}
    localStorage.getItem.mockReturnValue(data.token)

    const httpClient = require('@/lib/httpClient').default
    httpClient.auth.verify = jest.fn().mockImplementation((t) => {
      expect(t).toBe(data.token)
      return Promise.resolve({data: data})
    })

    const commit = jest.fn();

    user.actions.verifyToken({commit}).then(() => {
      expect(commit).toHaveBeenCalledWith('loggedIn', data)
      done()
    })
  })

  it('actions.verifyToken: invalid token', (done) => {
    const user = require('@/store/modules/user').default

    const token = 'test_token'
    localStorage.getItem.mockReturnValue(token)

    const httpClient = require('@/lib/httpClient').default
    httpClient.auth.verify = jest.fn().mockImplementation((t) => {
      expect(t).toBe(token)
      return Promise.reject()
    })

    const commit = jest.fn();

    user.actions.verifyToken({commit}).then(() => {

    }).catch(() => {
      expect(commit).toHaveBeenCalledWith('isTokenExpired', true)
      done()
    })
  })

  it('actions.updateUser', (done) => {
    const user = require('@/store/modules/user').default
    const httpClient = require('@/lib/httpClient').default
    const tenantId = 1
    const userId = 2
    const name = 'testname'
    const email = 'test@test.com'
    const password = '1234567'
    const role = 3
    const aws_environments = [1, 2, 3]
    const resData = {token: 'newToken', user: 'newUserdata'}
    const postData = {
      name,
      email,
      password,
      role,
      aws_environments
    }

    httpClient.tenant.editUser = jest.fn().mockImplementation((cid, uid, d) => {
      expect(tenantId).toBe(cid)
      expect(userId).toBe(uid)
      expect(postData).toBe(d)
      return Promise.resolve({data: resData})
    })

    const commit = jest.fn()
    const dispatch = jest.fn()
    const state = {
      userData: {
        id: 2,
        tenant: {
          id: 1
        }
      }
    }
    user.actions.updateUser({commit, state, dispatch}, postData).then(() => {
      expect(httpClient.tenant.editUser).toHaveBeenCalledWith(tenantId, userId, postData)
      expect(dispatch).toHaveBeenCalledWith('alert/pushSuccessAlert', `ユーザー testname (test@test.com)を編集しました。`, {root: true})
      expect(httpClient.defaults.headers.common['Authorization']).toBe(`JWT ${resData.token}`)
      expect(commit).toHaveBeenCalledWith('userData', resData.user)
      done()
    })
  })
})