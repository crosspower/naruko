<template>
    <div>
        <v-combobox
            v-model="country_code"
            prepend-icon="mdi-earth"
            :items="country_codes"
            item-text="label"
            :rules="codeRules"
            label="国番号*"
            return-object
        ></v-combobox>
        <v-text-field
            v-model="phone_number"
            :disabled=isProgress
            :rules="phoneRules"
            type="text"
            prepend-icon="mdi-phone"
            label="電話番号*"
        ></v-text-field>
    </div>
</template>

<script>
  import VALIDATION_RULE from '@/lib/definition/validationRule'
  import {AsYouType, isValidNumber} from 'libphonenumber-js'
  import {countries} from 'countries-list'

  export default {
    props: [`isProgress`],
    data() {
      return {
        phone_number: '',
        country_codes: this.countryList(),
        country_code: '',
        phoneRules: [
          v => !!v || '電話番号を入力してください。',
          (v) => {
            const message = '正しい電話番号を入力してください。'
            let valid = false
            if (v) {
              const region = this.country_code['countryCode']
              if (region == null) {
                return message
              }
                valid = new AsYouType(region).input(v) === v && isValidNumber(v, region)
            }
            return valid || message
          }
        ],
        codeRules: VALIDATION_RULE.NOTIFICATION.DESTINATION.CODE
      }
    },
    updated() {
      this.$emit('input', {
        phone_number: this.phone_number,
        country_code: this.country_code == null ? null : this.country_code['countryNo']
      })
    },
    methods: {
      countryList() {
        return Object.keys(countries).map(key => ({
          label: countries[key]['native'] + " +" + countries[key]['phone'],
          countryNo: countries[key]['phone'],
          countryCode: key
        }))
      }
    }
  }

</script>