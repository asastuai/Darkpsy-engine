// Drives the Pro flow: upload a track in chat -> backend separates -> multi-stem machine.
import puppeteer from "puppeteer";
import { mkdirSync } from "node:fs";

const BASE = "http://localhost:5173";
const OUT = "C:/Users/Juan/Desktop/Darkpsy-engine/mesa/shots/";
const FILE = "C:/Users/Juan/Desktop/Darkpsy-engine/forja/recreation_out/phase0/00_clip.wav";
mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function clickText(page, text, sels = "button, .level-card, .chip, .ptab") {
  const handles = await page.$$(sels);
  for (const h of handles) {
    const t = (await page.evaluate((el) => el.textContent || "", h)).trim();
    if (t.includes(text)) { await h.click(); return true; }
  }
  console.warn(`! no clickable "${text}"`);
  return false;
}

const browser = await puppeteer.launch({ headless: true, args: ["--autoplay-policy=no-user-gesture-required", "--no-sandbox"] });
const page = await browser.newPage();
await page.setViewport({ width: 1320, height: 860, deviceScaleFactor: 2 });
page.on("console", (m) => { if (m.type() === "error") console.log("  [browser]", m.text()); });

try {
  await page.goto(BASE, { waitUntil: "networkidle2", timeout: 20000 });
  await sleep(500);
  await clickText(page, "EMPEZAR");
  await sleep(400);
  await clickText(page, "Pro");
  await sleep(500);
  // upload the track into the chat's hidden file input
  const input = await page.$('input[type=file]');
  await input.uploadFile(FILE);
  await sleep(500);
  await page.screenshot({ path: `${OUT}r1-chat-file.png` });
  await clickText(page, "➤", "button");
  console.log("  enviado, esperando separación del backend...");
  await page.waitForSelector(".machine", { timeout: 180000 });
  await sleep(2500);
  await page.screenshot({ path: `${OUT}r2-machine-stems.png` });
  // count modules
  const mods = await page.$$eval(".module .module-name", (els) => els.map((e) => e.textContent));
  console.log("  módulos en la máquina:", mods.join(", "));
  console.log("listo.");
} catch (e) {
  console.error("ERROR:", e.message);
  await page.screenshot({ path: `${OUT}r9-error.png` });
} finally {
  await browser.close();
}
