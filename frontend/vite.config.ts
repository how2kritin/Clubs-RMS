import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:80/",
        changeOrigin: true,
        secure: false,
      },
      "/habits": {
        target: "http://localhost:1238/",
        changeOrigin: true,
        secure: false,
      },
      "/recommendations": {
        target: "http://localhost:1238/",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [react(), tailwindcss()],
});
