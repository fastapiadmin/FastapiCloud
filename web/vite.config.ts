import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  build: {
    chunkSizeWarningLimit: 1000, // 调整警告限制到1000kB
    outDir: path.resolve(__dirname, '../static/'), // 指定构建输出目录
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('vue-router')) {
              return 'vue'
            } else if (id.includes('element-plus')) {
              return 'elementPlus'
            } else if (id.includes('axios')) {
              return 'axios'
            }
          }
        }
      }
    }
  }
})
