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
                                   :width="3" :height="1"
                                   class="chart"></LineChart>
                    </v-card>

                </v-card>
            </v-flex>
            <v-flex xs12 class="table-flex">
                <v-card>
                    <v-data-table
                            :items="monthly_data"
                            :headers="headers"
                            :loading="isProgress"
                            class="elevation-1"
                            hide-actions
                    >
                        <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                        <template slot="items" slot-scope="props">
                            <td class="text-xs-center">{{ props.item.timestamp }}</td>
                            <td class="text-xs-center">${{ props.item.billing }}</td>
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
        data(){
            return{
                //共通
                billingGraph: {timestamps:[],values:[]},
                isProgress: false,

                //パンくずリスト
                title: {icon: MENU.cost.icon, text:MENU.cost.text},
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
                month: 1,
                months: [1,3,6,9,12,15],
                options: {
                    animation: false,
                    title: {
                        display: true
                    },
                    legend: {
                        display: false
                    },
                    responsive: true,
                    chartArea: {
                        backgroundColor: 'rgba(230, 238, 255, 0.6)'
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                autoSkip: true,
                                maxTicksLimit: 4
                            }
                        }],
                        xAxes: [{
                            ticks: {
                                maxTicksLimit: 15
                            }
                        }]
                    }
                },

                //表
                headers:[
                    {text: '年月',value: 'date',align: 'center',sortable: false},
                    {text: '請求額',value: 'dollar',align: 'center',sortable: false}
                ]
            }
        },
        computed: {
            ...mapGetters({
                account: 'user/userData'
            }),
            chartData: function () {
                let timestamps = this.billingGraph.timestamps.map(function( val ){
                    return Moment(val).tz('UTC').format("YYYY/MM/DD")
                })
                return {
                    labels: timestamps,
                    datasets: [{
                        label: 'Billing',
                        borderColor: '#f87979',
                        data: this.billingGraph.values,
                        backgroundColor: 'rgba(255, 99, 132, 0.08)',
                        pointBackgroundColor: 'white',
                        pointRadius: 0,
                        pointHitRadius: 10,
                        borderWidth: 1,
                        fill: true
                    }]
                }
            },
            monthly_data:function () {
                let groupeByMonth = this.billingGraph.timestamps.reduce((prev, cur) => {
                    let date = Moment(cur).tz('UTC')
                    let key = date.format('YYYY/MM')
                    prev[key] = (prev[key] || []).concat({timestamp: cur})
                    return prev
                }, {})
                let result = Object.keys(groupeByMonth).map((month) => {
                    let lastTimestamp = groupeByMonth[month][groupeByMonth[month].length - 1].timestamp
                    let dataIndex = this.billingGraph.timestamps.indexOf(lastTimestamp)
                    return {
                        timestamp: Moment(lastTimestamp).format('YYYY年MM月'),
                        billing: this.billingGraph.values[dataIndex]
                    }
                })
                return result
            }
        },
        methods: {
            ...mapActions('alert',['pushErrorAlert']),
            async fetchBillingGraph() {
                const now = new Date()
                const start_date = new Date()
                start_date.setMonth(start_date.getMonth() - this.month)
                let result = await httpClient.tenant.getBilling(
                    this.account.tenant.id,
                    this.aws_account_id,
                    {
                        start_time: start_date,
                        end_time: now,
                        period: 3600,
                        stat: "Maximum"
                    })
                this.billingGraph = result.data
            },
            async initChart() {
                this.isProgress = true
                //ローディング中グラフの値をリセット
                this.billingGraph = {
                    timestamps:[],
                    values:[]
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
            }
        },
        async mounted(){
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
    .table-flex{
        padding-top:50px;
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