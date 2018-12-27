<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">ユーザー登録</span>
                </v-card-title>
                <v-subheader>登録するユーザーの情報を入力してください。</v-subheader>

                <v-card-text>
                    <v-form ref="addUserForm" v-model="valid">

                        <v-text-field
                                v-model="name"
                                :counter="20"
                                :rules="nameRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-account"
                                label="ユーザー名*"
                        ></v-text-field>
                        <v-text-field
                                v-model="email"
                                :rules="emailRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-email-outline"
                                label="メールアドレス*"
                        ></v-text-field>
                        <v-select
                                v-model="role"
                                :rules="roleRules"
                                :items="selectableRoles"
                                :disabled="isProgress"
                                item-text="name"
                                item-value="id"
                                prepend-icon="mdi-account"
                                label="権限*"
                        ></v-select>
                        <v-text-field
                                v-model="password"
                                :rules="passwordRules"
                                :disabled="isProgress"
                                type="password"
                                prepend-icon="mdi-lock"
                                label="パスワード*"
                        ></v-text-field>
                        <v-text-field
                                v-model="passwordConfirm"
                                :rules="passwordConfirmRules"
                                :disabled="isProgress"
                                type="password"
                                prepend-icon="mdi-lock"
                                label="パスワードの確認*"
                        ></v-text-field>
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
                        登録
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        valid: true,
        name: '',
        email: '',
        password: '',
        passwordConfirm: '',
        awsEnvs: [],
        role: null,
        nameRules: VALIDATION_RULE.USER.NAME,
        emailRules: VALIDATION_RULE.USER.EMAIL,
        roleRules: VALIDATION_RULE.USER.ROLE,
        passwordRules: VALIDATION_RULE.USER.PASSWORD,
        passwordConfirmRules: [
          v => !!v || 'パスワードの確認を入力してください。',
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
      ...mapActions('users', ['addUser']),
      open(selectableRoles) {
        // モーダルを開く
        this.$refs.addUserForm.reset()
        this.isProgress = false
        this.selectableRoles = selectableRoles
        this.selectableAwsEnvs = this.awsAccounts
        this.isOpen = true
        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      confirm() {
        if (this.$refs.addUserForm.validate()) {
          this.isProgress = true
          const data = {
            name: this.name,
            email: this.email,
            password: this.password,
            role: this.role,
            aws_environments: this.awsEnvs
          }
          this.addUser(data).then(() => {
            return this.resolve(true)
          }).catch(() => {
            return this.reject()
          }).finally(() => {
            this.isOpen = false
            this.isProgress = false
            this.$refs.addUserForm.reset()
          })
        }
      },
      cancel() {
        this.isProgress = false
        this.isOpen = false
        this.$refs.addUserForm.reset()
        this.resolve(false)
      }
    }
  }
</script>