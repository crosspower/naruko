<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-flex xs12 slot="body">
            <v-card>
                <v-card-title class=" pb-0">
                    <h3 class="subheading">通知グループ</h3>
                </v-card-title>
                <v-card-title>
                    <v-text-field
                            v-model="groupDataTables.search"
                            class="pt-0"
                            append-icon="mdi-magnify"
                            label="Search"
                            single-line
                            hide-details
                            clearable
                    ></v-text-field>
                    <v-spacer></v-spacer>
                    <v-btn color="primary"
                           @click="openAddNotificationGroupModal"
                           :disabled="groupDataTables.isProgress">
                        <v-icon small>mdi-plus</v-icon>
                        グループ登録
                    </v-btn>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               @click="initGroupDataTables"
                               :loading="groupDataTables.isProgress"
                               :disabled="groupDataTables.isProgress">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>
                </v-card-title>
                <v-data-table
                        :headers="groupDataTables.headers"
                        :items="groups"
                        :search="groupDataTables.search"
                        :pagination.sync="groupDataTables.pagination"
                        :loading="groupDataTables.isProgress"
                        item-key="name"
                >
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr @click="props.expanded = !props.expanded">
                            <td>{{ props.item.name }}</td>
                            <td class="text-xs-right">{{ props.item.aws_environments.length }}</td>
                            <td class="text-xs-right">{{ props.item.destinations.length }}</td>
                            <td class="text-xs-center" width="20%">
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="blue darken-1"
                                           :loading="groupDataTables.isProgress"
                                           :disabled="groupDataTables.isProgress"
                                           @click.stop="props.expanded = !props.expanded"
                                    >
                                        <v-icon small>mdi-magnify</v-icon>
                                    </v-btn>
                                    <span>詳細表示</span>
                                </v-tooltip>
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="blue darken-1"
                                           :loading="groupDataTables.isProgress"
                                           :disabled="groupDataTables.isProgress"
                                           @click.stop="openEditNotificationGroupModal(props.item)">
                                        <v-icon small>mdi-pencil</v-icon>
                                    </v-btn>
                                    <span>編集</span>
                                </v-tooltip>
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="red darken-1"
                                           @click.stop="openDeleteNotificationModal(props.item)"
                                           :loading="groupDataTables.isProgress"
                                           :disabled="groupDataTables.isProgress">
                                        <v-icon small>mdi-delete</v-icon>
                                    </v-btn>
                                    <span>削除</span>
                                </v-tooltip>
                            </td>
                        </tr>
                    </template>
                    <template slot="expand" slot-scope="props">
                        <v-layout justify-start row class="pa-3">
                            <v-flex xs6>
                                <v-card flat>
                                    <v-card-title class="pa-2 pr-4">
                                        通知対象 AWSアカウント
                                    </v-card-title>
                                    <v-divider></v-divider>
                                    <v-list dense>
                                        <v-list-tile v-for="(item, i) in props.item.aws_environments" :key="i">
                                            <v-icon small class="pr-1">
                                                mdi-cloud
                                            </v-icon>
                                            <v-list-tile-content>
                                                {{item.name}}
                                            </v-list-tile-content>
                                        </v-list-tile>
                                    </v-list>
                                </v-card>
                            </v-flex>
                            <v-flex xs6>
                                <v-card flat>
                                    <v-card-title class="pa-2 pr-4">
                                        通知先
                                    </v-card-title>
                                    <v-divider></v-divider>
                                    <v-list dense>
                                        <v-list-tile v-for="(item, i) in props.item.destinations" :key="i">
                                            <v-icon small class="pr-1" v-if="item.type==='email'">
                                                mdi-email-outline
                                            </v-icon>
                                            <v-icon small class="pr-1" v-if="item.type==='telephone'">
                                                mdi-phone
                                            </v-icon>
                                            <v-list-tile-content>
                                                {{item.name}}
                                            </v-list-tile-content>
                                        </v-list-tile>
                                    </v-list>
                                </v-card>
                            </v-flex>
                        </v-layout>
                        <v-divider></v-divider>
                    </template>
                </v-data-table>
            </v-card>
        </v-flex>

        <v-flex xs12 slot="body" class="pt-5">
            <v-card>
                <v-card-title class=" pb-0">
                    <h3 class="subheading">通知先</h3>
                </v-card-title>
                <v-card-title>
                    <v-text-field
                            v-model="groupDataTables.search"
                            class="pt-0"
                            append-icon="mdi-magnify"
                            label="Search"
                            single-line
                            hide-details
                            clearable
                    ></v-text-field>
                    <v-spacer></v-spacer>
                    <v-btn color="primary"
                           @click="openAddNotificationDestinationModal"
                           :disabled="destDataTables.isProgress">
                        <v-icon small>mdi-plus</v-icon>
                        通知先登録
                    </v-btn>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               @click="initDestDataTables"
                               :loading="destDataTables.isProgress"
                               :disabled="destDataTables.isProgress">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>
                </v-card-title>
                <v-data-table
                        :headers="destDataTables.headers"
                        :items="destinations"
                        :search="destDataTables.search"
                        :pagination.sync="destDataTables.pagination"
                        :loading="destDataTables.isProgress"
                        item-key="name"
                >
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr>
                            <td>{{ props.item.name }}</td>
                            <td class="text-xs-left">{{ props.item.type.name }}</td>
                            <td class="text-xs-left">{{ props.item.value }}</td>
                            <td class="text-xs-center" width="1%">
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="red darken-1"
                                           @click="openDeleteNotificationDestinationModal(props.item)"
                                           :loading="destDataTables.isProgress"
                                           :disabled="destDataTables.isProgress">
                                        <v-icon small>mdi-delete</v-icon>
                                    </v-btn>
                                    <span>削除</span>
                                </v-tooltip>
                            </td>
                        </tr>
                    </template>
                </v-data-table>
            </v-card>
        </v-flex>
        <AddNotificationDestinationModal slot="body"
                                         ref="addNotificationDestinationModal"/>
        <DeleteNotificationDestinationModal slot="body"
                                            ref="deleteNotificationDestinationModal"/>
        <AddNotificationGroupModal slot="body"
                                   ref="addNotificationGroupModal"/>
        <EditNotificationGroupModal slot="body"
                                    ref="editNotificationGroupModal"/>
        <DeleteNotificationGroupModal slot="body"
                                      ref="deleteNotificationGroupModal"/>
    </TemplateBase>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import TemplateBase from '@/components/TemplateBase'
  import AddNotificationDestinationModal from '@/views/notifications/modal/AddNotificationDestinationModal'
  import DeleteNotificationDestinationModal from '@/views/notifications/modal/DeleteNotificationDestinationModal'
  import AddNotificationGroupModal from '@/views/notifications/modal/AddNotificationGroupModal'
  import EditNotificationGroupModal from '@/views/notifications/modal/EditNotificationGroupModal'
  import DeleteNotificationGroupModal from '@/views/notifications/modal/DeleteNotificationGroupModal'
  import MENU from '@/lib/definition/mainMenu'


  export default {
    components: {
      TemplateBase,
      AddNotificationDestinationModal,
      DeleteNotificationDestinationModal,
      AddNotificationGroupModal,
      EditNotificationGroupModal,
      DeleteNotificationGroupModal
    },
    data() {
      return {
        title: {icon: MENU.notifications.icon, text: MENU.notifications.text},
        breadcrumbs: [
          {text: 'ダッシュボード', disabled: false, to: '/dashboard'},
          {text: '通知設定', disabled: true, to: ''}
        ],
        isProgress: false,
        groupDataTables: {
          isProgress: false,
          search: '',
          pagination: {
            sortBy: 'name'
          },
          headers: [
            {text: 'グループ名', align: 'left', value: 'name'},
            {text: '通知対象 AWSアカウント数', align: 'right', value: 'aws_environments.length'},
            {text: '通知先件数', align: 'right', value: 'destinations.length'},
            {text: '', align: 'center', value: 'name', sortable: false}
          ]
        },
        destDataTables: {
          isProgress: false,
          search: '',
          pagination: {
            sortBy: 'name'
          },
          headers: [
            {text: '名前', align: 'left', value: 'name'},
            {text: 'タイプ', align: 'left', value: 'type.name'},
            {text: '通知先', align: 'left', value: 'address'},
            {text: '', value: 'name', sortable: false}
          ]
        }
      }
    },
    computed: {
      ...mapGetters({
        destinations: 'notifications/destinations',
        groups: 'notifications/groups'
      })
    },
    methods: {
      ...mapActions('notifications', ['fetchDestinations', 'fetchNotificationGroup']),
      ...mapActions('awsAccounts', ['fetchAwsAccounts']),
      initDestDataTables() {
        this.destDataTables.isProgress = true
        this.fetchDestinations().finally(() => {
          this.destDataTables.isProgress = false
        })
      },
      initGroupDataTables() {
        this.groupDataTables.isProgress = true
        this.fetchNotificationGroup().finally(() => {
          this.groupDataTables.isProgress = false
        })
      },
      openAddNotificationDestinationModal() {
        this.$refs.addNotificationDestinationModal.open().then((res) => {
          if (res) {
            this.initDestDataTables()
          }
        })
      },
      openDeleteNotificationDestinationModal(destination) {
        this.$refs.deleteNotificationDestinationModal.open(destination).then((res) => {
          if (res) {
            this.initDestDataTables()
            this.initGroupDataTables()
          }
        })
      },
      openAddNotificationGroupModal() {
        this.groupDataTables.isProgress = true
        this.fetchAwsAccounts().then(() => {
          this.$refs.addNotificationGroupModal.open().then((res) => {
            if (res) {
              this.initGroupDataTables()
            }
          })
        }).finally(() => {
          this.groupDataTables.isProgress = false
        })
      },
      openEditNotificationGroupModal(group) {
        this.groupDataTables.isProgress = true
        this.fetchAwsAccounts().then(() => {
          this.$refs.editNotificationGroupModal.open(group).then((res) => {
            if (res) {
              this.initGroupDataTables()
            }
          })
        }).finally(() => {
          this.groupDataTables.isProgress = false
        })
      },
      openDeleteNotificationModal(group) {
        this.$refs.deleteNotificationGroupModal.open(group).then((res) => {
          if (res) {
            this.initGroupDataTables()
          }
        })
      }
    },
    mounted() {
      this.initDestDataTables()
      this.initGroupDataTables()
    }
  }
</script>