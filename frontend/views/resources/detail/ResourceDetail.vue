<template>
    <TemplateBase :title="title" :breadcrumbs="breadcrumbs" ref="base">
        <v-flex slot="body" xs12>
            <v-card class="mb-3">
                <v-card-title class="pb-0">
                    <v-icon class="pr-2">mdi-information</v-icon>
                    <v-progress-circular
                            :width="2"
                            :size="20"
                            color="blue"
                            v-if="info.isProgress"
                            indeterminate
                    ></v-progress-circular>
                    <div class="subheading" v-else>
                        {{ resource.name }}
                    </div>
                    <v-spacer></v-spacer>
                    <v-tooltip top>
                        <v-menu offset-y v-if="info.actions.length"
                                slot="activator"
                                :disabled="info.isProgress">
                            <v-btn icon slot="activator"
                                   :disabled="info.isProgress">
                                <v-icon>mdi-dots-vertical</v-icon>
                            </v-btn>

                            <v-list>
                                <v-list-tile
                                        v-for="(item, i) in info.actions"
                                        :key="i"
                                        @click="openActionModal(item.id)"
                                >
                                    <v-list-tile-title>{{ item.name }}</v-list-tile-title>
                                </v-list-tile>
                            </v-list>
                        </v-menu>
                        <span>アクション</span>
                    </v-tooltip>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               :loading="info.isProgress"
                               :disabled="info.isProgress"
                               @click="initInfo">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>

                </v-card-title>
                <v-card flat>
                    <v-card-text class="pt-0">
                        <v-layout justify-start wrap>
                            <template v-for="(item, i) in info.items">
                                <v-flex xs3 sm3 md3 lg2 xl1 class="text-xs-right" :key="`key-${i}`">
                                    {{ item.name }}:
                                </v-flex>
                                <v-flex xs8 sm9 md9 lg10 xl11 class="pl-2" :key="`value-${i}`">
                                    <template v-if="item.id==='state'">
                                        <v-icon size="15" :color="getResourceStateColor()">mdi-circle</v-icon>
                                        {{ item.value }}
                                    </template>
                                    <template v-else>
                                        {{ item.value }}
                                    </template>
                                    <v-progress-circular
                                            :width="2"
                                            :size="15"
                                            color="blue"
                                            v-if="info.isProgress"
                                            indeterminate
                                    ></v-progress-circular>
                                </v-flex>
                            </template>
                        </v-layout>
                    </v-card-text>
                </v-card>
            </v-card>
            <v-card>
                <v-tabs v-model="tab.active">
                    <v-tabs-slider></v-tabs-slider>
                    <v-tab
                            v-for="(item, i) in tab.items"
                            :key="i"
                            :to="item.to"
                    >
                        <v-icon class="pr-2">{{ item.icon }}</v-icon>
                        {{ item.name }}
                    </v-tab>
                </v-tabs>
                <v-divider></v-divider>
                <transition name="fade-transition">
                    <router-view></router-view>
                </transition>
            </v-card>
        </v-flex>
        <Ec2StartModal slot="body" ref="ec2StartModal"/>
        <Ec2StopModal slot="body" ref="ec2StopModal"/>
        <Ec2RebootModal slot="body" ref="ec2RebootModal"/>
        <CreateEc2BackupModal slot="body" ref="createEc2BackupModal"/>
        <CreateRdsBackupModal slot="body" ref="createRdsBackupModal"/>
    </TemplateBase>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import TemplateBase from '@/components/TemplateBase'
  import Ec2StartModal from '@/views/resources/detail/modal/Ec2StartModal'
  import Ec2StopModal from '@/views/resources/detail/modal/Ec2StopModal'
  import Ec2RebootModal from '@/views/resources/detail/modal/Ec2RebootModal'
  import CreateEc2BackupModal from '@/views/resources/detail/modal/CreateEc2BackupModal'
  import CreateRdsBackupModal from '@/views/resources/detail/modal/CreateRdsBackupModal'
  import RESOURCES from '@/lib/definition/resources'

  export default {
    components: {
      TemplateBase,
      Ec2StartModal,
      Ec2StopModal,
      Ec2RebootModal,
      CreateEc2BackupModal,
      CreateRdsBackupModal
    },
    data() {
      return {
        isProgress: false,
        title: {icon: 'mdi-information', text: `リソース管理`},
        breadcrumbs: [
          {text: 'ダッシュボード', disabled: false, to: '/dashboard'},
          {text: 'リソース一覧', disabled: false, to: '/resources', exact: true},
          {text: 'リソース管理', disabled: true, to: ''}
        ],
        tab: {
          items: [
            {
              name: 'モニタリング',
              icon: 'mdi-chart-line',
              to: {path: '/resources/monitoring', query: this.$route.query}
            },
            {name: 'スケジュール', icon: 'mdi-calendar', to: {path: '/resources/schedule', query: this.$route.query}},
            {
              name: 'バックアップ',
              icon: 'mdi-file-restore',
              to: {path: '/resources/backup', query: this.$route.query}
            }],
          active: 0
        },
        actions: [],
        info: {
          isProgress: false,
          actions: [],
          items: []
        }
      }
    },
    computed: {
      ...mapGetters({
        metrics: 'resourceDetail/metrics',
        resource: 'resourceDetail/resource'
      })
    },
    methods: {
      ...mapActions('resourceDetail', ['fetchResource', 'fetchMonitors']),
      ...mapActions('alert', ['pushErrorAlert']),
      initInfo() {
        if (!this.$route.query.service) {
          this.pushErrorAlert('リソースの情報の取得に失敗しました。')
          return
        }
        this.info.isProgress = true
        this.info.actions = RESOURCES[this.$route.query.service.toUpperCase()].actions.getEnums()
        // 描画のため空の値を入れておく
        this.info.items = []
        RESOURCES[this.$route.query.service.toUpperCase()].infoKeys.forEach((key) => {
          this.info.items.push({name: key.name, value: ''})
        })
        // 詳細情報の取得
        this.fetchResource([this.$route.query.awsAccount, this.$route.query.region, this.$route.query.service, this.$route.query.resourceId]).then(() => {
          this.info.items = []
          RESOURCES[this.resource.service].infoKeys.forEach((key) => {
            this.info.items.push({id: key.id, name: key.name, value: this.resource[key.id]})
          })
        }).finally(() => {
          this.info.isProgress = false
        })
      },
      openActionModal(action) {
        const service = this.$route.query.service.toUpperCase()
        let modal = null
        if (service === 'EC2') {
          if (action === RESOURCES.EC2.actions.start.id) {
            modal = this.$refs.ec2StartModal
          } else if (action === RESOURCES.EC2.actions.stop.id) {
            modal = this.$refs.ec2StopModal
          } else if (action === RESOURCES.EC2.actions.reboot.id) {
            modal = this.$refs.ec2RebootModal
          } else if (action === RESOURCES.EC2.actions.backup.id) {
            modal = this.$refs.createEc2BackupModal
          }
        } else if (service === 'RDS') {
          if (action === RESOURCES.EC2.actions.backup.id) {
            modal = this.$refs.createRdsBackupModal
          }
        }
        if (modal !== null) {
          modal.open().then((res) => {
            if (res) {
              this.initInfo()
            }
          })
        }
      },
      getResourceStateColor() {
        return RESOURCES[this.resource.service].state[this.resource.state].color
      }
    },
    mounted() {
      this.tab.items = [
        {
          name: 'モニタリング',
          icon: 'mdi-chart-line',
          to: {path: '/resources/monitoring', query: this.$route.query}
        }]
      if (this.$route.query.service === 'ec2'
          || this.$route.query.service === 'rds') {
        this.tab.items.push({
          name: 'バックアップ',
          icon: 'mdi-file-restore',
          to: {path: '/resources/backup', query: this.$route.query}
        })
        this.tab.items.push({
          name: 'スケジュール',
          icon: 'mdi-calendar',
          to: {path: '/resources/schedule', query: this.$route.query}
        })
      }

      this.initInfo()
    }
  }
</script>
<style scoped>
    .tab-height-auto /deep/ .v-window__container.v-window__container--is-active {
        height: auto !important;
    }
</style>