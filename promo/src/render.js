// Renders reel.html to PNG frames.
//   node render.js <outDir> [startFrame endFrame] | node render.js <outDir> --stills 30,120,...
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FPS = 30, DUR = 23.5, TOTAL = FPS * DUR, WORKERS = 4;

(async () => {
  const out = process.argv[2];
  fs.mkdirSync(out, { recursive: true });
  let frames;
  if (process.argv[3] === '--stills') frames = process.argv[4].split(',').map(Number);
  else {
    const a = Number(process.argv[3] ?? 0), b = Number(process.argv[4] ?? TOTAL);
    frames = Array.from({ length: b - a }, (_, i) => a + i);
  }
  const browser = await chromium.launch();
  const url = 'file://' + path.join(__dirname, 'reel.html');
  let next = 0;
  await Promise.all(Array.from({ length: WORKERS }, async () => {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => { console.error(e); process.exit(1); });
    await page.goto(url);
    await page.evaluate(() => window.ready);
    while (next < frames.length) {
      const f = frames[next++];
      await page.evaluate(n => window.render(n), f);
      await page.screenshot({ path: path.join(out, String(f).padStart(5, '0') + '.png') });
    }
    await page.close();
  }));
  await browser.close();
  console.log('rendered', frames.length, 'frames');
})();
