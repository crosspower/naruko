import httpClient from '@/lib/httpClient'

// state
const state = {
  isLoggedIn: false,
  token: null,
  isTokenExpired: false,
  userData: null
}

// getters
const getters = {
  isLoggedIn: state => state.isLoggedIn,
  userData: state => state.userData,
  isTokenExpired: state => state.isTokenExpired
}

// mutations
const mutations = {
  loggedIn(state, data) {
    state.token = data.token
    state.userData = data.user
    state.isLoggedIn = true
  },
  loggedOut(state) {
    state.token = null
    state.userData = null
    state.isLoggedIn = false
  },
  userData(state, user) {
    state.userData = user
  },
  isTokenExpired(state, data) {
    state.isTokenExpired = data
  }
}

// actions
const actions = {
  login({commit}, [email, password]) {
    // ログイン処理
    return httpClient.auth.login(email, password).then(res => {
      httpClient.defaults.headers.common['Authorization'] = `JWT ${res.data.token}`
      localStorage.setItem('token', res.data.token)
      commit('loggedIn', res.data)
      return Promise.resolve(res)
    })
  },
  logout({commit}) {
    // ログアウト処理
    localStorage.clear()
    delete httpClient.defaults.headers.common['Authorization']
    commit('isTokenExpired', false)
    commit('loggedOut')
  },
  verifyToken({commit}) {
    // トークンを検証する
    const token = localStorage.getItem('token')
    if (token) {
      return httpClient.auth.verify(token).then((res) => {
        httpClient.defaults.headers.common['Authorization'] = `JWT ${res.data.token}`
        commit('loggedIn', res.data)
        return Promise.resolve(res)
      }).catch((err) => {
        commit('isTokenExpired', true)
        return Promise.reject(err)
      })
    } else {
      commit('loggedOut')
    }
  },
  updateUser({commit, state, dispatch}, data) {
    // ユーザー情報を更新する
    return httpClient.tenant.editUser(state.userData.tenant.id, state.userData.id, data).then((res) => {
      localStorage.setItem('token', res.data.token)
      httpClient.defaults.headers.common['Authorization'] = `JWT ${res.data.token}`
      commit('userData', res.data.user)
      dispatch('alert/pushSuccessAlert', `ユーザー ${data.name} (${data.email})を編集しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `ユーザー ${data.name} (${data.email})の編集に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  tokenExpired({commit}) {
    commit('isTokenExpired', true)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}