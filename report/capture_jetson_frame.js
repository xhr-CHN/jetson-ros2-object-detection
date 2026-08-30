const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const edge = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const root = path.resolve(__dirname, "..");
const videoUrl = pathToFileURL(
  path.join(root, "results", "jetson", "2026-08-30", "jetson_demo.mp4")
).href;

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: edge });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
  await page.goto(videoUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
  const video = page.locator("video");
  await video.waitFor({ state: "visible", timeout: 30000 });
  await page.evaluate(async () => {
    const element = document.querySelector("video");
    element.muted = true;
    element.currentTime = 8;
    await new Promise((resolve) => {
      element.addEventListener("seeked", resolve, { once: true });
      setTimeout(resolve, 5000);
    });
    element.controls = false;
  });
  await video.screenshot({ path: path.join(__dirname, "figures", "jetson_realtime.png") });
  await browser.close();
  console.log("Captured Jetson video frame at 8 seconds.");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
