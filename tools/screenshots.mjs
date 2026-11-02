// Optional: phone + desktop screenshots of every page into docs/screenshots/.
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
const sizes = [["phone", { width: 390, height: 844 }, 3], ["desktop", { width: 1440, height: 900 }, 1]];
const themes = (process.env.THEMES || "dark").split(",");

mkdirSync(new URL("../docs/screenshots/", import.meta.url), { recursive: true });
const browser = await chromium.launch();
for (const theme of themes) {
  for (const [sname, viewport, dpr] of sizes) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: dpr > 2 ? 2 : dpr, colorScheme: theme, reducedMotion: "reduce" });
    const page = await ctx.newPage();
    for (const [name, path] of pages) {
      await page.goto(base + path, { waitUntil: "networkidle" });
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (overflow > 0) console.warn(`  ! ${name} ${sname}: horizontal overflow ${overflow}px`);
      const suffix = theme === "dark" ? "" : `-${theme}`;
      const file = new URL(`../docs/screenshots/${name}-${sname}${suffix}.png`, import.meta.url);
      await page.screenshot({ path: file.pathname, fullPage: true });
      // also the first screen, which is what a recruiter sees first
      if (name === "home") await page.screenshot({ path: file.pathname.replace(".png", "-fold.png") });
      console.log(`  ${name} ${sname}${suffix}`);
    }
    await ctx.close();
  }
}
await browser.close();
