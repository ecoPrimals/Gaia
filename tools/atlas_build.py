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

Run (the inputs are checkouts that already exist on this gate):
  python tools/atlas_build.py --earth <folder of Natural Earth geojson: 110m land, lakes, borders, state lines; 50m land, lakes>
                              --tuebor <tuebor>/site/content
                              --catalog gardens/alexandria/catalog.json [--sporeprint <hud>/site/public/sporeprint] [--check]
      with --tuebor and --catalog but without --sporeprint or --detroit, those sites' pins stay as they are in the file.
  python tools/atlas_build.py --sporeprint <hud>/site/public/sporeprint [--check]
      on its own: only sporePrint's pins (SPORE_PLACES) are made again; every other pin in the file stays as it is.
  python tools/atlas_build.py --detroit <publicRecord>/site/public [--check]
      the same for the Detroit site (detroit.primals.eco, DETROIT_PLACES): the county seat, the halls and the courts
      its pages name, and the two far marks in Ireland. The built site lives on eastGate; a copy of its pages will do.

The file also carries THE TRIANGLE (TRIANGLE below): three pins to measure from, the far marks to sight on, and the
triangle widened by three more marks. It names pins by id and adds no place of its own. The home corner is the Lansing
shelf - the town, nothing finer.
With --sporeprint it also carries THE SPORE GRAPH (sporePrint's own graph/entity-graph.json, every node hung on a pin)
and it always carries the MOMENTS: times to travel to, each with the pin to stand on.
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
LAND_BOXES = [(-11.2, 51.0, -5.42, 55.8)]      # Ireland: the island from the finer map, so Dublin stands on its bay and Kerry has its headlands

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

# The same again for sporePrint: the offices and campuses its pages are written to, or build on.
# Same two rules. A person is never pinned: an invitation to somebody is pinned at the public office of the
# company or the school they are known for, and where the pages name nobody's office there is no pin.
SPORE_LIVE = 'https://primals.eco/sporeprint'
SPORE_PLACES = [
    ('valve', 'Valve — the invitations to GabeN and to Steam', 'Lincoln Square, 10400 NE 4th St, Bellevue, Washington', 47.6158, -122.2010, 'maker',
     r'\bValve\b|\bGabeN\b|Gabe Newell|Steam Deck|SteamOS',
     ['outreach/hadr-invitation', 'outreach/octopus-invitation', 'outreach/steam-invitation', 'outreach/gaming-invitation']),
    ('nvidia', 'NVIDIA', '2788 San Tomas Expressway, Santa Clara, California', 37.3708, -121.9668, 'maker',
     r'\bNVIDIA\b', ['outreach/gpu-invitation', 'science/14-sovereign-compute-hardware']),
    ('amd', 'AMD', '2485 Augustine Dr, Santa Clara, California', 37.3826, -121.9705, 'maker',
     r'\bAMD\b', ['outreach/gpu-invitation']),
    ('intel', 'Intel', '2200 Mission College Blvd, Santa Clara, California', 37.3876, -121.9636, 'maker',
     r'\bIntel\b', ['outreach/gpu-invitation']),
    ('brainchip', 'BrainChip — the Akida neuromorphic chip', '23041 Avenida de la Carlota, Laguna Hills, California', 33.6117, -117.7087, 'maker',
     r'BrainChip|\bAkida\b|AKD1000', ['outreach/neuromorphic-invitation', 'technical/neuromorphic-benchmark', 'science/26-neuromorphic-sovereign-driver']),
    ('99pi', '99% Invisible', 'uptown Oakland, California', 37.8107, -122.2660, 'media',
     r'99% Invisible|\b99pi\b|Roman Mars', ['outreach/99pi-radiolab-invitation']),
    ('radiolab', 'Radiolab — WNYC Studios', '160 Varick St, New York', 40.7262, -74.0057, 'media',
     r'\bRadiolab\b|\bWNYC\b', ['outreach/99pi-radiolab-invitation']),
    ('msu', 'Michigan State University — the science the springs reproduce', 'Engineering Building, 428 S Shaw Ln, East Lansing', 42.7247, -84.4812, 'school',
     r'\bMSU\b|Michigan State University', ['audience/faculty-spring-profiles', 'architecture/spring-catalog', 'technical/msu-asset-acceleration']),
    ('sandia', 'Sandia National Laboratories', 'Albuquerque, New Mexico', 35.0586, -106.5340, 'lab',
     r'\bSandia\b', ['lab/notebooks/cahill-smallwood-algae']),
    ('carleton', 'Carleton College', 'Northfield, Minnesota', 44.4613, -93.1540, 'school',
     r'\bCarleton\b', []),
    ('glerl', 'NOAA Great Lakes Environmental Research Laboratory', '4840 S State Rd, Ann Arbor', 42.2225, -83.7405, 'lab',
     r'\bGLERL\b|Lake Erie|Great Lakes HAB', ['science/09-field-genomics']),
    ('schofield', 'Schofield Barracks — 25th Infantry Division', 'the Army post on Oʻahu, Hawaii, as the backscatter page names it', 21.4959, -158.0623, 'mark',
     r'Schofield|25th Infantry', ['outreach/backscatter']),
    # the wide triangle: three projects, each stood by the house at a place on the ground (see SPORE_STANDS)
    ('pictured-rocks', 'Pictured Rocks — blueFish', 'Miners Castle, Pictured Rocks National Lakeshore, on Lake Superior, Michigan', 46.4908, -86.5492, 'mark',
     r'Pictured Rocks|blueFish', ['products/bluefish']),
    ('yellowstone', 'Yellowstone — wetSpring', 'Lower Geyser Basin, Yellowstone National Park, Wyoming — the hot springs Thermus aquaticus was found in', 44.5387, -110.7980, 'mark',
     r'Yellowstone|wetSpring', ['springs/wetspring', 'thesis/10-results-wetspring', 'thesis/01-introduction']),
    ('alexandria', 'Alexandria — hotSpring and lattice QCD', 'Bibliotheca Alexandrina, by the old harbour of Alexandria, Egypt — the city Ptolemy watched the sky from', 31.2089, 29.9092, 'mark',
     r'Alexandria|Ptolem|hotSpring|lattice QCD', ['springs/hotspring', 'products/lattice-qcd', 'thesis/08-results-hotspring', 'pseudospore/hotspring-qcd-sun']),
]
# A project the house stands at a place. The pages mostly name the project, not the ground, and the pin says so:
# id -> (the project as the pages write it, the words that name the place itself)
SPORE_STANDS = {
    'pictured-rocks': ('blueFish', r'Pictured Rocks'),
    'yellowstone': ('wetSpring', r'Yellowstone'),
    'alexandria': ('hotSpring and lattice QCD', r'Alexandria|Ptolem'),
}

# THE SPORE GRAPH. sporePrint serves its own graph of what it is made of (graph/entity-graph.json: primals, springs,
# products, concepts, and the lines between them). Every node of it is hung on a pin: the ones the house has stood at
# a place on the ground hang there, the rest hang at the Library shelf, which is where sporePrint itself is pinned.
# A line of the graph whose two ends hang on different pins is a line over the ground.
GRAPH_FILE = 'graph/entity-graph.json'
GRAPH_AT = {'bluefish': 'pictured-rocks', 'wetspring': 'yellowstone', 'hotspring': 'alexandria'}
GRAPH_HOME = 'shelf-library'
GRAPH_PAGES = ('primals', 'springs', 'products', 'architecture', 'methodology', 'glossary')   # where a node's own page is looked for

# THE BACKSCATTER. sporePrint's backscatter page is a timeline: a span of years, what it was, and where. Each span is
# hung on the pin its place names (first match below, tried against the place and then the heading), so the atlas's
# clock can go to the year and its globe to the place. Nothing is added to what the page itself says; a span whose
# place has no pin is reported and listed as not yet placed.
BACKSCATTER_PAGE = 'outreach/backscatter'
BACKSCATTER_AT = [
    (r'Schofield', 'schofield'),
    (r'Albuquerque|Sandia', 'sandia'),
    (r'East Lansing|Michigan State|\bMSU\b', 'msu'),
    (r'\bLansing\b', 'shelf-lansing'),
]

# MOMENTS to travel to. Each is a time and the pin to stand on. `when` is UT, written in the calendar of its day (the
# old calendar before 15 October 1582); a `rule` is worked out by the page from its own sky (static/sky.js).
# Nothing here is quoted from a book. The years are the ones the sources are known to give; the sky is worked out.
MOMENTS = [
    {'id': 'easter-588', 'at': 'skellig', 'rule': 'easter-sunrise', 'year': 588, 'name': 'Easter sunrise from the rock, AD 588',
     'say': 'The year the house’s record of Moorhouse’s Sun Dancing gives for the first monks on the rock. The old belief of the Gaelic west is that the sun dances as it rises on Easter morning. Easter is by the Alexandrian table; in 588 the Irish still kept an older table of their own, which in some years gave another Sunday.'},
    {'id': 'eclipse-664', 'at': 'skellig', 'when': '0664-05-01T15:56', 'name': 'The sun goes dark over Ireland, 1 May 664',
     'say': 'The Irish annals: darkness on the first of May, at the ninth hour. Worked out here, the moon crosses the sun that afternoon.'},
    {'id': 'easter-824', 'at': 'skellig', 'rule': 'easter-sunrise', 'year': 824, 'name': 'Easter sunrise from the rock, AD 824',
     'say': 'The year the Irish annals give for the Viking raid on the rock.'},
    {'id': 'easter-1222', 'at': 'skellig', 'rule': 'easter-sunrise', 'year': 1222, 'name': 'Easter sunrise from the rock, 1222',
     'say': 'The year the house’s record of Sun Dancing gives for the last monks rowing back to the mainland.'},
    {'id': 'ptolemy-133', 'at': 'alexandria', 'when': '0133-05-06T20:40', 'name': 'Ptolemy’s eclipse of the moon, Alexandria, 6 May 133',
     'say': 'One of three eclipses of the moon Ptolemy records watching from Alexandria (Almagest, book IV). Worked out here, the moon stands opposite the sun that night, on the sun’s path.'},
]

# The Detroit site (detroit.primals.eco): Detroit and Wayne County, and the far body in Ireland.
# Same two rules. Where the pages give a street address themselves, that is the address used.
# A page in these sections is a list the site makes by itself ("all pages referencing ..."); such a page can be
# a place's own card, but it is not counted as a page that names the place and it does not speak for it.
DETROIT_LIVE = 'https://detroit.primals.eco'
DETROIT_LISTS = ('tags/', 'connections/', 'entities/', 'actors/', 'counties/', 'courts/')
DETROIT_PLACES = [
    ('wayne', 'Wayne County — the county seat', 'Guardian Building, 500 Griswold St, Detroit — the county’s offices', 42.3296, -83.0461, 'civic',
     r'Wayne County', ['network/entities/wayne-county', 'entities/wayne-county']),
    ('caymc', 'Coleman A. Young Municipal Center — Detroit City Council, the City Clerk and the Wayne County Probate Court',
     '2 Woodward Ave, Detroit', 42.3295, -83.0437, 'civic',
     r'City Council|City Clerk|Probate Court|Municipal Center',
     ['entities/detroit-city-council', 'entities/wayne-county-probate-court']),
    ('murphy', 'Wayne County Prosecutor', 'Frank Murphy Hall of Justice, 1441 St. Antoine, Detroit — the address the pages give', 42.3365, -83.0420, 'civic',
     r'Wayne County Prosecutor|Frank Murphy', ['entities/wayne-county-prosecutor']),
    ('edmi', 'U.S. District Court — Eastern District of Michigan', 'Theodore Levin U.S. Courthouse, 231 W Lafayette Blvd, Detroit', 42.3298, -83.0494, 'court',
     r'Eastern District of Michigan|E\.D\. Mich', ['courts/eastern-district-of-michigan']),
    ('fbi', 'FBI Detroit — the federal building', 'Patrick V. McNamara Federal Building, 477 Michigan Ave, Detroit', 42.3316, -83.0530, 'state',
     r'FBI Detroit|McNamara Federal|477 Michigan', ['entities/fbi']),
    ('dpd', 'Detroit Police Department', 'Detroit Public Safety Headquarters, 1301 Third Ave, Detroit', 42.3325, -83.0577, 'civic',
     r'Detroit Police Department|\bDPD\b', ['network/entities/detroit-police-department', 'entities/dpd']),
    ('adb', 'Attorney Discipline Board', '333 W Fort St, Detroit', 42.3290, -83.0515, 'law',
     r'Attorney Discipline Board', ['entities/attorney-discipline-board']),
    # the far body
    ('meta-dublin', 'Meta — the Dublin office', 'Meta Platforms Ireland, Merrion Road, Ballsbridge, Dublin 4, Ireland', 53.3270, -6.2280, 'media',
     r'\bDublin\b|Meta Ireland|Meta Platforms Ireland', ['entities/meta-ireland', 'entities/dublin-datacenter']),
    ('skellig', 'Skellig Michael — Sceilg Mhichíl', 'the monks’ rock in the Atlantic, 12 km off the coast of Kerry, Ireland', 51.7711, -10.5406, 'mark',
     r'Skellig|Sceilg', []),
]
# a mark the pages do not write about yet still has ground to stand on: one public page about the place itself
DETROIT_OUTSIDE = {'skellig': [['Sceilg Mhichíl — UNESCO World Heritage List', 'https://whc.unesco.org/en/list/757/', 'outside']]}

# The triangle. Each corner and each far mark is a pin that already stands (by id); `short` is the word drawn on
# the globe, `as` is what the mark is in the triangle.
TRIANGLE = {
    'corners': [
        {'pin': 'shelf-lansing', 'short': 'home', 'as': 'home — the two houses, held at the town of Lansing'},
        {'pin': 'msu', 'short': 'Olympus', 'as': 'Mount Olympus — Michigan State, the alma mater'},
        {'pin': 'wayne', 'short': 'Wayne', 'as': 'Detroit and Wayne County'},
    ],
    'far': [
        {'pin': 'meta-dublin', 'short': 'Dublin', 'as': 'Meta in Dublin'},
        {'pin': 'skellig', 'short': 'Skellig', 'as': 'the monks’ rock — the old way of the sun'},
    ],
    # the triangle, widened: three more marks, far enough apart that the earth's curve shows between them
    'wide': [
        {'pin': 'pictured-rocks', 'short': 'Pictured Rocks', 'as': 'Pictured Rocks on Lake Superior — blueFish'},
        {'pin': 'yellowstone', 'short': 'Yellowstone', 'as': 'Yellowstone — wetSpring'},
        {'pin': 'alexandria', 'short': 'Alexandria', 'as': 'Egypt of the ancients, Ptolemy’s Alexandria — hotSpring and lattice QCD, to backscatter the stars'},
    ],
}

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


def within(b, box):
    return b[0] >= box[0] and b[1] >= box[1] and b[2] <= box[2] and b[3] <= box[3]


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
    land = [pack(r) for f in load(folder, 'ne_110m_land') for r in rings(f['geometry'])
            if not any(within(bbox(r), box) for box in LAND_BOXES)]
    for f in load(folder, 'ne_50m_land'):
        for r in rings(f['geometry']):
            if len(r) > 12 and any(within(bbox(r), box) for box in LAND_BOXES): land.append(pack(thin(r, 0.02)))
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
            links = [['The card catalog — find any work on this shelf', '/library#place=library', 'card'],
                     ['sporePrint — the science, as a site', 'https://ecoprimals.github.io/sporePrint/', 'card'],
                     ['The catalog — every work, by shelf', 'https://github.com/protoKarya/alexandria/blob/main/shelves.md', 'card'],
                     ['The library itself', 'https://github.com/protoKarya/alexandria', 'card']]
            links += [[c['title'], c['url'], 'soul'] for c in soul[:5]] + [[c['title'], c['url'], 'heart'] for c in sorted(heart, key=lambda c: -(c.get('words') or 0))[:4]]
        else:
            say = '%d works in the library are shelved here.' % len(here)
            links = [['The card catalog — find any work on this shelf', '/library#place=' + place, 'card']]   # the house's own page, on whichever name serves the atlas
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


def read_built(folder):
    """sporePrint as it is served: one folder per page with an index.html. -> {path: title, say, body}"""
    import html
    pages = {}
    for root, _, files in os.walk(folder):
        if 'index.html' not in files: continue
        key = os.path.relpath(root, folder).replace(os.sep, '/')
        if key == '.': continue
        with open(os.path.join(root, 'index.html'), encoding='utf-8', errors='replace') as f:
            text = f.read()
        t = re.search(r'<title>(.*?)</title>', text, re.S)
        d = (re.search(r'<meta[^>]*\bname="?description"?[^>]*\bcontent="([^"]*)"', text)
             or re.search(r'<meta[^>]*\bcontent="([^"]*)"[^>]*\bname="?description', text))
        body = re.sub(r'<(script|style|nav|header|footer)\b[^>]*>.*?</\1>', ' ', text, flags=re.S | re.I)
        body = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', body)).split())
        pages[key] = {'title': ' '.join(html.unescape(t.group(1)).split(' | ')[0].split()) if t else key,
                      'say': html.unescape(d.group(1)).strip() if d else '', 'body': body,
                      'index': key.count('/') == 0}                   # a section's own front page lists the others
    return pages


def build_spore_pins(folder):
    pages = read_built(folder)
    pins, missing = [], []
    for pid, name, where, lat, lon, kind, words, own in SPORE_PLACES:
        rx = re.compile(words)
        hits = sorted(((len(rx.findall(p['title'] + '\n' + p['body'])), key) for key, p in pages.items()
                       if rx.search(p['title'] + '\n' + p['body'])), key=lambda h: (-h[0], h[1]))
        links, seen, say = [], set(), ''
        for key in own:
            if key not in pages: missing.append((pid, key)); continue
            if not say and len(pages[key]['say']) >= 30 and rx.search(pages[key]['say']): say = pages[key]['say']
            links.append([pages[key]['title'], '%s/%s/' % (SPORE_LIVE, key), 'card']); seen.add(key)
        for n, key in hits:
            if len(links) >= len(seen & set(own)) + 8: break
            if key in seen or pages[key]['index'] or key == 'site-index': continue
            links.append([pages[key]['title'], '%s/%s/' % (SPORE_LIVE, key), 'page']); seen.add(key)
        pin = {'id': pid, 'name': name, 'where': where, 'lat': lat, 'lon': lon, 'kind': kind,
               'say': say, 'n': len(hits), 'links': links, 'from': 'sporePrint'}
        if pid in SPORE_STANDS:                     # the pages name the project; how many name the ground itself is said apart
            project, ground = SPORE_STANDS[pid]
            rg = re.compile(ground)
            pin['stands'] = project
            pin['n_place'] = sum(1 for p in pages.values() if rg.search(p['title'] + '\n' + p['body']))
        pins.append(pin)
    return pins, missing


def build_graph(folder, pins):
    """Hang every node of sporePrint's own graph on a pin. -> the summary for the file, or None if the graph is not there."""
    path = os.path.join(folder, *GRAPH_FILE.split('/'))
    if not os.path.exists(path):
        print('   the spore graph is not in %s (%s) - the pins keep the graph they have' % (folder, GRAPH_FILE))
        return None
    with open(path, encoding='utf-8') as f: graph = json.load(f)
    pages = read_built(folder)
    by_id = {p['id']: p for p in pins}
    for p in pins: p.pop('graph', None)
    at = {}
    for node in graph['nodes']:
        pin = by_id.get(GRAPH_AT.get(node['id'], GRAPH_HOME))
        if not pin: continue
        rx = re.compile(r'(?<![A-Za-z])' + re.escape(node['display']) + r'(?![A-Za-z])')
        named = sum(1 for k, p in pages.items() if not p['index'] and k != 'site-index' and rx.search(p['title'] + '\n' + p['body']))
        own = next(('%s/%s' % (s, node['id']) for s in GRAPH_PAGES if '%s/%s' % (s, node['id']) in pages), '')
        pin.setdefault('graph', []).append([node['display'], node['kind'], named, '%s/%s/' % (SPORE_LIVE, own) if own else ''])
        at[node['id']] = (pin['id'], node['display'])
    for p in pins:
        if 'graph' in p: p['graph'].sort(key=lambda g: (-g[2], g[0].lower()))
    lines = sorted({(at[e['source']][0], at[e['target']][0], '%s — %s — %s' % (at[e['source']][1], e['relation'], at[e['target']][1]))
                    for e in graph['edges'] if not e.get('inverse') and e['source'] in at and e['target'] in at
                    and at[e['source']][0] != at[e['target']][0]})
    return {'from': '%s/%s' % (SPORE_LIVE, GRAPH_FILE), 'nodes': len(graph['nodes']), 'edges': sum(1 for e in graph['edges'] if not e.get('inverse')),
            'hung': len(at), 'on_the_ground': sorted(k for k in at if k in GRAPH_AT), 'lines': [list(l) for l in lines]}


def build_backscatter(folder, pins):
    """The backscatter page's own timeline, each span hung on a pin. -> the summary for the file, or None if the page is not there."""
    import html
    path = os.path.join(folder, *BACKSCATTER_PAGE.split('/'), 'index.html')
    if not os.path.exists(path):
        print('   the backscatter page is not in %s - the file keeps the timeline it has' % folder)
        return None
    with open(path, encoding='utf-8', errors='replace') as f: text = f.read()

    def said(part, rx):
        m = re.search(rx, part, re.S)
        return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1))).split()) if m else ''
    have = {p['id'] for p in pins}
    title = said(text, r'<title>(.*?)</title>').split(' | ')[0] or said(text, r'<h1[^>]*>(.*?)</h1>')
    eras, unplaced = [], []
    for part in re.split(r'<div class="?era"?[^>]*>', text)[1:]:
        span, name, place = said(part, r'class="?date"?[^>]*>(.*?)</div>'), said(part, r'<h3[^>]*>(.*?)</h3>'), said(part, r'class="?place"?[^>]*>(.*?)</div>')
        year = re.search(r'\b(1[89]\d\d|20\d\d)\b', span)
        at = next((pin for src in (place, name) for rx, pin in BACKSCATTER_AT if re.search(rx, src)), None)
        if not (year and name and at in have):
            unplaced.append('%s %s (%s)' % (span, name, place)); continue
        eras.append({'span': span, 'year': int(year.group(1)), 'name': name, 'place': place, 'at': at})
    for u in unplaced: print('   a span of the backscatter has no pin: %s' % u)
    return {'page': '%s/%s/' % (SPORE_LIVE, BACKSCATTER_PAGE), 'title': title, 'eras': eras, 'unplaced': unplaced}


