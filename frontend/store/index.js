import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import users from './modules/users'
import resources from './modules/resources'
import resourceDetail from './modules/resourceDetail'
import tenants from './modules/tenants'
import awsAccounts from './modules/awsAccounts'
import notifications from './modules/notifications'
import alert from './modules/alert'
import operationLogs from './modules/operationLogs'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    user,
    users,
    tenants,
    resources,
    resourceDetail,
    awsAccounts,
    notifications,
    alert,
    operationLogs
  }
})
