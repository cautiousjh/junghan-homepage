# Jung Han Shin - personal homepage

Canonical website: **https://junghan.shin.ai.kr**

This is the only repository for homepage content. The separate
`cautiousjh/personal_page` repository retains `neuro.ai.kr` solely to redirect
old links. It is not a second homepage.

## Edit content

Research interests continues the biography with a modest 18px heading and no
divider. Its wider left column contains four interests (14px names, 13px
descriptions, 12px gaps). The original full flowing illustration is preserved
on the right, up to 480px wide, without forcing a square crop. Its frame extends
60px into the available inter-column space while label font sizes stay fixed.
Below 760px it
moves below the list, at up to 340px wide. Desktop positioning aligns the
visible bottom wisps with the last bullet's description; transparent padding
does not add layout height. News follows with a 24px top margin.
The PNG, display WebP and inline
preview all retain genuine alpha transparency; no white matte or CSS blend
mode is used. Once the full image loads, its preview is hidden so translucent
lines are not drawn twice. With JavaScript disabled, only the final image shows.
`research_schematic` controls this illustration independently of sharing cards.

`python tools/prepare_research_transparency.py` rebuilds the transparent
illustration from the preserved approved artwork; it needs Pillow and NumPy.
Run this only when changing that artwork, then run the usual image preparation
and site build. It removes near-white paper grain and retains the colored wisps.

The diagram's three labels are HTML buttons, and its connections are native
SVG paths. Hover or keyboard focus highlights a connection. Clicking/tapping
toggles the selection; Escape clears it. `assets/research-diagram.js` handles
the highlight state, with reduced-motion support in CSS. Without JavaScript,
the labels and diagram remain visible. There is no automatic animation.

The first two interest descriptions use middle-dot separators. The descriptions
of Brain-inspired AI and Cognitive augmentation retain their existing wording.

| File | Edit here |
| --- | --- |
| `content/site.json` | Name, affiliation, biography paragraphs, navigation, contact/CV links |
| `content/publications.json` | Publication entries, author order, equal contributions, status and links |
| `content/presentations.json` | Invited talks and conference presentations, with original CV text and year |
| `assets/site.css` | Responsive layout, light palette and typography |
| `assets/images/jung-han-shin.png` | Original supplied portrait (visual crop is CSS only) |
| `templates/page.html` | Shared page structure, navigation, metadata and footer |
| `tools/build_site.py` | Static HTML generator; Python standard library only |
| `tools/prepare_images.py` | Generate WebP display copies and inline previews; requires Pillow |

The `site_title` field controls the homepage browser and sharing-preview title, currently `Jung Han Shin · Neuro x AI`.

### Image loading

After adding or replacing a portrait/publication source image, run
`python tools/prepare_images.py`, then `python tools/build_site.py`.
The preparation step writes display-size WebP copies and a manifest under
`assets/images/optimized/`. Source PNGs are preserved. Publication viewBox crops,
clip paths, white masks, paper links and the portrait's CSS crop stay unchanged.

Small previews are embedded in the HTML and shown beneath the main images.
The browser covers them when each main image finishes loading; this needs no
JavaScript. Previews have no added blur. The portrait keeps high fetch priority,
and ordinary publication `<img>` elements retain native lazy loading.
The builder uses prepared files only if their recorded source hash matches;
otherwise it falls back to the original until preparation is rerun.

The portrait and eight publication images total about 338 KB, plus 40 KB of
inline previews. The transparent research illustration adds about 205 KB plus its
inline preview. Sharing-card artwork is managed separately.

The `bio` array in `content/site.json` contains the introduction: one quoted
string per paragraph. Edit only the text inside the double quotes, preserve
the separating commas, and save as UTF-8. `research_interests` holds the four
CV research areas. `additional_sections` includes Beyond research; its
`paragraphs` contains the sports sentence and `icons` contains emoji with
accessible labels. Food, tea and drinks are written as a sentence. Each sport has one small emoji placed via `activity_icons`. Do not use en or em dashes in site copy.

Add a publication by copying an object in `content/publications.json`. Display
order follows the file. Set `self: true` to emphasize the owner's name and
`equal: true` for equal contributions. Include only real, public links; an
empty links array is appropriate for an in-press paper without a public URL.
The `figures` array adds a 180px thumbnail column to the right of the citation. Each entry has `thumbnail`,
`full`, `width`, `height`, and `alt`. Optional `crop: [x, y, width, height]`
selects a displayed region through an SVG viewBox and clipPath without editing the PNG.
Optional `mask_rects: [[x, y, width, height]]` adds white display-only rectangles
inside that crop; training uses one to hide a clipped text fragment at the lower left.
Thumbnails link to the same paper URL as the title when one is available;
entries without a paper URL use non-clickable images. `full` retains the original
figure reference in the source data. Paired figures are stacked on desktop
and placed side by side below the citation on narrow screens. Entries without
figures keep the compact year column. Legacy `image` / `image_alt` still work.

News is managed in `content/news.json` and appears before Publications. Each item
has `date` (`YYYY-MM`) and `text`, with an optional `link` containing `label` and
`url`. Items sort newest first. The latest three are visible; older items appear
under a native Show more / Show less disclosure with a chevron. The control is
omitted when there are three or fewer items. Use only confirmed dates and facts.
Beyond research uses `activity_icons` with `after` and `symbol` to place one small
decorative emoji beside each sport while preserving the paragraph text.

