<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-flex xs12 slot="body">
            <v-card>
                <v-subheader>設定する情報を入力してください。</v-subheader>
                <v-card-text>
                    <v-form ref="userSettingForm" class="mr-5">
                        <v-text-field
                                v-model="tempUserData.name"
                                type="text"
                                prepend-icon="mdi-account"
                                label="ユーザー名*"
                                :rules="nameRules"
                                :disabled="isProgress"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="tempUserData.name === userData.name"
                                   @click="tempUserData.name = userData.name">
                                <v-icon small
                                        v-text="tempUserData.name === userData.name ? '' : 'mdi-undo'"
                                ></v-icon>
                            </v-btn>
                        </v-text-field>
                        <v-text-field
                                v-model="tempUserData.email"
                                type="text"
                                prepend-icon="mdi-email-outline"
                                label="メールアドレス*"
                                :rules="emailRules"
                                :disabled="isProgress"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="tempUserData.email === userData.email"
                                   @click="tempUserData.email = userData.email"
                            >
                                <v-icon small
                                        v-text="tempUserData.email === userData.email ? '' : 'mdi-undo'"
                                ></v-icon>
                            </v-btn>
                        </v-text-field>
                        <v-text-field
                                v-model="tempUserData.role.role_name"
                                prepend-icon="mdi-account"
                                readonly
                                disabled
                                label="権限"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small disabled></v-btn>
                        </v-text-field>
                        <v-text-field
                                v-model="tempUserData.password"
                                type="password"
                                prepend-icon="mdi-lock"
                                label="パスワード"
                                :disabled="isProgress"
                                :rules="tempUserData.password === '' ? [] : passwordRules"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small
                                   :disabled="tempUserData.password === ''"
                                   @click="tempUserData.password=''">
                                <v-icon small
                                        v-text="tempUserData.password === '' ? '' : 'mdi-undo'"
                                ></v-icon>
                            </v-btn>
                        </v-text-field>
                        <v-text-field
                                type="password"
                                prepend-icon="mdi-lock"
                                label="パスワードの確認"
                                v-if="tempUserData.password !== ''"
                                :rules="passwordConfirmRules"
                                :disabled="isProgress"
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small disabled></v-btn>
                        </v-text-field>
                        <v-autocomplete
                                v-model="tempUserData.aws_environments"
                                :items="tempUserData.aws_environments"
                                prepend-icon="mdi-cloud"
                                label="AWSアカウント"
                                disabled
                                dense
                                chips
                                multiple
                                readonly
                        >
                            <v-btn slot="append-outer" class="ma-0" icon flat small disabled></v-btn>
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
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat
                           @click="editUser"
                           :disabled="isProgress"
                           :loading="isProgress"
                    >
                        更新
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-flex>
    </TemplateBase>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'
  import TemplateBase from '@/components/TemplateBase'
  import MENU from '@/lib/definition/mainMenu'

  export default {
    components: {
      TemplateBase
    },
    data() {
      return {
        title: {icon: MENU.userSettings.icon, text: MENU.userSettings.text},
        breadcrumbs: [
          {
            text: 'ダッシュボード',
            disabled: false,
            to: '/dashboard'
          },
          {
            text: 'ユーザー設定',
            disabled: true,
            to: ''
          }
        ],
        tempUserData: {
          name: '',
          email: '',
          password: '',
          role: {},
          aws_environments: []
        },
        nameRules: VALIDATION_RULE.USER.NAME,
        emailRules: VALIDATION_RULE.USER.EMAIL,
        passwordRules: VALIDATION_RULE.USER.PASSWORD,
        passwordConfirmRules: [
          v => !!v || 'パスワードの確認を入力してください。',
          v => v === this.tempUserData.password || 'パスワードが一致しません。'
        ],
        isProgress: false
      }
    },
    computed: {
      ...mapGetters({
        userData: 'user/userData'
      })
    },
    methods: {
      ...mapActions('user', ['updateUser']),
      initPage() {
        this.tempUserData.name = this.userData.name
        this.tempUserData.email = this.userData.email
        this.tempUserData.password = ''
        this.tempUserData.role.role_name = this.userData.role.role_name
        this.tempUserData.aws_environments = []
        for (const awsEnv of this.userData.aws_environments) {
          this.tempUserData.aws_environments.push(awsEnv.name)
        }
      },
      editUser() {
        if (this.$refs.userSettingForm.validate()) {
          this.isProgress = true

          const name = this.tempUserData.name
          const email = this.tempUserData.email
          if (!this.tempUserData.password) {
            this.tempUserData.password = ''
          }
          const password = this.tempUserData.password

          const role = this.userData.role.id

          const awsEnvs = []
          for (const awsEnv of this.userData.aws_environments) {
            awsEnvs.push(awsEnv.id)
          }

          const data = {
            name,
            email,
            password,
            role,
            aws_environments: awsEnvs
          }
          this.updateUser(data).then(() => {
            this.initPage()
          }).finally(() => {
            this.isProgress = false
          })
        }
      }
    },
    mounted() {
      this.initPage()
    }
  }

</script>