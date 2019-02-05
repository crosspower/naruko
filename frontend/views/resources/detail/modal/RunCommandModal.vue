<template>
    <v-layout row justify-center>
        <v-dialog v-model="isOpen" persistent max-width="700">
            <v-card>
                <v-card-title class="headline">コマンド実行</v-card-title>

                <v-stepper v-model="step">
                    <v-stepper-header class="elevation-0">
                        <v-stepper-step step="1">
                            ドキュメント選択
                        </v-stepper-step>
                        <v-divider></v-divider>
                        <v-stepper-step step="2">
                            パラメータ入力
                        </v-stepper-step>
                    </v-stepper-header>
                    <v-stepper-items>
                        <v-stepper-content step="1">
                            <v-text-field
                                    v-model="dataTable.search"
                                    append-icon="mdi-magnify"
                                    label="Search"
                                    single-line
                                    hide-details
                                    clearable
                            ></v-text-field>
                            <v-data-table
                                :headers="dataTable.headers"
                                :items="documents"
                                :search="dataTable.search"
                                :loading="isProgress"
                                :pagination.sync="dataTable.pagination">
                                <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
                                <template slot="items" slot-scope="props">
                                    <tr @click="onSelectDocument(props.item)">
                                        <td width="1%">
                                            <v-radio-group hide-details
                                                           v-model="dataTable.selectedDocument"
                                                           name="rowSelector">
                                                <v-radio :value="props.item" :key="props.item.name"></v-radio>
                                            </v-radio-group>
                                        </td>
                                        <td>{{ props.item.name }}</td>
                                    </tr>
                                </template>
                            </v-data-table>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn flat @click="cancel">キャンセル</v-btn>
                                <v-btn color="primary" @click="next(step)">次へ</v-btn>
                            </v-card-actions>
                        </v-stepper-content>
                        <v-stepper-content step="2">
                            <v-card>
                                <v-card-title>
                                    <span class="headline">{{ this.document.name }}</span>
                                </v-card-title>
                                <v-subheader>使用するドキュメントのパラメータを入力してください。</v-subheader>
                                <v-form ref="runCommandForm" v-model="valid">
                                    <div v-for="param in document.parameters" :key="param.key">
                                        <v-text-field
                                                type="text"
                                                :label="param.key"
                                                :loading="isProgress"
                                                :disabled="isProgress"
                                                v-model="form[param.key]"
                                        ></v-text-field>
                                        {{ param.description }}
                                    </div>
                                </v-form>
                                <v-card
                                        v-if="ranCommand"
                                            dark
                                            color="primary"
                                >
                                    <v-card-title>
                                        <span class="headline">実行結果</span>
                                    </v-card-title>
                                    <v-card-text style="white-space:pre-line; word-wrap:break-word;">
                                        {{ command.out_put }}
                                    </v-card-text>
                                </v-card>
                                <v-card-actions>
                                    <v-spacer></v-spacer>
                                    <v-btn flat @click="cancel"
                                           :disabled="isProgress"
                                           :loading="isProgress">キャンセル</v-btn>
                                    <v-btn flat @click="step = 1"
                                           :disabled="isProgress"
                                           :loading="isProgress">戻る</v-btn>
                                    <v-btn color="primary"
                                           :disabled="isProgress"
                                           :loading="isProgress"
                                           @click="execute">実行</v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-stepper-content>
                    </v-stepper-items>
                </v-stepper>
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
          step: 1,
          valid: true,
          resolve: null,
          reject: null,
          form: {},
          ranCommand: false,
          dataTable: {
            isProgress: false,
            selectedDocument: null,
            search: '',
            headers: [
              {text: '', value: 'name', filter: 'name', sortable: false, align: 'center'},
              {text: 'ドキュメント名', value: 'name', filter: 'name', align: 'left'}
            ]
          }
        }
      },
      computed: {
        ...mapGetters({
          documents: 'resourceDetail/documents',
          document: 'resourceDetail/document',
          resource: 'resourceDetail/resource',
          command: 'resourceDetail/command'
        })
      },
      methods: {
        ...mapActions('resourceDetail', ['fetchDocuments', 'fetchDocument', "runCommand"]),
        initDataTable() {
          this.isProgress = true
          this.fetchDocuments([
            this.$route.query.awsAccount,
            this.$route.query.region]).then(() => {
            if (this.documents.length > 0) {
              if (!this.dataTable.selectedDocument) {
                this.dataTable.selectedDocument = this.documents[0]
              }
            }
          }).finally(() => {
            this.isProgress = false
          })
        },
        open() {
          // モーダルを開く
          this.$refs.runCommandForm.reset()
          this.isProgress = false
          this.step = 1
          this.isOpen = true
          this.ranCommand = false
          this.initDataTable()
          return new Promise((resolve, reject) => {
            this.resolve = resolve
            this.reject = reject
          })
        },
        execute() {
          this.isProgress = true
          let parameters = []
          for (const param of this.document.parameters) {
            parameters.push({
              key: param.key,
              value: this.form[param.key]
            })
          }
          const data = {
            name: this.document.name,
            parameters: parameters
          }
          this.runCommand(data).then(() => {
            this.ranCommand = true
          }).catch(() => {
            this.ranCommand = true
          }).finally(() => {
            this.isProgress = false
          })
        },
        confirm() {
          this.isProgress = true
          this.resolve(true)
          this.isProgress = false
          this.isOpen = false
        },
        next(currentStep) {
          if (currentStep === 1 ) {
            this.step = currentStep + 1
            this.getDocumentDetail(this.dataTable.selectedDocument.name)
          }
        },
        cancel() {
          this.isProgress = false
          this.isOpen = false
          this.resolve(false)
          this.$refs.runCommandForm.reset()
          // this.$refs.formStep1.reset()
        },
        getDocumentDetail(documentName) {
          this.isProgress = true
          this.fetchDocument([
            this.$route.query.awsAccount,
            this.$route.query.region,
            documentName]).then(() => {
          }).finally(() => {
            this.isProgress = false
          })
        },
        onSelectDocument(document) {
          if (this.dataTable.selectedDocument === document) {
            return
          }
          this.dataTable.selectedDocument = document
          this.ranCommand = false
        }
      }
    }
</script>