<template>
    <v-layout>
        <v-flex xs12>
            <v-card flat>
                <v-card-title class=" pb-0">
                    <div class="subheading">スケジュール一覧</div>
                </v-card-title>
                <v-card-title>
                    <v-text-field
                            v-model="dataTables.search"
                            class="pt-0"
                            append-icon="mdi-magnify"
                            label="Search"
                            single-line
                            hide-details
                            clearable
                    ></v-text-field>
                    <v-spacer></v-spacer>
                    <v-btn color="primary"
                           :disabled="isProgress"
                           @click="openAddScheduleModal">
                        <v-icon small>mdi-calendar-plus</v-icon>
                        スケジュール登録
                    </v-btn>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               @click="initDataTables"
                               :loading="isProgress"
                               :disabled="isProgress">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>
                </v-card-title>
                <v-data-table
                        :headers="dataTables.headers"
                        :items="schedules"
                        :search="dataTables.search"
                        :pagination.sync="dataTables.pagination"
                        :loading="isProgress"
                        item-key="name">
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr>
                            <td class="text-xs-left">{{ props.item.name}}</td>
                            <td class="text-xs-left">{{ props.item.is_active.text}}</td>
                            <td class="text-xs-left">{{ props.item.notification.text}}</td>
                            <td class="text-xs-left">{{ props.item.action.name }}</td>
                            <td class="text-xs-left">{{ props.item.next }}</td>
                            <td class="text-xs-left">
                                <v-tooltip top>
                                    <v-btn slot="activator"
                                           class="ma-0"
                                           color="blue darken-1"
                                           icon flat small
                                           @click="openEditScheduleModal(props.item)">
                                        <v-icon small>mdi-pencil</v-icon>
                                    </v-btn>
                                    <span>編集</span>
                                </v-tooltip>
                                <v-tooltip top>
                                    <v-btn slot="activator"
                                           class="ma-0"
                                           color="red darken-1"
                                           icon flat small
                                           @click="openDeleteScheduleModal(props.item)">
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
        <AddScheduleModal ref="addScheduleModal"></AddScheduleModal>
        <DeleteScheduleModal ref="deleteScheduleModal"></DeleteScheduleModal>
    </v-layout>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import AddScheduleModal from '@/views/resources/detail/schedule/modal/AddScheduleModal'
  import DeleteScheduleModal from '@/views/resources/detail/schedule/modal/DeleteScheduleModal'

  export default {
    components: {
      AddScheduleModal,
      DeleteScheduleModal
    },
    data() {
      return {
        isProgress: false,
        dataTables: {
          search: '',
          pagination: {
            sortBy: '作成日時'
          },
          headers: [
            {text: 'スケジュール名', align: 'left', value: 'name'},
            {text: '状態', align: 'left', value: 'is_active.text'},
            {text: '通知', align: 'left', value: 'notification.text'},
            {text: 'アクション', align: 'left', value: 'action.name'},
            {text: '次の実行日時', align: 'left', value: 'next'},
            {text: '', align: 'left', value: ''}
          ]
        }
      }
    },
    computed: {
      ...mapGetters({
        schedules: 'resourceDetail/schedules'
      })
    },
    methods: {
      ...mapActions('resourceDetail', ['fetchSchedules']),
      initDataTables() {
        this.isProgress = true
        this.fetchSchedules([
          this.$route.query.awsAccount,
          this.$route.query.region,
          this.$route.query.service,
          this.$route.query.resourceId]).finally(() => {
          this.isProgress = false
        })
      },
      openAddScheduleModal() {
        this.$refs.addScheduleModal.open().then((res) => {
          if (res) {
            this.initDataTables()
          }
        })
      },
      openEditScheduleModal(schedule) {
        this.$refs.addScheduleModal.open(schedule).then((res) => {
          if (res) {
            this.initDataTables()
          }
        })
      },
      openDeleteScheduleModal(schedule) {
        this.$refs.deleteScheduleModal.open(schedule).then((res) => {
          if (res) {
            this.initDataTables()
          }
        })
      }
    },
    mounted() {
      this.initDataTables()
    }
  }
</script>