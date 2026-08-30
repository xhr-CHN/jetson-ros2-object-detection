"""Build page contact sheets from Poppler-rendered report PNGs for visual QA."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted((ROOT / "tmp" / "pdfs").glob("report-page-*.png"))
OUT = ROOT / "tmp" / "pdfs"


def main() -> None:
    if not PAGES:
        raise RuntimeError("No rendered report pages found")
    for start in range(0, len(PAGES), 4):
        selected = PAGES[start : start + 4]
        thumbs = []
        for page in selected:
            with Image.open(page) as image:
                copy = image.convert("RGB")
                copy.thumbnail((720, 1020))
                thumbs.append((page, copy.copy()))
        sheet = Image.new("RGB", (1500, 2140), "#dddddd")
        draw = ImageDraw.Draw(sheet)
        for index, (page, thumb) in enumerate(thumbs):
            column = index % 2
            row = index // 2
            x = 20 + column * 740
            y = 35 + row * 1055
            sheet.paste(thumb, (x, y))
            draw.text((x, 10 + row * 1055), page.stem, fill="black")
        destination = OUT / f"contact-{start + 1:02d}-{start + len(selected):02d}.png"
        sheet.save(destination, optimize=True)
        print(destination)


if __name__ == "__main__":
    main()
