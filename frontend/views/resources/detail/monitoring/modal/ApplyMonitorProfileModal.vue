<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="650">
            <v-card>
                <v-card-title class="headline">
                    <v-icon class="pr-2">mdi-settings</v-icon>
                    一括設定
                </v-card-title>
                <v-card-text>
                    次の監視項目を設定します。
                    <v-expansion-panel
                            v-model="panel"
                            expand
                            popout>
                        <v-expansion-panel-content
                                v-for="(item,i) in profiles"
                                :key="i"
                        >
                            <template slot="header">{{getMetricName(item.metric_name)}}</template>
                            <v-card>
                                <v-layout align-center justify-start row>
                                    <v-flex xs3>
                                        <v-card class="text-xs-right">
                                            <v-card-text class="pa-0">警告閾値：</v-card-text>
                                        </v-card>
                                    </v-flex>
                                    <v-flex xs6>
                                        <v-card class="pa-0 text-xs-left">
                                            <v-card-text class="pa-0 pl-1">
                                                {{getMetricName(item.metric_name)}}
                                                {{getComparisonOperator(item.metric_name)}}
                                                {{item.values.caution}}
                                                {{getMetricUnit(item.metric_name)}}
                                            </v-card-text>
                                        </v-card>
                                    </v-flex>
                                </v-layout>
                                <v-layout align-center justify-start row>
                                    <v-flex xs3>
                                        <v-card class="text-xs-right">
                                            <v-card-text class="pa-0">危険閾値：</v-card-text>
                                        </v-card>
                                    </v-flex>
                                    <v-flex xs6>
                                        <v-card class="pa-0 text-xs-left">
                                            <v-card-text class="pa-0 pl-1">
                                                {{getMetricName(item.metric_name)}}
                                                {{getComparisonOperator(item.metric_name)}}
                                                {{item.values.danger}}
                                                {{getMetricUnit(item.metric_name)}}
                                            </v-card-text>
                                        </v-card>
                                    </v-flex>
                                </v-layout>

                                <v-layout align-center justify-start row>
                                    <v-flex xs3>
                                        <v-card class="text-xs-right">
                                            <v-card-text class="pa-0">統計：</v-card-text>
                                        </v-card>
                                    </v-flex>
                                    <v-flex xs6>
                                        <v-card class="pa-0 text-xs-left">
                                            <v-card-text class="pa-0 pl-1">{{getMetricStatisticText(item.statistic)}}
                                            </v-card-text>
                                        </v-card>
                                    </v-flex>
                                </v-layout>

                                <v-layout align-center justify-start row>
                                    <v-flex xs3>
                                        <v-card class="text-xs-right">
                                            <v-card-text class="pa-0">間隔：</v-card-text>
                                        </v-card>
                                    </v-flex>
                                    <v-flex xs6>
                                        <v-card class="pa-0 text-xs-left">
                                            <v-card-text class="pa-0 pl-1">{{getMetricPeriodText(item.period)}}
                                            </v-card-text>
                                        </v-card>
                                    </v-flex>
                                </v-layout>

                                <v-layout align-center justify-start row>
                                    <v-flex xs3>
                                        <v-card class="text-xs-right">
                                            <v-card-text class="pa-0  pb-3">試行回数：</v-card-text>
                                        </v-card>
                                    </v-flex>
                                    <v-flex xs6>
                                        <v-card class="pa-0 text-xs-left">
                                            <v-card-text class="pa-0 pl-1 pb-3">{{item.evaluation_period}}</v-card-text>
                                        </v-card>
                                    </v-flex>
                                </v-layout>
                            </v-card>
                        </v-expansion-panel-content>
                    </v-expansion-panel>
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
  import MONITOR_PROFILE from '@/lib/definition/monitorProfile'
  import METRICS from '@/lib/definition/metrics'
  import STATISTICS from '@/lib/definition/statistics'
  import COMPARISON_OPERATOR from '@/lib/definition/comparisonOperator'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        panel: [],
        profiles: [],
        title: '',
        resolve: null,
        reject: null
      }
    },
    computed: {
      ...mapGetters({
        resource: 'resourceDetail/resource',
        metrics: 'resourceDetail/metrics'
      })
    },
    methods: {
      ...mapActions('resourceDetail', ['applyProfiles']),
      open() {
        this.isProgress = true

        this.profiles = MONITOR_PROFILE[this.resource.service].default

        this.isProgress = false
        this.isOpen = true

        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      confirm() {
        this.isProgress = true
        this.applyProfiles(this.profiles).then(() => {
          this.resolve(true)
        }).catch(() => {
          this.reject()
        }).finally(() => {
          this.isOpen = false
          this.isProgress = false
        })
      },
      cancel() {
        this.isOpen = false
        this.isProgress = false
        this.resolve(false)
      },
      getMetricName(metricName) {
        // メトリクスの表示名を取得する
        return METRICS[this.resource.service][metricName].name
      },
      getMetricUnit(metricName) {
        // メトリクスの単位を取得する
        return METRICS[this.resource.service][metricName].unit
      },
      getMetricStatisticText(statistic) {
        // メトリクスの統計を取得する
        return STATISTICS[statistic].name
      },
      getMetricPeriodText(period) {
        // メトリクスの期間を表示する
        const periods = [
          {value: 10, name: '10秒'},
          {value: 30, name: '30秒'},
          {value: 60, name: '1分'},
          {value: 300, name: '5分'}
        ]
        return periods.find(v => period === v.value).name
      },
      getComparisonOperator(metricName) {
        const metric = this.metrics.find(v => v.metric_name === metricName)
        return COMPARISON_OPERATOR[metric.comparison_operator].name
      }
    }
  }
</script>
<style scoped>
    .fix-prefix /deep/ input {
        width: auto;
    }
</style>