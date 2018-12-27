<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-flex xs12 slot="body">
            <v-card>
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
                    <v-btn color="primary" @click="openAddUserModal"
                           :disabled="isProgress">
                        <v-icon small>mdi-plus</v-icon>
                        ユーザー登録
                    </v-btn>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               @click="initUsersDataTable"
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
                        :items="users"
                        :search="dataTable.search"
                        :pagination.sync="dataTable.pagination"
                        :loading="dataTable.isProgress"
                        item-key="name"
                >
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr>
                            <td>{{ props.item.name }}</td>
                            <td class="text-xs-left">{{ props.item.email }}</td>
                            <td class="text-xs-left">
                                <div v-for="aws in props.item.aws_environments" :key="aws.id">
                                    {{ aws.name }}
                                </div>
                            </td>
                            <td class="text-xs-left">{{ props.item.role.role_name }}</td>
                            <td class="text-xs-center" width="110px">
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="blue darken-1"
                                           :loading="isProgress"
                                           :disabled="isProgress"
                                           v-if="props.item.editable"
                                           @click="openEditUserModal(props.item)">
                                        <v-icon small>mdi-pencil</v-icon>
                                    </v-btn>
                                    <span>編集</span>
                                </v-tooltip>
                                <v-tooltip top>
                                    <v-btn slot="activator" class="ma-0" icon flat small
                                           color="red darken-1"
                                           :loading="isProgress"
                                           :disabled="isProgress"
                                           @click="openDeleteUserModal(props.item)"
                                           v-if="props.item.deletable">
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
        <DeleteUserModal slot="body" ref="deleteUserModal"></DeleteUserModal>
        <AddUserModal slot="body" ref="addUserModal"></AddUserModal>
        <EditUserModal slot="body" ref="editUserModal"></EditUserModal>
    </TemplateBase>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'

  import ROLE from '@/lib/definition/role'
  import TemplateBase from '@/components/TemplateBase'
  import DeleteUserModal from '@/views/users/modal/DeleteUserModal'
  import AddUserModal from '@/views/users/modal/AddUserModal'
  import EditUserModal from '@/views/users/modal/EditUserModal'
  import MENU from '@/lib/definition/mainMenu'


  export default {
    components: {
      TemplateBase,
      DeleteUserModal,
      AddUserModal,
      EditUserModal
    },
    data() {
      return {
        isProgress: false,
        title: {icon: MENU.users.icon, text: MENU.users.text},
        actionButtonItems: [
          {title: 'ユーザー編集', icon: 'mdi-pencil'},
          {title: 'ユーザー削除', icon: 'mdi-delete'}
        ],
        breadcrumbs: [
          {
            text: 'ダッシュボード',
            disabled: false,
            to: '/dashboard'
          },
          {
            text: 'ユーザー管理',
            disabled: true,
            to: ''
          }
        ],
        dataTable: {
          isProgress: false,
          pagination: {
            sortBy: 'name'
          },
          search: '',
          headers: [
            {text: 'ユーザー名', align: 'left', value: 'name'},
            {text: 'メールアドレス', align: 'left', value: 'email'},
            {
              text: 'AWS アカウント',
              align: 'left',
              value: 'aws_environments_joined'
            },
            {text: '権限', align: 'left', value: 'role.role_name'},
            {text: '', value: 'name', sortable: false}
          ],
          users: this.users,
          selected: [],
          adminUserCount: 0,
          masterUserCount: 0
        }
      }
    },
    computed: {
      ...mapGetters({
        userData: 'user/userData',
        users: 'users/users'
      })
    },
    methods: {
      ...mapActions('user', ['updateUser']),
      ...mapActions('users', ['fetchUsers']),
      ...mapActions('awsAccounts', ['fetchAwsAccounts']),
      initUsersDataTable() {
        // データテーブルを初期化する
        this.dataTable.isProgress = true
        this.isProgress = true

        // ユーザー情報取得
        this.fetchUsers()
            .catch(() => {
              this.$refs.base.pushAlert('error', 'mdi-alert-circle', `ユーザー情報の取得に失敗しました。`)
            })
            .finally(() => {
              this.dataTable.isProgress = false
              this.isProgress = false
            })
      },
      openDeleteUserModal(user) {
        // ユーザー削除モーダルを開く
        this.$refs.deleteUserModal.open(user).then((res) => {
          if (res) {
            this.initUsersDataTable()
          }
        })
      },
      openAddUserModal() {
        let selectableRoles = [ROLE.ADMIN, ROLE.USER]
        if (this.userData.role.id === ROLE.MASTER.id) {
          selectableRoles = [ROLE.MASTER, ROLE.ADMIN, ROLE.USER]
        }
        this.fetchAwsAccounts().then(() => {
          this.$refs.addUserModal.open(selectableRoles).then((res) => {
            if (res) {
              this.initUsersDataTable()
            }
          })
        })
      },
      openEditUserModal(user) {
        let selectableRoles = [ROLE.ADMIN, ROLE.USER]
        if (this.userData.role.id === ROLE.MASTER.id) {
          selectableRoles = [ROLE.MASTER, ROLE.ADMIN, ROLE.USER]
        }
        this.fetchAwsAccounts().then(() => {
          this.$refs.editUserModal.open(user, selectableRoles).then((res) => {
            if (res) {
              this.initUsersDataTable()
            }
          })
        })
      }
    },
    mounted() {
      // マウント時にユーザー情報を取得する
      this.initUsersDataTable()
    }
  }
</script>