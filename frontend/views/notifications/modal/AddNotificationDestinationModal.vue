<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">通知先登録</span>
                </v-card-title>
                <v-subheader>登録する通知先の情報を入力してください。</v-subheader>
                <v-card-text>
                    <v-form ref="form" v-model="valid">
                        <v-select
                                v-model="type"
                                prepend-icon="mdi-format-list-bulleted-type"
                                :items="types"
                                item-text="name"
                                item-value="id"
                                label="タイプ*"
                        ></v-select>
                        <v-text-field
                                v-model="name"
                                :disabled="isProgress"
                                :rules="nameRules"
                                type="text"
                                prepend-icon="mdi-information"
                                label="名前*"
                        ></v-text-field>
                        <v-text-field
                                v-model="address"
                                :disabled="isProgress"
                                :rules="addressRules"
                                type="text"
                                prepend-icon="mdi-email-outline"
                                label="メールアドレス*"
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
  import DESTINATION_TYPES from '@/lib/definition/destinationTypes'


  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        valid: true,
        types: DESTINATION_TYPES.getEnums(),
        type: '',
        name: '',
        address: '',
        nameRules: VALIDATION_RULE.NOTIFICATION.DESTINATION.NAME,
        addressRules: VALIDATION_RULE.NOTIFICATION.DESTINATION.ADDRESS,
        resolve: null,
        reject: null
      }
    },
    methods: {
      ...mapActions('notifications', ['addDestination']),
      open() {
        // モーダルを開く
        this.type = DESTINATION_TYPES.email.name

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
            type: this.type,
            address: this.address
          }
          this.addDestination(data).then(() => {
            return this.resolve(true)
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
        this.isProgress = false
        this.isOpen = false
        this.$refs.form.reset()
        this.resolve(false)
      }
    }
  }
</script>