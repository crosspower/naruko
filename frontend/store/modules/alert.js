// state
const state = {
  alerts: []
}

// getters
const getters = {
  alerts: state => state.alerts
}

// mutations
const mutations = {
  alerts(state, data) {
    state.alerts = data
  }
}

// actions
const actions = {
  pushAlert({state}, [type, icon, msg]) {
    const alert = {
      key: state.alerts.length,
      type: type,
      icon: icon,
      msg: msg,
      value: true
    }
    state.alerts.push(alert)
    window.setTimeout(function () {
      alert.value = false
    }, 10000)
  },
  pushInfoAlert({dispatch}, msg) {
    dispatch('pushAlert', ['info', 'mdi-alert-circle', msg])
  },
  pushSuccessAlert({dispatch}, msg) {
    dispatch('pushAlert', ['success', 'mdi-alert-circle', msg])
  },
  pushWarningAlert({dispatch}, msg) {
    dispatch('pushAlert', ['warning', 'mdi-alert-circle', msg])
  },
  pushErrorAlert({dispatch}, msg) {
    dispatch('pushAlert', ['error', 'mdi-alert-circle', msg])
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}