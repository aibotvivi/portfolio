#!/usr/bin/env python3
"""Rebuild the travel map's data in index.html from Natural Earth.

The map in the Travel Map window is drawn from two grids embedded in the page:

  MAP    a land-or-sea mask, four cells per hex character
  VISIT  which place each land cell belongs to, one base-62 character per cell

Both are rasterised here, offline, from Natural Earth's public-domain 110m
data, so the page itself never fetches anything to draw a world map. Add a
place to PLACES below and run this; it rewrites MAP, VISIT, SHARE and PLACES in
index.html in place.

    python3 scripts/build-travel-map.py

Needs the network, once, to pull the two Natural Earth files.
"""
import json
import math
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'index.html'

# Alphabetical: the legend is numbered, and 30-odd numbers are only usable if
# the list can be scanned.
PLACES = [
    'Austria', 'Belgium', 'Canada', 'China', 'Croatia', 'Czechia', 'Denmark', 'Egypt',
    'France', 'Germany', 'Hong Kong', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'Italy',
    'Japan', 'Jordan', 'Malaysia', 'Mexico', 'Morocco', 'Nepal', 'Netherlands', 'Norway',
    'Philippines', 'Poland', 'Portugal', 'Singapore', 'Slovakia', 'South Africa',
    'South Korea', 'Spain', 'Sweden', 'Turkey', 'United Kingdom', 'United States',
    'Vietnam',
]

# Natural Earth's name where it differs from the label shown on the page.
NE_NAME = {'United States': 'United States of America'}

# Places with no polygon at 110m because they are smaller than one grid cell.
# Their single cell is placed from a coordinate instead.
BY_HAND = {'Hong Kong': (22.3, 114.2), 'Singapore': (1.35, 103.82)}

# Grid. The latitude span trims the empty Arctic and most of Antarctica, which
# is why SHARE is a share of the land the map actually covers.
W, H = 168, 66
LAT0, LAT1 = 84.0, -58.0

BASE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
SOURCES = {'land': 'ne_110m_land.geojson', 'countries': 'ne_110m_admin_0_countries.geojson'}


def fetch(name):
    cache = ROOT / '.cache' / SOURCES[name]
    if cache.exists():
        return json.loads(cache.read_text())
    print('fetching', SOURCES[name])
    with urllib.request.urlopen(BASE + SOURCES[name], timeout=60) as r:
        raw = r.read().decode()
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(raw)
    return json.loads(raw)


def edges_of(features):
    """Every non-horizontal edge of every ring, for scanline filling."""
    out = []
    for f in features:
        g = f['geometry']
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        for poly in polys:
            for ring in poly:
                for i in range(len(ring) - 1):
                    x1, y1 = ring[i][0], ring[i][1]
                    x2, y2 = ring[i + 1][0], ring[i + 1][1]
                    if y1 != y2:
                        out.append((x1, y1, x2, y2))
    return out


def rasterise(edges, grid, value, mask=None):
    """Scanline fill with the even-odd rule, which handles holes for free."""
    cells = []
    for row in range(H):
        lat = LAT0 + (LAT1 - LAT0) * ((row + 0.5) / H)
        xs = sorted(x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
                    for x1, y1, x2, y2 in edges if (y1 <= lat < y2) or (y2 <= lat < y1))
        for i in range(0, len(xs) - 1, 2):
            ca = int((xs[i] + 180.0) / 360.0 * W)
            cb = int((xs[i + 1] + 180.0) / 360.0 * W)
            for c in range(max(0, ca), min(W - 1, cb) + 1):
                if mask is not None and not mask[row][c]:
                    continue
                grid[row][c] = value
                cells.append((c, row))
    return cells


def cell_of(lat, lon):
    return int((lon + 180.0) / 360.0 * W), int((lat - LAT0) / (LAT1 - LAT0) * H)


def nearest_land(land, c, r):
    if land[r][c]:
        return c, r
    for rad in range(1, 5):
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                y, x = r + dy, c + dx
                if 0 <= y < H and 0 <= x < W and land[y][x]:
                    return x, y
    return c, r


