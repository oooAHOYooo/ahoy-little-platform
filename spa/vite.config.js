import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const envApiBase = (env.VITE_API_BASE || '').trim()
  const envProxyTarget = (env.VITE_API_PROXY_TARGET || '').trim()
  const proxyTarget = envProxyTarget || (envApiBase ? envApiBase : '') || 'http://localhost:5002'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    // Build output goes to ../spa-dist so Capacitor can point webDir at it
    build: {
      outDir: '../spa-dist',
      emptyOutDir: true,
    },
    server: {
      // Proxy API calls to the Flask backend during development
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
        '/payments': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
