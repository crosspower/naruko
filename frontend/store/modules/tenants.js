import httpClient from '@/lib/httpClient'

// state
const state = {
  tenants: []
}

// getters
const getters = {
  tenants: state => state.tenants
}

// mutations
const mutations = {
  tenants(state, data) {
    state.tenants = data
  }
}

// actions
const actions = {
  fetchTenants({commit, dispatch}) {
    return httpClient.tenant.getTenants().then((res) => {
      commit('tenants', res.data.tenants)
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', 'テナント情報の取得に失敗しました。', {root: true})
      return Promise.reject(res)
    })
  },
  addTenant({dispatch}, data) {
    return httpClient.tenant.addTenant(data).then((res) => {
      dispatch('alert/pushSuccessAlert', `${data.tenant.tenant_name} を登録しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `${data.tenant.tenant_name} の登録に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  editTenant({dispatch}, [tenantId, data]) {
    return httpClient.tenant.editTenant(tenantId, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `${data.tenant_name} を編集しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `${data.tenant_name} の編集に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  deleteTenant({state, dispatch}, tenantId) {
    const target = state.tenants.find(c => c.id === tenantId)
    if (!target) {
      dispatch('alert/pushErrorAlert', `存在しないテナントです。`, {root: true})
      return Promise.reject()
    }
    return httpClient.tenant.deleteTenant(tenantId).then((res) => {
      dispatch('alert/pushSuccessAlert', `${target.tenant_name} を削除しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `${target.tenant_name} の削除に失敗しました。`, {root: true})
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