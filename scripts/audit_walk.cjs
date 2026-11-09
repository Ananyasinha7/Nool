const { chromium } = require("C:/Users/Ananya Sinha/VS code docs/Flagship/nool/frontend/node_modules/@playwright/test");
const path = require("path");
const fs = require("fs");

const BASE = "http://localhost:5173";
const OUT_DIR = path.resolve(__dirname, "../docs/screens");

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

async function run() {
  console.log("Launching Chrome...");
  const browser = await chromium.launch({ channel: "chrome", headless: true });

  // --------------------------------------------------------------------------
  // JOURNEY 1: Supervisor Update
  // --------------------------------------------------------------------------
  console.log("--- Walking Journey 1: Supervisor Update ---");

  // Mobile 360px
  {
    console.log("  J1 Mobile (360px)...");
    const ctx = await browser.newContext({ viewport: { width: 360, height: 740 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.waitForSelector('input[autocomplete="username"]');
    await page.fill('input[autocomplete="username"]', "murugan.u1");
    await page.fill('input[type="password"]', "246810");
    await page.click('button[type="submit"]');

    await page.waitForURL("**/s");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_home_360.png") });

    // Click "Add count" on first card
    const addCountBtn = page.locator('a[href*="/s/update/"]').first();
    await addCountBtn.click();
    await page.waitForURL("**/s/update/**");
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_update_360.png") });

    // Set offline simulation
    await ctx.setOffline(true);
    await page.fill("#qty", "500");
    await page.fill("#note", "2 தையல் மெசின் பழுது");
    await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_update_entered_360.png") });

    // Send while offline
    const sendBtn = page.locator('button:has-text("அனுப்பு"), button:has-text("Send")').last();
    await sendBtn.click();

    // Check if confirm sheet pops up
    const dialog = page.locator('[role="dialog"]');
    if (await dialog.isVisible({ timeout: 1000 }).catch(() => false)) {
      await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_confirm_sheet_360.png") });
      const confirmInDialog = dialog.locator('button:has-text("அனுப்பு"), button:has-text("Send")').first();
      await confirmInDialog.click();
    }

    await page.waitForURL("**/s", { timeout: 4000 }).catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_offline_queued_360.png") });

    // Reconnect
    await ctx.setOffline(false);
    await page.evaluate(() => window.dispatchEvent(new Event("online")));
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_reconnected_360.png") });

    await ctx.close();
  }

  // Desktop 1280px Supervisor
  {
    console.log("  J1 Desktop (1280px)...");
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.fill('input[autocomplete="username"]', "murugan.u1");
    await page.fill('input[type="password"]', "246810");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/s");
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_home_1280.png") });

    const addCountBtn = page.locator('a[href*="/s/update/"]').first();
    await addCountBtn.click();
    await page.waitForURL("**/s/update/**");
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(OUT_DIR, "j1_sup_update_1280.png") });

    await ctx.close();
  }

  // --------------------------------------------------------------------------
  // JOURNEY 2: Warning & Merchandiser Board
  // --------------------------------------------------------------------------
  console.log("--- Walking Journey 2: Merchandiser Board & Warnings ---");

  // Desktop 1280px
  {
    console.log("  J2 Desktop (1280px)...");
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.fill('input[autocomplete="username"]', "priya.merch");
    await page.fill('input[type="password"]', "Nool@Demo2026");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/board");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_board_1280.png") });

    // Navigate to Warnings
    await page.goto(`${BASE}/warnings`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_warnings_1280.png") });

    // Select category if needed and confirm
    const catSelect = page.locator('select').first();
    if (await catSelect.isVisible()) {
      await catSelect.selectOption("MACHINE_BREAKDOWN");
      await page.waitForTimeout(400);
    }
    await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_warning_detail_1280.png") });

    // Confirm warning
    const confirmBtn = page.locator('button:has-text("Confirm"), button:has-text("உறுதிப்படுத்து")').first();
    if (await confirmBtn.isVisible() && await confirmBtn.isEnabled()) {
      await confirmBtn.click();
      await page.waitForTimeout(1200);
      await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_warning_confirmed_1280.png") });
    }

    // Go to outbox to see confirmed notice
    await page.goto(`${BASE}/outbox`);
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_outbox_1280.png") });

    await ctx.close();
  }

  // Mobile 360px Merchandiser
  {
    console.log("  J2 Mobile (360px)...");
    const ctx = await browser.newContext({ viewport: { width: 360, height: 740 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.fill('input[autocomplete="username"]', "priya.merch");
    await page.fill('input[type="password"]', "Nool@Demo2026");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/board");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_board_360.png") });

    await page.goto(`${BASE}/warnings`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_warnings_360.png") });

    const firstWarningBtn = page.locator('button:has-text("PO-"), button:has-text("B-PO")').first();
    if (await firstWarningBtn.isVisible()) {
      await firstWarningBtn.click();
      await page.waitForTimeout(600);
      await page.screenshot({ path: path.join(OUT_DIR, "j2_merch_warning_detail_360.png") });
    }

    await ctx.close();
  }

  // --------------------------------------------------------------------------
  // JOURNEY 3: New Order Setup (4 Steps)
  // --------------------------------------------------------------------------
  console.log("--- Walking Journey 3: New Order Setup ---");

  // Desktop 1280px
  {
    console.log("  J3 Desktop (1280px)...");
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.fill('input[autocomplete="username"]', "priya.merch");
    await page.fill('input[type="password"]', "Nool@Demo2026");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/board");

    await page.goto(`${BASE}/orders/new`);
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUT_DIR, "j3_setup_step1_1280.png") });

    // Click "Load a sample" if present
    const loadSample = page.locator('button:has-text("Load a sample"), button:has-text("மாதிரியை ஏற்று")').first();
    if (await loadSample.isVisible({ timeout: 4000 }).catch(() => false)) {
      await loadSample.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(OUT_DIR, "j3_setup_step1_filled_1280.png") });

      // Step 2
      const nextBtn = page.locator('button:has-text("Next"), button:has-text("அடுத்து")').first();
      await nextBtn.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(OUT_DIR, "j3_setup_step2_1280.png") });

      // Step 3
      await nextBtn.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(OUT_DIR, "j3_setup_step3_1280.png") });

      // Step 4
      await nextBtn.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(OUT_DIR, "j3_setup_step4_1280.png") });
    }

    await ctx.close();
  }

  // Mobile 360px Setup Step 1
  {
    console.log("  J3 Mobile (360px)...");
    const ctx = await browser.newContext({ viewport: { width: 360, height: 740 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.fill('input[autocomplete="username"]', "priya.merch");
    await page.fill('input[type="password"]', "Nool@Demo2026");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/board");

    await page.goto(`${BASE}/orders/new`);
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUT_DIR, "j3_setup_step1_360.png") });

    await ctx.close();
  }

  // --------------------------------------------------------------------------
  // JOURNEY 4: Buyer Self-Service
  // --------------------------------------------------------------------------
  console.log("--- Walking Journey 4: Buyer Self-Service ---");

  // Desktop 1280px
  {
    console.log("  J4 Desktop (1280px)...");
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/b/demo-b-0001`);
    await page.waitForURL("**/b", { timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUT_DIR, "j4_buyer_list_1280.png") });

    // Click first order row
    const firstOrder = page.locator('a[href*="/b/orders/"]').first();
    if (await firstOrder.isVisible()) {
      await firstOrder.click();
      await page.waitForURL("**/b/orders/**");
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(OUT_DIR, "j4_buyer_order_1280.png") });
    }

    await ctx.close();
  }

  // Mobile 360px Buyer
  {
    console.log("  J4 Mobile (360px)...");
    const ctx = await browser.newContext({ viewport: { width: 360, height: 740 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/b/demo-b-0001`);
    await page.waitForURL("**/b", { timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUT_DIR, "j4_buyer_list_360.png") });

    const firstOrder = page.locator('a[href*="/b/orders/"]').first();
    if (await firstOrder.isVisible()) {
      await firstOrder.click();
      await page.waitForURL("**/b/orders/**");
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(OUT_DIR, "j4_buyer_order_360.png") });
    }

    await ctx.close();
  }

  // --------------------------------------------------------------------------
  // JOURNEY 5: Merchandiser changes ex-factory date
  // --------------------------------------------------------------------------
  console.log("--- Walking Journey 5: Merchandiser Order Detail & Change Date ---");

  // Desktop 1280px
  {
    console.log("  J5 Desktop (1280px)...");
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.fill('input[autocomplete="username"]', "priya.merch");
    await page.fill('input[type="password"]', "Nool@Demo2026");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/board");

    // Click into an order (e.g. first order link)
    const orderLink = page.locator('a[href^="/orders/"]:not([href="/orders/new"]):visible').first();
    await orderLink.waitFor({ state: "visible", timeout: 8000 }).catch(() => {});
    if (await orderLink.isVisible()) {
      await orderLink.click();
      await page.waitForURL("**/orders/**");
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(OUT_DIR, "j5_merch_order_detail_1280.png") });

      // Click "Change date" button
      const changeDateBtn = page.locator('button:has-text("Change date"), button:has-text("தேதியை மாற்று")').first();
      await changeDateBtn.waitFor({ state: "visible", timeout: 4000 }).catch(() => {});
      if (await changeDateBtn.isVisible()) {
        await changeDateBtn.click();
        await page.waitForTimeout(600);
        await page.screenshot({ path: path.join(OUT_DIR, "j5_change_date_sheet_1280.png") });
      }
    }

    await ctx.close();
  }

  // Mobile 360px
  {
    console.log("  J5 Mobile (360px)...");
    const ctx = await browser.newContext({ viewport: { width: 360, height: 740 } });
    const page = await ctx.newPage();

    await page.goto(`${BASE}/login`);
    await page.fill('input[autocomplete="username"]', "priya.merch");
    await page.fill('input[type="password"]', "Nool@Demo2026");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/board");

    const orderLink = page.locator('a[href^="/orders/"]:not([href="/orders/new"]):visible').first();
    await orderLink.waitFor({ state: "visible", timeout: 8000 }).catch(() => {});
    if (await orderLink.isVisible()) {
      await orderLink.click();
      await page.waitForURL("**/orders/**");
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(OUT_DIR, "j5_merch_order_detail_360.png") });

      const changeDateBtn = page.locator('button:has-text("Change date"), button:has-text("தேதியை மாற்று")').first();
      await changeDateBtn.waitFor({ state: "visible", timeout: 4000 }).catch(() => {});
      if (await changeDateBtn.isVisible()) {
        await changeDateBtn.click();
        await page.waitForTimeout(600);
        await page.screenshot({ path: path.join(OUT_DIR, "j5_change_date_sheet_360.png") });
      }
    }

    await ctx.close();
  }

  await browser.close();
  console.log("All journey screenshots captured successfully!");
}

run().catch((err) => {
  console.error("Audit walk failed:", err);
  process.exit(1);
});
