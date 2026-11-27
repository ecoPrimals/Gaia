#!/usr/bin/env python3
"""atlas_stars.py - make the file of fixed stars the atlas page (static/atlas.html) draws.

  static/atlas-stars.json   every star a clear dark sky shows to the eye without effort: where it stood in the
                            year 2000, how bright it is, its colour, and how fast it drifts across the sky

The stars come from one public catalogue and nothing here is written by hand except the short table of names below:

  The Bright Star Catalogue, 5th revised edition (Hoffleit and Warren, 1991; Yale University Observatory),
  catalogue V/50 at the CDS in Strasbourg. The file is named catalog.gz there and bsc5.dat.gz at the Harvard
  Telescope Data Center (tdc-www.harvard.edu/catalogs). Fetch it once and hand it to this tool:

      python tools/atlas_stars.py bsc5.dat.gz              write static/atlas-stars.json
      python tools/atlas_stars.py bsc5.dat.gz --limit 5.5  more stars (the file grows: about 2,900 instead of 1,600)
      python tools/atlas_stars.py bsc5.dat.gz --check      say what would be written, and write nothing

What is kept of each star, six whole numbers in a row (s):
  right ascension and declination for the year 2000, in thousandths of a degree
  brightness (V magnitude) in hundredths; colour (B-V) in hundredths, 65 where the catalogue gives none
  its own drift a year, east and north, in thousandths of a second of arc (the catalogue's proper motion)
The stars are in order of brightness, the brightest first, so a page can stop early. names gives the old names of
the best known ones by their place in that order. Where each star stands at another time - the slow turning of the
earth's axis, the star's own drift - is worked out on the page, in static/sky.js.
"""
import argparse
import datetime
import gzip
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'static', 'atlas-stars.json')
SOURCE = 'Bright Star Catalogue, 5th revised edition (Hoffleit and Warren 1991, Yale University Observatory; CDS catalogue V/50)'

# The names, by the star's letter in its constellation as the catalogue writes it. Where two entries carry the same
# letter (a double star listed twice), the brighter one takes the name.
NAMES = {
    'Alp CMa': 'Sirius', 'Alp Car': 'Canopus', 'Alp Cen': 'Rigil Kentaurus', 'Alp Boo': 'Arcturus', 'Alp Lyr': 'Vega',
    'Alp Aur': 'Capella', 'Bet Ori': 'Rigel', 'Alp CMi': 'Procyon', 'Alp Eri': 'Achernar', 'Alp Ori': 'Betelgeuse',
    'Bet Cen': 'Hadar', 'Alp Aql': 'Altair', 'Alp Cru': 'Acrux', 'Alp Tau': 'Aldebaran', 'Alp Sco': 'Antares',
    'Alp Vir': 'Spica', 'Bet Gem': 'Pollux', 'Alp PsA': 'Fomalhaut', 'Alp Cyg': 'Deneb', 'Bet Cru': 'Mimosa',
    'Alp Leo': 'Regulus', 'Eps CMa': 'Adhara', 'Alp Gem': 'Castor', 'Gam Cru': 'Gacrux', 'Lam Sco': 'Shaula',
    'Gam Ori': 'Bellatrix', 'Bet Tau': 'Elnath', 'Bet Car': 'Miaplacidus', 'Eps Ori': 'Alnilam', 'Zet Ori': 'Alnitak',
    'Del Ori': 'Mintaka', 'Kap Ori': 'Saiph', 'Alp UMi': 'Polaris', 'Alp UMa': 'Dubhe', 'Bet UMa': 'Merak',
    'Gam UMa': 'Phecda', 'Del UMa': 'Megrez', 'Eps UMa': 'Alioth', 'Zet UMa': 'Mizar', 'Eta UMa': 'Alkaid',
    'Bet UMi': 'Kochab', 'Alp Dra': 'Thuban', 'Gam Dra': 'Eltanin', 'Alp And': 'Alpheratz', 'Alp Per': 'Mirfak',
    'Bet Per': 'Algol', 'Alp Ari': 'Hamal', 'Eta Tau': 'Alcyone', 'Bet Leo': 'Denebola', 'Alp CrB': 'Alphecca',
    'Alp Oph': 'Rasalhague', 'Alp Peg': 'Markab', 'Alp Cas': 'Schedar', 'Alp Hya': 'Alphard', 'Alp Gru': 'Alnair',
    'Alp Pav': 'Peacock', 'Alp Cep': 'Alderamin', 'Eps Sgr': 'Kaus Australis', 'Omi Cet': 'Mira',
}
LETTER = re.compile(r'^\s*\d*\s*([A-Z][a-z]{1,2})\s*\d?\s*([A-Za-z]{3})\s*$')