To add a simple future section, append an object to `additional_sections` in
`content/site.json`. It accepts `id`, `title`, `paragraphs` (list of strings),
and `items` (objects with `title`, `text`, and optional `url`). Add its anchor
to `navigation` when needed. Empty sections are not shown. More specialized
sections can have their own renderer in the build script.

## Build and publish

From this repository:

```powershell
python tools/build_site.py
python -m http.server 8765 --bind 127.0.0.1
```

Preview at http://127.0.0.1:8765. Review the change, then commit the content,
templates, assets **and generated HTML** together and push to `origin/main`.
GitHub Pages publishes the root of `main`; `.nojekyll` serves static files.
Do not edit generated `index.html`, `cv/index.html`, `presentations/index.html`, `404.html`, `sitemap.xml`,
or `robots.txt` directly. No theme package or JavaScript framework is required.

Keep `content/site.json`'s `url`, `CNAME`, and `_config.yml` aligned. The domain
is `junghan.shin.ai.kr`, not the default account-level github.io URL.
The existing Google Analytics property is retained.

## Content decisions - 2026-11-11

- Official name: Jung Han Shin. Light appearance; an al-folio-inspired academic
  layout with publications directly below the short introduction.
- No GitHub profile link, posts or news feed. A compact Work in progress list now follows publications.
- Bio combines the supplied research profile with the author's LinkedIn
  description of methods and the two-way connection between neuroscience and AI.
- CV link keeps the existing stable Google Drive file ID. CV source documents
  and versioned PDFs are maintained separately, not committed here.
- JOCN DOI `10.1162/jocn_a_02229` uses the final 2025 citation
  (37(11), 1873-1888; Crossref and PubMed PMID 39106162), rather than the CV's 2024 year.
- NeuroImage DOI `10.1016/j.neuroimage.2025.121101` uses the publisher's final
  title, “Stimulation of the anterior thalamus modulates behavior in multiple
  cognitive domains”.
- The Nature Communications article remains **In press**, as in the supplied CV;
  no unverified DOI/PDF button is displayed.

The original site's Git history is retained. The legacy domain preserves HTTPS
and redirects in the browser, including paths, query strings and fragments;
it does not return an HTTP 301 response.

## Sharing image and hobby paragraph

The owner selected variant 2 (head-focused network) on 2026-11-12: a green person with an anatomical brain facing a blue person with a network only inside the head, joined by a soft flowing connection. It is stored as `assets/images/human-ai-head-network-share-20261112.png`, copied without image changes from `../design/mri-thumbnail-20261111/right-network-02-head-focused-20261112.png`. Earlier image assets are retained.
`sharing_image` in `content/site.json` controls Open Graph and large-image
Twitter/X cards independently of the on-page portrait. Original dimensions
are 1672 by 940, and the PNG is about 1.70 MB.

Beyond research uses one paragraph, starting with "Outside research,".
`inline_icons_after` identifies the sentence after which the small water
emoji are inserted. If editing that sentence, update the marker too.

Work in progress entries live in content/site.json under additional_sections.
Keep manuscript titles verbatim from the supplied CV. The first is marked
In revision; do not imply publication or add unconfirmed target journals.
The favicon is a simple teal brain outline, with a content-hashed URL.

Work in progress shows all authors in CV order, with equal contributions
marked. The owner authorized the first manuscript's Nature Communications
venue label; its status remains In revision until formal acceptance.

## Presentations

The separate `/presentations/` page is linked in the top navigation. It contains
the six invited talks and lectures and 33 conference presentations from the
owner-supplied 202611 CV. `content/presentations.json` preserves every entry's
text, author order, presentation type, and award labels. Entries are grouped by
year within each section, newest first, with no visible bullets or numbers.
Edit the JSON for future updates; do not copy CV source documents into this repo.
Award labels in parentheses are displayed in bold while retaining the CV text.

The Email, Google Scholar and CV links sit beneath the portrait on desktop.
At widths up to 760px they remain a full-width row below the introduction.

## Education

Education is a compact homepage section immediately before Beyond research,
without a navigation tab. It is stored in `additional_sections` in `content/site.json`
with `style: education`. Degrees, dates, thesis title and advisor affiliations
follow the 202611 CV; advisor names link to their official profile pages.

Homepage section headings use a shared size, weight and thin divider. The
Presentations heading links to the separate page with an inline SVG link icon;
its text is underlined only on hover or keyboard focus. Body typography is retained.

## Publication figure sources

The owner supplied source images in `../figures/`; original PNGs and PPTX files
stay there. Public copies are under `assets/images/publications/`.
Training uses the navigation-task region of `2026_training1.png` and the
hippocampal-subfield region of `2026_training2.png`, retaining both full originals.
Boundary and fNIRS each pair the original `ppt/media/image1.png` picture
extracted from the supplied PPTX with a result region from the full PNG overview.
Boundary shows the task and brain results; fNIRS shows the device and delay/decision results.
DBS and macaque thumbnails use the supplied PNGs in full. No scientific pixels,
data, labels, or source slide files were edited.

Education items may include `projects` with a `title` and optional `url`. These render as small 12px bullets under the degree. Undergraduate demo links were supplied by the owner; the two laboratory research topics come from the November 2026 CV.

Sharing images: `sharing_image` is optional. The current override uses the approved human/AI illustration and a large-image card. With no override, Open Graph and Twitter fall back to the existing `portrait`, with a compact Twitter summary card. Previous graphics are retained as unused assets; local MRI materials are not part of the public repository.