def cos_area(grid):
    """Latitude-weighted, so this is an area share and not a cell count."""
    total = 0.0
    for r in range(H):
        w = math.cos(math.radians(LAT0 + (LAT1 - LAT0) * ((r + 0.5) / H)))
        total += sum(1 for c in range(W) if grid[r][c]) * w
    return total


land = [[0] * W for _ in range(H)]
rasterise(edges_of(fetch('land')['features']), land, 1)

countries = {}
for f in fetch('countries')['features']:
    countries.setdefault(f['properties'].get('NAME'), []).append(f)

visit = [[0] * W for _ in range(H)]
owned = {}
for n, name in enumerate(PLACES, start=1):
    if name in BY_HAND:
        owned[n] = [nearest_land(land, *cell_of(*BY_HAND[name]))]
        continue
    key = NE_NAME.get(name, name)
    if key not in countries:
        sys.exit('no polygon named %r — add it to NE_NAME or BY_HAND' % key)
    scratch = [[0] * W for _ in range(H)]
    cells = rasterise(edges_of(countries[key]), scratch, n, mask=land)
    if not cells:
        sys.exit('%s caught no cell; it needs a BY_HAND coordinate' % name)
    owned[n] = cells

# Paint the largest first so the smallest are painted last and survive. At this
# resolution Belgium is a couple of cells it shares with France, Germany and the
# Netherlands; in list order those neighbours simply erased it.
pins = []
for n in sorted(owned, key=lambda k: -len(owned[k])):
    for c, r in owned[n]:
        visit[r][c] = n
for n, name in enumerate(PLACES, start=1):
    cells = owned[n]
    # the pin sits on a cell the place actually owns, nearest its own middle
    mc = sum(c for c, _ in cells) / len(cells)
    mr = sum(r for _, r in cells) / len(cells)
    pc, pr = min(cells, key=lambda t: (t[0] - mc) ** 2 + (t[1] - mr) ** 2)
    pins.append((name, pc + 0.5, pr + 0.5))

held = {v for row in visit for v in row if v}
missing = [PLACES[n - 1] for n in range(1, len(PLACES) + 1) if n not in held]
if missing:
    sys.exit('lost to overlaps, every cell taken by a neighbour: %s' % missing)

share = cos_area(visit) / cos_area(land) * 100

rows = []
for r in land:
    bits = ''.join(str(c) for c in r)
    rows.append(''.join('%x' % int(bits[i:i + 4], 2) for i in range(0, len(bits), 4)))
map_hex = ''.join(rows)
# Base 62: thirty-five places filled base 36, and the page's visitedAt() looks
# a character up in this same string rather than parsing a number.
digits = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
if len(PLACES) >= len(digits):
    sys.exit('more places than base-62 digits; VISIT needs a wider encoding')
visit_txt = ''.join(digits[visit[r][c]] for r in range(H) for c in range(W))

page = PAGE.read_text(encoding='utf-8')
subs = [
    (r"    var MAP = '[0-9a-f]+';", "    var MAP = '%s';" % map_hex),
    (r"    var VISIT = '[0-9a-zA-Z]+';", "    var VISIT = '%s';" % visit_txt),
    (r"    var SHARE = [\d.]+;", "    var SHARE = %.1f;" % share),
    (r"    var PLACES = \[\n(?:.*\n)*?    \];",
     "    var PLACES = [\n" + ',\n'.join("      ['%s', %s, %s]" % p for p in pins) + "\n    ];"),
]
for pattern, replacement in subs:
    page, count = re.subn(pattern, lambda _: replacement, page, count=1)
    if count != 1:
        sys.exit('could not find %s in index.html' % pattern[:24])
PAGE.write_text(page, encoding='utf-8')

print('%d places, %d land cells, %.1f%% of the land the map covers' %
      (len(PLACES), sum(sum(r) for r in land), share))
print('wrote', PAGE)
