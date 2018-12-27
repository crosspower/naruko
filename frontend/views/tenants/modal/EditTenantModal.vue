<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">テナント編集</span>
                </v-card-title>
                <v-subheader>編集するテナントの情報を入力してください。</v-subheader>

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
                        <v-text-field
                                v-model="tel"
                                :rules="telRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-phone"
                                label="電話番号*"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="tel === telUndo"
                                   @click="tel = telUndo">
                                <v-icon small
                                        v-text="tel === telUndo ? '' : 'mdi-undo'"></v-icon>
                            </v-btn>
                        </v-text-field>
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
  import {mapActions} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        tenant: null,
        valid: true,
        name: '',
        nameUndo: '',
        email: '',
        emailUndo: '',
        tel: '',
        telUndo: '',
        nameRules: VALIDATION_RULE.TENANT.NAME,
        emailRules: VALIDATION_RULE.TENANT.EMAIL,
        telRules: VALIDATION_RULE.TENANT.TEL,
        resolve: null,
        reject: null
      }
    },
    methods: {
      ...mapActions('tenants', ['editTenant']),
      open(tenant) {
        // モーダルを開く
        this.tenant = tenant
        this.isProgress = false
        this.name = this.nameUndo = tenant.tenant_name
        this.email = this.emailUndo = tenant.email
        this.tel = this.telUndo = tenant.tel

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
            tenant_name: this.name,
            email: this.email,
            tel: this.tel
          }
          this.editTenant([this.tenant.id, data]).then(() => {
            this.resolve(true)
          }).catch(() => {
            this.reject()
          }).finally(() => {
            this.isOpen = false
            this.isProgress = false
            this.$refs.form.reset()
          })
        }
      },
      cancel() {
        this.isOpen = false
        this.isProgress = false
        this.tenant = null
        this.$refs.form.reset()
        this.resolve(false)
      }
    }
  }
</script>