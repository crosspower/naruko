<template>
    <v-layout>
        <v-flex xs12>
            <v-card flat>
                <v-card-title class=" pb-0">
                    <div class="subheading">バックアップ一覧</div>
                </v-card-title>
                <v-card-title>
                    <v-text-field
                            v-model="dataTables.search"
                            class="pt-0"
                            append-icon="mdi-magnify"
                            label="Search"
                            single-line
                            hide-details
                            clearable
                    ></v-text-field>
                    <v-spacer></v-spacer>
                    <v-tooltip top>
                        <v-btn icon flat
                               slot="activator"
                               @click="initDataTables"
                               :loading="isProgress"
                               :disabled="isProgress">
                            <v-icon>
                                mdi-refresh
                            </v-icon>
                        </v-btn>
                        <span>更新</span>
                    </v-tooltip>
                </v-card-title>
                <v-data-table
                        :headers="dataTables.headers"
                        :items="backups"
                        :search="dataTables.search"
                        :pagination.sync="dataTables.pagination"
                        :loading="isProgress"
                        item-key="name"
                >
                    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                    <template slot="items" slot-scope="props">
                        <tr>
                            <td>{{ props.item.id }}</td>
                            <td class="text-xs-left">{{ props.item.name || props.item.id}}</td>
                            <td class="text-xs-left">{{ props.item.state }}</td>
                            <td class="text-xs-left">{{ props.item.created_at }}</td>
                        </tr>
                    </template>
                </v-data-table>
            </v-card>
        </v-flex>
    </v-layout>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'

  export default {
    data() {
      return {
        isProgress: false,
        dataTables: {
          search: '',
          pagination: {
            sortBy: '作成日時'
          },
          headers: [
            {text: 'ID', align: 'left', value: 'id'},
            {text: '名前', align: 'left', value: 'name'},
            {text: 'ステータス', align: 'left', value: 'name'},
            {text: '作成日時', align: 'left', value: 'created_at'}
          ]
        }
      }
    },
    computed: {
      ...mapGetters({
        backups: 'resourceDetail/backups'
      })
    },
    methods: {
      ...mapActions('resourceDetail', ['fetchBackups']),
      initDataTables() {
        this.isProgress = true
        this.fetchBackups([
          this.$route.query.awsAccount,
          this.$route.query.region,
          this.$route.query.service,
          this.$route.query.resourceId]).then(() => {

        }).finally(() => {
          this.isProgress = false
        })
      }
    },
    mounted() {
      this.initDataTables()
    }
  }
</script>