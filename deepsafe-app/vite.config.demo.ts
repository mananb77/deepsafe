import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

/**
 * Vite configuration for standalone demo build
 *
 * Usage:
 *   npm run build:demo   - Build standalone demo
 *   npm run preview:demo - Preview built demo
 */
export default defineConfig({
  plugins: [react()],

  // Build configuration
  build: {
    outDir: 'dist-demo',
    emptyOutDir: true,

    // Entry point for standalone build
    rollupOptions: {
      input: {
        demo: resolve(__dirname, 'demo.html'),
      },
      output: {
        // Optimize chunk names for the demo
        entryFileNames: 'assets/demo-[hash].js',
        chunkFileNames: 'assets/demo-chunk-[hash].js',
        assetFileNames: 'assets/demo-[hash].[ext]',
      },
    },

    // Increase chunk size limit for demo (it's self-contained)
    chunkSizeWarningLimit: 1000,

    // Minification settings - use esbuild (Vite's default)
    minify: 'esbuild',
  },

  // Base URL - can be customized for deployment
  base: './',

  // Development server for standalone preview
  server: {
    port: 5174, // Different port than main app
    open: '/demo.html',
  },

  // Preview server settings
  preview: {
    port: 4174,
  },
});
