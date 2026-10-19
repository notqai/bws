// Renders site/capability.html to site/assets/docs/bws-capability-statement.pdf (A4).
// Run after tools/generate_site.py:  node tools/make_capability_pdf.js
// Needs Playwright with Chromium (npm i -g playwright && npx playwright install chromium), then run
// generate_site.py again so the vendor page shows the download button.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const site = path.join(__dirname, "..", "site");
const out = path.join(site, "assets", "docs", "bws-capability-statement.pdf");

(async () => {
  const opts = process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {};
  const browser = await chromium.launch(opts);
  const page = await browser.newPage();
  await page.goto("file://" + path.join(site, "capability.html"), { waitUntil: "networkidle" });
  fs.mkdirSync(path.dirname(out), { recursive: true });
  await page.pdf({
    path: out, format: "A4", printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: "<span></span>",
    footerTemplate: '<div style="width:100%;font:8px Arial,sans-serif;color:#5B6675;padding:0 14mm;display:flex;justify-content:space-between"><span>BWS Engineering Sdn Bhd · Capability statement</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
  });
  await browser.close();
  console.log("wrote " + path.relative(process.cwd(), out) + " (" + Math.round(fs.statSync(out).size / 1024) + " KB)");
})();
