import { defineConfig } from "@playwright/test";

// Starts the real API (needs a seeded dev database via DATABASE_URL) and the built SPA preview.
// The preview proxies /api to the API (see vite.config.ts "preview.proxy").
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  use: { baseURL: "http://localhost:4173", trace: "retain-on-failure" },
  webServer: [
    { command: "cd .. && python -m uvicorn backend.app.main:app --port 8000", port: 8000, reuseExistingServer: true,
      env: { DEMO_TODAY: "2026-11-03", AI_MODE: "mock", ENV: "dev" } },
    { command: "npm run build && npm run preview", port: 4173, reuseExistingServer: true },
  ],
});
