# AI Content Engine

`ai-content-engine` generates TikTok-style carousel image posts from a CSV file and local product images.

## Version 0.2.0

This version includes:

- modular Python project structure
- CSV-based post definitions
- local image input
- PNG slide output
- TikTok layout (`1080x1350`)
- Pillow and pandas based rendering
- basic validation and readable error messages
- variable product counts from 1 to 8
- dynamic product slides in chunks of up to 4 items
- improved cover and grid layouts for different item counts

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Project Structure

```text
ai-content-engine/
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── input/
│   ├── product.csv.example
│   └── images/
├── output/
├── assets/
│   ├── fonts/
│   ├── backgrounds/
│   └── logos/
└── engine/
    ├── __init__.py
    ├── background.py
    ├── export.py
    ├── generator.py
    ├── image_tools.py
    ├── layout.py
    ├── products.py
    └── typography.py
```

## Usage

Place your CSV file in `input/` and your product images in `input/images/`.

```bash
python main.py --csv input/product.csv --platform tiktok
```

`tiktok` creates the existing multi-slide carousel flow. `pinterest` creates a single vertical pin with background, title, subtitle and all products on one slide.

## CSV Format

Use the example file as a template:

```csv
post_id,title,subtitle,date,bild_1,bild_2,bild_3,bild_4,bild_5,bild_6,bild_7,bild_8
001,AMAZON FINDS,Pilz Lampen,23.06.26,bild_1.png,bild_2.png,bild_3.png,bild_4.png,bild_5.png,bild_6.png,bild_7.png,bild_8.png
002,AMAZON FINDS,Kitchen Finds,24.06.26,bild_1.png,bild_2.png,bild_3.png,,,,,
```

Required columns:

- `post_id`
- `title`
- `subtitle`
- `date`
- `bild_1` to `bild_8` as optional image columns

You now need at least one image and can provide up to eight.

## Output

For each row in the CSV, the generator writes:

```text
output/<post_id>/
├── slide_1.png      # cover
├── slide_2.png      # first product slide
├── slide_3.png      # optional second product slide
└── slide_N.png      # CTA
```

For Pinterest, the output is a single file:

```text
output/<post_id>/
└── slide_1.png
```

## Fonts

You can control fonts per text role:

- `assets/fonts/title.ttf`
- `assets/fonts/subtitle.ttf`
- `assets/fonts/body.ttf`
- fallback: `assets/fonts/font.ttf`

If none of them exist the generator falls back to Arial, then Pillow's default font.

## Cover Background

If one of these files exists, slide 1 uses it automatically with `50%` opacity:

- `assets/backgrounds/cover.png`
- `assets/backgrounds/cover.jpg`
- `assets/backgrounds/cover.jpeg`
- `assets/backgrounds/cover.webp`

## Local Testing

1. Copy `input/product.csv.example` to `input/product.csv`.
2. Add one to eight transparent PNG product images to `input/images/`.
3. Run:

```bash
python main.py --csv input/product.csv --platform tiktok
```

4. Open the generated slides under `output/<post_id>/`.

## Known Scope

Version `0.2.0` does not yet include:

- OpenAI integration
- Google Sheets or Drive
- Make automation
- theme engine
- theme engine

## Suggested Next Issues

- improve grid balancing and scaling logic
- add theme presets
- export caption and metadata files
- support Google Sheets as a source
- support automated publishing workflows