def num(text):
    text = text.strip()
    return float(text) if text else None


def read(path):
    """The catalogue's rows as stars: fixed columns, as its own ReadMe lays them out."""
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt', encoding='latin-1') as f:
        rows = [r.rstrip('\n') for r in f if r.strip()]
    stars, empty = [], 0
    for r in rows:
        r = r.ljust(160)
        if not r[75:77].strip() or not r[102:107].strip():           # the few entries that are not stars carry no place
            empty += 1
            continue
        ra = (int(r[75:77]) + int(r[77:79]) / 60 + float(r[79:83]) / 3600) * 15
        dec = (int(r[84:86]) + int(r[86:88]) / 60 + int(r[88:90]) / 3600) * (-1 if r[83] == '-' else 1)
        m = LETTER.match(r[4:14])
        stars.append({'hr': int(r[0:4]), 'letter': '%s %s' % (m.group(1), m.group(2)) if m else '', 'ra': ra, 'dec': dec,
                      'mag': float(r[102:107]), 'bv': num(r[109:114]), 'pmra': num(r[148:154]) or 0.0, 'pmdec': num(r[154:160]) or 0.0})
    return rows, stars, empty


def build(stars, limit):
    kept = sorted((s for s in stars if s['mag'] <= limit), key=lambda s: (s['mag'], s['hr']))
    flat, names, taken = [], {}, set()
    for i, s in enumerate(kept):
        flat += [round(s['ra'] * 1000), round(s['dec'] * 1000), round(s['mag'] * 100),
                 65 if s['bv'] is None else round(s['bv'] * 100), round(s['pmra'] * 1000), round(s['pmdec'] * 1000)]
        if s['letter'] in NAMES and s['letter'] not in taken:        # in order of brightness, so the first one met is the brighter
            names[str(i)] = NAMES[s['letter']]
            taken.add(s['letter'])
    return kept, flat, names, sorted(set(NAMES) - taken)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('catalogue', help='the Bright Star Catalogue file (bsc5.dat.gz / catalog.gz, or the same unpacked)')
    ap.add_argument('--limit', type=float, default=5.0, help='the faintest magnitude kept (default 5.0)')
    ap.add_argument('--check', action='store_true', help='say what would be written, and write nothing')
    a = ap.parse_args()
    rows, stars, empty = read(a.catalogue)
    kept, flat, names, unmet = build(stars, a.limit)
    out = {'made': datetime.date.today().isoformat(), 'from': SOURCE,
           'note': 'six whole numbers a star, brightest first: right ascension and declination for the year 2000 in thousandths of a degree, '
                   'magnitude in hundredths, colour (B-V) in hundredths, drift a year east and north in thousandths of a second of arc',
           'limit': a.limit, 'n': len(kept), 'per': 6, 's': flat, 'names': names}
    text = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    print('catalogue rows: %d   stars with a place: %d   not stars: %d' % (len(rows), len(stars), empty))
    print('kept to magnitude %.1f: %d   named: %d   size: %d KB' % (a.limit, len(kept), len(names), len(text.encode('utf-8')) // 1024))
    if unmet:
        print('names with no star found: %s' % ', '.join(unmet))
    for i in list(range(5)) + [int(k) for k in names if names[k] in ('Polaris', 'Thuban', 'Arcturus')]:
        s = kept[i]
        print('  %-16s HR %-4d  %8.3f %+8.3f  mag %5.2f  drift %+.3f %+.3f' % (names.get(str(i), s['letter']), s['hr'], s['ra'], s['dec'], s['mag'], s['pmra'], s['pmdec']))
    if a.check:
        print('nothing written (--check)')
        return 0 if not unmet else 1
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('wrote %s' % os.path.relpath(OUT, ROOT))
    return 0 if not unmet else 1


if __name__ == '__main__':
    sys.exit(main())
