import Vue from 'vue'
import Router from 'vue-router'
import store from './store'
import ROLE from '@/lib/definition/role'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'index',
      meta: {
        isPublic: true,
        role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
      },
      component: () => import(/* webpackChunkName: "home" */ './views/Index.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      meta: {
        role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
      },
      component: () => import(/* webpackChunkName: "dashboard" */ './views/dashboard/Dashboard.vue')
    },
    {
      path: '/resources',
      meta: {
        role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
      },
      component: () => import(/* webpackChunkName: "resources" */ './views/resources/Resources.vue')
    },
    {
      path: '/resources/monitoring',
      meta: {
        role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
      },
      component: () => import(/* webpackChunkName: "resourceDetail" */ './views/resources/detail/ResourceDetail.vue'),
      children: [
        {
          path: '',
          name: 'monitoring',
          meta: {
            role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
          },
          component: () => import(/* webpackChunkName: "monitoring" */ './views/resources/detail/monitoring/Monitoring.vue')
        },
        {
          path: '/resources/schedule',
          name: 'schedule',
          meta: {
            role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
          },
          component: () => import(/* webpackChunkName: "schedule" */ './views/resources/detail/schedule/Schedule.vue')
        },
        {
          path: '/resources/backup',
          name: 'backup',
          meta: {
            role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
          },
          component: () => import(/* webpackChunkName: "backup" */ './views/resources/detail/backup/Backup.vue')
        }
      ]
    },
    {
      path: '/aws-accounts',
      name: 'aws-accounts',
      meta: {
        role: [ROLE.MASTER.id, ROLE.ADMIN.id]
      },
      component: () => import(/* webpackChunkName: "awsAccounts" */ './views/awsAccounts/AwsAccounts.vue')
    },
    {
      path: '/users',
      name: 'users',
      meta: {
        role: [ROLE.MASTER.id, ROLE.ADMIN.id]
      },
      component: () => import(/* webpackChunkName: "users" */ './views/users/Users.vue')
    },
    {
      path: '/usersettings',
      name: 'usersettings',
      meta: {
        role: [ROLE.MASTER.id, ROLE.ADMIN.id, ROLE.USER.id]
      },
      component: () => import(/* webpackChunkName: "usersettings" */ './views/userSettings/UserSettings.vue')
    },
    {
      path: '/tenants',
      name: 'tenants',
      meta: {
        role: [ROLE.MASTER.id]
      },
      component: () => import(/* webpackChunkName: "tenants" */ './views/tenants/Tenants.vue')
    },
    {
      path: '/costs',
      name: 'costs',
      meta: {
        role: [ROLE.ADMIN.id, ROLE.MASTER.id]
      },
      component: () => import(/*webpackChunkName: "costs" */ './views/cost/Cost.vue')
    },
    {
      path: '/notifications',
      name: 'notifications',
      meta: {
        role: [ROLE.MASTER.id, ROLE.ADMIN.id]
      },
      component: () => import(/* webpackChunkName: "notifications" */ './views/notifications/Notifications.vue')
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  try {
    store.dispatch('resources/cancelFetch')

    // isPublic でない場合ログイン状態を確認する
    if (to.matched.some(record => !record.meta.isPublic)) {
      await store.dispatch('user/verifyToken').catch(() => {
        // トークン有効期限切れ
        store.dispatch('user/tokenExpired')
        next({path: '/', query: {redirect: to.fullPath}})
      })

      if (!store.getters['user/isLoggedIn']) {
        next({path: '/', query: {redirect: to.fullPath}})
      }

      // ユーザーロールを確認する
      if (to.meta.role.indexOf(store.getters['user/userData'].role.id) <= -1) {
        next({path: '/', query: {redirect: to.fullPath}})
      }
    }
    next()
  } catch (e) {
    next({path: '/', query: {redirect: to.fullPath}})
  }
})


export default router
