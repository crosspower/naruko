<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="400">
            <v-card>
                <v-card-title class="headline">インスタンスの起動</v-card-title>
                <v-card-text>
                    {{ body }}
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat
                           @click="cancel"
                           :disabled="isProgress">キャンセル
                    </v-btn>
                    <v-btn color="blue darken-1" flat
                           @click="confirm"
                           :loading="isProgress"
                           :disabled="isProgress">起動
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
  import {mapActions, mapGetters} from 'vuex'

  export default {
    data() {
      return {
        isOpen: false,
        isProgress: false,
        body: '',
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
      ...mapActions('resourceDetail', ['startEc2Instance']),
      open() {
        // モーダルを開く
        this.isProgress = false
        this.body = `${this.resource.name}を起動します。`
        this.isOpen = true
        return new Promise((resolve, reject) => {
          this.resolve = resolve
          this.reject = reject
        })
      },
      confirm() {
        this.isProgress = true
        this.startEc2Instance().then(() => {
          this.resolve(true)
        }).catch(() => {
          this.reject()
        }).finally(() => {
          this.isProgress = false
          this.isOpen = false
        })
      },
      cancel() {
        this.isProgress = false
        this.isOpen = false
        this.resolve(false)
      }
    }
  }
</script>