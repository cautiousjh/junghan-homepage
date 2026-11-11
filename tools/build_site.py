"""Build public pages from JSON content using only Python's standard library."""
from pathlib import Path
from html import escape
from string import Template
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
site = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
papers = json.loads((ROOT / 'content/publications.json').read_text(encoding='utf-8'))
presentations = json.loads((ROOT / 'content/presentations.json').read_text(encoding='utf-8'))
template = Template((ROOT / 'templates/page.html').read_text(encoding='utf-8'))
e = escape

def link(item, cls=''):
    url = item['url']
    if not url.startswith(('https://', 'mailto:', '/', '#')):
        raise ValueError(f'Unsupported link URL: {url}')
    external = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    return f'<a href="{e(url)}" class="{cls}"{external}>{e(item["label"])}</a>'

def render_paper(p):
    authors = []
    for a in p['authors']:
        name = e(a['name'])
        if a.get('self'):
            name = f'<strong>{name}</strong>'
        if a.get('equal'):
            name += '<sup aria-label="equal contribution">*</sup>'
        authors.append(name)
    title = link({'url': p['links'][0]['url'], 'label': p['title']}) if p['links'] else e(p['title'])
    links = ''.join(link(x, 'paper-link') for x in p['links'])
    links = f'<div class="paper-links">{links}</div>' if links else ''
    year_class = ' forthcoming' if p['year'] == 'In press' else ''
    details = ', ' + e(p['details']) if p.get('details') else ''
    visual = f'<div class="publication-year{year_class}">{e(p["year"])}</div>'
    classes = 'publication'
    if p.get('image'):
        classes += ' has-thumbnail'
        visual = f'<div class="publication-visual"><img src="{e(p["image"])}" alt="{e(p.get("image_alt", p["title"]))}" width="120" height="80" loading="lazy">{visual}</div>'
    return f'''<li class="{classes}" id="{e(p['id'])}">
      {visual}
      <article><h3>{title}</h3><p class="authors">{', '.join(authors)}</p>
        <p class="venue"><cite>{e(p['venue'])}</cite>{details}</p>{links}</article></li>'''

def render_extra(s):
    if not re.fullmatch(r'[a-z][a-z0-9-]*', s['id']):
        raise ValueError('Section IDs must use lowercase letters, numbers and hyphens')
    body = ''
    for index, paragraph in enumerate(s.get('paragraphs', [])):
        inline = ''
        if index == 0 and s.get('inline_icons'):
            icons = ''.join(f'<span role="img" aria-label="{e(i["label"])}" title="{e(i["label"])}">{e(i["symbol"])}</span>' for i in s['inline_icons'])
            inline = f' <span class="inline-interest-icons">{icons}</span>'
        text = e(paragraph)
        marker = s.get('inline_icons_after')
        if inline and marker and marker in paragraph:
            before, separator, after = paragraph.partition(marker)
            text = e(before + separator) + inline + e(after)
        else:
            text += inline
        body += f'<p>{text}</p>'
    if s.get('style') == 'compact-list':
        entries = []
        for item in s.get('items', []):
            status = f' <span class="work-status">({e(item["status"])})</span>' if item.get('status') else ''
            author_names = []
            for author in item.get('authors', []):
                name = e(author['name'])
                if author.get('self'):
                    name = f'<strong>{name}</strong>'
                if author.get('equal'):
                    name += '<sup aria-label="equal contribution">*</sup>'
                author_names.append(name)
            if len(author_names) > 2:
                author_text = ', '.join(author_names[:-1]) + ', &amp; ' + author_names[-1]
            else:
                author_text = ' &amp; '.join(author_names)
            authors = f'<span class="authors work-authors">{author_text}.</span> ' if author_names else ''
            venue = f'<cite>{e(item["venue"])}</cite>' if item.get('venue') else ''
            details = f' <span class="work-details">{venue}{status}</span>' if venue or status else ''
            entries.append(f'<li>{authors}{e(item["title"])}{details}</li>')
        body += '<ul class="work-list">' + ''.join(entries) + '</ul>'
    else:
        for item in s.get('items', []):
            heading = link({'url': item['url'], 'label': item['title']}) if item.get('url') else e(item['title'])
            body += f'<article><h3>{heading}</h3><p>{e(item.get("text", ""))}</p></article>'
    if s.get('icons'):
        icons = ''.join(f'<li><span role="img" aria-label="{e(i["label"])}" title="{e(i["label"])}">{e(i["symbol"])}</span></li>' for i in s['icons'])
        body += f'<ul class="interest-icons" aria-label="Other interests">{icons}</ul>'
    classes = 'extra-section compact-section' if s.get('style') == 'compact-list' else 'extra-section'
    return f'<section class="{classes}" id="{s["id"]}" aria-labelledby="{s["id"]}-title"><h2 id="{s["id"]}-title">{e(s["title"])}</h2>{body}</section>'

