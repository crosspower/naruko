<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">AWSアカウント登録</span>
                </v-card-title>
                <v-subheader>登録するAWSアカウントの情報を入力してください。</v-subheader>

                <v-card-text>
                    <v-form ref="form" v-model="valid">
                        <v-text-field
                                v-model="name"
                                :counter="20"
                                :rules="nameRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-cloud"
                                label="AWSアカウント名*"
                        ></v-text-field>
                        <v-text-field
                                v-model="id"
                                :rules="idRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-cloud"
                                label="AWSアカウントID*"
                        ></v-text-field>
                        <v-text-field
                                v-model="roleName"
                                :rules="roleNameRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-cloud"
                                label="AWSロール名*"
                        ></v-text-field>
                        <v-text-field
                                v-model="externalId"
                                :rules="externalIdRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-cloud"
                                label="AWS外部ID*"
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
        roleName: '',
        id: '',
        externalId: '',
        nameRules: VALIDATION_RULE.AWS_ACCOUNT.NAME,
        roleNameRules: VALIDATION_RULE.AWS_ACCOUNT.ROLE_NAME,
        idRules: VALIDATION_RULE.AWS_ACCOUNT.ID,
        externalIdRules: VALIDATION_RULE.AWS_ACCOUNT.EXTERNAL_ID,
        resolve: null,
        reject: null
      }
    },
    computed: {},
    methods: {
      ...mapActions('awsAccounts', ['addAwsAccount']),
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
            name: this.name,
            aws_account_id: this.id,
            aws_role: this.roleName,
            aws_external_id: this.externalId
          }
          this.addAwsAccount(data).then(() => {
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