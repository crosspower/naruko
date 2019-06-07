<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-layout slot="body" row wrap>
            <v-flex xs12
                    class="pb-3"
                    v-for="(awsAccount, i) in userData.aws_environments"
                    :key="i">
                <v-card>
                    <v-card-title primary-title>
                        <v-icon class="pr-2">mdi-cloud</v-icon>
                        <span class="subheading">{{awsAccount.name}}</span>
                    </v-card-title>
                    <v-card-text class="pt-0">
                        <v-layout row wrap>
                            <v-flex xs12 sm6 md3 pa-2>
                                <v-card>
                                    <v-card-title class="pa-2 pr-4">
                                        <v-flex xs6>
                                            <v-icon :color=STATUS.CAUTION.color size="50">
                                                {{STATUS.CAUTION.icon}}
                                            </v-icon>
                                        </v-flex>
                                        <v-flex xs6 class="text-xs-right">
                                            <h6 :class="`caption ${STATUS.CAUTION.color}--text text--darken-2`">
                                                {{STATUS.CAUTION.name}}</h6>
                                            <h3 :class="`display-1 ${STATUS.CAUTION.color}--text text--darken-2`"
                                                v-if="!dataTable.isProgress">
                                                {{cautionResources[awsAccount.id].length}}</h3>
                                            <v-progress-circular
                                                    :size="40"
                                                    color="blue"
                                                    v-if="dataTable.isProgress"
                                                    indeterminate
                                            ></v-progress-circular>
                                        </v-flex>
                                    </v-card-title>
                                </v-card>
                            </v-flex>
                            <v-flex xs12 sm6 md3 pa-2>
                                <v-card>
                                    <v-card-title class="pa-2 pr-4">
                                        <v-flex xs6>
                                            <v-icon :color=STATUS.DANGER.color size="50">{{STATUS.DANGER.icon}}
                                            </v-icon>
                                        </v-flex>
                                        <v-flex xs6 class="text-xs-right">
                                            <h6 :class="`caption ${STATUS.DANGER.color}--text text--darken-2`">
                                                {{STATUS.DANGER.name}}</h6>
                                            <h3 :class="`display-1 ${STATUS.DANGER.color}--text text--darken-2`"
                                                v-if="!dataTable.isProgress">
                                                {{dangerResources[awsAccount.id].length}}</h3>
                                            <v-progress-circular
                                                    :size="40"
                                                    color="blue"
                                                    v-if="dataTable.isProgress"
                                                    indeterminate
                                            ></v-progress-circular>
                                        </v-flex>
                                    </v-card-title>
                                </v-card>
                            </v-flex>
                        </v-layout>
                        <v-data-table
                                :items="alertedResources[awsAccount.id]"
                                :headers="dataTable.headers"
                                class="elevation-0"
                                :loading="dataTable.isProgress"
                                hide-actions>
                            <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                            <template slot="items" slot-scope="props">
                                <td>{{ props.item.id }}</td>
                                <td>{{ props.item.name }}</td>
                                <td>{{ props.item.service }}</td>
                                <td>
                                    <v-icon small
                                            class="pr-1"
                                            :color=props.item.status.color>
                                        {{ props.item.status.icon }}
                                    </v-icon>
                                    <span :class="`${props.item.status.color}--text text--darken-2`">
                                        {{ props.item.status.name }}
                                    </span>
                                </td>
                                <td class="text-xs-center">
                                    <v-tooltip top>
                                        <v-btn slot="activator" class="ma-0" icon flat small
                                               color="blue darken-1"
                                               :to="`/resources/monitoring?awsAccount=${props.item.aws_environment.id}&region=${props.item.region}&service=${props.item.service.toLowerCase()}&resourceId=${props.item.id}`"
                                               @click="cancelFetch"
                                        >
                                            <v-icon small>mdi-magnify</v-icon>
                                        </v-btn>
                                        <span>詳細表示</span>
                                    </v-tooltip>
                                </td>
                            </template>
                        </v-data-table>
                    </v-card-text>
                </v-card>
            </v-flex>
            <v-flex xs12 class="pb-3">
                <v-card>
                    <v-card-title primary-title>
                        <v-icon class="pr-2">mdi-format-list-bulleted</v-icon>
                        <span class="subheading">操作ログ</span>
                    </v-card-title>
                    <v-card-title>
                    <v-text-field
                            v-model="dataTable.search"
                            append-icon="mdi-magnify"
                            label="Search"
                            single-line
                            hide-details
                            clearable
                            class="pt-0"
                    ></v-text-field>
                    <v-spacer></v-spacer>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               @click="initLogDataTable"
                               :loading="logDataTables.isProgress"
                               :disabled="logDataTables.isProgress">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>
                    </v-card-title>
                    <v-data-table
                            :headers="logDataTables.headers"
                            :items="operationLogs"
                            :search="logDataTables.search"
                            :pagination.sync="logDataTables.pagination"
                            :loading="logDataTables.isProgress"
                            item-key="name"
                            class="elevation-0"
                    >
                        <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                        <template slot="items" slot-scope="props">
                            <tr>
                                <td>{{ props.item.created_at }}</td>
                                <td class="text-xs-left">{{ props.item.tenant.tenant_name }}</td>
                                <td class="text-xs-left">{{ props.item.executor.name }}</td>
                                <td class="text-xs-left">{{props.item.operation }}</td>
                            </tr>
                        </template>
                    </v-data-table>
                </v-card>
            </v-flex>
        </v-layout>
    </TemplateBase>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import TemplateBase from '@/components/TemplateBase'
  import MENU from '@/lib/definition/mainMenu'
  import STATUS from '@/lib/definition/monitorStatus'
  import {getObjectValueByPath} from 'vuetify/es5/util/helpers'

  export default {
    components: {
      TemplateBase
    },
    data() {
      return {
        title: {icon: MENU.dashboard.icon, text: 'ダッシュボード'},
        breadcrumbs: [
          {text: 'ダッシュボード', disabled: true, to: '/dashboard'}
        ],
        STATUS: STATUS,
        dataTable: {
          isProgress: false,
          headers: [
            {text: 'ID', value: 'id', filter: 'id', align: 'left'},
            {text: '名前', value: 'name', filter: 'name', align: 'left'},
            {text: 'サービス', value: 'service', filter: 'service', align: 'left'},
            {text: 'ステータス', value: 'status.sortText', filter: 'status.name', align: 'left'},
            {text: '', value: 'name', sortable: false}
          ]
        },
        logDataTables: {
          isProgress: false,
          pagination : {
            sortBy: 'created_at',
            descending: true
          },
          headers: [
            {text: '実行日時', value: 'created_at', filter: 'created_at', align: 'left'},
            {text: 'テナント', value: 'tenant', filter: 'tenant', align: 'left'},
            {text: '実行者', value: 'executor', filter: 'executor', align: 'left'},
            {text: '操作内容', value: 'operation', filter: 'operation', align: 'left'}
          ]
        }
      }
    },
    computed: {
      ...mapGetters({
        userData: 'user/userData',
        resources: 'resources/resources',
        awsEnvFilter: 'resources/awsEnvFilter',
        operationLogs: 'operationLogs/operationLogs'
      }),
      cautionResources: function () {
        const resources = {}
        for (const awsAccount of this.userData.aws_environments) {
          resources[awsAccount.id] = this.resources.filter(r => r.status.id === STATUS.CAUTION.id && r.aws_environment.id === awsAccount.id)
        }
        return resources
      },
      dangerResources: function () {
        const resources = {}
        for (const awsAccount of this.userData.aws_environments) {
          resources[awsAccount.id] = this.resources.filter(r => r.status.id === STATUS.DANGER.id && r.aws_environment.id === awsAccount.id)
        }
        return resources
      },
      alertedResources: function () {
        const resources = {}
        for (const awsAccount of this.userData.aws_environments) {
          resources[awsAccount.id] = this.dangerResources[awsAccount.id].concat(this.cautionResources[awsAccount.id])
        }
        return resources
      }
    },
    methods: {
      ...mapActions('resources', ['fetch', 'cancelFetch']),
      ...mapActions('operationLogs', ['fetchOperationLogs']),
      initDatatable() {
        this.dataTable.isProgress = true
        this.fetch().finally(() => {
          this.dataTable.isProgress = false
        })
      },
      customFilter(items, search, filter) {
        search = search.toString().toLowerCase()
        if (search.trim() === '') return items
        const props = this.dataTable.headers.map(h => h.filter)
        return items.filter(item => props.some(prop => filter(getObjectValueByPath(item, prop), search)))
      },
      initLogDataTable() {
        this.logDataTables.isProgress = true
        this.fetchOperationLogs().finally(() => {
          this.logDataTables.isProgress = false
        })
      }
    },
    mounted() {
      // マウント時にインスタンス情報を取得する
      this.initDatatable()
      this.initLogDataTable()
    }
  }
</script>