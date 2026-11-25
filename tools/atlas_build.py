#!/usr/bin/env python3
"""atlas_build.py - make the two files the atlas page (static/atlas.html) reads.

  static/atlas-earth.json   coastlines, lakes and borders, as lines to draw on a globe
  static/atlas-pins.json    the stories, pinned above the places they are about

Nothing here is written by hand except the PLACES table below: a short list of PUBLIC buildings and offices
(a law firm's office, a state department, a court, a school) with where each stands. Everything said about a
place comes from the published pages themselves - their titles, their own description line, and a count of how
many pages name the place. Every link goes to a page that is already public.

Two rules for the table:
  - no homes. A person, or an organisation registered at somebody's house, is pinned at the public building it
    is tied to in the pages (the school, the court, the hall), never at a residence.
  - places are good to about a kilometre. They were set from the street address or the town, not surveyed.

Run (the three inputs are checkouts that already exist on this gate):
  python tools/atlas_build.py --earth <folder of Natural Earth geojson> --tuebor <tuebor>/site/content
                              --catalog gardens/alexandria/catalog.json [--check]
  --check asks the live site for every link once and reports the ones that do not answer.

Natural Earth is public domain (naturalearthdata.com). Only the outlines are kept, thinned to what a globe needs.
"""
import argparse
import collections
import concurrent.futures
import datetime
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LIVE = 'https://amicuscontra.github.io/tuebor'
LAKES_BOX = (-93.0, 41.0, -75.0, 50.0)          # the Great Lakes: taken from the finer map so Michigan has its shape

