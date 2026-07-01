import { expect, test } from "@playwright/test";

test("protege dashboard, autentica e faz logout", async ({ page }) => {
  await page.context().clearCookies();
  await page.goto("/login");
  await page.evaluate(() => localStorage.clear());
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);

  await page.getByRole("button", { name: /entrar/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText("Admin Demo - Administrador")).toBeVisible();

  await page.getByRole("button", { name: /sair/i }).click();
  await expect(page).toHaveURL(/\/login$/);

  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);
});
