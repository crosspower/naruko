<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-layout slot="body" row wrap>
            <v-flex xs12>
                <v-card>
                    <v-card-title class="pb-0">
                        <div class="subheading">請求情報</div>
                        <v-spacer></v-spacer>
                        <v-select
                                :items="account.aws_environments"
                                item-text="name"
                                item-value="id"
                                label="AWSアカウント"
                                v-model="aws_account_id"
                                dense
                                hide-details
                        ></v-select>
                        <v-select
                                :items="months"
                                label="表示月数"
                                v-model="month"
                                dense
                                hide-details
                        ></v-select>
                        <v-tooltip top>
                            <v-btn icon flat
                                   slot="activator"
                                   :disabled="isProgress"
                                   :loading="isProgress"
                                   @click="initChart">
                                <v-icon>
                                    mdi-refresh
                                </v-icon>
                            </v-btn>
                            <span>更新</span>
                        </v-tooltip>
                    </v-card-title>
                    <v-card class="position-relative" flat>
                        <div class="overlay-chart" v-show="isProgress">
                            <span class="overlay-chart-span">
                                <v-progress-circular
                                        :size="50"
                                        color="primary"
                                        indeterminate
                                ></v-progress-circular>
                            </span>
                        </div>
                        <LineChart :chartData="chartData" :options="options"
                                   :height="400"
                                   class="chart">
                        </LineChart>
                        <v-layout row wrap class="px-2 pb-2">
                            <v-flex v-for="(service,i) in billingGraph.services" :key=i xs6 md3 order-md>
                                <v-checkbox
                                        v-model="graphShow[i]"
                                        :label="service"
                                        :color="`rgb(${colorPalette[i%colorPalette.length]})`"
                                        value=true
                                        hide-details
                                ></v-checkbox>
                            </v-flex>
                        </v-layout>
                    </v-card>

                </v-card>
            </v-flex>
            <v-flex xs12 class="table-flex">
                <v-card>
                    <v-card-title class="pb-0">
                        <div class="subheading">月間請求情報</div>
                    </v-card-title>
                    <v-data-table
                            :items="monthly_data"
                            :headers="headers"
                            :loading="isProgress"
                            class="elevation-1"
                            hide-actions
                    >
                        <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                        <template slot="items" slot-scope="props">
                            <td class="text-xs-center">{{ props.item.service }}</td>
                            <td class="text-xs-center" v-for="(month,i) in Object.keys(groupByMonth)" :key="i">
                                {{ (props.item[month])? "$"+(props.item[month]): "-"}}
                            </td>
                        </template>
                    </v-data-table>
                </v-card>
            </v-flex>
        </v-layout>
    </TemplateBase>
</template>

