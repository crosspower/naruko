import httpClient from '@/lib/httpClient'
import DESTINATION_TYPES from '@/lib/definition/destinationTypes'


// state
const state = {
  destinations: [],
  groups: []
}

// getters
const getters = {
  destinations: state => state.destinations,
  groups: state => state.groups
}

// mutations
const mutations = {
  destinations(state, data) {
    state.destinations = data
  },
  groups(state, data) {
    state.groups = data
  }
}

// actions
const actions = {
  fetchDestinations({commit, rootGetters, dispatch}) {
    return httpClient.tenant.getNotificationDestinations(rootGetters['user/userData'].tenant.id).then((res) => {
      for (const dest of res.data) {
        // 通知先のタイプを取得する
        dest.type = DESTINATION_TYPES[dest.type]

        // 表示用の値を取得する
        if (dest.type.id === DESTINATION_TYPES.email.id) {
          dest.value = dest.address
        } else if (dest.type.id === DESTINATION_TYPES.telephone.id) {
          dest.value = dest.phone_number
        }
      }
      commit('destinations', res.data)
      return Promise.resolve(res)
    }).catch((err) => {
      dispatch('alert/pushErrorAlert', '通知先の取得に失敗しました。', {root: true})
      return Promise.reject(err)
    })
  },
  addDestination({rootGetters, dispatch}, data) {
    return httpClient.tenant.addNotificationDestination(rootGetters['user/userData'].tenant.id, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `通知先 ${data.name} を登録しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `通知先 ${data.name} の登録に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  deleteDestination({state, rootGetters, dispatch}, id) {
    const target = state.destinations.find(d => d.id === id)
    if (!target) {
      dispatch('alert/pushErrorAlert', `存在しない通知先です。`, {root: true})
      return Promise.reject()
    }

    return httpClient.tenant.deleteNotificationDestination(rootGetters['user/userData'].tenant.id, id).then((res) => {
      dispatch('alert/pushSuccessAlert', `通知先 ${target.name} を削除しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `通知先 ${target.name} の削除に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  fetchNotificationGroup({commit, rootGetters, dispatch}) {
    return httpClient.tenant.getNotificationGroups(rootGetters['user/userData'].tenant.id).then((res) => {
      commit('groups', res.data)
      return Promise.resolve(res)
    }).catch((err) => {
      dispatch('alert/pushErrorAlert', '通知グループの取得に失敗しました。', {root: true})
      return Promise.reject(err)
    })
  },
  addNotificationGroup({rootGetters, dispatch}, data) {
    return httpClient.tenant.addNotificationGroup(rootGetters['user/userData'].tenant.id, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `通知グループ ${data.name} を登録しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `通知グループ ${data.name} の登録に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  editNotificationGroup({rootGetters, dispatch}, [groupId, data]) {
    return httpClient.tenant.editNotificationGroup(rootGetters['user/userData'].tenant.id, groupId, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `通知グループ ${data.name} を編集しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `通知グループ ${data.name} の編集に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  deleteNotificationGroup({state, rootGetters, dispatch}, groupId) {
    const target = state.groups.find(g => g.id === groupId)
    if (!target) {
      dispatch('alert/pushErrorAlert', `存在しない通知グループです。`, {root: true})
      return Promise.reject()
    }
    return httpClient.tenant.deleteNotificationGroup(rootGetters['user/userData'].tenant.id, groupId).then((res) => {
      dispatch('alert/pushSuccessAlert', `通知グループ ${target.name} を削除しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `通知グループ ${name} の削除に失敗しました。`, {root: true})
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