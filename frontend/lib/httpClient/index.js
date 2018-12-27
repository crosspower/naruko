import Vue from 'vue'
import axios from 'axios'
import auth from './auth'
import tenant from './tenant'
import store from '@/store'

const httpClient = axios.create({
  baseURL: process.env.VUE_APP_API_ENDPOINT
})

httpClient.install = function (Vue) {
  Object.defineProperty(Vue.prototype, '$request', {
    get() {
      return httpClient
    }
  })
}

httpClient.auth = auth(httpClient)
httpClient.tenant = tenant(httpClient)

httpClient.interceptors.request.use(function (config) {
  // リクエストの前にトークンを更新する
  const url = config.url.replace(config.baseURL, '')

  // 認証系のURLはスキップする
  if (url.startsWith('/api/auth/')) {
    return config
  }

  // ヘッダにトークンが含まれる場合は更新する
  if (httpClient.defaults.headers.common['Authorization']) {
    const token = httpClient.defaults.headers.common['Authorization'].split(/\s/)[1]
    const payload = JSON.parse(window.atob(token.split('.')[1]))

    // トークンの有効期限に余裕がある場合はスキップ
    if (payload.exp - 60 > (Date.now() / 1000).toFixed(0)) {
      return config
    }

    // トークン更新
    httpClient.auth.refresh(token).then((res) => {
      localStorage.setItem('token', res.data.token)
      httpClient.defaults.headers.common['Authorization'] = `JWT ${res.data.token}`
      return config
    }).catch(() => {
      store.dispatch('user/tokenExpired')
      return config
    })
  }

  return config
}, function (error) {
  return Promise.reject(error)
})

Vue.use(httpClient)

export default httpClient