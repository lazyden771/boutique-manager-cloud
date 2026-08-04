import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Makes the web build installable straight to a phone/desktop home
    // screen (Add to Home Screen / Install App) with no app store needed -
    // the fastest path to "on my friend's device" while store submissions
    // are in progress separately.
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Boutique Manager',
        short_name: 'Boutique',
        description: 'Inventory and sales manager for boutiques',
        theme_color: '#3880ff',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    }),
  ],
})
