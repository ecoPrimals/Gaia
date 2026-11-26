#!/usr/bin/env python3
"""library_build.py - make the file the library page (static/alexandria.html, served at /library) reads.

  static/alexandria-catalog.json   the card catalog: every work of the library, one row, with where to read it

The cards come from the library's own catalog (gardens/alexandria/catalog.json, made by its tools/catalog.py).
This tool adds one thing: the address where each work can be READ. A work is linked to a live page only when
that site's own list of pages has it; otherwise it is linked to its source. Nothing is asked of the live sites
except their sitemaps, and no address is made up.

Run:
  python tools/library_build.py --catalog gardens/alexandria/catalog.json
                                [--pages defendDetroit/publicRecord=<file>] [--pages ecoPrimals/sporePrint=<file>]

  --pages <site>=<file>   that site's pages, one path per line ("science/01-anderson-qs"), instead of its sitemap
                          (for a site whose sitemap is short or cannot be reached).
  --sample N              ask N live addresses (spread over the sites) whether they answer, and report.
  --all                   ask every live address the catalog gives, and fail if one does not answer.

The same file is the agents' face of the library: it says how to read itself in "how".
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Where each site is read, and where its own list of pages is published. Each list is asked of the same
# address the works are read at, so a work is never linked to a page its site does not have.
SITES = {
    'ecoPrimals/sporePrint': {'live': 'https://sporeprint.primals.eco/', 'sitemap': 'https://sporeprint.primals.eco/sitemap.xml'},
    'amicusContra/tuebor': {'live': 'https://amicuscontra.github.io/tuebor/', 'sitemap': 'https://amicuscontra.github.io/tuebor/sitemap.xml'},
    'amicusContra/lansing': {'live': 'https://amicuscontra.github.io/lansing/', 'sitemap': 'https://amicuscontra.github.io/lansing/sitemap.xml'},
    'defendDetroit/publicRecord': {'live': 'https://detroit.primals.eco/', 'sitemap': 'https://detroit.primals.eco/sitemap.xml'},
}
COLUMNS = ['title', 'site', 'path', 'live', 'also', 'class', 'also_class', 'kind', 'place', 'place_by', 'organ', 'words', 'date']
HOW = ('Each row follows "columns". site is a number into "sites". A work is read at sites[site].live + live (an empty '
       'live is the site\'s front page); when live is null the work is not on a live site yet, so read its source. The source of every work is '
       'sites[site].source + path. also lists other sites that publish the same page, at sites[n].live + live. '
       'class and also_class are keys of "classes" (Dewey numbers); place is a key of "places", and place_by says how '
       'the place was decided. organ is soul (the science) or heart (the hardware and the Lansing Scuffle) or empty. '
       'For people the same catalog is the page at "page"; a place on the globe is at places[place].atlas.')


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': 'library_build'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def slug(path):
    """The page's path on its site, as Zola makes it from the file's path: lower case, every run of other
    characters one hyphen. A section's _index is the section itself."""
    key = path[:-3] if path.endswith('.md') else path
    if key == '_index' or key.endswith('/_index'):
        key = key[:-6].rstrip('/')
    return '/'.join(re.sub(r'[^a-z0-9]+', '-', part.lower()).strip('-') for part in key.split('/') if part)