# id, name, where it stands, lat, lon, kind, the words that name it in a page, its own pages (first = the card)
PLACES = [
    # Lansing
    ('dykema', 'Dykema — Lansing office', 'Capitol View, 201 Townsend St, Lansing', 42.7323, -84.5540, 'law',
     r'dykema', ['network/entities/dykema', 'network/entities/dykema-gossett-federal-pac', 'braid/dykema-pac']),
    ('mde', 'Michigan Department of Education', 'Hannah Building, 608 W Allegan St, Lansing', 42.7318, -84.5606, 'state',
     r'michigan department of education|\bMDE\b|state board of education',
     ['network/entities/michigan-department-of-education', 'network/entities/michigan-state-board-of-education']),
    ('ag', 'Michigan Attorney General', 'Williams Building, 525 W Ottawa St, Lansing', 42.7343, -84.5597, 'state',
     r'attorney general|\bnessel\b', ['network/institutional/ag-office']),
    ('statebar', 'State Bar of Michigan', '306 Townsend St, Lansing', 42.7302, -84.5541, 'law',
     r'state bar of michigan|state bar upl|\bSBM\b', ['network/entities/state-bar-of-michigan', 'network/entities/state-bar-upl']),
    ('msc', 'Michigan Supreme Court', 'Hall of Justice, 925 W Ottawa St, Lansing', 42.7339, -84.5652, 'court',
     r'michigan supreme court', ['network/entities/michigan-supreme-court']),
    ('msulaw', 'MSU College of Law', 'East Lansing', 42.7262, -84.4736, 'school',
     r'msu college of law|michigan state university college of law', ['network/institutional/msu-college-of-law']),
    # Detroit
    ('canfield', '10101 E. Canfield — Purpose Charter Academy and the Banks organisations', '10101 E Canfield St, Detroit', 42.3810, -82.9900, 'school',
     r'purpose charter|purpose group|purpose foundation|banks strategy|canfield|city hill church|sun community development|serenity guardianship|save detroit jobs|inner link graphics',
     ['network/actors/brian-banks', 'network/entities/purpose-charter-academy', 'network/entities/purpose-group-llc',
      'network/entities/purpose-foundation', 'network/entities/banks-strategy-llc', 'network/entities/city-hill-church',
      'network/entities/sun-community-development', 'network/entities/serenity-guardianship', 'network/entities/save-detroit-jobs',
      'network/entities/inner-link-graphics', 'analysis/land-deal', 'analysis/corporate-network-lara']),
    ('macdowell', 'MacDowell Preparatory Academy', '4201 W Outer Drive, Detroit', 42.4215, -83.1590, 'school',
     r'macdowell', ['network/entities/macdowell-prep', 'network/entities/macdowell']),
    ('dpscd', 'Detroit Public Schools Community District', 'Fisher Building, 3011 W Grand Blvd, Detroit', 42.3694, -83.0771, 'school',
     r'\bDPSCD\b|detroit public schools', ['network/entities/detroit-public-schools-community-district']),
    ('court3', 'Third Circuit Court and the City of Detroit', 'Coleman A. Young Municipal Center, 2 Woodward Ave, Detroit', 42.3295, -83.0437, 'court',
     r'third circuit|3rd circuit|wayne county circuit', ['network/institutional/court-3rd', 'network/entities/city-of-detroit', 'network/entities/wayne-county']),
    ('court36', '36th District Court', '421 Madison St, Detroit', 42.3359, -83.0432, 'court',
     r'36th district', ['network/institutional/court-36th']),
    ('jtc', 'Judicial Tenure Commission', 'Cadillac Place, 3034 W Grand Blvd, Detroit', 42.3688, -83.0757, 'court',
     r'judicial tenure', ['network/entities/judicial-tenure-commission']),
    ('wsulaw', 'Wayne State University Law School', '471 W Palmer Ave, Detroit', 42.3601, -83.0700, 'school',
     r'wayne state', ['network/entities/wayne-state-university-law-school']),
    ('marygrove', 'Marygrove Conservancy', '8425 W McNichols Rd, Detroit', 42.4165, -83.1560, 'school',
     r'marygrove', ['network/entities/marygrove-conservancy']),
    ('martin', 'Roland S. Martin — where the pages meet him in Michigan', 'Detroit, June 2025 (the pages name the NAACP Detroit dinner)', 42.3276, -83.0500, 'media',
     r'roland (s\. )?martin|black star network|nu ?vision media|school choice is the black choice',
     ['network/actors/roland-s-martin', 'evidence/the-money-flows-through-nulls', 'network/entities/school-choice-is-the-black-choice-tour',
      'analysis/antithesis-what-if-we-are-the-pattern']),
    # the rest of Michigan
    ('cmu', 'Central Michigan University — the authorizer', 'Mount Pleasant', 43.5912, -84.7745, 'school',
     r'central michigan university|\bCMU\b', ['network/entities/central-michigan-university']),
    ('agc', 'Attorney Grievance Commission', 'PNC Center, 755 W Big Beaver Rd, Troy', 42.5618, -83.1575, 'law',
     r'attorney grievance|\bAGC\b', ['network/entities/attorney-grievance-commission']),
    ('wresa', 'Wayne RESA', '33500 Van Born Rd, Wayne', 42.2640, -83.3716, 'school',
     r'wayne resa', ['network/entities/wayne-resa', 'network/entities/wayne-resa-financial-oversight']),
    ('plante', 'Plante Moran', 'Southfield', 42.4780, -83.2440, 'money',
     r'plante', ['network/entities/plante-moran']),
    ('mackinac', 'Mackinac Center for Public Policy', 'Midland', 43.6145, -84.2440, 'money',
     r'mackinac center', ['network/entities/mackinac-center-for-public-policy']),
    ('devos', 'DeVos family foundations', 'Grand Rapids', 42.9655, -85.6710, 'money',
     r'devos', ['network/entities/devos-foundation', 'network/entities/dick-betsy-devos-family-foundation', 'network/entities/amway']),
    # beyond Michigan
    ('used', 'U.S. Department of Education', '400 Maryland Ave SW, Washington DC', 38.8860, -77.0190, 'state',
     r'u\.?s\.? (department|dept\.?) of education', ['network/entities/us-dept-of-education']),
    ('walton', 'Walton Family Foundation', 'Bentonville, Arkansas', 36.3724, -94.2102, 'money',
     r'walton', ['network/entities/walton-family-foundation', 'evidence/the-money-flows-through-nulls']),
    ('meta', 'Meta — Facebook', 'Menlo Park, California', 37.4848, -122.1484, 'media',
     r'meta platforms|facebook|zuckerberg', ['analysis/meta-two-faces', 'analysis/bad-meta', 'analysis/meta-in-the-open']),
]

# the four places the library's own catalog sorts works into; the count and the works come from the catalog
SHELVES = {
    'library':  ('The Library — sporePrint, the heart and the soul', 'in HUD space above the Library of Congress, Washington DC', 'library'),
    'lansing':  ('Lansing — the Capitol and the Scuffle', 'above the Capitol, Lansing · Tuebor: I will defend', 'place'),
    'detroit':  ('Above Detroit — the Detroit network', 'above the city', 'place'),
    'michigan': ('Michigan, statewide', 'above the middle of the state', 'place'),
}


# ---------------------------------------------------------------- the earth

