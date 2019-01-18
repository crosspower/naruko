import {AsYouType, isValidNumber} from 'libphonenumber-js'
import Enum from '@/lib/definition/enum'

export default new Enum({
  USER: new Enum({
    NAME: [
      v => !!v || 'ユーザー名を入力してください。'
    ],
    EMAIL: [
      v => !!v || 'メールアドレスを入力してください。',
      v => /.+@.+/.test(v) || '正しいメールアドレスを入力してください。'
    ],
    PASSWORD: [
      v => !!v || 'パスワードを入力してください。',
      v => /^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?\d)(?=.*?[!-/:-@[-`{-~])[!-~]{8,200}$/.test(v) || '半角英数字、大文字、小文字、記号を含む、8文字以上で入力してください。'
    ],
    ROLE: [
      v => !!v || '権限を選択してください。'
    ],
    AWS_ENV: [
      v => v.length !== 0 || 'AWSアカウントを選択してください。'
    ]
  }),
  TENANT: new Enum({
    NAME: [
      v => !!v || 'テナント名を入力してください。'
    ],
    EMAIL: [
      v => !!v || 'メールアドレスを入力してください。',
      v => /.+@.+/.test(v) || '正しいメールアドレスを入力してください。'
    ],
    TEL: [
      v => !!v || '電話番号を入力してください。',
      (v) => {
        const message = '正しい電話番号を入力してください。'
        let valid = false
        if (v) {
          valid = new AsYouType('JP').input(v) === v && isValidNumber(v, 'JP')
        }
        return valid || message
      }
    ]
  }),
  AWS_ACCOUNT: new Enum({
    NAME: [
      v => !!v || 'AWSアカウント名を入力してください。'
    ],
    ID: [
      v => !!v || 'AWSアカウントIDを入力してください。'
    ],
    ROLE_NAME: [
      v => !!v || 'AWSロール名を入力してください。'
    ],
    EXTERNAL_ID: [
      v => !!v || 'AWS外部IDを入力してください。'
    ]
  }),
  MONITOR: new Enum({
    CAUTION_THRESHOLD: [
      v => !!v || '警告閾値を入力してください。',
      v => /^([1-9]\d*|0)(\.\d+)?$/.test(v) || '正しい警告閾値を入力してください。'
    ],
    DANGER_THRESHOLD: [
      v => !!v || '危険閾値を入力してください。',
      v => /^([1-9]\d*|0)(\.\d+)?$/.test(v) || '正しい警告閾値を入力してください。'
    ],
    STATISTIC: [
      v => !!v || '統計を選択してください。'
    ],
    PERIOD: [
      v => !!v || '間隔を選択してください。'
    ],
    EVALUATION_PERIOD: [
      v => !!v || '試行回数を入力してください。'
    ]
  }),
  NOTIFICATION: new Enum({
    DESTINATION: {
      NAME: [
        v => !!v || '名前を入力してください。'
      ],
      ADDRESS: [
        v => !!v || 'メールアドレスを入力してください。',
        v => /.+@.+/.test(v) || '正しいメールアドレスを入力してください。'
      ],
      TEL: [
        v => !!v || '電話番号を入力してください。',
        (v) => {
          const message = '正しい電話番号を入力してください。'
          let valid = false
          if (v) {
            valid = new AsYouType('JP').input(v) === v && isValidNumber(v, 'JP')
          }
          return valid || message
        }
      ]
    },
    GROUP: {
      NAME: [
        v => !!v || '名前を入力してください。'
      ]
    }
  }),
  SCHEDULE: new Enum({
    NAME: [
      v => !!v || 'スケジュール名を入力してください。'
    ],
    ACTION: [
      v => !!v || 'アクションを選択してください。'
    ],
    MONTH: [
      v => !!v.length || '予定月を選択してください。'
    ],
    WEEK_OF_DAYS: [
      v => !!v.length || '予定曜日を選択してください。'
    ],
    DATE: [
      v => !!/^([1-9]\d*|0)$/.test(v) || '予定日を選択してください。'
    ],
    HOUR: [
      v => !!/^([1-9]\d*|0)$/.test(v) || '予定時刻を選択してください。'
    ],
    MINUTES: [
      v => !!/^([1-9]\d*|0)$/.test(v) || '予定時刻(分)を選択してください。'
    ],
    SCHEDULE_TYPE: [
      v => !!/^([1-9]\d*|0)$/.test(v) || 'スケジュールタイプを選択してください。'
    ]
  })
})