<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-flex slot="body" xs12>
            <v-card>
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

                    <v-btn color="primary"
                           @click="openAddAwsAccountModal"
                           :disabled="isProgress">
                        <v-icon small>mdi-plus</v-icon>
                        AWSアカウント登録
                    </v-btn>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               @click="initDataTable"
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
                        :headers="dataTable.headers"
                        :items="awsAccounts"
                        :search="dataTable.search"
                        :pagination.sync="dataTable.pagination"
                        :loading="dataTable.isProgress"
                        item-key="name"
                        class="elevation-0"
                >
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr>
                            <td>{{ props.item.name }}</td>
                            <td class="text-xs-left">{{ props.item.aws_account_id }}</td>
                            <td class="text-xs-left">{{props.item.aws_role }}</td>
                            <td class="text-xs-center" width="110px">
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="blue darken-1"
                                           :loading="isProgress"
                                           :disabled="isProgress"
                                           @click="openEditAwsAccountModal(props.item)">
                                        <v-icon small>mdi-pencil</v-icon>
                                    </v-btn>
                                    <span>編集</span>
                                </v-tooltip>
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="red darken-1"
                                           :loading="isProgress"
                                           :disabled="isProgress"
                                           @click="openDeleteAwsAccountModal(props.item)">
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
        <AddAwsAccountModal slot="body" ref="addAwsAccountModal"></AddAwsAccountModal>
        <EditAwsAccountModal slot="body" ref="editAwsAccountModal"></EditAwsAccountModal>
        <DeleteAwsAccountModal slot="body" ref="deleteAwsAccountModal"></DeleteAwsAccountModal>
    </TemplateBase>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import TemplateBase from '@/components/TemplateBase'
  import AddAwsAccountModal from '@/views/awsAccounts/modal/AddAwsAccountModal'
  import EditAwsAccountModal from '@/views/awsAccounts/modal/EditAwsAccountModal'
  import DeleteAwsAccountModal from '@/views/awsAccounts/modal/DeleteAwsAccountModal'
  import MENU from '@/lib/definition/mainMenu'


  export default {
    components: {
      TemplateBase,
      AddAwsAccountModal,
      EditAwsAccountModal,
      DeleteAwsAccountModal
    },
    data() {
      return {
        isProgress: false,
        title: {icon: MENU.awsAccounts.icon, text: MENU.awsAccounts.text},
        breadcrumbs: [
          {
            text: 'ダッシュボード',
            disabled: false,
            to: '/dashboard'
          },
          {
            text: 'AWSアカウント管理',
            disabled: true,
            to: ''
          }
        ],
        dataTable: {
          isProgress: false,
          headers: [
            {text: 'アカウント名', align: 'left', value: 'name'},
            {text: 'AWSアカウントID', align: 'left', value: 'email'},
            {text: 'AWSロール名', align: 'left', value: 'tel'},
            {text: '', value: 'name', sortable: false}
          ],
          pagination: {
            sortBy: 'name'
          }
        }
      }
    },
    computed: {
      ...mapGetters({
        awsAccounts: 'awsAccounts/awsAccounts'
      })
    },
    methods: {
      ...mapActions('awsAccounts', ['fetchAwsAccounts']),
      initDataTable() {
        this.dataTable.isProgress = true
        this.isProgress = true
        this.fetchAwsAccounts().finally(() => {
          this.dataTable.isProgress = false
          this.isProgress = false
        })
      },
      openAddAwsAccountModal() {
        this.$refs.addAwsAccountModal.open().then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      },
      openDeleteAwsAccountModal(awsAccount) {
        // 削除モーダルを開く
        this.$refs.deleteAwsAccountModal.open(awsAccount).then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      },
      openEditAwsAccountModal(awsAccount) {
        this.$refs.editAwsAccountModal.open(awsAccount).then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      }
    },
    mounted() {
      // マウント時にAWSアカウント情報を取得する
      this.initDataTable()
    }
  }
</script>