const path = require('path')

module.exports = {
    outputDir: 'dist',
    assetsDir: 'static',
    lintOnSave: true,
    configureWebpack: {
        resolve: {
          alias: {
            '@': path.join(__dirname, '/frontend') // @の参照先の変更
          }
        }
    },
    pages: {
        index: {
            entry: 'frontend/main.js', // エントリーポイント
            template: 'public/index.html', // index.htmlテンプレート
            filename: 'index.html'
        }
    }
}