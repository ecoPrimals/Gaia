#!/usr/bin/env python3
"""sitemap_build.py - write a built site's sitemap.xml from the pages that are really in its folder.

Zola lists only the pages it rendered from content. A site that also carries generated pages (the Detroit
record: people, entities, connections, tags) ends up with a sitemap that names a fraction of itself, and a
search engine is never told about the rest. This reads the built folder and lists every page in it.

  python tools/sitemap_build.py --root <site>/public --base https://detroit.primals.eco/

A page is a folder with an index.html (listed as base/folder/), or an .html file at the top of the site.
Left out: 404.html, a page that is only a redirect, and a page that asks not to be indexed. Each page is
dated by its file. --keep <file> copies the old sitemap somewhere first; --dry only counts.
Run it again after the site is built: a build puts the short sitemap back.
"""
import argparse
import datetime
import os
import re
import sys
import urllib.parse
from xml.sax.saxutils import escape

SKIP = re.compile(rb'http-equiv=["\']?refresh|<meta[^>]+name=["\']robots["\'][^>]+noindex', re.I)


def pages(root):
    """(path on the site, file) for every page in the built folder, front page first."""
    out = []
    for folder, dirs, files in os.walk(root):
        dirs.sort()
        rel = os.path.relpath(folder, root).replace(os.sep, '/')
        if 'index.html' in files:
            out.append(('' if rel == '.' else rel + '/', os.path.join(folder, 'index.html')))
        if rel == '.':
            out += [(f, os.path.join(folder, f)) for f in sorted(files) if f.endswith('.html') and f not in ('index.html', '404.html')]
    return out


def build(root, base):
    """(xml text, pages listed, pages left out) for the built folder at root, addressed under base."""
    base = base.rstrip('/') + '/'
    rows, left = [], []
    for path, file in pages(root):
        with open(file, 'rb') as f:
            head = f.read(4096)
        if SKIP.search(head):
            left.append(path)
            continue
        day = datetime.datetime.fromtimestamp(os.path.getmtime(file), datetime.timezone.utc).strftime('%Y-%m-%d')
        rows.append((base + urllib.parse.quote(path, safe='/'), day))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += ['<url><loc>%s</loc><lastmod>%s</lastmod></url>' % (escape(u), d) for u, d in rows]
    xml.append('</urlset>')
    return '\n'.join(xml) + '\n', rows, left


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True, help='the built site folder (Zola: public)')
    ap.add_argument('--base', required=True, help='the address the site is read at, e.g. https://detroit.primals.eco/')
    ap.add_argument('--out', help='where to write (default: <root>/sitemap.xml)')
    ap.add_argument('--dry', action='store_true', help='count only, write nothing')
    ap.add_argument('--keep', help='copy the old sitemap to this file first (somewhere outside the served folder)')
    a = ap.parse_args()
    root = os.path.realpath(a.root)
    if not os.path.isfile(os.path.join(root, 'index.html')):
        sys.exit('%s has no index.html: not a built site' % root)
    xml, rows, left = build(root, a.base)
    out = a.out or os.path.join(root, 'sitemap.xml')
    old = 0
    if os.path.isfile(out):
        with open(out, encoding='utf-8', errors='replace') as f:
            old = len(re.findall(r'<loc>', f.read()))
    tops = {}
    for u, _ in rows:
        top = u[len(a.base.rstrip('/')) + 1:].split('/')[0] or '(front page)'
        tops[top] = tops.get(top, 0) + 1
    print('pages in the folder: %d   listed: %d   left out (redirect or noindex): %d   the sitemap had: %d' % (len(rows) + len(left), len(rows), len(left), old))
    print('by section: ' + ', '.join('%s %d' % kv for kv in sorted(tops.items(), key=lambda kv: -kv[1])))
    if len(rows) > 50000:
        sys.exit('more than 50,000 pages: one sitemap file cannot hold them')
    if a.dry:
        return
    if old and a.keep:
        with open(out, 'rb') as f, open(a.keep, 'wb') as g:
            g.write(f.read())
        print('the old sitemap is kept at %s' % a.keep)
    tmp = out + '.new'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(xml)
    os.replace(tmp, out)
    print('wrote %s (%d KB)' % (out, os.path.getsize(out) // 1024))


if __name__ == '__main__':
    main()
