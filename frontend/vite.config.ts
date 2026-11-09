/// <reference types="vitest" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";
import { VitePWA } from "vite-plugin-pwa";

declare const process: { env: Record<string, string | undefined> };

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      // "prompt": a new version never reloads the page mid-entry; the UpdateToast asks first (Doc2 section 12)
      registerType: "prompt",
      includeAssets: ["favicon.svg", "icons/*.png"],
      manifest: {
        id: "/",
        name: "Nool",
        short_name: "Nool",
        description: "Every order, on thread.",
        display: "standalone",
        start_url: "/",
        scope: "/",
        lang: "en",
        orientation: "portrait",
        theme_color: "#14181F",
        background_color: "#FAFAF7",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "/icons/maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // App shell + fonts + supervisor routes (they are all the same SPA shell) are precached.
        globPatterns: ["**/*.{js,css,html,svg,png,woff2,woff}"],
        navigateFallback: "/index.html",
        navigateFallbackDenylist: [/^\/api\//],
        runtimeCaching: [
          {
            // The supervisor's order list works offline from the last good copy.
            urlPattern: ({ url }) => url.pathname === "/api/sup/orders",
            handler: "StaleWhileRevalidate",
            options: { cacheName: "nool-sup-orders", expiration: { maxEntries: 4, maxAgeSeconds: 7 * 86400 } },
          },
          // Every other /api call (mutations, buyer and merchandiser data) is never cached.
          { urlPattern: ({ url }) => url.pathname.startsWith("/api/"), handler: "NetworkOnly" },
        ],
      },
    }),
  ],
  server: { proxy: { "/api": { target: process.env.VITE_BACKEND_URL || "http://localhost:8001", changeOrigin: true } } },
  preview: { proxy: { "/api": { target: process.env.VITE_BACKEND_URL || "http://localhost:8001", changeOrigin: true } } },
  build: {
    target: "es2020",
    minify: "terser", // ~3% smaller than esbuild: the supervisor route has a hard 100 KB gzip budget (NFR-1)
    terserOptions: {
      compress: {
        passes: 3,
        pure_getters: true,
      },
      format: {
        comments: false,
      },
    },
    sourcemap: false,
    rollupOptions: {
      output: {
        // Named vendor chunks: better long-term caching, and it shows where the floor bundle's weight is.
        manualChunks(id: string) {
          if (id.includes("node_modules/react-dom") || id.includes("node_modules/scheduler")) return "vendor-react-dom";
          if (id.includes("node_modules/react-router") || id.includes("node_modules/@remix-run")) return "vendor-router";
          if (id.includes("node_modules/dexie")) return "vendor-dexie";
          if (id.includes("node_modules/react/")) return "vendor-react";
          return undefined;
        },
      },
    },
  },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
});
