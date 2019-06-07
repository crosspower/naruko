<script>
import { Line, mixins } from 'vue-chartjs'

export default {
  extends: Line,
  mixins: [mixins.reactiveProp],
  props: ['options','chartData'],
  watch: {
    options: {
      handler() {
        this.$data._chart.destroy()
        this.renderChart(this.chartData, this.options)
      },
      deep: true
    }
  },
  mounted() {
    this.renderChart(this.chartData, this.options)
  }
}
</script>