<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="650">
            <v-card>
                <v-card-title class="headline">
                    <v-icon class="pr-2">mdi-settings</v-icon>
                    {{ title }}
                </v-card-title>
                <v-card-text>
                    <v-form ref="form" v-model="valid">
                        <v-text-field
                                v-model="cautionThreshold"
                                :rules="cautionThresholdRules"
                                :disabled="isProgress"
                                type="number"
                                min="0"
                                class="fix-prefix"
                                prepend-icon="mdi-alert"
                                label="警告閾値*"
                                :prefix="thresholdPrefix"
                                :suffix="thresholdSuffix"
                        ></v-text-field>
                        <v-text-field
                                v-model="dangerThreshold"
                                :rules="dangerThresholdRules"
                                :disabled="isProgress"
                                type="number"
                                min="0"
                                class="fix-prefix"
                                prepend-icon="mdi-alert-circle"
                                label="危険閾値*"
                                :prefix="thresholdPrefix"
                                :suffix="thresholdSuffix"
                        ></v-text-field>
                        <v-select
                                prepend-icon="mdi-chart-line-variant"
                                v-model="statistic"
                                :disabled="isProgress"
                                :rules="statisticRules"
                                :items="statistics"
                                item-text="name"
                                item-value="id"
                                label="統計*"
                        ></v-select>
                        <v-select
                                prepend-icon="mdi-clock-outline"
                                v-model="period"
                                :disabled="isProgress"
                                :rules="periodRules"
                                :items="periods"
                                item-text="name"
                                item-value="value"
                                label="間隔*"
                        ></v-select>
                        <v-text-field
                                v-model="evaluationPeriod"
                                :rules="evaluationPeriodRules"
                                :disabled="isProgress"
                                type="number"
                                min="1"
                                prepend-icon="mdi-clock-outline"
                                suffix="回連続で発生した場合にアラートを発生させます。"
                                label="試行回数*"
                        ></v-text-field>
                        <v-checkbox
                                :disabled="isProgress"
                                prepend-icon="mdi-bell"
                                label="通知"
                                v-model="alertEnabled"
                        ></v-checkbox>
                    </v-form>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat
                           @click="cancel"
                           :disabled="isProgress">キャンセル
                    </v-btn>
                    <v-btn color="blue darken-1" flat
                           @click="confirm"
                           :loading="isProgress"
                           :disabled="isProgress">設定
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
  import {mapActions, mapGetters} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'
  import STATISTICS from '@/lib/definition/statistics'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        title: '',
        metric: null,
        valid: true,
        thresholdPrefix: '',
        thresholdSuffix: '',
        cautionThreshold: '',
        dangerThreshold: '',
        statistic: null,
        period: null,
        evaluationPeriod: 1,
        alertEnabled: true,
        periods: [
          {value: 10, name: '10秒'},
          {value: 30, name: '30秒'},
          {value: 60, name: '1分'},
          {value: 300, name: '5分'}
        ],
        statistics: STATISTICS.getEnums(),
        cautionThresholdRules: VALIDATION_RULE.MONITOR.CAUTION_THRESHOLD.concat(
            [
              (v) => {
                if (!this.metric) {
                  return true
                }
                if (this.metric.comparison_operator === 'GreaterThanOrEqualToThreshold') {
                  return +v <= +this.dangerThreshold || '正しい警告閾値を入力してください。'
                } else {
                  return +v >= +this.dangerThreshold || '正しい警告閾値を入力してください。'
                }
              }
            ]
        ),
        dangerThresholdRules: VALIDATION_RULE.MONITOR.DANGER_THRESHOLD.concat(
            [
              (v) => {
                if (!this.metric) {
                  return true
                }
                if (this.metric.comparison_operator === 'GreaterThanOrEqualToThreshold') {
                  return +this.cautionThreshold <= +v || '正しい危険閾値を入力してください。'
                } else {
                  return +this.cautionThreshold >= +v || '正しい危険閾値を入力してください。'
                }
              }
            ]
        ),
        statisticRules: VALIDATION_RULE.MONITOR.STATISTIC,
        periodRules: VALIDATION_RULE.MONITOR.PERIOD,
        evaluationPeriodRules: VALIDATION_RULE.MONITOR.EVALUATION_PERIOD,
        resolve: null,
        reject: null
      }
    },
    computed: {
      ...mapGetters({
        monitorGraph: 'resourceDetail/monitorGraph'
      })
    },
    methods: {
      ...mapActions('resourceDetail', ['addMonitor']),
      open(metric) {
        this.isProgress = true
        this.metric = metric

        this.title = `${metric.name}の監視設定`
        const operator = (metric.comparison_operator === 'GreaterThanOrEqualToThreshold') ? '≦' : '≧'
        this.thresholdPrefix = `${this.metric.name} ${operator} `
        this.thresholdSuffix = this.metric.unit
        this.dangerThreshold = metric.values.danger || '0'
        this.cautionThreshold = metric.values.caution || '0'
        this.evaluationPeriod = metric.evaluation_period || 1

        this.period = metric.period || 300
        this.statistic = metric.statistic || STATISTICS.Average.id
        this.alertEnabled = metric.enabled.value
        if (this.alertEnabled == null) {
          this.alertEnabled = true
        }

        this.isProgress = false
        this.isOpen = true

        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      confirm() {
        if (this.$refs.form.validate()) {
          this.isProgress = true

          const data = {
            metric_name: this.metric.metric_name,
            values: {
              caution: this.cautionThreshold,
              danger: this.dangerThreshold
            },
            enabled: this.alertEnabled,
            period: this.period,
            evaluation_period: this.evaluationPeriod,
            statistic: this.statistic
          }
          this.addMonitor(data).then(() => {
            this.resolve(true)
          }).catch(() => {
            this.reject()
          }).finally(() => {
            this.isOpen = false
            this.isProgress = false
            this.$refs.form.reset()
          })
        }
      },
      cancel() {
        this.isOpen = false
        this.isProgress = false
        this.$refs.form.reset()
        this.resolve(false)
      }
    }
  }
</script>
<style scoped>
    .fix-prefix /deep/ input {
        width: auto;
    }
</style>