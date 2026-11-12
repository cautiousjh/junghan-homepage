"""Build public pages from JSON content using only Python's standard library."""
from pathlib import Path
from html import escape
from string import Template
import hashlib
import json
import re
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
site = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
papers = json.loads((ROOT / 'content/publications.json').read_text(encoding='utf-8'))
presentations = json.loads((ROOT / 'content/presentations.json').read_text(encoding='utf-8'))
news = json.loads((ROOT / 'content/news.json').read_text(encoding='utf-8'))
template = Template((ROOT / 'templates/page.html').read_text(encoding='utf-8'))
image_manifest = ROOT / 'assets/images/optimized/manifest.json'
image_assets = json.loads(image_manifest.read_text(encoding='utf-8'))['assets'] if image_manifest.exists() else {}
e = escape

def display_image(url):
    """Use a prepared asset only while its source is unchanged."""
    asset = image_assets.get(url)
    if asset and (ROOT / asset['path'].lstrip('/')).exists():
        if hashlib.sha256((ROOT / url.lstrip('/')).read_bytes()).hexdigest() == asset['source_sha256']:
            return asset
    return {'path': url}

def progressive_image(url, alt, width, height, *, portrait=False):
    asset = display_image(url)
    preview = (f'<img class="image-preview" src="{asset["preview"]}" alt="" aria-hidden="true" '
               f'width="{width}" height="{height}">') if asset.get('preview') else ''
    priority = 'fetchpriority="high"' if portrait else 'loading="lazy"'
    image = (f'<img class="image-full" src="{e(asset["path"])}" alt="{e(alt)}" '
             f'width="{width}" height="{height}" {priority} decoding="async">')
    return f'<span class="progressive-image">{preview}{image}</span>'

def link(item, cls=''):
    url = item['url']
    if not url.startswith(('https://', 'mailto:', '/', '#')):
        raise ValueError(f'Unsupported link URL: {url}')
    external = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    return f'<a href="{e(url)}" class="{cls}"{external}>{e(item["label"])}</a>'

def link_icon(cls='section-link-icon', size=19):
    return f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M15 3h6v6M10 14 21 3"/><path d="M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"/></svg>'

def profile_link(item):
    paths = {
        'Email': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
        'Google Scholar': '<path d="m2 9 10-6 10 6-10 6-10-6Zm4 3v6c3 3 9 3 12 0v-6M22 9v8"/>',
        'CV': '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-6-6Zm0 0v6h6M8 13h8M8 17h6"/>',
        'LinkedIn': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 10v7M11 17v-7M11 13a3 3 0 0 1 6 0v4"/><circle cx="7" cy="7" r=".7" fill="currentColor" stroke="none"/>',
    }
    shape = paths.get(item['label'], '')
    icon = f'<svg class="profile-link-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{shape}</svg>' if shape else ''
    return link(item).replace(e(item['label']) + '</a>', icon + '<span>' + e(item['label']) + '</span></a>')

def render_news(items):
    if not items:
        return ''
    entries = []
    for item in sorted(items, key=lambda item: item['date'], reverse=True):
        month = date.fromisoformat(item['date'] + '-01')
        label = month.strftime('%b %Y')
        text = e(item['text'])
        if item.get('link'):
            target = e(item['link']['label'])
            text = text.replace(target, link(item['link']), 1)
        entries.append(f'<li><time datetime="{e(item["date"])}">{label}</time><p>{text}</p></li>')
    body = '<ul class="news-list" role="list">' + ''.join(entries[:3]) + '</ul>'
    if len(entries) > 3:
        chevron = '<svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 7.5 5 5 5-5"/></svg>'
        body += '<details class="news-archive"><summary><span class="news-show-more">Show more</span><span class="news-show-less">Show less</span>' + chevron + '</summary><ul class="news-list" role="list">' + ''.join(entries[3:]) + '</ul></details>'
    return '<section class="extra-section news-section" id="news" aria-labelledby="news-title"><h2 id="news-title">News</h2>' + body + '</section>'

