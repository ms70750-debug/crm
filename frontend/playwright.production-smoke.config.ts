import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./smoke",
  timeout: 90_000,
  expect: { timeout: 12_000 },
  use: {
    ...devices["Desktop Chrome"],
    baseURL: process.env.PRODUCTION_FRONTEND_URL ?? "https://crm-sepia-beta.vercel.app",
    channel: "chrome",
    trace: "retain-on-failure",
  },
});
