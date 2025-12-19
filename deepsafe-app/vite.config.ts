import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Base path for GitHub Pages deployment
  // Update 'deepsafe-app' to match your repository name
  base: process.env.GITHUB_ACTIONS ? '/deepsafe-app/' : '/',
})
