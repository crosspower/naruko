<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">テナント登録</span>
                </v-card-title>
                <v-subheader>登録するテナントの情報を入力してください。</v-subheader>

                <v-card-text>
                    <v-form ref="form" v-model="valid">
                        <v-text-field
                                v-model="name"
                                :counter="20"
                                :rules="nameRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-domain"
                                label="テナント名*"
                        ></v-text-field>
                        <v-text-field
                                v-model="email"
                                :rules="emailRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-email-outline"
                                label="メールアドレス*"
                        ></v-text-field>
                        <v-text-field
                                v-model="tel"
                                :rules="telRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-phone"
                                label="電話番号*"
                        ></v-text-field>
                        <v-text-field
                                v-model="username"
                                :rules="usernameRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-account"
                                label="初期ユーザー名*"
                        ></v-text-field>
                        <v-text-field
                                v-model="userEmail"
                                :rules="userEmailRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-email-outline"
                                label="初期ユーザーメールアドレス*"
                        ></v-text-field>
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
  import {mapActions} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        valid: true,
        name: '',
        email: '',
        tel: '',
        username: '',
        userEmail: '',
        nameRules: VALIDATION_RULE.TENANT.NAME,
        emailRules: VALIDATION_RULE.TENANT.EMAIL,
        telRules: VALIDATION_RULE.TENANT.TEL,
        usernameRules: VALIDATION_RULE.USER.NAME,
        userEmailRules: VALIDATION_RULE.USER.EMAIL,
        resolve: null,
        reject: null
      }
    },
    computed: {},
    methods: {
      ...mapActions('tenants', ['addTenant']),
      open() {
        // モーダルを開く
        this.$refs.form.reset()
        this.isProgress = false
        this.isOpen = true
        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      confirm() {
        if (this.$refs.form.validate()) {
          this.isProgress = true

          const data = {
            tenant: {
              tenant_name: this.name,
              email: this.email,
              tel: this.tel
            },
            user: {
              name: this.username,
              email: this.userEmail
            }
          }

          this.addTenant(data).then(() => {
            return this.resolve(true)
          }).catch(() => {
            return this.reject()
          }).finally(() => {
            this.isOpen = false
            this.isProgress = false
            this.$refs.form.reset()
          })
        }
      },
      cancel() {
        this.isProgress = false
        this.isOpen = false
        this.$refs.form.reset()
        this.resolve(false)
      }
    }
  }
</script>