def rings(geom):
    t, c = geom['type'], geom['coordinates']
    if t == 'Polygon': return c
    if t == 'MultiPolygon': return [r for p in c for r in p]
    if t == 'LineString': return [c]
    if t == 'MultiLineString': return c
    return []


def bbox(ring):
    xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def meets(b, box):
    return not (b[2] < box[0] or b[0] > box[2] or b[3] < box[1] or b[1] > box[3])


def thin(ring, step):
    """Keep a point when it has moved at least `step` degrees from the last one kept; ends always kept."""
    out = [ring[0]]
    for p in ring[1:-1]:
        if abs(p[0] - out[-1][0]) >= step or abs(p[1] - out[-1][1]) >= step:
            out.append(p)
    out.append(ring[-1])
    return out


def pack(ring):
    flat = []
    for p in ring:
        flat += [round(p[0] * 100), round(p[1] * 100)]
    return flat


def load(folder, name):
    with open(os.path.join(folder, name + '.geojson'), encoding='utf-8') as f:
        return json.load(f)['features']


def build_earth(folder):
    land = [pack(r) for f in load(folder, 'ne_110m_land') for r in rings(f['geometry'])]
    lakes = []
    for f in load(folder, 'ne_110m_lakes'):
        for r in rings(f['geometry']):
            if not meets(bbox(r), LAKES_BOX): lakes.append(pack(r))
    for f in load(folder, 'ne_50m_lakes'):
        for r in rings(f['geometry']):
            if meets(bbox(r), LAKES_BOX) and len(r) > 12: lakes.append(pack(thin(r, 0.03)))
    states = [pack(r) for f in load(folder, 'ne_110m_admin_1_states_provinces_lines') for r in rings(f['geometry'])]
    borders = [pack(r) for f in load(folder, 'ne_110m_admin_0_boundary_lines_land') for r in rings(f['geometry'])]
    return {'note': 'Outlines from Natural Earth (public domain). Each line is lon,lat,lon,lat... in hundredths of a degree.',
            'land': land, 'lakes': lakes, 'states': states, 'borders': borders}


# ---------------------------------------------------------------- the pages

FRONT = re.compile(r'^\+\+\+\s*\n(.*?)\n?\+\+\+', re.S)


def read_pages(content):
    pages = {}
    for root, _, files in os.walk(content):
        for name in files:
            if not name.endswith('.md'): continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, content).replace(os.sep, '/')
            with open(full, encoding='utf-8', errors='replace') as f:
                text = f.read()
            m = FRONT.match(text)
            head = m.group(1) if m else ''
            body = text[m.end():] if m else text
            t = re.search(r'^title\s*=\s*"(.*?)"\s*$', head, re.M)
            d = re.search(r'^description\s*=\s*"(.*?)"\s*$', head, re.M)
            if re.search(r'^draft\s*=\s*true', head, re.M): continue
            key = rel[:-3]
            if key.endswith('/_index'): key = key[:-7]
            elif key == '_index': key = ''
            pages[key] = {'title': (t.group(1) if t else key.rsplit('/', 1)[-1]).replace('\\"', '"'),
                          'say': (d.group(1) if d else '').replace('\\"', '"'), 'body': body, 'index': name == '_index.md'}
    return pages


def url_of(key):
    return LIVE + '/' + (key + '/' if key else '')


