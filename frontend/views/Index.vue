<template>
    <v-container>
        <Alert></Alert>
        <v-layout align-center justify-center row>
            <v-card class="elevation-12 mt-5" width="500">
                <v-toolbar dark color="primary">
                    <v-toolbar-title>
                        ログイン
                    </v-toolbar-title>
                    <v-spacer></v-spacer>
                </v-toolbar>
                <v-card-text>
                    <v-form ref="form" id="check-login-form" @submit.prevent="submitLogin">
                        <v-text-field prepend-icon="mdi-email-outline" v-model="email" name="email" label="メールアドレス"
                                      type="text"
                                      required :rules="emailRules"></v-text-field>
                        <v-text-field id="password" v-model="password" prepend-icon="mdi-lock" name="password"
                                      label="パスワード"
                                      :rules="passwordRules"
                                      type="password" required></v-text-field>
                    </v-form>
                </v-card-text>
                <v-card-actions>
                    <v-btn flat class="ma-1" @click="openResetPassModal">
                        <small class="ml-1">
                            <v-icon small>mdi-information</v-icon>
                            パスワードを忘れた方はこちら
                        </small>
                    </v-btn>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" type="submit" :loading="loginProgress" :disabled="loginProgress"
                           form="check-login-form">
                        ログイン
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-layout>
        <!-- パスワード再発行 -->
        <v-layout row justify-center>
            <v-dialog v-model="resetPassModal.isOpen" persistent max-width="600px">
                <v-card>
                    <v-card-title>
                        <span class="headline">パスワード再発行</span>
                    </v-card-title>
                    <v-subheader>新しいパスワードがご登録のメールアドレスに送信されます。</v-subheader>
                    <v-card-text>
                        <v-form ref="resetPassForm" v-model="resetPassModal.valid">
                            <v-text-field
                                    v-model="resetPassModal.email"
                                    :rules="resetPassModal.emailRules"
                                    type="text"
                                    prepend-icon="mdi-email-outline"
                                    label="メールアドレス*"
                            ></v-text-field>
                        </v-form>
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="blue darken-1" flat @click.native="closeResetPassModal"
                               :disabled="resetPassModal.isProgress"
                               :loading="resetPassModal.isProgress"
                               @click="closeResetPassModal">
                            キャンセル
                        </v-btn>
                        <v-btn color="blue darken-1" flat @click.native="dialog = false"
                               :disabled="resetPassModal.isProgress"
                               :loading="resetPassModal.isProgress"
                               @click="resetPass">
                            送信
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </v-layout>
        <!-- パスワード再発行 -->
    </v-container>
</template>

<script>
  import {mapActions, mapGetters} from 'vuex'
  import Alert from '@/components/Alert'
  import VALIDATION_RULE from '@/lib/definition/validationRule'

  export default {
    components: {
      Alert
    },
    data() {
      return {
        valid: true,
        email: null,
        emailRules: [
          v => !!v || 'メールアドレスを入力してください。',
          v => /.+@.+/.test(v) || '正しいメールアドレスを入力してください。'
        ],
        password: null,
        passwordRules: [
          v => !!v || 'パスワードを入力してください。'
        ],
        loginProgress: false,
        errorMsg: null,
        resetPassModal: {
          isOpen: false,
          isProgress: false,
          valid: true,
          email: '',
          emailRules: VALIDATION_RULE.USER.EMAIL
        }
      }
    },
    computed: {
      ...mapGetters({
        isTokenExpired: 'user/isTokenExpired'
      })
    },
    methods: {
      ...mapActions('user', ['login', 'logout']),
      ...mapActions('alert', ['pushSuccessAlert', 'pushErrorAlert']),
      submitLogin() {
        if (this.$refs.form.validate()) {
          this.loginProgress = true
          this.errorMsg = null
          this.login([this.email, this.password]).then(() => {
            // ホーム画面にリダイレクト
            this.$router.push('/dashboard')
          }).catch(err => {
            // エラーメッセージを表示する
            if (err.response.data.non_field_errors) {
              this.pushErrorAlert(err.response.data.non_field_errors[0])
            }
          }).finally(() => {
            this.loginProgress = false
          })
        }
      },
      openResetPassModal() {
        this.$refs.resetPassForm.reset()
        this.resetPassModal.isOpen = true
      },
      closeResetPassModal() {
        this.resetPassModal.isProgress = false
        this.resetPassModal.isOpen = false
        this.$refs.resetPassForm.reset()
      },
      resetPass() {
        if (this.$refs.resetPassForm.validate()) {
          this.resetPassModal.isProgress = true
          const email = this.resetPassModal.email
          this.$request.auth.reset(email).then(() => {
            this.pushSuccessAlert(`パスワードを再発行しました。`)
          }).catch(() => {
            this.pushErrorAlert(`パスワードの再発行に失敗しました。`)
          }).finally(() => {
            this.closeResetPassModal()
          })
        }
      }
    },
    beforeMount() {
      if (!this.isTokenExpired) {
        this.logout()
      }
    }
  }
</script>
