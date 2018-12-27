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
                           @click="openAddTenantModal"
                           :disabled="isProgress">
                        <v-icon small>mdi-plus</v-icon>
                        テナント登録
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
                        :items="tenants"
                        :search="dataTable.search"
                        :pagination.sync="dataTable.pagination"
                        :loading="dataTable.isProgress"
                        item-key="name"
                >
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr>
                            <td>{{ props.item.tenant_name }}</td>
                            <td class="text-xs-left">{{ props.item.email }}</td>
                            <td class="text-xs-left">{{props.item.tel }}</td>
                            <td class="text-xs-right" width="1%">{{ props.item.aws_environments.length }}</td>
                            <td class="text-xs-center" width="110px">
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="blue darken-1"
                                           :loading="isProgress"
                                           :disabled="isProgress"
                                           @click="openEditTenantModal(props.item)">
                                        <v-icon small>mdi-pencil</v-icon>
                                    </v-btn>
                                    <span>編集</span>
                                </v-tooltip>
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="red darken-1"
                                           :loading="isProgress"
                                           :disabled="isProgress"
                                           @click="openDeleteTenantModal(props.item)">
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
        <DeleteTenantModal slot="body" ref="deleteTenantModal"></DeleteTenantModal>
        <AddTenantModal slot="body" ref="addTenantModal"></AddTenantModal>
        <EditTenantModal slot="body" ref="editTenantModal"></EditTenantModal>
    </TemplateBase>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import TemplateBase from '@/components/TemplateBase'
  import DeleteTenantModal from '@/views/tenants/modal/DeleteTenantModal'
  import AddTenantModal from '@/views/tenants/modal/AddTenantModal'
  import EditTenantModal from '@/views/tenants/modal/EditTenantModal'
  import MENU from '@/lib/definition/mainMenu'


  export default {
    components: {
      TemplateBase,
      DeleteTenantModal,
      AddTenantModal,
      EditTenantModal
    },
    data() {
      return {
        isProgress: false,
        title: {icon: MENU.tenants.icon, text: MENU.tenants.text},
        breadcrumbs: [
          {
            text: 'ダッシュボード',
            disabled: false,
            to: '/dashboard'
          },
          {
            text: 'テナント管理',
            disabled: true,
            to: ''
          }
        ],
        dataTable: {
          isProgress: false,
          headers: [
            {text: 'テナント名', align: 'left', value: 'tenant_name'},
            {text: 'メールアドレス', align: 'left', value: 'email'},
            {text: '電話番号', align: 'left', value: 'tel'},
            {
              text: 'AWS アカウント数',
              align: 'center',
              value: 'aws_environments.length'
            },
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
        tenants: 'tenants/tenants'
      })
    },
    methods: {
      ...mapActions('tenants', ['fetchTenants']),
      initDataTable() {
        this.dataTable.isProgress = true
        this.isProgress = true
        this.fetchTenants().finally(() => {
          this.dataTable.isProgress = false
          this.isProgress = false
        })
      },
      openAddTenantModal() {
        this.$refs.addTenantModal.open().then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      },
      openEditTenantModal(tenant) {
        this.$refs.editTenantModal.open(tenant).then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      },
      openDeleteTenantModal(tenant) {
        // 削除モーダルを開く
        this.$refs.deleteTenantModal.open(tenant).then((res) => {
          if (res) {
            this.initDataTable()
          }
        })
      }
    },
    mounted() {
      // マウント時にテナント情報を取得する
      this.initDataTable()
    }
  }
</script>