import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // Build output goes to ../spa-dist so Capacitor can point webDir at it
  build: {
    outDir: '../spa-dist',
    emptyOutDir: true,
  },
  server: {
    // Proxy API calls to the Flask backend during development
    proxy: {
      '/api': {
        target: 'https://app.ahoy.ooo',
        changeOrigin: true,
      },
    },
  },
})
