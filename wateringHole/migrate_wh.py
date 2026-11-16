#!/usr/bin/env python3
import os, re, glob

CSS_FILE = "/opt/Gaia/static/gaia.css"
with open(CSS_FILE, 'r') as f:
    CSS = f.read()

NAV = '<nav class="gaia-nav"><div class="gaia-nav-inner">'
NAV += '<a href="https://primals.eco" class="gaia-nav-brand">gaia</a>'
NAV += '<a href="https://primals.eco/#organism">Organism</a>'
NAV += '<a href="https://primals.eco/#investigation">Investigation</a>'
NAV += '<a href="https://primals.eco/#knowledge">Knowledge</a>'
NAV += '<a href="https://primals.eco/#infrastructure">Infrastructure</a>'
NAV += '</div></nav>'

FOOTER = '<footer class="gaia-footer"><div class="gaia-shell">'
FOOTER += '<div class="gaia-footer-bottom">'
FOOTER += '<p><a href="https://primals.eco">Gaia</a> &mdash; sovereign living digital organism</p>'
FOOTER += '</div></div></footer>'

def extract_title(html):
    m = re.search(r'<title>([^<]+)</title>', html, re.I)
    return m.group(1).strip() if m else 'Gaia'

def extract_body(html):
    m = re.search(r'<body[^>]*>(.*?)</body>', html, re.S | re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r'</head>(.*)', html, re.S | re.I)
    if m:
        return m.group(1).strip()
    return html.strip()

count = 0
for base in ['/opt/Gaia/wateringHole/tuebor-flat',
             '/opt/Gaia/wateringHole/clutch-flat',
             '/opt/Gaia/wateringHole/lansing-flat']:
    for root, dirs, files in os.walk(base):
        for fname in files:
            if not fname.endswith('.html'):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                html = f.read()
            if 'gaia-nav' in html:
                continue
            title = extract_title(html)
            body = extract_body(html)
            
            new_html = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            new_html += '<meta charset="utf-8">\n'
            new_html += '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            new_html += '<title>' + title + '</title>\n'
            new_html += '<style>\n' + CSS + '\n</style>\n'
            new_html += '</head>\n<body>\n'
            new_html += NAV + '\n'
            new_html += '<main class="gaia-shell" style="padding-top:24px;padding-bottom:48px">\n'
            new_html += body + '\n'
            new_html += '</main>\n'
            new_html += FOOTER + '\n'
            new_html += '</body>\n</html>'
            
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            count += 1

print(f'Migrated {count} wateringHole HTML files to unified face')
