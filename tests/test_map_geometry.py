"""Regression tests for the embedded, offline map geometry."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from map_geometry import PROJECTION, land_svg


class MapGeometryTests(unittest.TestCase):
    def test_no_coastline_crosses_the_whole_map_at_the_antimeridian(self):
        svg = land_svg(ROOT / 'data' / 'world-land-110m.json')
        for ring in re.findall(r'M([^MZ]+)Z', svg):
            points = [tuple(map(float, p.split(','))) for p in ring.split('L')]
            for start, end in zip(points, points[1:] + points[:1]):
                self.assertLessEqual(abs(end[0] - start[0]), PROJECTION['width'] / 2,
                                     f'False antimeridian edge: {start} -> {end}')

    def test_land_stays_within_shared_projection_bounds(self):
        svg = land_svg(ROOT / 'data' / 'world-land-110m.json')
        points = re.findall(r'[ML]([-\d.]+),([-\d.]+)', svg)
        self.assertGreater(len(points), 4000)
        for x, y in points:
            self.assertGreaterEqual(float(x), PROJECTION['left'] - .001)
            self.assertLessEqual(float(x), PROJECTION['left'] + PROJECTION['width'] + .001)
            self.assertGreaterEqual(float(y), PROJECTION['top'] - .001)
            self.assertLessEqual(float(y), PROJECTION['top'] + PROJECTION['height'] + .001)


if __name__ == '__main__':
    unittest.main(verbosity=2)
