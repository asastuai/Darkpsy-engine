// Drives the MESA flow in headless Chrome and screenshots each screen,
// so we can SEE the UI and iterate the aesthetic.
import puppeteer from "puppeteer";
import { mkdirSync } from "node:fs";

const BASE = process.env.URL || "http://localhost:5173";
const OUT = "C:/Users/Juan/Desktop/Darkpsy-engine/mesa/shots/";
mkdirSync(OUT, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function clickText(page, text, sels = "button, .level-card, .chip, .tab, .vibe") {
  const handles = await page.$$(sels);
  for (const h of handles) {
    const t = (await page.evaluate((el) => el.textContent || "", h)).trim();
    if (t.includes(text)) { await h.click(); return true; }
  }
  console.warn(`! no encontré clickable con texto "${text}"`);
  return false;
}

async function shot(page, name) {
  await page.screenshot({ path: `${OUT}${name}.png` });
  console.log(`  📸 ${name}.png`);
}

const browser = await puppeteer.launch({
  headless: true,
  args: ["--autoplay-policy=no-user-gesture-required", "--no-sandbox"],
});
const page = await browser.newPage();
await page.setViewport({ width: 1320, height: 860, deviceScaleFactor: 2 });
page.on("console", (m) => { if (m.type() === "error") console.log("  [browser error]", m.text()); });

try {
  await page.goto(BASE, { waitUntil: "networkidle2", timeout: 20000 });
  await sleep(600);
  await shot(page, "01-intro");

  await clickText(page, "EMPEZAR");
  await sleep(500);
  await shot(page, "02-level");

  await clickText(page, "Intermedio");
  await sleep(500);
  await shot(page, "03-chat");

  await clickText(page, "Orden");        // pick a preset chip
  await sleep(300);
  await shot(page, "04-chat-picked");
  await clickText(page, "➤", "button");  // send
  // wait for the machine to appear (cook overlay -> workspace)
  await page.waitForSelector(".machine", { timeout: 15000 });
  await sleep(2200);                      // let spectrogram + meters draw
  await shot(page, "05-workspace");

  console.log("listo.");
} catch (e) {
  console.error("ERROR:", e.message);
  await shot(page, "99-error-state");
} finally {
  await browser.close();
}
