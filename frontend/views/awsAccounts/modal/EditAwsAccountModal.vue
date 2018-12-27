<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">AWSアカウント編集</span>
                </v-card-title>
                <v-subheader>編集するAWSアカウントの情報を入力してください。</v-subheader>

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
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="name === nameUndo"
                                   @click="name = nameUndo">
                                <v-icon small
                                        v-text="name === nameUndo ? '' : 'mdi-undo'"></v-icon>
                            </v-btn>
                        </v-text-field>
                        <v-text-field
                                v-model="id"
                                :rules="idRules"
                                disabled
                                type="text"
                                prepend-icon="mdi-cloud"
                                label="AWSアカウントID*"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small disabled>
                            </v-btn>
                        </v-text-field>
                        <v-text-field
                                v-model="roleName"
                                :rules="roleNameRules"
                                disabled
                                type="text"
                                prepend-icon="mdi-cloud"
                                label="AWSロール名*"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small disabled>
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
        awsAccount: null,
        valid: true,
        name: '',
        nameUndo: '',
        roleName: '',
        id: '',
        externalId: '',
        nameRules: VALIDATION_RULE.AWS_ACCOUNT.NAME,
        roleNameRules: VALIDATION_RULE.AWS_ACCOUNT.ROLE_NAME,
        idRules: VALIDATION_RULE.AWS_ACCOUNT.ID,
        externalIdRules: [],
        resolve: null,
        reject: null
      }
    },
    methods: {
      ...mapActions('awsAccounts', ['editAwsAccount']),
      open(awsAccount) {
        // モーダルを開く
        this.awsAccount = awsAccount
        this.isProgress = false
        this.name = this.nameUndo = awsAccount.name
        this.id = awsAccount.aws_account_id
        this.roleName = awsAccount.aws_role

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
            name: this.name
          }
          this.editAwsAccount([this.awsAccount.id, data]).then(() => {
            this.resolve(true)
          }).catch(() => {
            this.reject()
          }).finally(() => {
            this.isOpen = false
            this.isProgress = false
            this.awsAccount = null
            this.$refs.form.reset()
          })
        }
      },
      cancel() {
        this.isOpen = false
        this.isProgress = false
        this.awsAccount = null
        this.$refs.form.reset()
        this.resolve(false)
      }
    }
  }
</script>