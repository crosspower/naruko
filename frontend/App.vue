<template>
    <v-app>
        <v-navigation-drawer v-if="isLoggedIn" v-model="drawer" clipped app class="primary darken-1" width="250">
            <v-layout justify-center row hidden-lg-and-up>
                <v-flex xs12>
                    <v-img
                            :src="require('@/assets/naruko_logo_dark.png')"
                            contain
                            height="40"
                            width="150"
                            max-width="150"
                            class="ml-5 mt-3 mb-3"
                    ></v-img>
                </v-flex>
            </v-layout>
            <v-list dense dark>
                <template v-for="(item, i) in menuItems">
                    <v-divider v-if="item.divider" :key="i"></v-divider>
                    <v-list-tile v-else :key="i" :to="item.to" active-class="primary">
                        <v-list-tile-action>
                            <v-icon>{{ item.icon }}</v-icon>
                        </v-list-tile-action>
                        <v-list-tile-content>
                            <v-list-tile-title>
                                {{ item.text }}
                            </v-list-tile-title>
                        </v-list-tile-content>
                    </v-list-tile>
                </template>
            </v-list>
        </v-navigation-drawer>

        <v-toolbar app v-if="isLoggedIn" clipped-left>
            <v-toolbar-side-icon v-if="isLoggedIn" @click="drawer = !drawer"></v-toolbar-side-icon>
            <v-img
                    :src="require('@/assets/naruko_logo.png')"
                    contain
                    height="40"
                    width="125"
                    max-width="125"
                    class="ml-3"
            ></v-img>
            <v-spacer></v-spacer>
            <span class="pr-4 subheading">
                <v-icon>
                    mdi-account
                </v-icon>
                {{ userData.name }} ({{ userData.email }})
            </span>
            <v-btn v-if="isLoggedIn" icon @click="submitLogout">
                <v-icon>mdi-exit-to-app</v-icon>
            </v-btn>
        </v-toolbar>

        <v-content>
            <router-view>
            </router-view>
        </v-content>

        <v-dialog v-model="isTokenExpired" persistent width="500">
            <v-card>
                <v-card-title primary-title>
                    <v-icon class="pr-2">mdi-information</v-icon>
                    もう一度ログインしてください
                </v-card-title>
                <v-card-text>
                    トークンの有効期限が切れました。
                    もう一度ログインしてください。
                </v-card-text>
                <v-divider></v-divider>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat @click="submitLogout">
                        ログインページに戻る
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-app>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import MENU from '@/lib/definition/mainMenu'

  export default {
    name: 'App',
    data() {
      return {
        drawer: true
      }
    },
    methods: {
      ...mapActions('user', ['logout', 'confirmTokenExpired']),
      submitLogout() {
        this.logout().then(() => {
          this.$router.push('/')
        })
      }
    },
    computed: {
      ...mapGetters({
        isLoggedIn: 'user/isLoggedIn',
        userData: 'user/userData',
        isTokenExpired: 'user/isTokenExpired'
      }),
      menuItems() {
        // メニューをロールでフィルタする
        const items = []
        MENU.forEach((menu) => {
          if (menu.role.indexOf(this.userData.role.id) > -1) {
            items.push(menu)
          }
        })
        return items
      }
    }
  }
</script>
