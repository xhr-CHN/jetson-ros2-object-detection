const path = require("path");
const { chromium } = require("playwright");

const figures = path.join(__dirname, "figures");
const edge = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";

async function captureGitHub(page, url, filename) {
  await page.goto(url, { waitUntil: "networkidle", timeout: 90000 });
  await page.evaluate(() => {
    document.documentElement.style.background = "white";
    document.body.style.background = "white";
    document.body.style.filter = "grayscale(1)";
  });
  await page.screenshot({ path: path.join(figures, filename), fullPage: false });
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: edge });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
  await captureGitHub(
    page,
    "https://github.com/xhr-CHN/jetson-ros2-object-detection",
    "github_repository.png"
  );
  await captureGitHub(
    page,
    "https://github.com/xhr-CHN/jetson-ros2-object-detection/commits/main/",
    "github_commits.png"
  );
  await browser.close();
  console.log("Captured monochrome GitHub repository and commit-history evidence.");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
