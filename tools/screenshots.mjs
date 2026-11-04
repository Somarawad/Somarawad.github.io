// Optional: phone + desktop screenshots of every page into docs/screenshots/ (dark theme;
// with THEMES=dark,light also light-theme samples of home and NOVARA).
// Needs Node and Playwright (npm i -D playwright && npx playwright install chromium).
// Start a server first:  python3 -m http.server 8000
// Then:                  node tools/screenshots.mjs [http://localhost:8000]
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright");
import { mkdirSync, readFileSync } from "node:fs";

const base = (process.argv[2] || "http://localhost:8000").replace(/\/$/, "");
const data = JSON.parse(readFileSync(new URL("../data/projects.json", import.meta.url)));
const pages = [["home", "/"], ["about", "/about/"], ["404", "/404.html"]];
for (const p of data.projects) if (p.published) pages.push([p.slug, `/work/${p.slug}/`]);
const sizes = [["phone", { width: 390, height: 844 }], ["desktop", { width: 1440, height: 900 }]];
const themes = (process.env.THEMES || "dark").split(",");

mkdirSync(new URL("../docs/screenshots/", import.meta.url), { recursive: true });
const browser = await chromium.launch();
for (const theme of themes) {
  for (const [sname, viewport] of sizes) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: "reduce" });
    const page = await ctx.newPage();
    for (const [name, path] of pages) {
      // light theme: only a sample, to keep the repo small
      if (theme !== "dark" && !["home", "novara"].includes(name)) continue;
      await page.goto(base + path, { waitUntil: "networkidle" });
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (overflow > 0) console.warn(`  ! ${name} ${sname}: horizontal overflow ${overflow}px`);
      const suffix = theme === "dark" ? "" : `-${theme}`;
      const file = new URL(`../docs/screenshots/${name}-${sname}${suffix}.jpg`, import.meta.url);
      await page.screenshot({ path: file.pathname, fullPage: true, type: "jpeg", quality: 72 });
      // also the first screen, which is what a recruiter sees first
      if (name === "home") await page.screenshot({ path: file.pathname.replace(".jpg", "-fold.jpg"), type: "jpeg", quality: 80 });
      console.log(`  ${name} ${sname}${suffix}`);
    }
    await ctx.close();
  }
}
await browser.close();
