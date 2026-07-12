import { defineConfig } from "vite";
import uni from "@dcloudio/vite-plugin-uni";

const previewPort = Number(process.env.PORT);

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [uni()],
  server: {
    ...(Number.isInteger(previewPort) && previewPort > 0 ? { port: previewPort } : {}),
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
