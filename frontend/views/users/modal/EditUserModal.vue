<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">ユーザー編集</span>
                </v-card-title>
                <v-subheader>編集するユーザーの情報を入力してください。</v-subheader>

                <v-card-text>
                    <v-form ref="editUserForm" v-model="valid">
                        <v-text-field
                                v-model="name"
                                :counter="20"
                                :rules="nameRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-account"
                                label="ユーザー名*"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="name === nameUndo"
                                   @click="name = nameUndo">
                                <v-icon small
                                        v-text="name === nameUndo ? '' : 'mdi-undo'"></v-icon>
                            </v-btn>
                        </v-text-field>
                        <v-text-field
                                v-model="email"
                                :rules="emailRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-email-outline"
                                label="メールアドレス*"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="email === emailUndo"
                                   @click="email = emailUndo">
                                <v-icon small
                                        v-text="email === emailUndo ? '' : 'mdi-undo'"></v-icon>
                            </v-btn>
                        </v-text-field>
                        <v-select
                                v-model="role"
                                :rules="roleRules"
                                :items="selectableRoles"
                                :disabled="isProgress || !roleEditable"
                                item-text="name"
                                item-value="id"
                                prepend-icon="mdi-account"
                                label="権限*"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="role === roleUndo"
                                   @click="role = roleUndo">
                                <v-icon small
                                        v-text="role === roleUndo ? '' : 'mdi-undo'"></v-icon>
                            </v-btn>
                        </v-select>
                        <v-text-field
                                v-model="password"
                                :rules="password === '' ? [] : passwordRules"
                                :disabled="isProgress"
                                type="password"
                                prepend-icon="mdi-lock"
                                label="パスワード"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="password === ''"
                                   @click="password = '', passwordConfirm = ''">
                                <v-icon small
                                        v-text="password === '' ? '' : 'mdi-undo'"
                                ></v-icon>
                            </v-btn>
                        </v-text-field>
                        <v-text-field
                                v-model="passwordConfirm"
                                :rules="passwordConfirmRules"
                                :disabled="isProgress"
                                type="password"
                                prepend-icon="mdi-lock"
                                label="パスワードの確認"
                                v-if="password"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small disabled></v-btn>
                        </v-text-field>
                        <v-autocomplete
                                v-model="awsEnvs"
                                prepend-icon="mdi-cloud"
                                :rules="awsRules"
                                :items="selectableAwsEnvs"
                                :disabled="isProgress"
                                item-text="name"
                                item-value="id"
                                label="AWSアカウント*"
                                dense
                                chips
                                deletable-chips
                                multiple
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="awsEnvs.toString() === awsEnvsUndo.toString()"
                                   @click="awsEnvs = awsEnvsUndo.concat()">
                                <v-icon small
                                        v-text="awsEnvs.toString() === awsEnvsUndo.toString() ? '' : 'mdi-undo'"
                                ></v-icon>
                            </v-btn>
                            <template
                                    slot="item"
                                    slot-scope="{parent,item, tile}"
                            >
                                <v-list-tile-action>
                                    <v-checkbox hide-details v-model="tile.props.value"
                                                color="parent.color"></v-checkbox>
                                </v-list-tile-action>
                                <v-list-tile-content>
                                    <span v-html="`${parent.genFilteredText(item.name)}`">
                                    </span>
                                </v-list-tile-content>
                            </template>
                        </v-autocomplete>
                    </v-form>
                    <small>*必須項目</small>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat
                           @click="cancel"
                           :disabled="isProgress">
                        キャンセル
                    </v-btn>
                    <v-btn color="blue darken-1" flat
                           @click="confirm"
                           :disabled="isProgress"
                           :loading="isProgress">
                        編集
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
  import {mapActions, mapGetters} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        user: null,
        valid: true,
        name: '',
        nameUndo: '',
        email: '',
        emailUndo: '',
        password: '',
        passwordConfirm: '',
        awsEnvs: [],
        awsEnvsUndo: [],
        role: null,
        roleUndo: null,
        roleEditable: true,
        nameRules: VALIDATION_RULE.USER.NAME,
        emailRules: VALIDATION_RULE.USER.EMAIL,
        roleRules: VALIDATION_RULE.USER.ROLE,
        passwordRules: VALIDATION_RULE.USER.PASSWORD,
        passwordConfirmRules: [
          v => v === this.password || 'パスワードが一致しません。'
        ],
        awsRules: VALIDATION_RULE.USER.AWS_ENV,
        selectableRoles: [],
        selectableAwsEnvs: [],
        resolve: null,
        reject: null
      }
    },
    computed: {
      ...mapGetters({
        userData: 'user/userData',
        awsAccounts: 'awsAccounts/awsAccounts'
      })
    },
    methods: {
      ...mapActions('users', ['editUser']),
      ...mapActions('user', ['updateUser']),
      open(user, selectableRoles) {
        // モーダルを開く
        this.user = user
        this.selectableAwsEnvs = this.awsAccounts
        this.selectableRoles = selectableRoles
        this.isProgress = false

        this.name = this.nameUndo = user.name
        this.email = this.emailUndo = user.email
        this.role = this.roleUndo = user.role.id
        this.password = ''
        this.awsEnvs = []
        for (const awsEnv of user.aws_environments) {
          this.awsEnvs.push(awsEnv.id)
        }
        this.awsEnvsUndo = this.awsEnvs.concat()

        this.roleEditable = user.roleEditable

        this.isOpen = true
        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      confirm() {
        if (this.$refs.editUserForm.validate()) {
          this.isProgress = true

          if (!this.password) {
            this.password = ''
          }

          const data = {
            name: this.name,
            email: this.email,
            password: this.password,
            role: this.role,
            aws_environments: this.awsEnvs
          }

          let editUserPromise = null
          if (this.user.id === this.userData.id) {
            // 編集対象が自分の場合
            editUserPromise = this.updateUser(data)
          } else {
            // 編集対象が自分以外の場合
            editUserPromise = this.editUser([this.user.id, data])
          }

          editUserPromise.then(() => {
            this.resolve(`ユーザー ${this.name} (${this.email})を編集しました。`)
          }).catch(() => {
            this.reject(`ユーザー ${this.name} (${this.email})の編集に失敗しました。`)
          }).finally(() => {
            this.isOpen = false
            this.isProgress = false
            this.$refs.editUserForm.reset()
          })
        }
      },
      cancel() {
        this.isProgress = false
        this.user = null
        this.isOpen = false
        this.resolve()
      }
    }
  }
</script>