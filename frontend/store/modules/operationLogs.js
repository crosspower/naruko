import httpClient from '@/lib/httpClient'
import moment from 'moment-timezone'

// state
const state = {
  operationLogs: []
}

// getters
const getters = {
  operationLogs: state => state.operationLogs
}

// mutations
const mutations = {
  operationLogs(state, data) {
    state.operationLogs = data
  }
}

// actions
const actions = {
  fetchOperationLogs({commit, rootGetters, dispatch}) {
    return httpClient.tenant.getOperationLog(rootGetters['user/userData'].tenant.id).then((res) => {
      for (const log of res.data) {
        log.created_at = moment(new Date(log.created_at)).format("YYYY/MM/DD HH:mm:ss")
        log.executor = log.executor == null ? {name: '-'} : log.executor
      }
      commit('operationLogs', res.data)
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', '操作ログの取得に失敗しました。', {root: true})
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