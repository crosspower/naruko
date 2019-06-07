<template>
    <div>
        <v-text-field
            v-model="address"
            :disabled=isProgress
            :rules="addressRules"
            type="text"
            prepend-icon="mdi-email-outline"
            label="メールアドレス*"
        ></v-text-field>
    </div>
</template>

<script>
  import VALIDATION_RULE from '@/lib/definition/validationRule'

  export default {
    props: [`isProgress`],
    data() {
      return {
        address: '',
        addressRules: VALIDATION_RULE.NOTIFICATION.DESTINATION.ADDRESS
      }
    },
    updated() {
      this.$emit('input', {
        address: this.address
      })
    }
  }
</script>