def pages_of(label, given):
    """The set of page paths a site says it has."""
    if label in given:
        raw = open(given[label], 'rb').read()
        text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8', 'replace')
        out = set()
        for line in text.splitlines():
            p = line.strip().replace('\\', '/')
            p = re.sub(r'^\./', '', p)
            p = re.sub(r'(^|/)index\.html$', '', p).strip('/')
            out.add(p)
        return out, 'the list given (%s)' % os.path.basename(given[label])
    site = SITES[label]
    _, body = get(site['sitemap'])
    locs = re.findall(r'<loc>\s*(.*?)\s*</loc>', body.decode('utf-8', 'replace'))
    return {l[len(site['live']):].strip('/') for l in locs if l.startswith(site['live'])}, 'its sitemap'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', required=True)
    ap.add_argument('--pages', action='append', default=[], help='site=file with that site\'s page paths, one per line')
    ap.add_argument('--sample', type=int, default=0)
    ap.add_argument('--all', action='store_true', help='ask every live address the catalog gives')
    a = ap.parse_args()
    given = dict(p.split('=', 1) for p in a.pages)
    folder = os.path.dirname(os.path.abspath(a.catalog))
    with open(a.catalog, encoding='utf-8') as f: catalog = json.load(f)
    with open(os.path.join(folder, 'dewey.json'), encoding='utf-8') as f: dewey = json.load(f)
    with open(os.path.join(folder, 'places.json'), encoding='utf-8') as f: where = json.load(f)
    cards = catalog['cards']

    labels = list(catalog['sources'])
    for label in labels:
        if label not in SITES: sys.exit('no live address is known for %s: add it to SITES' % label)
    pages = {}
    for label in labels:
        pages[label], how = pages_of(label, given)
        print('%-28s %5d pages, from %s' % (label, len(pages[label]), how))

    sites = []
    for label in labels:
        first = next((c for c in cards if c['source'] == label), None)
        # a card's url is the source file; the site's source base is that url without the file's own path
        source = first['url'][:-len(first['path'])] if first else 'https://github.com/%s/' % label
        sites.append({'name': label, 'live': SITES[label]['live'], 'source': source, 'nucleus': label == catalog.get('centre'), 'works': 0, 'live_works': 0})
    index = {label: i for i, label in enumerate(labels)}

    rows, no_live, shelf = [], [], {}
    for c in cards:
        i = index[c['source']]
        key = slug(c['path'])
        if c.get('slug'):   # the page names its own last step on the site
            key = '/'.join(key.split('/')[:-1] + [slug(c['slug'])])
        live = (key + '/' if key else '') if key in pages[c['source']] else None
        if live is None: no_live.append(c['source'] + ':' + c['path'])
        also = [index[o] for o in c.get('also_in', []) if o in index and key in pages[o]]
        sites[i]['works'] += 1
        sites[i]['live_works'] += live is not None
        for o in also: sites[o]['live_works'] += 1
        shelf[c['place']] = shelf.get(c['place'], 0) + 1
        rows.append([c['title'], i, c['path'], live, also if live is not None else [], c['class'], c.get('also_class') or '',
                     c['kind'], c['place'], c.get('place_by') or '', c.get('organ') or '', c.get('words') or 0, c.get('date') or ''])

    places = {}
    for key, n in sorted(shelf.items(), key=lambda kv: -kv[1]):
        p = where[key]
        places[key] = {'name': p['name'], 'lat': p['lat'], 'lon': p['lon'], 'works': n,
                       'atlas': '/atlas#pin=shelf-' + key if p['lat'] is not None else ''}
    used = sorted({r[5] for r in rows} | {r[6] for r in rows if r[6]})
    out = {'what': 'The card catalog of the library (Alexandria): every work, one row each, with where to read it.',
           'made': datetime.date.today().isoformat(), 'works': len(rows), 'page': '/library', 'how': HOW, 'columns': COLUMNS,
           'sites': sites, 'classes': {code: dewey[code] for code in used}, 'places': places, 'organs': catalog.get('organs', {}),
           'kinds': sorted({r[7] for r in rows}), 'rows': rows}
    path = os.path.join(REPO, 'static', 'alexandria-catalog.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print('works: %d   with a live page: %d   source only: %d   also on another site: %d   %d KB' % (
        len(rows), len(rows) - len(no_live), len(no_live), sum(1 for r in rows if r[4]), os.path.getsize(path) // 1024))
    print('shelves: ' + ', '.join('%s %d' % (k, v['works']) for k, v in places.items()))
    for s in sites: print('   %-28s works %4d   pages live there %4d   %s' % (s['name'], s['works'], s['live_works'], s['live']))
    if no_live:
        print('source only (no live page listed):')
        for x in no_live: print('   ' + x)

    if a.sample or a.all:
        import random
        import time
        import urllib.error
        rnd, bad = random.Random(7), []
        picks = []
        for i, s in enumerate(sites):
            mine = [r for r in rows if (r[1] == i and r[3] is not None) or i in r[4]]
            if not a.all: mine = rnd.sample(mine, min(len(mine), max(1, a.sample // len(sites))))
            picks += [(s['live'] + r[3], r[0]) for r in mine]
        for n, (url, title) in enumerate(picks):
            status = None
            for attempt in range(4):
                try: status = get(url, 30)[0]
                except urllib.error.HTTPError as e:
                    status = e.code
                    if e.code == 429:                      # the house asks a fast reader to wait: wait, and ask again
                        time.sleep(min(30, int(e.headers.get('Retry-After') or 4) + 1)); continue
                except Exception as e: status = str(e)[:60]
                break
            if status != 200: bad.append((status, url))
            if not a.all: print('   %s  %s' % (status, url))
            elif n and n % 250 == 0: print('   ... %d asked, %d did not answer' % (n, len(bad)))
        for status, url in bad[:40]: print('   NO ANSWER  %s  %s' % (status, url))
        print('%s: %d asked, %d did not answer 200' % ('every live address' if a.all else 'sample', len(picks), len(bad)))
        if bad: sys.exit(1)


if __name__ == '__main__':
    main()