def render_paper(p):
    authors = []
    for a in p['authors']:
        name = e(a['name'])
        if a.get('self'):
            name = f'<strong>{name}</strong>'
        if a.get('equal'):
            name += '<sup aria-label="equal contribution">*</sup>'
        authors.append(name)
    author_text = ', '.join(authors[:-1]) + ', &amp; ' + authors[-1] if len(authors) > 2 else ' &amp; '.join(authors)
    title = e(p['title'])
    if p['links']:
        beginning, separator, last_word = p['title'].rpartition(' ')
        label = e(beginning + separator) + f'<span class="paper-title-tail">{e(last_word)}{link_icon("paper-title-icon", 14)}</span>'
        title = link({'url': p['links'][0]['url'], 'label': p['title']}).replace(e(p['title']) + '</a>', label + '</a>')
    links = ''.join(link(x, 'paper-link') for x in p['links'][1:])
    links = f'<div class="paper-links">{links}</div>' if links else ''
    year_class = ' forthcoming' if p['year'] == 'In press' else ''
    details = ', ' + e(p['details']) if p.get('details') else ''
    year = f'<div class="publication-year{year_class}">{e(p["year"])}</div>'
    visual = year
    classes = 'publication'
    if p.get('figures'):
        classes += ' has-thumbnail'
        thumbnails = []
        for figure_index, figure in enumerate(p['figures']):
            alt = e(figure['alt'])
            if figure.get('crop'):
                crop = ' '.join(str(v) for v in figure['crop'])
                x, y, w, h = figure['crop']
                clip_id = f'figure-clip-{p["id"]}-{figure_index}'
                clip = f'<defs><clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>'
                masks = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/>' for x, y, w, h in figure.get('mask_rects', []))
                asset = display_image(figure['thumbnail'])
                preview = (f'<image href="{asset["preview"]}" width="{figure["width"]}" height="{figure["height"]}" aria-hidden="true"/>') if asset.get('preview') else ''
                img = f'<svg viewBox="{crop}" width="180" height="108" role="img" aria-label="{alt}">{clip}<g clip-path="url(#{clip_id})">{preview}<image href="{e(asset["path"])}" width="{figure["width"]}" height="{figure["height"]}"/>{masks}</g></svg>'
            else:
                img = progressive_image(figure['thumbnail'], figure['alt'], figure['width'], figure['height'])
            if p['links']:
                thumbnails.append(f'<a class="publication-thumbnail figure-link" href="{e(p["links"][0]["url"])}" target="_blank" rel="noopener noreferrer" aria-label="Read paper: {e(p["title"])}">{img}</a>')
            else:
                thumbnails.append(f'<div class="publication-thumbnail">{img}</div>')
        multi = ' multi' if len(thumbnails) > 1 else ''
        visual = f'<div class="publication-visual"><div class="publication-figures{multi}">{"".join(thumbnails)}</div></div>'
    elif p.get('image'):
        classes += ' has-thumbnail'
        visual = f'<div class="publication-visual"><img src="{e(p["image"])}" alt="{e(p.get("image_alt", p["title"]))}" width="120" height="80" loading="lazy"></div>'
    has_thumbnail = bool(p.get('figures') or p.get('image'))
    article = f'''<article>{year if has_thumbnail else ''}<h3>{title}</h3><p class="authors">{author_text}</p>
        <p class="venue"><cite>{e(p['venue'])}</cite>{details}</p>{links}</article>'''
    content = article + visual if has_thumbnail else visual + article
    return f'<li class="{classes}" id="{e(p["id"])}">{content}</li>'

def render_extra(s):
    if not re.fullmatch(r'[a-z][a-z0-9-]*', s['id']):
        raise ValueError('Section IDs must use lowercase letters, numbers and hyphens')
    if s.get('style') == 'section-link':
        heading = link({'url': s['url'], 'label': s['title']}, 'section-heading-link')
        icon = link_icon()
        heading = heading.replace(e(s['title']) + '</a>', f'<span class="section-link-label">{e(s["title"])}</span>{icon}</a>')
        return f'<section class="extra-section link-section" id="{s["id"]}" aria-labelledby="{s["id"]}-title"><h2 id="{s["id"]}-title">{heading}</h2></section>'
    body = ''
    for index, paragraph in enumerate(s.get('paragraphs', [])):
        inline = ''
        if index == 0 and s.get('inline_icons'):
            icons = ''.join(f'<span role="img" aria-label="{e(i["label"])}" title="{e(i["label"])}">{e(i["symbol"])}</span>' for i in s['inline_icons'])
            inline = f' <span class="inline-interest-icons">{icons}</span>'
        text = e(paragraph)
        for icon in s.get('activity_icons', []):
            marker = e(icon['after'])
            symbol = f'<span class="activity-icon" aria-hidden="true">{e(icon["symbol"])}</span>'
            text = text.replace(marker, marker + '&nbsp;' + symbol, 1)
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
    elif s.get('style') == 'education':
        entries = []
        for item in s['items']:
            details = f'<p>{e(item["institution"])} <span class="education-location">({e(item["location"])})</span></p>'
            if item.get('thesis'):
                details += f'<p>Thesis: <cite>{e(item["thesis"])}</cite></p>'
            if item.get('advisors'):
                advisors = '; '.join(e(a['role']) + ': ' + link({'url': a['url'], 'label': a['name']}) + ' (' + e(a['affiliation']) + ')' for a in item['advisors'])
                details += f'<p>{advisors}</p>'
            if item.get('projects'):
                projects = ''.join('<li>' + (link({'url': project['url'], 'label': project['title']}).replace('</a>', link_icon('education-project-icon', 11) + '</a>') if project.get('url') else e(project['title'])) + '</li>' for project in item['projects'])
                details += '<ul class="education-projects" aria-label="Undergraduate research and projects">' + projects + '</ul>'
            entries.append(f'<li class="education-entry"><div class="education-heading"><h3>{e(item["degree"])}</h3><span class="education-date">{e(item["date"])}</span></div>{details}</li>')
        body += '<ul class="education-list" role="list">' + ''.join(entries) + '</ul>'
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
                text = re.sub(r'(\([^()]*\bAward\))', r'<strong class="presentation-award">\1</strong>', text)
                entries.append(f'<li>{text}</li>')
            year_id = f'{section["id"]}-{year}'
            groups.append(f'<section class="presentation-year-group" aria-labelledby="{year_id}"><h3 id="{year_id}">{year}</h3><ul role="list">{"".join(entries)}</ul></section>')
        sections.append(f'<section class="presentation-section" aria-labelledby="{e(section["id"])}"><h2 id="{e(section["id"])}">{e(section["title"])}</h2>{"".join(groups)}</section>')
    return '<div class="presentations-page"><h1>Presentations</h1>' + ''.join(sections) + '</div>'

