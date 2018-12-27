import METRICS from '@/lib/definition/metrics'
import Enum from '@/lib/definition/enum'

export default new Enum({
  EC2: new Enum({
    default: [
      {
        metric_name: METRICS.EC2.CPUUtilization.id,
        values: {
          caution: 72,
          danger: 90
        },
        period: 300,
        evaluation_period: 3,
        statistic: 'Average',
        enabled: true
      },
      {
        metric_name: METRICS.EC2.StatusCheckFailed.id,
        values: {
          caution: 1,
          danger: 1
        },
        period: 300,
        evaluation_period: 3,
        statistic: 'Maximum',
        enabled: true
      }
    ]
  }),
  RDS: new Enum({
    default: [
      {
        metric_name: METRICS.RDS.CPUUtilization.id,
        values: {
          caution: 72,
          danger: 90
        },
        period: 300,
        evaluation_period: 3,
        statistic: 'Average',
        enabled: true
      },
      {
        metric_name: METRICS.RDS.ReplicaLag.id,
        values: {
          caution: 24,
          danger: 30
        },
        period: 300,
        evaluation_period: 3,
        statistic: 'Average',
        enabled: true
      }
    ]
  }),
  ELB: new Enum({
    default: [
      {
        metric_name: METRICS.ELB.Latency.id,
        values: {
          caution: 24,
          danger: 30
        },
        period: 300,
        evaluation_period: 3,
        statistic: 'Average',
        enabled: true
      }
    ]
  })
})