def render_presentations():
    sections = []
    for section in presentations['sections']:
        years = dict.fromkeys(item['year'] for item in section['items'])
        groups = []
        for year in years:
            entries = []
            for item in section['items']:
                if item['year'] != year:
                    continue
                text = re.sub(r'Shin, J\. H\.', '<strong>Shin, J. H.</strong>', e(item['text']))
                entries.append(f'<li>{text}</li>')
            year_id = f'{section["id"]}-{year}'
            groups.append(f'<section class="presentation-year-group" aria-labelledby="{year_id}"><h3 id="{year_id}">{year}</h3><ul role="list">{"".join(entries)}</ul></section>')
        sections.append(f'<section class="presentation-section" aria-labelledby="{e(section["id"])}"><h2 id="{e(section["id"])}">{e(section["title"])}</h2>{"".join(groups)}</section>')
    return '<div class="presentations-page"><h1>Presentations</h1>' + ''.join(sections) + '</div>'

def page(main, title, path='/'):
    sharing = site['sharing_image']
    structured = {'@context': 'https://schema.org', '@type': 'Person', 'name': site['name'],
                  'jobTitle': site['role'], 'url': site['url'], 'image': site['url'] + site['portrait'],
                  'affiliation': {'@type': 'Organization', 'name': site['institution']}}
    analytics = ''
    if site.get('analytics_id'):
        ga = site['analytics_id']
        if not re.fullmatch(r'G-[A-Z0-9]+', ga):
            raise ValueError('Invalid analytics ID')
        analytics = f'''<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga}');</script>'''
    return template.substitute(title=e(title), description=e(site['description']), canonical=e(site['url'] + path),
       sharing_image_url=e(site['url'] + sharing['path']), sharing_image_alt=e(sharing['alt']),
       sharing_image_width=sharing['width'], sharing_image_height=sharing['height'],
       name=e(site['name']), email=e(site['email']),
       navigation=''.join(link(x).replace('<a ', '<a aria-current="page" ', 1) if x['url'] == path else link(x) for x in site['navigation']), main=main,
       structured_data=json.dumps(structured, ensure_ascii=False).replace('<', '\\u003c'), analytics=analytics,
       css_hash=hashlib.sha256((ROOT/'assets/site.css').read_bytes()).hexdigest()[:10],
       favicon_hash=hashlib.sha256((ROOT/'assets/favicon.svg').read_bytes()).hexdigest()[:10])

bio = ''.join(f'<p>{e(p)}</p>' for p in site['bio'])
interests = ''
if site.get('research_interests'):
    items = ''.join(f'<li><strong>{e(i["title"])}</strong><span>{e(i["description"])}</span></li>' for i in site['research_interests'])
    interests = f'<section class="research-interests" aria-labelledby="research-interests-title"><h2 id="research-interests-title">Research interests</h2><ul>{items}</ul></section>'
social = ''.join(link(x) for x in site['links'])
scholar = next(x for x in site['links'] if x['label'] == 'Google Scholar')
cv = next(x for x in site['links'] if x['label'] == 'CV')
main = f'''<section class="profile" id="about" aria-labelledby="profile-name">
  <div class="profile-copy"><div class="identity"><h1 id="profile-name">{e(site['name'])}</h1>
    <p class="role">{e(site['role'])}</p><p class="affiliation">{e(site['department'])}<br>{e(site['institution'])}</p></div>
    <div class="bio">{bio}</div><div class="profile-links" aria-label="Contact and profiles">{social}</div>
  </div><figure class="portrait"><img src="{e(site['portrait'])}" alt="{e(site['name'])}" width="842" height="1178" fetchpriority="high"></figure>
</section>
{interests}
<section class="publications" id="publications" aria-labelledby="publications-title">
  <div class="section-heading"><h2 id="publications-title">{e(site['publications_heading'])}</h2>{link({'label':'Google Scholar ↗', 'url':scholar['url']})}</div>
  <ol class="publications-list">{''.join(render_paper(p) for p in papers)}</ol>
  <p class="contribution-note">* Equal contribution.</p>
</section>'''
main += ''.join(render_extra(s) for s in site.get('additional_sections', []))
(ROOT/'index.html').write_text(page(main, site['site_title']), encoding='utf-8')
(ROOT/'cv').mkdir(exist_ok=True)
cv_html = f'''<section class="cv-page"><h1>Curriculum vitae</h1><p>{e(site['name'])}<br>{e(site['role'])}, {e(site['institution'])}</p>
{link({'label':'View CV ↗', 'url':cv['url']}, 'primary-link')}<p><a href="/#publications">Browse publications</a></p></section>'''
(ROOT/'cv/index.html').write_text(page(cv_html, 'CV · ' + site['name'], '/cv/'), encoding='utf-8')
(ROOT/'presentations').mkdir(exist_ok=True)
(ROOT/'presentations/index.html').write_text(page(render_presentations(), 'Presentations · ' + site['name'], '/presentations/'), encoding='utf-8')
not_found = '<section class="cv-page"><h1>Page not found</h1><p>The page you are looking for may have moved.</p><a href="/">Return to the homepage</a></section>'
(ROOT/'404.html').write_text(page(not_found, 'Page not found · ' + site['name'], '/404.html'), encoding='utf-8')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{e(site["url"] + p)}</loc></url>' for p in ['/', '/cv/', '/presentations/']) + '</urlset>\n', encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+site['url']+'/sitemap.xml\n', encoding='utf-8')
print(f'Built homepage, CV, presentations, 404, sitemap and robots.txt with {len(papers)} publications and {sum(len(s["items"]) for s in presentations["sections"])} presentations.')
