import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
  },
  server: {
    proxy: {
      '/notes': 'http://localhost:8000',
      '/action-items': 'http://localhost:8000',
      '/tags': 'http://localhost:8000',
    },
  },
})