def moments(pins):
    """The moments whose pin stands."""
    have = {p['id'] for p in pins}
    for m in MOMENTS:
        if m['at'] not in have: print('   a moment names a pin that does not stand: %s at %s' % (m['id'], m['at']))
    return [m for m in MOMENTS if m['at'] in have]


def build_detroit_pins(folder):
    pages = read_built(folder)
    for p in pages.values(): p['title'] = p['title'].split(' — Cash for Kids 2')[0]
    written = {k: p for k, p in pages.items() if not p['index'] and not k.startswith(DETROIT_LISTS) and k != 'site-index'}
    pins, missing = [], []
    for pid, name, where, lat, lon, kind, words, own in DETROIT_PLACES:
        rx = re.compile(words)
        hits = sorted(((len(rx.findall(p['title'] + '\n' + p['body'])), key) for key, p in written.items()
                       if rx.search(p['title'] + '\n' + p['body'])), key=lambda h: (-h[0], h[1]))
        links, seen, say = [], set(), ''
        for key in own:
            if key not in pages: missing.append((pid, key)); continue
            if not say and key in written and len(pages[key]['say']) >= 30 and rx.search(pages[key]['say']): say = pages[key]['say']
            links.append([pages[key]['title'], '%s/%s/' % (DETROIT_LIVE, key), 'card']); seen.add(key)
        links += DETROIT_OUTSIDE.get(pid, [])
        own_n = len(links)
        for n, key in hits:
            if len(links) >= own_n + 8: break
            if key in seen or key.startswith('network/'): continue
            links.append([pages[key]['title'], '%s/%s/' % (DETROIT_LIVE, key), 'page']); seen.add(key)
        pins.append({'id': pid, 'name': name, 'where': where, 'lat': lat, 'lon': lon, 'kind': kind,
                     'say': say, 'n': len(hits), 'links': links, 'from': 'detroit'})
    return pins, missing


