import { expect, test } from "@playwright/test";

test("login, cliente, opt-in e WhatsApp simulado", async ({ page }) => {
  const suffix = Date.now().toString().slice(-9);
  const name = `Cliente E2E ${suffix}`;

  await page.goto("/login");
  await page.getByRole("button", { name: /entrar/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.goto("/clientes");
  await page.getByPlaceholder("Nome").fill(name);
  await page.getByPlaceholder("CPF").fill(`37${suffix}`);
  await page.getByPlaceholder("Telefone").fill(`1197${suffix}`);
  await page.getByPlaceholder("E-mail").fill(`e2e${suffix}@demo.local`);
  await page.getByRole("button", { name: "Criar cliente" }).click();
  await expect(page.getByText("Cliente ficticio cadastrado.")).toBeVisible();
  await expect(page.getByText(name)).toBeVisible();
  await page.locator("tr", { hasText: name }).getByRole("button", { name: "Opt-in WhatsApp" }).click();
  await expect(page.getByText(`Opt-in de WhatsApp registrado para ${name}.`)).toBeVisible();

  await page.goto("/whatsapp");
  await page.locator("select").first().selectOption("cliente");
  const recipient = page.locator("select").nth(1);
  await expect(recipient.locator("option", { hasText: name })).toHaveCount(1);
  const recipientValue = await recipient.locator("option", { hasText: name }).getAttribute("value");
  await recipient.selectOption(recipientValue ?? "");
  await page.getByRole("button", { name: "Gerar previa" }).click();
  await expect(page.locator("textarea")).toContainText(name);
  await page.getByRole("button", { name: "Registrar simulacao" }).click();
  await expect(page.getByText("Simulacao registrada. Nenhuma mensagem real foi enviada.")).toBeVisible();
  await expect(page.getByText("Registrada em simulacao").first()).toBeVisible();
});
