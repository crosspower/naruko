import Enum from '@/lib/definition/enum'

export default new Enum({
  '1day': {id: '1day', name: '1日', months: 0, days: 1, period: 60},
  '1week': {id: '1week', name: '1周間', months: 0, days: 7, period: 300},
  '1month': {id: '1month', name: '1月', months: 1, days: 0, period: 600},
  '3months': {id: '3months', name: '3月', months: 3, days: 0, period: 3600},
  '6months': {id: '6months', name: '6月', months: 6, days: 0, period: 3600},
  '1year': {id: '1year', name: '1年', months: 12, days: 0, period: 3600}
})