def triangle(pins):
    """The triangle as the page reads it; a corner whose pin does not stand is reported, and the triangle is left out."""
    have = {p['id'] for p in pins}
    gone = [m['pin'] for part in TRIANGLE.values() for m in part if m['pin'] not in have]
    for g in gone: print('   the triangle names a pin that does not stand: %s' % g)
    return None if gone else TRIANGLE


def check(pins):
    urls = sorted({l[1] for p in pins['pins'] for l in p['links']})

    def ask(u):
        try:
            full = u if '://' in u else 'https://primals.eco' + u     # a link to the house's own page is asked of the house
            with urllib.request.urlopen(urllib.request.Request(full, headers={'User-Agent': 'atlas-build'}), timeout=25) as r:
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
    ap.add_argument('--earth'); ap.add_argument('--tuebor'); ap.add_argument('--catalog'); ap.add_argument('--sporeprint')
    ap.add_argument('--detroit')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = os.path.join(REPO, 'static')
    if a.earth:
        earth = build_earth(a.earth)
        path = os.path.join(out, 'atlas-earth.json')
        with open(path, 'w', encoding='utf-8') as f: json.dump(earth, f, separators=(',', ':'))
        print('earth: %d land, %d lake, %d state, %d border lines   %d KB' % (
            len(earth['land']), len(earth['lakes']), len(earth['states']), len(earth['borders']), os.path.getsize(path) // 1024))
    if (a.sporeprint or a.detroit) and not (a.tuebor and a.catalog):
        # one site's pins on their own: the pins file as it stands keeps every other pin, these are replaced
        path = os.path.join(out, 'atlas-pins.json')
        with open(path, encoding='utf-8') as f: pins = json.load(f)
        new, missing = [], []
        for label, folder, build in (('sporePrint', a.sporeprint, build_spore_pins), ('detroit', a.detroit, build_detroit_pins)):
            if not folder: continue
            made, gone = build(folder)
            pins['pins'] = [p for p in pins['pins'] if p.get('from') != label] + made
            new += made; missing += gone
            print('%s pins: %d   links: %d' % (label, len(made), sum(len(p['links']) for p in made)))
        pins['made'] = datetime.date.today().isoformat()
        tri = triangle(pins['pins'])
        if tri: pins['triangle'] = tri
        else: pins.pop('triangle', None)
        if a.sporeprint:
            graph = build_graph(a.sporeprint, pins['pins'])
            if graph:
                pins['graph'] = graph
                print('spore graph: %d nodes hung (%d on the ground: %s; the rest at %s)   %d lines over the ground' % (
                    graph['hung'], len(graph['on_the_ground']), ' '.join(graph['on_the_ground']), GRAPH_HOME, len(graph['lines'])))
            back = build_backscatter(a.sporeprint, pins['pins'])
            if back:
                pins['backscatter'] = back
                print('backscatter: %d spans on pins (%s)   not placed: %d' % (len(back['eras']), ' '.join('%d:%s' % (e['year'], e['at']) for e in back['eras']), len(back['unplaced'])))
        pins['moments'] = moments(pins['pins'])
        with open(path, 'w', encoding='utf-8') as f: json.dump(pins, f, ensure_ascii=False, indent=1)
        print('all pins now: %d   %d KB   triangle: %s   moments: %d' % (len(pins['pins']), os.path.getsize(path) // 1024, 'yes' if tri else 'no', len(pins['moments'])))
        for pid, key in missing: print('   no such page for %s: %s' % (pid, key))
        for p in new: print('   %-12s named on %3d pages, %2d links   %s' % (p['id'], p['n'], len(p['links']), p['name'][:60]))
        if a.check and check({'pins': new}): sys.exit(1)
        return
    if a.tuebor and a.catalog:
        pins, missing = build_pins(a.tuebor, a.catalog)
        path = os.path.join(out, 'atlas-pins.json')
        standing = []
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f: standing = json.load(f).get('pins', [])
        for label, folder, build in (('sporePrint', a.sporeprint, build_spore_pins), ('detroit', a.detroit, build_detroit_pins)):
            if folder:
                more, gone = build(folder)
                missing += gone
            else:
                # a site whose folder is not given keeps the pins it already has in the file
                more = [p for p in standing if p.get('from') == label]
                if more: print('%s pins: %d kept as they stand' % (label, len(more)))
            pins['pins'] += more
        tri = triangle(pins['pins'])
        if tri: pins['triangle'] = tri
        graph = build_graph(a.sporeprint, pins['pins']) if a.sporeprint else None
        back = build_backscatter(a.sporeprint, pins['pins']) if a.sporeprint else None
        if os.path.exists(path) and not (graph and back):   # what this run did not make again stays as the file has it
            with open(path, encoding='utf-8') as f: was = json.load(f)
            if not graph:
                graph = was.get('graph')
                hung = {p['id']: p['graph'] for p in was.get('pins', []) if 'graph' in p}
                for p in pins['pins']:
                    if p['id'] in hung: p['graph'] = hung[p['id']]
            back = back or was.get('backscatter')
        if graph: pins['graph'] = graph
        if back: pins['backscatter'] = back
        pins['moments'] = moments(pins['pins'])
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
