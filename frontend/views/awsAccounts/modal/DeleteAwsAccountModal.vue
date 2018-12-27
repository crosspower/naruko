<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="400">
            <v-card>
                <v-card-title class="headline">AWSアカウント削除</v-card-title>
                <v-card-text>
                    {{ body }}
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat
                           @click="cancel"
                           :disabled="isProgress">キャンセル
                    </v-btn>
                    <v-btn color="red darken-1" flat
                           @click="confirm"
                           :loading="isProgress"
                           :disabled="isProgress">削除
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
  import {mapActions} from 'vuex'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        body: '',
        awsAccount: null,
        resolve: null,
        reject: null
      }
    },
    methods: {
      ...mapActions('awsAccounts', ['deleteAwsAccount']),
      open(awsAccount) {
        // モーダルを開く
        this.awsAccount = awsAccount
        this.isProgress = false
        this.body = `${awsAccount.name}を削除します。`
        this.isOpen = true
        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      confirm() {
        this.isProgress = true
        this.deleteAwsAccount(this.awsAccount.id).then(() => {
          this.resolve(true)
        }).catch(() => {
          this.reject()
        }).finally(() => {
          this.awsAccount = null
          this.isProgress = false
          this.isOpen = false
        })
      },
      cancel() {
        this.isProgress = false
        this.awsAccount = null
        this.isOpen = false
        this.resolve(false)
      }
    }
  }
</script>