def page(main, title, path='/'):
    sharing = site.get('sharing_image') or {'path': site['portrait'], 'alt': site['name']}
    sharing_size_meta = '\n  '.join(f'<meta property="og:image:{dimension}" content="{int(sharing[dimension])}">' for dimension in ('width', 'height') if dimension in sharing)
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
       sharing_size_meta=sharing_size_meta,
       sharing_card='summary_large_image' if site.get('sharing_image') else 'summary',
       name=e(site['name']), email=e(site['email']),
       navigation=''.join(link(x).replace('<a ', '<a aria-current="page" ', 1) if x['url'] == path else link(x) for x in site['navigation']), main=main,
       structured_data=json.dumps(structured, ensure_ascii=False).replace('<', '\\u003c'), analytics=analytics,
       css_hash=hashlib.sha256((ROOT/'assets/site.css').read_bytes()).hexdigest()[:10],
       favicon_hash=hashlib.sha256((ROOT/'assets/favicon.svg').read_bytes()).hexdigest()[:10])

bio = ''.join(f'<p>{e(p)}</p>' for p in site['bio'])
interests = ''
if site.get('research_interests'):
    items = ''.join(f'<li><strong>{e(i["title"])}</strong><span>{e(i["description"])}</span></li>' for i in site['research_interests'])
    schematic = site.get('research_schematic')
    visual = ''
    if schematic:
        visual = (f'<figure class="research-schematic"><a class="research-schematic-link" href="{e(schematic["path"])}" '
                  'target="_blank" rel="noopener noreferrer" aria-label="View research schematic at full size">'
                  + progressive_image(schematic['path'], schematic['alt'], schematic['width'], schematic['height'])
                  + '</a></figure>')
    interests = f'<section class="research-interests" aria-labelledby="research-interests-title"><h2 id="research-interests-title">Research interests</h2><div class="research-interests-layout"><ul>{items}</ul>{visual}</div></section>'
social = ''.join(profile_link(x) for x in site['links'])
scholar = next(x for x in site['links'] if x['label'] == 'Google Scholar')
cv = next(x for x in site['links'] if x['label'] == 'CV')
main = f'''<section class="profile" id="about" aria-labelledby="profile-name">
  <div class="profile-copy"><div class="identity"><h1 id="profile-name">{e(site['name'])}</h1>
    <p class="role">{e(site['role'])}</p><p class="affiliation">{e(site['department'])}<br>{e(site['institution'])}</p></div>
    <div class="bio">{bio}</div>
  </div><div class="profile-aside"><figure class="portrait">{progressive_image(site['portrait'], site['name'], 842, 1178, portrait=True)}</figure>
    <div class="profile-links" aria-label="Contact and profiles">{social}</div></div>
</section>
{interests}
{render_news(news)}
<section class="publications" id="publications" aria-labelledby="publications-title">
  <div class="section-heading"><h2 id="publications-title">{e(site['publications_heading'])}</h2><div class="section-heading-meta"><p class="contribution-note">* Equal contribution.</p></div></div>
  <ol class="publications-list">{''.join(render_paper(p) for p in papers)}</ol>
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
