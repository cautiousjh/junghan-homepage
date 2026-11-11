# Jung Han Shin - personal homepage

Canonical website: **https://junghan.shin.ai.kr**

This is the only repository for homepage content. The separate
`cautiousjh/personal_page` repository retains `neuro.ai.kr` solely to redirect
old links. It is not a second homepage.

## Edit content

| File | Edit here |
| --- | --- |
| `content/site.json` | Name, affiliation, biography paragraphs, navigation, contact/CV links |
| `content/publications.json` | Publication entries, author order, equal contributions, status and links |
| `assets/site.css` | Responsive layout, light palette and typography |
| `assets/images/jung-han-shin.png` | Original supplied portrait (visual crop is CSS only) |
| `templates/page.html` | Shared page structure, navigation, metadata and footer |
| `tools/build_site.py` | Static HTML generator; Python standard library only |

The `site_title` field controls the homepage browser and sharing-preview title.
The `bio` array in `content/site.json` contains the introduction: one quoted
string per paragraph. Edit only the text inside the double quotes, preserve
the separating commas, and save as UTF-8. `research_interests` holds the four
CV research areas. `additional_sections` includes Beyond research; its
`paragraphs` contains the sports sentence and `icons` contains emoji with
accessible labels. Food, tea and drinks are written as a sentence. Small wave and diving-mask emoji follow the first hobby sentence via `inline_icons`. Do not use en or em dashes in site copy.

Add a publication by copying an object in `content/publications.json`. Display
order follows the file. Set `self: true` to emphasize the owner's name and
`equal: true` for equal contributions. Include only real, public links; an
empty links array is appropriate for an in-press paper without a public URL.
Optional `image` and `image_alt` fields add a 120 by 80 pixel thumbnail. Leave
them absent until a real paper figure is available; no empty slot is reserved.

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
Do not edit generated `index.html`, `cv/index.html`, `404.html`, `sitemap.xml`,
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

The sharing image is the owner-selected attachment showing a soft brain on the left connected to a network on the right, stored as brain-network-share-v2.png. This supersedes the previously mismatched concept 03 selection.
`sharing_image` in `content/site.json` controls Open Graph and large-image
Twitter/X cards independently of the on-page portrait. Original dimensions
are 1734 by 907 (1.912:1), and the PNG is about 1.13 MB.

Beyond research uses one paragraph, starting with "Outside research,".
`inline_icons_after` identifies the sentence after which the small water
emoji are inserted. If editing that sentence, update the marker too.

Work in progress entries live in content/site.json under additional_sections.
Keep manuscript titles verbatim from the supplied CV. The first is marked
In revision; do not imply publication or add unconfirmed target journals.
The favicon is a simple teal brain outline, with a content-hashed URL.
