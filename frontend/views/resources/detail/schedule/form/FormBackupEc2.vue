<template>
    <v-form>
        <v-checkbox
                label="再起動しない"
                v-model="noReboot"
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
</template>
<script>
  export default {
    data() {
      return {
        noReboot: false
      }
    }
  }
</script>