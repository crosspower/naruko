<template>
    <v-layout>
        <v-flex xs12>
            <v-card flat>
                <v-card-title class="pb-0">
                    <div class="subheading">{{dataTable.selectedMetric.name}}</div>
                    <v-spacer></v-spacer>
                    <v-select
                            :items="chart.periods"
                            v-model="chart.selectedPeriod"
                            item-text="name"
                            item-value="id"
                            label="期間"
                            class="pl-2"
                            dense
                            hide-details
                            :disabled="chart.isProgress"
                            @change="initChart"
                    ></v-select>
                    <v-select
                            :items="chart.statistics"
                            v-model="chart.selectedStatistic"
                            item-text="name"
                            item-value="id"
                            label="統計"
                            dense
                            hide-details
                            :disabled="chart.isProgress"
                            @change="initChart"
                    ></v-select>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               :loading="chart.isProgress"
                               :disabled="chart.isProgress"
                               @click="initChart">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>
                </v-card-title>
                <v-card class="position-relative" flat>
                    <div class="overlay-chart" v-show="chart.isProgress">
                            <span class="overlay-chart-span">
                                <v-progress-circular
                                        :size="50"
                                        color="primary"
                                        indeterminate
                                ></v-progress-circular>
                            </span>
                    </div>
                    <LineChartHighlight :chartData="monitorGraph" :options="chart.options"
                                        class="pb-4"
                                        :styles="{height: '400px', position: 'relative'}"></LineChartHighlight>
                </v-card>
            </v-card>
            <v-divider></v-divider>
            <v-card flat>
                <v-card-title class="pb-0" height="70px">
                    <div class="subheading">メトリクス一覧</div>
                </v-card-title>
                <v-card-title>
                    <v-text-field
                            v-model="dataTable.search"
                            class="pt-0"
                            append-icon="mdi-magnify"
                            label="Search"
                            single-line
                            hide-details
                            clearable
                    ></v-text-field>
                    <v-spacer></v-spacer>
                    <v-btn color="primary"
                           :loading="isProgress"
                           :disabled="isProgress"
                           @click="openApplyMonitorProfileModal">
                        <v-icon small>mdi-settings</v-icon>
                        一括設定
                    </v-btn>

                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               :loading="isProgress"
                               :disabled="isProgress"
                               @click="initDataTable">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>
                </v-card-title>
                <v-data-table
                        :headers="dataTable.headers"
                        :items="metrics"
                        :custom-filter="customFilter"
                        :search="dataTable.search"
                        :loading="isProgress"
                        :pagination.sync="dataTable.pagination">
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr @click="onSelectMetric(props.item)">
                            <td width="1%">
                                <v-radio-group hide-details
                                               v-model="dataTable.selectedMetric"
                                               name="rowSelector">
                                    <v-radio :value="props.item" :key="props.item.metric_name"></v-radio>
                                </v-radio-group>
                            </td>
                            <td>{{ props.item.name }}</td>
                            <td width="1%">
                                {{ props.item.enabled.name}}
                            </td>
                            <td width="1%">
                                <v-icon small class="pr-1" :color=props.item.status.color>
                                    {{ props.item.status.icon }}
                                </v-icon>
                                <span :class="`${props.item.status.color}--text text--darken-2`">{{ props.item.status.name }}</span>
                            </td>
                            <td class="text-xs-center" width="1%">
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="blue darken-1"
                                           @click.stop="openMonitorSettingsModal(props.item)">
                                        <v-icon small>mdi-settings</v-icon>
                                    </v-btn>
                                    <span>設定</span>
                                </v-tooltip>
                            </td>
                        </tr>
                    </template>
                    <v-alert slot="no-results" :value="true" color="error" icon="mdi-alert">
                        Your search for "{{ dataTable.search }}" found no results.
                    </v-alert>
                </v-data-table>
                <MonitorSettingsModal ref="monitorSettingsModal"></MonitorSettingsModal>
                <ApplyMonitorProfileModal ref="applyMonitorProfileModal"></ApplyMonitorProfileModal>
            </v-card>
        </v-flex>
    </v-layout>
</template>

