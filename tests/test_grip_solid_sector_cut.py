import unittest
import math
from fusion_app import grip_solid_sector_cut as s

class SectorTests(unittest.TestCase):
    def test_minor_sector_uses_radius_and_preserves_hint_directions(self):
        d=s.sector_data()
        self.assertLess(d['sweep_radians'],0)
        self.assertLess(abs(d['sweep_radians']),math.pi)
        for p,h in zip(d['ends_mm'],s.HINTS_MM):
            self.assertAlmostEqual(math.dist(p,s.CENTER_MM),35.565)
            self.assertLess(math.dist(p,h),0.02)
            self.assertAlmostEqual((p[0]-s.CENTER_MM[0])*(h[1]-s.CENTER_MM[1])-(p[1]-s.CENTER_MM[1])*(h[0]-s.CENTER_MM[0]),0)
        self.assertAlmostEqual(s.END_Z_MM-s.CENTER_MM[2],0.8)
