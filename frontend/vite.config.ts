import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "EburSeal",
        short_name: "EburSeal",
        description: "Le sceau invisible des diplômes ivoiriens",
        lang: "fr",
        theme_color: "#14325C",
        background_color: "#ffffff",
        display: "standalone",
        icons: [
          { src: "icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icon-512.png", sizes: "512x512", type: "image/png" },
        ],
      },
      workbox: {
        // SR-CON-06 : seul le « shell » statique est mis en cache.
        globPatterns: ["**/*.{js,css,html,png,svg,ico}"],
        navigateFallbackDenylist: [/^\/api\//],
        runtimeCaching: [
          { urlPattern: ({ url }) => url.pathname.startsWith("/api/"), handler: "NetworkOnly" },
        ],
      },
    }),
  ],
  server: {
    // En développement, l'API WildFly est relayée (même origine → pas de CORS permissif)
    proxy: { "/api": { target: "https://localhost:8443", secure: false } },
  },
  build: { sourcemap: false },
});
