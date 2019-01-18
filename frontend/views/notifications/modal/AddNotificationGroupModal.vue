<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">通知グループ登録</span>
                </v-card-title>
                <v-subheader>登録する通知グループの情報を入力してください。</v-subheader>
                <v-card-text>
                    <v-form ref="form" v-model="valid">
                        <v-text-field
                                v-model="name"
                                :rules="nameRules"
                                :disabled="isProgress"
                                type="text"
                                prepend-icon="mdi-information"
                                label="名前*"
                        ></v-text-field>
                        <v-autocomplete
                                v-model="targetAwsAccounts"
                                prepend-icon="mdi-cloud"
                                :items="awsAccounts"
                                :disabled="isProgress"
                                item-text="name"
                                item-value="id"
                                label="通知対象 AWSアカウント*"
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
                        <v-autocomplete
                                v-model="targetDestinations"
                                prepend-icon="mdi-cloud"
                                :items="destinations"
                                :disabled="isProgress"
                                item-text="name"
                                item-value="id"
                                label="通知先*"
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
                                <v-list-tile-action class>
                                    <v-icon small v-if="item.type.id==='email'">mdi-email-outline</v-icon>
                                    <v-icon small v-if="item.type.id==='telephone'">mdi-phone</v-icon>
                                </v-list-tile-action>

                                <v-list-tile-content>
                                    <span v-html="`${parent.genFilteredText(item.name)}`">
                                    </span>
                                </v-list-tile-content>
                            </template>
                            <template slot="selection" slot-scope="data">
                                <v-chip
                                        :close="!data.parent.disabled"
                                        class="chip--select-multi"
                                        @input="data.parent.selectItem(data.item)"
                                >
                                    <v-icon small class="pr-1" v-if="data.item.type.id==='email'">mdi-email-outline</v-icon>
                                    <v-icon small class="pr-1" v-if="data.item.type.id==='telephone'">mdi-phone</v-icon>
                                    {{ data.item.name }}
                                </v-chip>
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
  import {mapActions, mapGetters} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'


  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        valid: true,
        name: '',
        nameRules: VALIDATION_RULE.NOTIFICATION.GROUP.NAME,
        targetAwsAccounts: [],
        targetDestinations: [],
        resolve: null,
        reject: null
      }
    },
    computed: {
      ...mapGetters({
        awsAccounts: 'awsAccounts/awsAccounts',
        destinations: 'notifications/destinations'
      })
    },
    methods: {
      ...mapActions('notifications', ['addNotificationGroup']),
      open() {
        // モーダルを開く
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
            aws_environments: this.targetAwsAccounts,
            destinations: this.targetDestinations
          }
          this.addNotificationGroup(data).then(() => {
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

<style scoped> .v-list__tile__action {
    min-width: 25px;
} </style>