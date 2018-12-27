import httpClient from '@/lib/httpClient'
import ROLE from '@/lib/definition/role'

// state
const state = {
  users: []
}

// getters
const getters = {
  users: state => state.users
}

// mutations
const mutations = {
  users(state, data) {
    state.users = data
  }
}

// actions
const actions = {
  fetchUsers({commit, rootGetters, dispatch}) {
    return httpClient.tenant.getUsers(rootGetters['user/userData'].tenant.id).then((res) => {
      let adminUserCount = 0
      let masterUserCount = 0
      for (const user of res.data.users) {
        if (user.role.id === ROLE.ADMIN.id) {
          adminUserCount++
        }
        if (user.role.id === ROLE.MASTER.id) {
          masterUserCount++
        }

        // 検索用にAWSアカウント名を連結する
        const awsEnvList = []
        for (const awsEnv of user.aws_environments) {
          awsEnvList.push(awsEnv.name)
        }
        user.aws_environments_joined = awsEnvList.join(' ')

        user.editable = true
        user.deletable = true
        user.roleEditable = true

        // ログインユーザーがADMIN場合はMASTERユーザーを操作できない
        if (rootGetters['user/userData'].role.id === ROLE.ADMIN.id && user.role.id === ROLE.MASTER.id) {
          user.editable = false
          user.deletable = false
        }
      }

      // MASTER、ADMINの最後の一人は消せない、ロール変更不可
      if (adminUserCount === 1) {
        const user = res.data.users.find(u => u.role.id === ROLE.ADMIN.id)
        user.deletable = false
        user.roleEditable = false
      }
      if (masterUserCount === 1) {
        const user = res.data.users.find(u => u.role.id === ROLE.MASTER.id)
        user.deletable = false
        user.roleEditable = false
      }

      commit('users', res.data.users)
      return Promise.resolve()
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', 'ユーザー情報の取得に失敗しました。', {root: true})
      return Promise.reject(res)
    })
  },
  deleteUser({rootGetters, dispatch}, userId) {
    // ユーザーを削除する
    const target = state.users.find(u => u.id === userId)
    if (!target) {
      dispatch('alert/pushErrorAlert', `存在しないユーザーです。`, {root: true})
      return Promise.reject()
    }

    return httpClient.tenant.deleteUser(rootGetters['user/userData'].tenant.id, userId).then((res) => {
      dispatch('alert/pushSuccessAlert', `ユーザー ${target.name} (${target.email})を削除しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `ユーザー ${target.name} (${target.email})の削除に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  editUser({rootGetters, dispatch}, [userId, data]) {
    // ユーザーを編集する
    return httpClient.tenant.editUser(rootGetters['user/userData'].tenant.id, userId, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `ユーザー ${data.name} (${data.email})を編集しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `ユーザー ${data.name} (${data.email})の編集に失敗しました。`, {root: true})
      return Promise.reject(res)
    })
  },
  addUser({rootGetters, dispatch}, data) {
    // ユーザーを追加する
    return httpClient.tenant.addUser(rootGetters['user/userData'].tenant.id, data).then((res) => {
      dispatch('alert/pushSuccessAlert', `ユーザー ${data.name} (${data.email})を登録しました。`, {root: true})
      return Promise.resolve(res)
    }).catch((res) => {
      dispatch('alert/pushErrorAlert', `ユーザー ${data.name} (${data.email})の登録に失敗しました。`, {root: true})
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