import Enum from '@/lib/definition/enum'
import ROLE from '@/lib/definition/role'

export default new Enum({
  dashboard: {icon: 'mdi-view-dashboard', text: 'ダッシュボード', to: '/dashboard', role: [ROLE.ADMIN.id, ROLE.MASTER.id, ROLE.USER.id]},
  resources: {icon: 'mdi-information', text: 'リソース一覧', to: '/resources', role: [ROLE.ADMIN.id, ROLE.MASTER.id, ROLE.USER.id]},
  userSettings: {
    icon: 'mdi-account-settings',
    text: 'ユーザー設定',
    to: '/usersettings',
    role: [ROLE.ADMIN.id, ROLE.MASTER.id, ROLE.USER.id]
  },
  notifications: {icon: 'mdi-bell', text: '通知設定', to: '/notifications', role: [ROLE.ADMIN.id, ROLE.MASTER.id]},
  users: {icon: 'mdi-account-multiple', text: 'ユーザー管理', to: '/users', role: [ROLE.ADMIN.id, ROLE.MASTER.id]},
  awsAccounts: {icon: 'mdi-cloud', text: 'AWSアカウント管理', to: '/aws-accounts', role: [ROLE.ADMIN.id, ROLE.MASTER.id]},
  tenants: {icon: 'mdi-domain', text: 'テナント管理', to: '/tenants', role: [ROLE.MASTER.id]},
  cost: {icon: 'mdi-currency-usd', text: '請求管理', to:'/costs', role: [ROLE.ADMIN.id, ROLE.MASTER.id]}
})
