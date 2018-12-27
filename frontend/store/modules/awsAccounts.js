import httpClient from '@/lib/httpClient'

// state
const state = {
  awsAccounts: []
}

// getters
const getters = {
  awsAccounts: state => state.awsAccounts
}

// mutations
const mutations = {
  awsAccounts(state, data) {
    state.awsAccounts = data
  }
}

// actions
const actions = {
  fetchAwsAccounts({commit, rootGetters, dispatch}) {
    return httpClient.tenant.getAwsAccount(rootGetters['user/userData'].tenant.id).then((res) => {
      commit('awsAccounts', res.data.aws_environments)
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', 'AWSアカウントの取得に失敗しました。', {root: true})
      return Promise.reject(res)
    })
  },
  addAwsAccount({rootGetters, dispatch}, data) {
    return httpClient.tenant.addAwsAccount(rootGetters['user/userData'].tenant.id, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `${data.name} を登録しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `${data.name} の登録に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  editAwsAccount({rootGetters, dispatch}, [awsAccountId, data]) {
    return httpClient.tenant.editAwsAccount(rootGetters['user/userData'].tenant.id, awsAccountId, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `${data.name} を編集しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `${data.name} の編集に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  deleteAwsAccount({state, rootGetters, dispatch}, awsAccountId) {
    const target = state.awsAccounts.find(a => a.id === awsAccountId)
    if (!target) {
      dispatch('alert/pushErrorAlert', `存在しないAWSアカウントです。`, {root: true})
      return Promise.reject()
    }
    return httpClient.tenant.deleteAwsAccount(rootGetters['user/userData'].tenant.id, awsAccountId).then((res) => {
      dispatch('alert/pushSuccessAlert', `${target.name} を削除しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `${target.name} の削除に失敗しました。`, {root: true})
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