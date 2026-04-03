import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
const base = process.env.BASE_URL || '/'

export default defineConfig({
  base,
  plugins: [vue()],
})
