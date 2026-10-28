#!/usr/bin/env python3
"""Build the self-contained Hamilton World Atlas HTML from editable JSON data."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'hamilton-world.json'
TEMPLATE = ROOT / 'src' / 'index.template.html'
OUTPUT = ROOT / 'index.html'
obj = json.loads(DATA.read_text(encoding='utf-8'))
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
template = TEMPLATE.read_text(encoding='utf-8')
marker = '__HAMILTON_DATA__'
if template.count(marker) != 1:
    raise SystemExit('Template must contain exactly one data placeholder')
html = template.replace(marker, json.dumps(obj, ensure_ascii=False, separators=(',', ':')))
OUTPUT.write_text(html, encoding='utf-8')
print(f'Built {OUTPUT} ({len(stops)} stops, {len(productions)} productions, {len(obj.get("regions", []))} regions)')
