import { expect, test } from "@playwright/test";

const backendUrl = process.env.PRODUCTION_BACKEND_URL ?? "https://crm-2340.onrender.com";
const allowedMethods = new Set(["GET", "HEAD"]);

test.beforeEach(async ({ page }) => {
  await page.route("**/*", async (route) => {
    const method = route.request().method().toUpperCase();
    if (!allowedMethods.has(method)) {
      throw new Error(`Smoke de producao bloqueou metodo de escrita: ${method}`);
    }
    await route.continue();
  });
});

test("frontend publico carrega login sem escrita", async ({ page }) => {
  const response = await page.goto("/login", { waitUntil: "domcontentloaded" });
  expect(response?.ok()).toBe(true);
  await expect(page.getByRole("heading", { name: /entrar no crm/i })).toBeVisible();
});

test("backend publico responde healthz sem escrita", async ({ request }) => {
  const response = await request.get(`${backendUrl}/healthz`);
  expect(response.ok()).toBe(true);
  const health = await response.json();
  expect(health.status).toBe("ok");
  expect(health.database).toBe("ok");
  expect(health.environment).toBe("production");
  expect(health.auth_email.enabled).toBe(false);
  expect(health.auth_email.mode).toBe("simulate");
});
