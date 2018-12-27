import Enum from '@/lib/definition/enum'

export default new Enum({
  OK: {
    id: 'OK',
    name: '正常',
    sortText: '1',
    icon: 'mdi-checkbox-marked-circle',
    color: 'green'
  },
  CAUTION: {
    id: 'CAUTION',
    name: '警告',
    sortText: '2',
    icon: 'mdi-alert',
    color: 'amber'
  },
  DANGER: {
    id: 'DANGER',
    name: '危険',
    sortText: '3',
    icon: 'mdi-alert-circle',
    color: 'deep-orange'
  },
  UNSET: {
    id: 'UNSET',
    name: '未設定',
    sortText: '4',
    icon: 'mdi-alert-circle-outline',
    color: 'blue-grey'
  }
})