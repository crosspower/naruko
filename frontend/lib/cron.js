import moment from 'moment-timezone'
import parser from 'cron-parser'

export default class Cron {

  static timezoneToUtc(cronString, timezone) {
    const splited = cronString.split(/\s/)
    const minute = splited[0].slice(5)
    let hour = splited[1]
    let date = splited[2].split(',')
    let month = splited[3].split(',')
    let dayOfWeek = splited[4].split(',')

    const testDate = 15
    const utc = moment.tz(`2000-01-${testDate} ${('00' + hour).slice(-2)}:${('00' + minute).slice(-2)}`, timezone).utc()

    if (utc.date() > testDate) {
      const incrimented = this._incrimentDate(date, dayOfWeek, month)
      date = incrimented.date
      month = incrimented.month
      dayOfWeek = incrimented.dayOfWeek
    } else if (utc.date() < testDate) {
      const decremented = this._decrementDate(date, dayOfWeek, month)
      date = decremented.date
      month = decremented.month
      dayOfWeek = decremented.dayOfWeek
    }

    return `cron(${utc.minutes()} ${utc.hour()} ${date.join()} ${month.join()} ${dayOfWeek.join()} *)`
  }

  static utcToTimezone(cronString, timezone) {
    const splited = cronString.split(/\s/)
    const minute = splited[0].slice(5)
    let hour = splited[1]
    let date = splited[2].split(',')
    let month = splited[3].split(',')
    let dayOfWeek = splited[4].split(',')

    const testDate = 15
    const tz = moment.utc(`2000-01-${testDate} ${('00' + hour).slice(-2)}:${('00' + minute).slice(-2)}`).tz(timezone)

    if (tz.date() > testDate) {
      const incrimented = this._incrimentDate(date, dayOfWeek, month)
      date = incrimented.date
      month = incrimented.month
      dayOfWeek = incrimented.dayOfWeek
    } else if (tz.date() < testDate) {
      const decremented = this._decrementDate(date, dayOfWeek, month)
      date = decremented.date
      month = decremented.month
      dayOfWeek = decremented.dayOfWeek
    }

    return `cron(${tz.minutes()} ${tz.hour()} ${date.join()} ${month.join()} ${dayOfWeek.join()} *)`
  }

  static _incrimentDate(date, dayOfWeek, month) {
    // 日付繰り上がり
    date = date.map((v) => {
      if (/^([1-9]\d*|0)$/.test(v)) {
        ++v
      }
      // 日付は31まで、Lは月末なので1を入れる
      if (v === 32 || v === 'L') {
        v = 1
      }
      return v
    })

    // 日付に1が含まれる場合月が変わっている
    if (date.includes(1)) {
      month = month.map((v) => {
        if (/^([1-9]\d*|0)$/.test(v)) {
          ++v
        }
        // 月は12まで
        if (v === 13) {
          v = 1
        }
        return v
      })
    }

    //曜日をずらす
    dayOfWeek = dayOfWeek.map((v) => {
      if (/^([1-9]\d*|0)$/.test(v)) {
        ++v
      }
      // 週は7まで
      if (v === 8) {
        v = 1
      }
      return v
    })

    return {date, dayOfWeek, month}
  }

  static _decrementDate(date, dayOfWeek, month) {
    // 日付繰り下がり
    let isMonthDecrement = false
    date = date.map((v) => {
      if (/^([1-9]\d*|0)$/.test(v)) {
        --v
      }
      // 日付が0の場合はLとなる
      if (v === 0) {
        v = "L"
        isMonthDecrement = true
      }
      return v
    })

    if (isMonthDecrement) {
      month = month.map((v) => {
        if (/^([1-9]\d*|0)$/.test(v)) {
          --v
        }
        // 月が0の場合は12
        if (v === 0) {
          v = 12
        }
        return v
      })
    }

    //曜日をずらす
    dayOfWeek = dayOfWeek.map((v) => {
      if (/^([1-9]\d*|0)$/.test(v)) {
        --v
      }
      if (v === 0) {
        v = 7
      }
      return v
    })

    return {date, dayOfWeek, month}
  }

  static next(cron, timezone, format) {
    const splited = cron.split(/\s/)
    const minute = splited[0].slice(5)
    let hour = splited[1]
    let date = splited[2]
    let month = splited[3]
    let dayOfWeek = splited[4]

    let hasLastDayOfMonth = false
    if (date === 'L') {
      date = '28-31'
      hasLastDayOfMonth = true
    }

    const interval = parser.parseExpression(`${minute} ${hour} ${date} ${month} ${dayOfWeek}`, {utc: true})

    if (hasLastDayOfMonth) {
      for (; ;) {
        const nextDate = interval.next().toDate()
        const next = moment.utc(nextDate)
        const endOfMonth = moment.utc(nextDate).endOf('month').date()
        if (next.date() === endOfMonth) {
          return next.tz(timezone).format(format)
        }
      }
    } else {
      return moment.utc(interval.next().toDate()).tz(timezone).format(format)
    }
  }
}

