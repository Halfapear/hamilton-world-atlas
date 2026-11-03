#!/usr/bin/env python3
"""Build the self-contained Hamilton World Atlas HTML from editable JSON data."""
from pathlib import Path
import json
from map_geometry import PROJECTION, land_svg
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'hamilton-world.json'
TEMPLATE = ROOT / 'src' / 'index.template.html'
OUTPUT = ROOT / 'index.html'
obj = json.loads(DATA.read_text(encoding='utf-8'))
obj['mapProjection'] = PROJECTION
stops = obj.get('stops', [])
productions = obj.get('productions', [])
if not stops or not productions:
    raise SystemExit('Data must include at least one stop and one production')
stop_ids = [s.get('id') for s in stops]
production_ids = [p.get('id') for p in productions]
if len(set(stop_ids)) != len(stop_ids) or any(not x for x in stop_ids):
    raise SystemExit('Stop IDs must be present and unique')
if len(set(production_ids)) != len(production_ids) or any(not x for x in production_ids):
    raise SystemExit('Production IDs must be present and unique')
if any(s.get('productionId') not in set(production_ids) for s in stops):
    raise SystemExit('Every stop must reference a known productionId')
for stop in stops:
    if not all(isinstance(stop.get(k), (int, float)) and not isinstance(stop[k], bool)
               and -limit <= stop[k] <= limit for k, limit in [('lat', 90), ('lon', 180)]):
        raise SystemExit(f'Invalid latitude/longitude for {stop.get("id")}')
template = TEMPLATE.read_text(encoding='utf-8')
for placeholder, source in [('__MOBILE_POLISH__','mobile-polish.css'),('__QUICK_START__','quick-start.js')]:
    if template.count(placeholder)!=1:
        raise SystemExit('Expected one shared UI placeholder: '+placeholder)
    template=template.replace(placeholder,(ROOT/'src'/source).read_text(encoding='utf-8'))
marker = '__HAMILTON_DATA__'
if template.count(marker) != 1:
    raise SystemExit('Template must contain exactly one data placeholder')
html = template.replace(marker, json.dumps(obj, ensure_ascii=False, separators=(',', ':')))
if html.count('__WORLD_LAND__') != 1:
    raise SystemExit('Template must contain exactly one land placeholder')
html = html.replace('__WORLD_LAND__', land_svg(ROOT / 'data' / 'world-land-110m.json'))
OUTPUT.write_text(html, encoding='utf-8')
print(f'Built {OUTPUT} ({len(stops)} stops, {len(productions)} productions, {len(obj.get("regions", []))} regions)')
