<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="600">
            <v-card>
                <v-card-title class="headline">スケジュールの{{editMode? '編集':'登録'}}</v-card-title>

                <v-stepper v-model="step">
                    <v-stepper-header class="elevation-0">
                        <v-stepper-step step="1">
                            基本設定
                        </v-stepper-step>
                        <v-divider></v-divider>
                        <v-stepper-step step="2">
                            アクション設定
                        </v-stepper-step>
                        <v-divider></v-divider>
                        <v-stepper-step step="3">
                            実行日時設定
                        </v-stepper-step>
                    </v-stepper-header>
                    <v-stepper-items>
                        <v-stepper-content step="1">
                            <v-card>
                                <v-card-text class="pt-0">
                                    <v-form ref="formStep1" @submit.prevent="">
                                        <v-text-field
                                                v-model="name"
                                                :disabled="isProgress"
                                                :rules="nameRules"
                                                type="text"
                                                label="スケジュール名"
                                        ></v-text-field>
                                        <v-checkbox
                                                :disabled="isProgress"
                                                hide-details
                                                label="有効"
                                                v-model="enabled"
                                                class="ma-0 pb-2"
                                        ></v-checkbox>
                                        <v-checkbox
                                                :disabled="isProgress"
                                                label="実行結果を通知する"
                                                v-model="alertEnabled"
                                                class="ma-0"
                                        ></v-checkbox>
                                    </v-form>
                                </v-card-text>
                                <v-card-actions>
                                    <v-spacer></v-spacer>
                                    <v-btn flat @click="cancel">キャンセル</v-btn>
                                    <v-btn color="primary" @click="next(step)">次へ</v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-stepper-content>
                        <v-stepper-content step="2">
                            <v-card>
                                <v-card-text class="pt-0">
                                    <v-form ref="formStep2" @submit.prevent="">
                                        <v-select
                                                :items="actions"
                                                v-model="action"
                                                :rules="actionRules"
                                                label="アクション"
                                                item-text="name"
                                                item-value="id"
                                        ></v-select>
                                        <v-checkbox
                                                label="再起動しない"
                                                v-model="noReboot"
                                                class="ma-0"
                                                v-if="resource.service === 'EC2' && action === 'BACKUP'"
                                        >
                                            <v-tooltip top slot="append">
                                                <v-icon slot="activator">mdi-information</v-icon>
                                                <span>
                                                    有効な場合、Amazon EC2 はイメージの作成前にインスタンスをシャットダウンしません。<br>
                                                    このオプションを使用すると、作成したイメージのファイルシステムの完全性は保証できません。
                                                </span>
                                            </v-tooltip>
                                        </v-checkbox>
                                    </v-form>
                                </v-card-text>
                                <v-card-actions>
                                    <v-spacer></v-spacer>
                                    <v-btn flat @click="step = 1">戻る</v-btn>
                                    <v-btn color="primary" @click="next(step)">次へ</v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-stepper-content>
                        <v-stepper-content step="3">
                            <v-card>
                                <v-form ref="formStep3" @submit.prevent="">
                                    <v-card-text class="pt-0">
                                        <v-select
                                                :items="scheduleTypes"
                                                v-model="selectedScheduleType"
                                                :disabled="isProgress"
                                                :rules="scheduleTypeRules"
                                                label="スケジュールタイプ"
                                                prepend-icon="mdi-calendar"
                                                item-text="name"
                                                item-value="value"
                                        ></v-select>
                                        <template>
                                            <v-select v-if="selectedScheduleType === 0"
                                                      :items="month"
                                                      v-model="selectedMonth"
                                                      :rules="monthRules"
                                                      :disabled="isProgress"
                                                      item-text="name"
                                                      item-value="value"
                                                      label="予定月"
                                                      prepend-icon="mdi-calendar"
                                                      multiple
                                                      @change="onChangeMonth">
                                            </v-select>
                                            <v-select v-if="selectedScheduleType === 0"
                                                      label="予定日"
                                                      prepend-icon="mdi-calendar"
                                                      :items="date"
                                                      v-model="selectedDate"
                                                      :rules="dateRules"
                                                      :disabled="isProgress"
                                                      item-text="name"
                                                      item-value="value"
                                            ></v-select>
                                            <v-select v-if="selectedScheduleType === 1"
                                                      :items="weekOfDays"
                                                      v-model="selectedWeekOfDays"
                                                      :rules="weekOfDaysRules"
                                                      :disabled="isProgress"
                                                      item-text="name"
                                                      item-value="value"
                                                      label="予定曜日"
                                                      prepend-icon="mdi-calendar"
                                                      multiple
                                                      @change="onChangeWeekOfDays">
                                            </v-select>
                                            <v-layout row wrap>
                                                <v-flex xs6>
                                                    <v-select
                                                            label="予定時刻"
                                                            prepend-icon="mdi-clock-outline"
                                                            :items="hours"
                                                            :rules="hourRules"
                                                            v-model="selectedHour"
                                                            suffix="時"
                                                            :disabled="isProgress"
                                                    ></v-select>
                                                </v-flex>
                                                <v-flex xs6>
                                                    <v-select
                                                            :items="minutes"
                                                            v-model="selectedMinutes"
                                                            :rules="minutesRules"
                                                            suffix="分"
                                                            :disabled="isProgress"
                                                    ></v-select>
                                                </v-flex>
                                            </v-layout>
                                        </template>
                                    </v-card-text>
                                </v-form>
                                <v-card-actions>
                                    <v-spacer></v-spacer>
                                    <v-btn flat
                                           :disabled="isProgress"
                                           :loading="isProgress"
                                           @click="step = 2">
                                        戻る
                                    </v-btn>
                                    <v-btn color="primary"
                                           :disabled="isProgress"
                                           :loading="isProgress"
                                           @click="confirm">
                                        {{editMode? '編集':'登録'}}
                                    </v-btn>
                                </v-card-actions>

                            </v-card>
                        </v-stepper-content>
                    </v-stepper-items>
                </v-stepper>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
  import {mapActions, mapGetters} from 'vuex'
  import VALIDATION_RULE from '@/lib/definition/validationRule'
  import RESOURCES from '@/lib/definition/resources'
  import Cron from '@/lib/cron'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        editMode: 'false',
        title: '',
        body: '',
        schedule: null,
        step: 1,
        scheduleTypes: [
          {name: '月指定', value: 0},
          {name: '曜日指定', value: 1},
          {name: '毎日', value: 2}
        ],
        hours: [...Array(24).keys()],
        minutes: [...Array(60).keys()],
        month: [],
        date: [],
        weekOfDays: [
          {name: '日曜日', value: 1},
          {name: '月曜日', value: 2},
          {name: '火曜日', value: 3},
          {name: '水曜日', value: 4},
          {name: '木曜日', value: 5},
          {name: '金曜日', value: 6},
          {name: '土曜日', value: 7}
        ],
        selectedScheduleType: 0,
        alertEnabled: true,
        enabled: true,
        name: '',

        actions: [],
        action: null,
        selectedHour: 0,
        selectedMinutes: 0,
        selectedMonth: [],
        selectedWeekOfDays: [],
        selectedDate: null,
        nameRules: VALIDATION_RULE.SCHEDULE.NAME,
        actionRules: VALIDATION_RULE.SCHEDULE.ACTION,
        monthRules: VALIDATION_RULE.SCHEDULE.MONTH,
        weekOfDaysRules: VALIDATION_RULE.SCHEDULE.WEEK_OF_DAYS,
        dateRules: VALIDATION_RULE.SCHEDULE.DATE,
        scheduleTypeRules: VALIDATION_RULE.SCHEDULE.SCHEDULE_TYPE,
        hourRules: VALIDATION_RULE.SCHEDULE.HOUR,
        minutesRules: VALIDATION_RULE.SCHEDULE.MINUTES,
        noReboot: true,
        resolve: null,
        reject: null
      }
    },
    computed: {
      ...mapGetters({
        resource: 'resourceDetail/resource'
      })
    },
    methods: {
      ...mapActions('resourceDetail', ['addSchedule', 'editSchedule']),
      init() {
        this.month = []
        this.month.push({name: '毎月', value: 0})
        for (let i = 0; i < 12; i++) {
          this.month.push({
            name: `${i + 1}月`,
            value: i + 1
          })
        }

        this.date = []
        for (let i = 0; i < 31; i++) {
          this.date.push({
            name: `${i + 1}日`,
            value: i + 1
          })
        }

        this.actions = RESOURCES[this.$route.query.service.toUpperCase()].scheduleActions.getEnums()
      },
      open(schedule) {
        // モーダルを開く
        if (schedule) {
          this.editMode = true
          this.schedule = schedule
          this.name = schedule.name
          this.alertEnabled = schedule.notification.value
          this.enabled = schedule.is_active.value
          this.action = schedule.action.id
          this.noReboot = schedule.params.no_reboot
          const cron = Cron.utcToTimezone(schedule.schedule_expression, 'Asia/Tokyo')
          this.setCronValue(cron)
        } else {
          this.editMode = false
          this.alertEnabled = true
          this.enabled = true
          this.noReboot = true
        }
        if (this.noReboot === undefined) {
          this.noReboot = true
        }

        this.step = 1
        this.isProgress = false
        this.body = `${this.resource.name}のバックアップを作成します。`
        this.isOpen = true
        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      next(currentStep) {
        if (currentStep === 1 && this.$refs.formStep1.validate()) {
          this.step = currentStep + 1
        } else if (currentStep === 2 && this.$refs.formStep2.validate()) {
          this.step = currentStep + 1
        }
      },
      onChangeMonth(v) {
        // 毎月が選択された場合にすべての選択を解除する
        if (v[v.length - 1] === 0) {
          this.selectedMonth = [0]
        } else if (v.length > 1 && v[0] === 0) {
          this.selectedMonth.shift()
        }
        // ソート
        this.selectedMonth.sort((a, b) => a - b)
      },
      onChangeWeekOfDays() {
        this.selectedWeekOfDays.sort((a, b) => a - b)
      },
      createCron() {
        const minute = this.selectedMinutes
        const hour = this.selectedHour
        let date = '*'
        let month = '*'
        let dayOfWeek = '?'

        if (this.selectedScheduleType === 0) {
          // 月指定
          date = this.selectedDate
          month = this.selectedMonth.join(',')
          if (month === '0') {
            month = '*'
          }
          dayOfWeek = '?'
        }

        if (this.selectedScheduleType === 1) {
          // 曜日指定
          if (this.selectedWeekOfDays.length !== 7) {
            date = '?'
            dayOfWeek = this.selectedWeekOfDays.join(',')
          }
        }
        return Cron.timezoneToUtc(`cron(${minute} ${hour} ${date} ${month} ${dayOfWeek} *)`, 'Asia/Tokyo')
      },
      setCronValue(cron) {
        const splited = cron.split(/\s/)
        const minutes = splited[0].slice(5)
        const hour = splited[1]
        const date = splited[2].split(',')
        const month = splited[3].split(',')
        const dayOfWeek = splited[4].split(',')

        this.selectedMinutes = parseInt(minutes)
        this.selectedHour = parseInt(hour)

        if (date.length > 1) {
          // 日付が複数の場合はパースできない
          return
        }

        if (date.includes('?')) {
          // dateが?の場合は曜日選択
          this.selectedScheduleType = 1
          this.selectedWeekOfDays = dayOfWeek.map(v => parseInt(v))
        } else if (date.includes('*')) {
          // *は毎日
          this.selectedScheduleType = 2
        } else {
          // 月指定
          this.selectedScheduleType = 0
          if (month.includes('*')) {
            this.selectedMonth = [0]
          } else {
            this.selectedMonth = month.map(v => parseInt(v))
          }
          this.selectedDate = parseInt(date[0])
        }
      },
      confirm() {
        if (this.$refs.formStep1.validate() && this.$refs.formStep2.validate() && this.$refs.formStep3.validate()) {
          this.isProgress = true
          let params = {}
          if (this.action === RESOURCES.EC2.scheduleActions.BACKUP.id) {
            params = {
              no_reboot: this.noReboot
            }
          }
          const data = {
            name: this.name,
            is_active: this.enabled,
            action: this.action,
            schedule_expression: this.createCron(),
            params: params,
            notification: this.alertEnabled
          }
          let request
          if (this.editMode) {
            request = this.editSchedule([this.schedule.id, data])
          } else {
            request = this.addSchedule(data)
          }
          request.then(() => {
            this.resolve(true)
          }).catch(() => {
            this.reject()
          }).finally(() => {
            this.isProgress = false
            this.isOpen = false
            this.$refs.formStep1.reset()
            this.$refs.formStep2.reset()
            this.$refs.formStep3.reset()
          })
        }
      },
      cancel() {
        this.isProgress = false
        this.isOpen = false
        this.resolve(false)
        this.$refs.formStep1.reset()
        this.$refs.formStep2.reset()
        this.$refs.formStep3.reset()
      }
    },
    created() {
      this.init()
    }
  }
</script>
