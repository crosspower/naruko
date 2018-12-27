<script>
  import Chart from 'chart.js'
  import {generateChart, mixins} from 'vue-chartjs'

  Chart.defaults.LineWithLine = Chart.defaults.line
  Chart.controllers.LineWithLine = Chart.controllers.line.extend({
    draw: function (ease) {

      const data = this.chart.config.data

      if (data.yHighlightRanges !== undefined) {
        for (let k of Object.keys(data.yHighlightRanges)) {
          const ctx = this.chart.ctx
          const yRangeBegin = data.yHighlightRanges[k].begin
          const yRangeEnd = data.yHighlightRanges[k].end

          const xaxis = this.chart.scales['x-axis-0']
          const yaxis = this.chart.scales['y-axis-0']
          const yRangeBeginPixel = yaxis.getPixelForValue(yRangeBegin)
          const yRangeEndPixel = yaxis.getPixelForValue(yRangeEnd)

          ctx.save()
          // The fill style of the rectangle we are about to fill.
          ctx.fillStyle = data.yHighlightRanges[k].color
          // Fill the rectangle that represents the highlight region. The parameters are the closest-to-starting-point pixel's x-coordinate,
          // the closest-to-starting-point pixel's y-coordinate, the width of the rectangle in pixels, and the height of the rectangle in pixels, respectively.
          ctx.fillRect(xaxis.left, Math.min(yRangeBeginPixel, yRangeEndPixel), xaxis.right - xaxis.left, Math.max(yRangeBeginPixel, yRangeEndPixel) - Math.min(yRangeBeginPixel, yRangeEndPixel))
          ctx.restore()
        }
      }
      Chart.controllers.line.prototype.draw.call(this, ease)
    }
  })
  const CustomLine = generateChart('custom-line', 'LineWithLine')

  export default {
    extends: CustomLine,
    mixins: [mixins.reactiveProp],
    props: ['options'],
    mounted() {
      this.renderChart(this.chartData, this.options)
    }
  }

</script>