<script>
  import {getObjectValueByPath} from 'vuetify/es5/util/helpers'
  import {mapGetters, mapActions} from 'vuex'
  import STATISTICS from '@/lib/definition/statistics'
  import PERIODS from '@/lib/definition/periods'
  import LineChartHighlight from '@/components/chart/LineChartHighlight'
  import MonitorSettingsModal from '@/views/resources/detail/monitoring/modal/MonitorSettingsModal'
  import ApplyMonitorProfileModal from "@/views/resources/detail/monitoring/modal/ApplyMonitorProfileModal"
  import moment from 'moment-timezone'


  export default {
    components: {
      LineChartHighlight,
      ApplyMonitorProfileModal,
      MonitorSettingsModal
    },
    data() {
      return {
        isProgress: false,
        dataTable: {
          isProgress: false,
          pagination: {
            sortBy: 'name',
            rowsPerPage: 10
          },
          search: '',
          selectedMetric: '',
          headers: [
            {text: '', value: 'name', filter: 'name', sortable: false, align: 'center'},
            {text: '監視項目', value: 'name', filter: 'name', align: 'left'},
            {text: '通知', value: 'enabled.name', filter: 'enabled.name', align: 'left'},
            {text: 'ステータス', value: 'status.sortText', filter: 'status.name', align: 'left'},
            {text: '', value: 'name', filter: 'name', sortable: false, align: 'center'}
          ]
        },
        chart: {
          isProgress: false,
          statistics: STATISTICS.getEnums(),
          selectedStatistic: STATISTICS.Average.id,
          periods: PERIODS.getEnums(),
          selectedPeriod: '1day',
          options: {
            legend: {
              display: false
            },
            scales: {
              yAxes: [{
                ticks: {beginAtZero: true},
                gridLines: {display: true}
              }],
              xAxes: [{
                gridLines: {display: false}
              }]
            },
            elements: {
              line: {tension: 0}
            },
            animation: {duration: 0},
            hover: {animationDuration: 0},
            responsiveAnimationDuration: 0,
            responsive: true,
            maintainAspectRatio: false
          }
        }
      }
    },
    computed: {
      ...mapGetters({
        metrics: 'resourceDetail/metrics',
        resource: 'resourceDetail/resource',
        monitorGraph: 'resourceDetail/monitorGraph'
      })
    },
    methods: {
      ...mapActions('resourceDetail', ['fetchResource', 'fetchMonitors', 'fetchMonitorGraph']),
      initDataTable() {
        this.isProgress = true
        this.fetchMonitors([
          this.$route.query.awsAccount,
          this.$route.query.region,
          this.$route.query.service,
          this.$route.query.resourceId]).then(() => {
          if (this.metrics.length > 0) {
            if (!this.dataTable.selectedMetric) {
              this.onSelectMetric(this.metrics[0])
            }
          }
          this.initChart()
        }).finally(() => {
          this.isProgress = false
        })
      },
      initChart() {
        const metric = this.dataTable.selectedMetric
        if (!metric) {
          return
        }
        this.chart.isProgress = true
        const period = PERIODS[this.chart.selectedPeriod]
        const data = {
          start_time: moment().subtract(period.days, 'day').subtract(period.months, 'month').format(),
          end_time: moment().format(),
          period: period.period,
          stat: this.chart.selectedStatistic
        }

        this.chart.options.scales.yAxes[0].scaleLabel = {
          display: true,          //表示設定
          labelString: metric.unit,  //ラベル
          fontSize: 14               //フォントサイズ
        }

        this.fetchMonitorGraph([
          this.$route.query.awsAccount,
          this.$route.query.region,
          this.$route.query.service,
          this.$route.query.resourceId,
          metric.metric_name,
          data
        ]).finally(() => {
          this.chart.isProgress = false
        })
      },
      openMonitorSettingsModal(metric) {
        this.$refs.monitorSettingsModal.open(metric).then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      },
      openApplyMonitorProfileModal() {
        this.$refs.applyMonitorProfileModal.open().then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      },
      customFilter(items, search, filter) {
        search = search.toString().toLowerCase()
        if (search.trim() === '') return items
        const props = this.dataTable.headers.map(h => h.filter)
        return items.filter(item => props.some(prop => filter(getObjectValueByPath(item, prop), search)))
      },
      onSelectMetric(metric) {
        if (this.dataTable.selectedMetric === metric) {
          return
        }
        this.dataTable.selectedMetric = metric
        if (metric.statistic) {
          this.chart.selectedStatistic = metric.statistic
        } else {
          this.chart.selectedStatistic = STATISTICS.Average.id
        }
        this.initChart()
      }
    },
    mounted() {
      this.initDataTable()
    }
  }
</script>
<style scoped>
    .position-relative {
        position: relative;
    }

    .overlay-chart {
        background-color: rgba(0, 0, 0, 0.2);
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 100%;
        text-align: center;
        z-index: 1;
    }

    .overlay-chart-span {
        position: absolute;
        top: 50%;
        left: 50%;
        -webkit-transform: translate(-50%, -50%);
        transform: translate(-50%, -50%);
    }
</style>