<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-layout slot="body" row wrap>
            <v-flex xs12 sm6 md3 pa-2>
                <v-card hover @click.native="filterStatus(STATUS.OK)">
                    <v-card-title class="pa-2 pr-4">
                        <v-flex xs6>
                            <v-icon :color=STATUS.OK.color size="50">{{STATUS.OK.icon}}</v-icon>
                        </v-flex>
                        <v-flex xs6 class="text-xs-right">
                            <h6 :class="`caption ${STATUS.OK.color}--text text--darken-2`">
                                {{STATUS.OK.name}}</h6>
                            <h3 :class="`display-1 ${STATUS.OK.color}--text text--darken-2`"
                                v-if="!datatable.isProgress">
                                {{okResources.length}}</h3>
                            <v-progress-circular
                                    :size="40"
                                    color="blue"
                                    v-if="datatable.isProgress"
                                    indeterminate
                            ></v-progress-circular>
                        </v-flex>
                    </v-card-title>
                </v-card>
            </v-flex>
            <v-flex xs12 sm6 md3 pa-2>
                <v-card hover @click.native="filterStatus(STATUS.CAUTION)">
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
                                v-if="!datatable.isProgress">
                                {{cautionResources.length}}</h3>
                            <v-progress-circular
                                    :size="40"
                                    color="blue"
                                    v-if="datatable.isProgress"
                                    indeterminate
                            ></v-progress-circular>
                        </v-flex>
                    </v-card-title>
                </v-card>
            </v-flex>
            <v-flex xs12 sm6 md3 pa-2>
                <v-card hover @click.native="filterStatus(STATUS.DANGER)">
                    <v-card-title class="pa-2 pr-4">
                        <v-flex xs6>
                            <v-icon :color=STATUS.DANGER.color size="50">{{STATUS.DANGER.icon}}
                            </v-icon>
                        </v-flex>
                        <v-flex xs6 class="text-xs-right">
                            <h6 :class="`caption ${STATUS.DANGER.color}--text text--darken-2`">
                                {{STATUS.DANGER.name}}</h6>
                            <h3 :class="`display-1 ${STATUS.DANGER.color}--text text--darken-2`"
                                v-if="!datatable.isProgress">
                                {{dangerResources.length}}</h3>
                            <v-progress-circular
                                    :size="40"
                                    color="blue"
                                    v-if="datatable.isProgress"
                                    indeterminate
                            ></v-progress-circular>
                        </v-flex>
                    </v-card-title>
                </v-card>
            </v-flex>
            <v-flex xs12 sm6 md3 pa-2>
                <v-card hover @click.native="filterStatus(STATUS.UNSET)">
                    <v-card-title class="pa-2 pr-4">
                        <v-flex xs6>
                            <v-icon :color=STATUS.UNSET.color size="50">{{STATUS.UNSET.icon}}
                            </v-icon>
                        </v-flex>
                        <v-flex xs6 class="text-xs-right">
                            <h6 :class="`caption ${STATUS.UNSET.color}--text text--darken-2`">
                                {{STATUS.UNSET.name}}</h6>
                            <h3 :class="`display-1 ${STATUS.UNSET.color}--text text--darken-2`"
                                v-if="!datatable.isProgress">
                                {{unsetResources.length}}</h3>
                            <v-progress-circular
                                    :size="40"
                                    color="blue"
                                    v-if="datatable.isProgress"
                                    indeterminate
                            ></v-progress-circular>
                        </v-flex>
                    </v-card-title>
                </v-card>
            </v-flex>

            <v-flex xs12>
                <v-card>
                    <v-card-title>
                        <v-text-field
                                v-model="datatable.search"
                                class="pt-0"
                                append-icon="mdi-magnify"
                                label="Search"
                                single-line
                                hide-details
                                clearable
                        ></v-text-field>
                        <v-spacer></v-spacer>
                        <v-tooltip top>
                            <v-btn icon flat
                                   slot="activator"
                                   @click="initDatatable"
                                   :loading="datatable.isProgress"
                                   :disabled="datatable.isProgress">
                                <v-icon>
                                    mdi-refresh
                                </v-icon>
                            </v-btn>
                            <span>更新</span>
                        </v-tooltip>
                    </v-card-title>
                    <v-data-table
                            :headers="datatable.headers"
                            :items="resources"
                            :custom-filter="customFilter"
                            :search="datatable.search"
                            :loading="datatable.isProgress"
                            :pagination.sync="datatable.pagination"
                            :rows-per-page-items="datatable.rowsPerPageItems"
                    >
                        <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                        <template slot="items" slot-scope="props">
                            <td>{{ props.item.id }}</td>
                            <td>{{ props.item.name }}</td>
                            <td>{{ props.item.aws_environment.name }}</td>
                            <td>{{ props.item.service }}</td>
                            <td>
                                <v-icon small class="pr-1" :color=props.item.status.color>{{ props.item.status.icon }}
                                </v-icon>
                                <span :class="`${props.item.status.color}--text text--darken-2`">{{ props.item.status.name }}</span>
                            </td>
                            <td class="text-xs-center" width="1%">
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
                        <v-alert slot="no-results" :value="true" color="error" icon="mdi-alert">
                            Your search for "{{ datatable.search }}" found no results.
                        </v-alert>
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
        title: {icon: MENU.resources.icon, text: 'リソース一覧'},
        breadcrumbs: [
          {text: 'ダッシュボード', disabled: false, to: '/dashboard'},
          {text: 'リソース一覧', disabled: true, to: ''}
        ],
        STATUS: STATUS,
        datatable: {
          isProgress: false,
          rowsPerPageItems: [25, 50, 100, {"text": "$vuetify.dataIterator.rowsPerPageAll", "value": -1}],
          pagination: {
            sortBy: 'name',
            rowsPerPage: 25
          },
          search: '',
          headers: [
            {text: 'ID', value: 'id', filter: 'id', align: 'left'},
            {text: '名前', value: 'name', filter: 'name', align: 'left'},
            {text: 'AWSアカウント', value: 'aws_environment.name', filter: 'aws_environment.name', align: 'left'},
            {text: 'サービス', value: 'service', filter: 'service', align: 'left'},
            {text: 'ステータス', value: 'status.sortText', filter: 'status.name', align: 'left'},
            {text: '', value: 'name', sortable: false}
          ]
        }
      }
    },
    computed: {
      ...mapGetters({
        userData: 'user/userData',
        resources: 'resources/resources',
        awsEnvFilter: 'resources/awsEnvFilter',
        okCount: 'resources/okCount',
        cautionCount: 'resources/cautionCount',
        dangerCount: 'resources/dangerCount',
        unsetCount: 'resources/unsetCount'
      }),
      cautionResources: function () {
        return this.resources.filter(r => r.status.id === STATUS.CAUTION.id)
      },
      dangerResources: function () {
        return this.resources.filter(r => r.status.id === STATUS.DANGER.id)
      },
      okResources: function () {
        return this.resources.filter(r => r.status.id === STATUS.OK.id)
      },
      unsetResources: function () {
        return this.resources.filter(r => r.status.id === STATUS.UNSET.id)
      }
    },
    methods: {
      ...mapActions('resources', ['fetch', 'cancelFetch']),
      initDatatable() {
        this.datatable.isProgress = true
        this.fetch().finally(() => {
          this.datatable.isProgress = false
        })
      },
      customFilter(items, search, filter) {
        search = search.toString().toLowerCase()
        if (search.trim() === '') return items
        const props = this.datatable.headers.map(h => h.filter)
        return items.filter(item => props.some(prop => filter(getObjectValueByPath(item, prop), search)))
      },
      filterStatus(status) {
        this.datatable.search = status.name
      }
    },
    mounted() {
      // マウント時にインスタンス情報を取得する
      this.initDatatable()
    }
  }
</script>