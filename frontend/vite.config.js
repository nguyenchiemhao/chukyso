import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    proxy: {
      // Use 127.0.0.1 to avoid localhost/IPv6 resolution mismatch that can cause 502.
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
