#!/usr/bin/env python3
import os, re, glob, shutil

STATIC_DIR = "/opt/Gaia/static"
BACKUP_DIR = "/opt/Gaia/static/_backup_pre_unified"
CSS_FILE = "/opt/Gaia/static/gaia.css"

with open(CSS_FILE, 'r') as f:
    CSS = f.read()

REPLACEMENTS = [
    ('gAIa', 'Gaia'),
    ('golgiBody', 'organism'),
    ('golgi layer', 'organism layer'),
    ('157.230.3.183', '(retired)'),
]

NAV = '<nav class="gaia-nav"><div class="gaia-nav-inner">'
NAV += '<a href="/" class="gaia-nav-brand">gaia</a>'
NAV += '<a href="/#organism">Organism</a>'
NAV += '<a href="/#investigation">Investigation</a>'
NAV += '<a href="/#knowledge">Knowledge</a>'
NAV += '<a href="/#infrastructure">Infrastructure</a>'
NAV += '<a href="https://nestgate.io">NestGate</a>'
NAV += '</div></nav>'

FOOTER = '<footer class="gaia-footer"><div class="gaia-shell">'
FOOTER += '<div class="gaia-footer-bottom">'
FOOTER += '<p><a href="/">Gaia</a> &mdash; sovereign living digital organism &mdash; '
FOOTER += '<a href="https://primals.eco">primals.eco</a></p>'
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

def has_unified(html):
    return 'gaia-nav' in html and 'gaia-footer' in html

def clean_patterns(text):
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text

def migrate_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
    
    if has_unified(html):
        return 'SKIP-UNIFIED'
    if len(html) < 50:
        return 'SKIP-SMALL'
    
    title = clean_patterns(extract_title(html))
    body = clean_patterns(extract_body(html))
    body = re.sub(r'<script[^>]*piGut[^>]*></script>', '', body)
    
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
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    return 'MIGRATED'

os.makedirs(BACKUP_DIR, exist_ok=True)

files = sorted(glob.glob(os.path.join(STATIC_DIR, '*.html')))
migrated = skipped = errors = 0

for filepath in files:
    fname = os.path.basename(filepath)
    if fname.startswith('_') or fname == 'primals-old.html' or fname == 'primals-v2.html':
        continue
    
    backup_path = os.path.join(BACKUP_DIR, fname)
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
    
    try:
        result = migrate_file(filepath)
        if result == 'MIGRATED':
            migrated += 1
        else:
            skipped += 1
        print(f'{fname:35} {result}')
    except Exception as e:
        errors += 1
        print(f'{fname:35} ERROR: {e}')

print(f'\nTOTAL: {migrated} migrated, {skipped} skipped, {errors} errors')