<script>
    import '@/store/modules/user'
    import {mapGetters, mapActions} from 'vuex'
    import TemplateBase from '@/components/TemplateBase'
    import MENU from '@/lib/definition/mainMenu'
    import LineChart from '@/components/chart/LineChart'
    import httpClient from '@/lib/httpClient'
    import Moment from 'moment'


    export default {
        components: {
            TemplateBase,
            LineChart
        },
        data() {
            return {
                colorPalette: ['244,67,54', '233,30,99', '156,39,176', '103,58,183', '63,81,181', '33,150,243', '3,169,244', '0,188,212', '0,150,136', '76,175,80', '139,195,74', '205,220,57', '255,235,59', '255,193,7', '255,152,0', '255,87,34'],
                graphShow: [],
                //共通
                billingGraph: {timestamps: [], values: [], services: []},
                isProgress: false,

                //パンくずリスト
                title: {icon: MENU.cost.icon, text: MENU.cost.text},
                breadcrumbs: [
                    {
                        text: 'ダッシュボード',
                        disabled: false,
                        to: '/dashboard'
                    },
                    {
                        text: MENU.cost.text,
                        disabled: true,
                        to: ''
                    }
                ],

                //グラフ
                aws_account_id: 1,
                month: 3,
                months: [3, 6, 9, 12, 15],
                options: {
                    animation: false,
                    title: {
                        display: true
                    },
                    legend: {
                        display: false
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    chartArea: {
                        backgroundColor: 'rgba(230, 28, 255, 1)'
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                autoSkip: true,
                                maxTicksLimit: 4,
                                callback: function (val) {
                                    return '$' + val;
                                }
                            }
                        }],
                        xAxes: [{
                            ticks: {
                                maxTicksLimit: 15
                            }
                        }]
                    }
                }
            }
        },
        computed: {
            ...mapGetters({
                account: 'user/userData'
            }),
            chartData: function () {
                let timestamps = this.billingGraph.timestamps.map(function (val) {
                    return Moment(val).tz('UTC').format("YYYY/MM/DD")
                })
                let chartData = {
                    labels: timestamps,
                    datasets: []
                }
                // グラフに渡すデータを詰める。ただし、表示しないときは値をすべてnullにして渡す
                // 色については順番につけていく。ただし、用意数を超えたら最初に戻る
                this.billingGraph.values.forEach((value, i) => {
                    chartData.datasets.push(
                        {
                            label: this.billingGraph.services[i],
                            borderColor: `rgb(${this.colorPalette[i % this.colorPalette.length]})`,
                            data: (this.graphShow[i]) ? value : Array(this.billingGraph.timestamps.length).fill(null),
                            backgroundColor: `rgba(${this.colorPalette[i % this.colorPalette.length]},0.1)`,
                            pointBackgroundColor: `rgb(${this.colorPalette[i % this.colorPalette.length]})`,
                            pointRadius: 0,
                            pointHitRadius: 5,
                            borderWidth: 2,
                            fill: true
                        }
                    )
                })
                return chartData
            },
            //タイムスタンプの一覧を月毎に分類
            //各月の要素として、timestampとその日時の請求額が表示される
            groupByMonth: function () {
                let result = this.billingGraph.timestamps.reduce((prev, cur, id) => {
                    let date = Moment(cur).tz('UTC')
                    let key = date.format('YYYY/MM')
                    if (!prev[key]) {
                        prev[key] = {"timestamps": []}
                    }
                    prev[key]["timestamps"].push(cur)
                    this.billingGraph.services.forEach((service, i) => {
                        if (!prev[key][service]){
                            prev[key][service] = []
                        }
                        prev[key][service].push(
                            this.billingGraph.values[i][id]
                        )
                    })
                    return prev
                }, {})
                return result
            },
            //表のheaderを生成
            headers: function () {
                let result = [{text: 'サービス名', value: 'service', align: 'center', sortable: true}]
                result = result.concat(Object.keys(this.groupByMonth).map((month) => {
                    return {
                        text: Moment(new Date(month)).format('YYYY年MM月'),
                        value: month,
                        align: 'center',
                        sortable: true
                    }
                }))
                return result
            },
            monthly_data: function () {
                let result = (this.billingGraph.services).map((service) => {
                    let data = {service: service}
                    Object.keys(this.groupByMonth).forEach(month => {
                        //あるサービスについて、月の情報がすべてnullか確認
                        if(this.groupByMonth[month][service].every(ele => ele === null)){
                            data[month] = null
                        }else{
                            data[month] = Math.max(...this.groupByMonth[month][service])
                        }
                    })
                    return data
                })
                return result
            }
        },
        methods: {
            ...mapActions('alert', ['pushErrorAlert']),
            async fetchBillingGraph() {
                const now = new Date()
                const startDate = new Date()
                startDate.setMonth(startDate.getMonth() - this.month)
                // APIリクエスト実行
                let result = await httpClient.tenant.getBilling(
                    this.account.tenant.id,
                    this.aws_account_id,
                    {
                        start_time: startDate,
                        end_time: now,
                        period: 3600,
                        stat: "Maximum"
                    })
                // サービス毎にデータをソート
                result.data.sort((a, b) => {
                    if (a.service === "Total") return -1;
                    if (b.service === "Total") return 1;
                    if (a.service < b.service) return -1;
                    if (a.service > b.service) return 1;
                    return 0;
                })
                // 全てのサービスのtimestampsを統合
                let timestampList = []
                result.data.forEach((data) => {
                    Array.prototype.push.apply(timestampList, data.timestamps)
                })
                // 統合したtimestampsの重複を消す
                this.billingGraph.timestamps = Array.from(new Set(timestampList)).sort()
                // 対応するtimestampsに値を割り当てる.無いときはnull
                result.data.forEach((service) => {
                    this.billingGraph.services.push(service.service)
                    // 必要な要素数の配列を用意、全てnullで埋める
                    let serviceValues =  Array(this.billingGraph.timestamps.length).fill(null)
                    service.timestamps.forEach((time, i) => {
                        let key = this.billingGraph.timestamps.indexOf(time)
                        serviceValues[key] = service.values[i]
                    })
                    this.billingGraph.values.push(serviceValues)
                })
            },
            initChart: async function () {
                this.isProgress = true
                //ローディング中グラフの値をリセット
                this.billingGraph = {
                    timestamps: [],
                    values: [],
                    services: []
                }

                //請求情報をAWSにリクエスト
                try {
                    await this.fetchBillingGraph()
                } catch (e) {
                    console.error(e)
                    this.pushErrorAlert('請求情報の取得に失敗しました。')
                } finally {
                    this.isProgress = false
                }

                this.graphShow = Array(this.billingGraph.services.length).fill('true')
            }
        },
        async mounted() {
            //AWSアカウントの取得を確認
            if (!this.account.aws_environments.length) {
                this.pushErrorAlert('AWSアカウントの取得に失敗しました。')
                this.isProgress = false
            } else {
                //AWSアカウントIDの初期値を設定
                this.aws_account_id = this.account.aws_environments[0].id

                await this.initChart();
            }
        }

    }
</script>
<style scoped>
    .table-flex {
        padding-top: 50px;
    }

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