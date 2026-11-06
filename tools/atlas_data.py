"""Canonical JSON loading and release data invariants for both builders."""
import json
import math
import re
from map_geometry import PROJECTION

def load_data(root):
    data = json.loads((root / 'data/hamilton-world.json').read_text(encoding='utf-8'))
    data['mapProjection'] = PROJECTION
    stops, productions = data.get('stops', []), data.get('productions', [])
    if not stops or not productions:
        raise ValueError('Data must include stops and productions')
    stop_ids = [s.get('id') for s in stops]
    prod_ids = [p.get('id') for p in productions]
    if any(not x for x in stop_ids + prod_ids) or len(set(stop_ids)) != len(stop_ids) or len(set(prod_ids)) != len(prod_ids):
        raise ValueError('Stop and production IDs must be present and unique')
    if any(s.get('productionId') not in set(prod_ids) for s in stops):
        raise ValueError('Unknown productionId')
    leads = data.get('tourLeads', [])
    lead_ids = [s.get('id') for s in leads]
    if any(not x for x in lead_ids) or len(set(lead_ids)) != len(lead_ids) or set(lead_ids) & set(stop_ids):
        raise ValueError('Lead IDs must be unique and separate from official stops')
    for point in stops + leads:
        for field, limit in [('lat', 90), ('lon', 180)]:
            value = point.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not -limit <= value <= limit:
                raise ValueError('Invalid coordinate for ' + point['id'])
    for lead in leads:
        if any(key in lead for key in ('bookingUrl', 'prices', 'ticketOpen', 'startDate', 'endDate')):
            raise ValueError('Unconfirmed leads cannot contain booking fields')
        if not all(lead.get(key) for key in ('evidenceLevel', 'verificationStatus', 'dateText', 'sources')):
            raise ValueError('Lead must retain provenance and verification status')
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?', data['meta']['version']):
        raise ValueError('Invalid release version')
    return data

def script_json(data):
    # Do not let a future source title close the HTML script element.
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
