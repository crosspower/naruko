<template>
    <v-layout>
        <v-flex xs12 class="fixed-center">
            <v-alert
                    :value="alert.value"
                    :type="alert.type"
                    :icon="alert.icon"
                    dismissible
                    transition="slide-x-reverse-transition"
                    v-for="alert in alerts" :key="alert.key"
                    class="elevation-5"
            >
                {{ alert.msg }}
            </v-alert>
        </v-flex>
    </v-layout>
</template>

<script>
  import {mapGetters} from 'vuex'

  export default {
    data() {
      return {}
    },
    computed: {
      ...mapGetters({alerts: 'alert/alerts'})
    }
  }
</script>

<style scoped>
    .fixed-center {
        position: fixed;
        left: 50%;
        width: 600px;
        transform: translate(-50%, -15px);
        z-index: 1;
    }
</style>
