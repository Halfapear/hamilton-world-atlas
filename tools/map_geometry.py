"""Project vendored Natural Earth land using the same bounds as the app."""
import json
import math

PROJECTION = {'left': 30, 'top': 35, 'width': 940, 'height': 430}


def _clip_x(points, boundary, keep_right):
    """Clip a polygon against a vertical map edge, retaining intersections."""
    if not points:
        return []
    out = []
    previous = points[-1]
    prev_inside = (previous[0] >= boundary) if keep_right else (previous[0] <= boundary)
    for current in points:
        inside = (current[0] >= boundary) if keep_right else (current[0] <= boundary)
        if inside != prev_inside:
            ratio = (boundary - previous[0]) / (current[0] - previous[0])
            out.append((boundary, previous[1] + ratio * (current[1] - previous[1])))
        if inside:
            out.append(current)
        previous, prev_inside = current, inside
    return out


def _wrap_ring(points):
    """Unwrap longitude jumps, then clip wrapped copies to the world bounds."""
    width, left = PROJECTION['width'], PROJECTION['left']
    unwrapped = [points[0]]
    for x, y in points[1:]:
        x += round((unwrapped[-1][0] - x) / width) * width
        unwrapped.append((x, y))
    # Antarctica winds around the south pole: close via that pole rather than
    # drawing a false coast from +180 to -180 across the whole globe.
    if abs(unwrapped[-1][0] - unwrapped[0][0]) > width / 2:
        bottom = PROJECTION['top'] + PROJECTION['height']
        middle = (unwrapped[0][0] + unwrapped[-1][0]) / 2
        unwrapped.extend([(unwrapped[-1][0], bottom), (middle, bottom),
                          (unwrapped[0][0], bottom)])
    minimum = min(x for x, _ in unwrapped)
    maximum = max(x for x, _ in unwrapped)
    rings = []
    for shift in range(math.ceil((left - maximum) / width),
                       math.floor((left + width - minimum) / width) + 1):
        shifted = [(x + shift * width, y) for x, y in unwrapped]
        clipped = _clip_x(_clip_x(shifted, left, True), left + width, False)
        if len(clipped) >= 3:
            rings.append(clipped)
    return rings


def land_svg(path):
    topology = json.loads(path.read_text(encoding='utf-8'))
    transform = topology['transform']
    decoded = []
    for arc in topology['arcs']:
        x = y = 0
        points = []
        for dx, dy in arc:
            x += dx
            y += dy
            lon = x * transform['scale'][0] + transform['translate'][0]
            lat = y * transform['scale'][1] + transform['translate'][1]
            points.append((PROJECTION['left'] + (lon + 180) / 360 * PROJECTION['width'],
                           PROJECTION['top'] + (90 - lat) / 180 * PROJECTION['height']))
        decoded.append(points)

    paths = []
    for geometry in topology['objects']['land']['geometries']:
        polygons = geometry['arcs'] if geometry['type'] == 'MultiPolygon' else [geometry['arcs']]
        for polygon in polygons:
            rings = []
            for ring in polygon:
                points = []
                for index in ring:
                    arc = decoded[index] if index >= 0 else list(reversed(decoded[~index]))
                    points.extend(arc if not points else arc[1:])
                for clipped in _wrap_ring(points):
                    rings.append('M' + 'L'.join(f'{x:.3f},{y:.3f}' for x, y in clipped) + 'Z')
            paths.append('<path class="land" fill-rule="evenodd" d="' + ''.join(rings) + '"/>')
    return '\n'.join(paths)
