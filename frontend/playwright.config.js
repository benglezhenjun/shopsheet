import { defineConfig, devices } from "@playwright/test";

const backendPort = process.env.SHOPSHEET_E2E_BACKEND_PORT ?? "8011";
const frontendPort = process.env.SHOPSHEET_E2E_FRONTEND_PORT ?? "5179";
const backendUrl = `http://127.0.0.1:${backendPort}`;
const frontendUrl = `http://127.0.0.1:${frontendPort}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: {
    timeout: 5_000
  },
  use: {
    baseURL: frontendUrl,
    trace: "on-first-retry"
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ],
  webServer: [
    {
      command: `python -m uvicorn shopsheet.api:app --host 127.0.0.1 --port ${backendPort}`,
      cwd: "..",
      env: {
        PYTHONPATH: "src"
      },
      url: `${backendUrl}/health`,
      reuseExistingServer: false,
      timeout: 30_000
    },
    {
      command: `npm run dev -- --port ${frontendPort} --strictPort`,
      env: {
        VITE_API_PROXY: backendUrl
      },
      url: frontendUrl,
      reuseExistingServer: false,
      timeout: 30_000
    }
  ]
});
