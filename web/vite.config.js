import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    base: '/srujan/', // Base URL for GitHub Pages
    build: {
        outDir: '../docs',
        emptyOutDir: false, // Don't delete existing files in docs (like images/legacy)
    },
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    }
})
