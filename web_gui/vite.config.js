import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Standard Vite + React config. The server host is passed via the CLI
// (--host 0.0.0.0) in docker-compose.yml so the dev server is reachable
// from the host browser.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Allows hot-reload to work reliably when the project is mounted from
    // the host into the container.
    watch: {
      usePolling: true,
    },
  },
});