def build_pins(content, catalog_path):
    pages = read_pages(content)
    pins, missing = [], []
    for pid, name, where, lat, lon, kind, words, own in PLACES:
        rx = re.compile(words, re.I)
        hits = []
        for key, p in pages.items():
            n = len(rx.findall(p['title'] + '\n' + p['body']))
            if n: hits.append((n, key))
        hits.sort(key=lambda h: (-h[0], h[1]))
        links, seen, say = [], set(), ''
        for key in own:
            if key not in pages: missing.append((pid, key)); continue
            # the first of its own pages whose description actually names the place speaks for it; otherwise nothing does
            if not say and len(pages[key]['say']) >= 30 and rx.search(pages[key]['say']):
                say = pages[key]['say']
            links.append([pages[key]['title'], url_of(key), 'card']); seen.add(key)
        for n, key in hits:
            if len(links) >= len([k for k in own if k in pages]) + 8: break
            if key in seen or pages[key]['index'] or key.startswith('network/'): continue
            links.append([pages[key]['title'], url_of(key), 'page']); seen.add(key)
        pins.append({'id': pid, 'name': name, 'where': where, 'lat': lat, 'lon': lon, 'kind': kind,
                     'say': say, 'n': len(hits), 'links': links})

    with open(catalog_path, encoding='utf-8') as f:
        catalog = json.load(f)
    with open(os.path.join(os.path.dirname(catalog_path), 'places.json'), encoding='utf-8') as f:
        where = json.load(f)
    cards = catalog['cards']
    for place, (name, stands, kind) in SHELVES.items():
        here = [c for c in cards if c.get('place') == place]
        here.sort(key=lambda c: -(c.get('words') or 0))
        if place == 'library':
            soul = [c for c in here if c.get('organ') == 'soul']; heart = [c for c in cards if c.get('organ') == 'heart']
            say = ('The nucleus: %d works of the soul (the science) and %d of the heart (the hardware and the Lansing Scuffle), '
                   'with %d more that belong to no one place. Open to everyone.' % (len(soul), len(heart), len(here) - len(soul)))
            links = [['sporePrint — the science, as a site', 'https://ecoprimals.github.io/sporePrint/', 'card'],
                     ['The catalog — every work, by shelf', 'https://github.com/protoKarya/alexandria/blob/main/shelves.md', 'card'],
                     ['The library itself', 'https://github.com/protoKarya/alexandria', 'card']]
            links += [[c['title'], c['url'], 'soul'] for c in soul[:5]] + [[c['title'], c['url'], 'heart'] for c in sorted(heart, key=lambda c: -(c.get('words') or 0))[:4]]
        else:
            say = '%d works in the library are shelved here.' % len(here)
            links = []
            if place == 'detroit': links.append(['The Detroit network — every node', url_of('network'), 'card'])
            if place == 'lansing': links.append(['Tuebor — I will defend', url_of(''), 'card'])
            for c in here[:9]:
                key = c['path'][:-3] if c['source'] == 'amicusContra/tuebor' else None
                links.append([c['title'], url_of(key) if key and key in pages else c['url'], 'page'])
        pins.append({'id': 'shelf-' + place, 'name': name, 'where': stands, 'lat': where[place]['lat'], 'lon': where[place]['lon'],
                     'kind': kind, 'say': say, 'n': len(here), 'links': links})
    unplaced = sum(1 for c in cards if c.get('place') == 'unplaced')
    return {'made': datetime.date.today().isoformat(),
            'note': 'Public buildings and offices only, placed to about a kilometre. No homes. What is said about each place is '
                    'the published page\'s own description; n is how many published pages name it.',
            'works': len(cards), 'unplaced': unplaced, 'pins': pins}, missing


def check(pins):
    urls = sorted({l[1] for p in pins['pins'] for l in p['links']})

    def ask(u):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'atlas-build'}), timeout=25) as r:
                return u, r.status
        except Exception as e:                      # noqa: BLE001 - any failure is a link that did not answer
            return u, getattr(e, 'code', str(e)[:60])
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        got = list(pool.map(ask, urls))
    bad = [(u, s) for u, s in got if s != 200]
    print('links asked: %d   answered: %d   did not: %d' % (len(got), len(got) - len(bad), len(bad)))
    for u, s in bad: print('   ', s, u)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--earth'); ap.add_argument('--tuebor'); ap.add_argument('--catalog')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = os.path.join(REPO, 'static')
    if a.earth:
        earth = build_earth(a.earth)
        path = os.path.join(out, 'atlas-earth.json')
        with open(path, 'w', encoding='utf-8') as f: json.dump(earth, f, separators=(',', ':'))
        print('earth: %d land, %d lake, %d state, %d border lines   %d KB' % (
            len(earth['land']), len(earth['lakes']), len(earth['states']), len(earth['borders']), os.path.getsize(path) // 1024))
    if a.tuebor and a.catalog:
        pins, missing = build_pins(a.tuebor, a.catalog)
        path = os.path.join(out, 'atlas-pins.json')
        with open(path, 'w', encoding='utf-8') as f: json.dump(pins, f, ensure_ascii=False, indent=1)
        kinds = collections.Counter(p['kind'] for p in pins['pins'])
        print('pins: %d   links: %d   %s   %d KB' % (len(pins['pins']), sum(len(p['links']) for p in pins['pins']),
              '  '.join('%s:%d' % k for k in kinds.most_common()), os.path.getsize(path) // 1024))
        for pid, key in missing: print('   no such page for %s: %s' % (pid, key))
        for p in pins['pins']:
            print('   %-14s named on %3d pages, %2d links   %s' % (p['id'], p['n'], len(p['links']), p['name'][:60]))
        if a.check and check(pins): sys.exit(1)


if __name__ == '__main__':
    main()
