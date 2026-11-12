"""Prepare lightweight display images; never modify or crop source images.

Run after changing a portrait or publication image, before build_site.py.
Requires Pillow. Cropping and masks remain in the existing HTML/SVG/CSS.
"""
from pathlib import Path
from io import BytesIO
import base64
import hashlib
import json

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/images/optimized'
OUT.mkdir(exist_ok=True)
site = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
papers = json.loads((ROOT / 'content/publications.json').read_text(encoding='utf-8'))

# Scale whole images, not crops. SVG viewBox and mask coordinates stay untouched.
jobs = {site['portrait']: {'display_width': 220 * 1.17, 'display_height': None,
                         'preview_width': 144, 'background': '#e8edf0', 'quality': 88}}
if site.get('research_schematic'):
    jobs[site['research_schematic']['path']] = {
        'display_width': 360, 'display_height': None,
        'preview_width': 236, 'background': '#ffffff', 'quality': 92}
for paper in papers:
    figures = paper.get('figures', [])
    for figure in figures:
        visible = figure.get('crop', [0, 0, figure['width'], figure['height']])
        box_height = 108 if len(figures) > 1 and figure.get('crop') else 120
        display_scale = min(180 / visible[2], box_height / visible[3])
        # 2.5x display density keeps thin figure lines clear on high-DPI screens.
        job = {'display_width': figure['width'] * display_scale,
               'display_height': figure['height'] * display_scale,
               'preview_width': figure['width'] * display_scale * (96 / 180),
               'background': '#ffffff', 'quality': 92}
        previous = jobs.get(figure['thumbnail'])
        if previous is None or job['display_width'] > previous['display_width']:
            jobs[figure['thumbnail']] = job

assets = {}
for url, settings in jobs.items():
    source = ROOT / url.lstrip('/')
    original_bytes = source.read_bytes()
    rgba = ImageOps.exif_transpose(Image.open(source)).convert('RGBA')
    # Match the existing element's background, so the loaded image fully covers
    # its preview even when the source PNG contains transparency.
    original = Image.new('RGB', rgba.size, settings['background'])
    original.paste(rgba, mask=rgba.getchannel('A'))
    density = 2.5
    width = min(original.width, round(settings['display_width'] * density))
    size = (width, max(1, round(original.height * width / original.width)))
    display = original.resize(size, Image.Resampling.LANCZOS)
    data = BytesIO()
    display.save(data, format='WEBP', quality=settings['quality'], method=6)
    encoded = data.getvalue()
    digest = hashlib.sha256(encoded).hexdigest()[:10]
    name = f'{source.stem}-{digest}.webp'
    (OUT / name).write_bytes(encoded)

    preview_width = min(original.width, max(1, round(settings['preview_width'])))
    preview = original.resize((preview_width, max(1, round(original.height * preview_width / original.width))),
                              Image.Resampling.LANCZOS)
    data = BytesIO()
    preview.save(data, format='WEBP', quality=78, method=6)
    preview_bytes = data.getvalue()
    assets[url] = {
        'path': '/assets/images/optimized/' + name,
        'width': size[0], 'height': size[1],
        'source_sha256': hashlib.sha256(original_bytes).hexdigest(),
        'source_bytes': len(original_bytes), 'display_bytes': len(encoded),
        'preview_bytes': len(preview_bytes),
        'preview': 'data:image/webp;base64,' + base64.b64encode(preview_bytes).decode('ascii'),
    }

manifest = {'version': 1, 'assets': assets}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
old = sum(a['source_bytes'] for a in assets.values())
new = sum(a['display_bytes'] for a in assets.values())
previews = sum(len(a['preview']) for a in assets.values())
print(json.dumps({'images': len(assets), 'original_bytes': old, 'display_bytes': new,
                  'inline_preview_characters': previews,
                  'reduction_including_previews_pct': round(100 * (1 - (new + previews) / old), 1)}))
