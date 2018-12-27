<template>
    <v-container>
        <v-layout row wrap>
            <v-flex xs12>
                <Alert ref="alert"/>
            </v-flex>
            <v-flex xs12 class="pb-4">
                <v-breadcrumbs :items="breadcrumbs">
                    <v-icon slot="divider">mdi-chevron-right</v-icon>
                </v-breadcrumbs>

                <div class="headline">
                    <v-icon size="30" class="mr-2">{{ title.icon }}</v-icon>
                    {{ title.text }}
                </div>
            </v-flex>
            <slot name="body"></slot>
        </v-layout>
    </v-container>
</template>

<script>
  import Alert from '@/components/Alert'

  export default {
    components: {
      Alert
    },
    props: {
      title: {
        icon: '',
        text: ''
      },
      breadcrumbs: {}
    },
    methods: {
      pushAlert(type, icon, msg) {
        this.$refs.alert.pushAlert(type, icon, msg)
      }
    }
  }
</script>