import { expect, test } from "@playwright/test";

test("ativa primeiro administrador por link privado", async ({ page }) => {
  const activationLink = process.env.ADMIN_ACTIVATION_LINK;
  test.skip(!activationLink, "ADMIN_ACTIVATION_LINK ausente");

  await page.context().clearCookies();
  await page.goto(activationLink as string);
  await expect(page).toHaveURL(/\/ativar-admin$/);
  await expect(page.getByLabel("Nova senha")).toBeVisible();
  await page.getByLabel("Nova senha").fill("SenhaForte!2026");
  await page.getByLabel("Confirmar senha").fill("SenhaForte!2026");
  await page.getByRole("button", { name: /ativar acesso/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText(/Administrador/)).toBeVisible();
});
