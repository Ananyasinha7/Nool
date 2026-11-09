import { expect, test } from "@playwright/test";

// The headline story: a supervisor submits OFFLINE, reconnects, the order turns non-green, the merchandiser
// confirms the warning, and the buyer's link shows the notice. NOT RUN in the build sandbox (browser downloads
// are blocked there): run `npx playwright install chromium && npm run e2e` locally or in CI.
test("supervisor offline -> board -> confirm -> buyer notice", async ({ page, context, browser }) => {
  // 1. Supervisor signs in (Tamil by default), then goes offline
  await page.goto("/login");
  await page.getByLabel(/Username|பயனர் பெயர்/).fill("murugan.u1");
  await page.getByLabel(/PIN|பின்/).fill("246810");
  await page.getByRole("button", { name: /Sign in|உள்நுழை/ }).click();
  await expect(page).toHaveURL(/\/s$/);
  await expect(page.getByText("B-PO-88329").first()).toBeVisible();
  await context.setOffline(true);

  // 2. A very slow day with a Tamil note: Send returns at once and the entry is queued
  const card = page.locator("div", { hasText: "B-PO-88329" }).filter({ has: page.getByRole("link") }).last();
  await card.getByRole("link", { name: /எண்ணிக்கை சேர்|Add count/ }).click();
  await page.locator("#qty").fill("5");
  await page.locator("#note").fill("2 தையல் மெசின் பழுது");
  await page.getByRole("button", { name: /அனுப்பு|Send/ }).click();
  await expect(page).toHaveURL(/\/s$/, { timeout: 2000 });
  await expect(page.getByText(/வரிசையில்|Queued/).first()).toBeVisible();

  // 3. Reconnect: the queue drains by itself
  await context.setOffline(false);
  await page.evaluate(() => window.dispatchEvent(new Event("online")));
  await expect(page.getByLabel(/அனைத்தும் அனுப்பப்பட்டன|All sent/)).toBeVisible({ timeout: 15_000 });

  // 4. Merchandiser: a draft warning is waiting; confirm it
  const merch = await (await browser.newContext()).newPage();
  await merch.goto("/login");
  await merch.getByLabel("Username").fill("priya.merch");
  await merch.getByLabel(/Password or PIN/).fill("Nool@Demo2026");
  await merch.getByRole("button", { name: "Sign in" }).click();
  await expect(merch).toHaveURL(/\/board/);
  await merch.getByRole("link", { name: /Warnings/ }).first().click();
  await merch.getByRole("button", { name: /B-PO-88329/ }).click();
  await expect(merch.getByText("2 தையல் மெசின் பழுது").first()).toBeVisible();
  await merch.getByRole("button", { name: "Confirm and send to buyer" }).click();

  // 5. Buyer: the magic link shows the delay notice, never the raw floor note
  const buyer = await (await browser.newContext()).newPage();
  await buyer.goto("/b/demo-b-0001");
  await expect(buyer).toHaveURL(/\/b$/);
  await expect(buyer.getByText(/Delay notice/).first()).toBeVisible();
  await expect(buyer.getByText("மெசின்")).toHaveCount(0);
});
