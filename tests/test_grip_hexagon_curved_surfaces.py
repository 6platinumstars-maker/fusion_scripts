import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_hexagon_curved_surfaces as s, grip_reference_ellipse as e, grip_twist as v

class CurvedHexagonSurfaceTests(unittest.TestCase):
    def test_only_dg1_to_hexagon_interval_and_curved_midpoint(self):
        env=load_grip();c=env['calculate_finger_c_line']();d=env['calculate_finger_d_line']()
        data=e.from_cd_hexagon(c,d)
        for identifier in ('Ref9','Ref10','Ref11'):
            curve=data[identifier];piece=s.section(curve)
            self.assertEqual(piece['ends'][0],d['points_mm'][1])
            self.assertEqual(piece['ends'][1],curve['points'][2])
            ends=[e.point_at(curve,t) for t in (piece['start'],piece['start']+piece['sweep'])]
            for p in piece['ends']:self.assertLess(min(math.dist(p,q) for q in ends),1e-8)
            self.assertGreater((curve['angles'][0]-piece['start'])%math.tau,piece['sweep'])
            mid=e.point_at(curve,piece['start']+piece['sweep']/2)
            chord=v.sub(piece['ends'][1],piece['ends'][0])
            distance=v.norm(v.cross(v.sub(mid,piece['ends'][0]),chord))/v.norm(chord)
            self.assertGreater(distance,.1)
            self.assertGreater(piece['sweep'],0)
            self.assertLess(piece['sweep'],curve['sweep'])

if __name__=='__main__':unittest.main()
