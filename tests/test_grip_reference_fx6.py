import unittest
import math
from test_grip_twist import load_grip
from fusion_app import grip_reference_fx6 as f,grip_twist as v


class Fx6PointTests(unittest.TestCase):
    def test_current_points_are_inside_segments_and_follow_lengths(self):
        e=load_grip();data={k:e['calculate_finger_'+k.lower()+'_line']() for k in 'CD'}
        direction=v.sub(e['GRIP_FINGER_A_POINT_P_MM'],e['GRIP_FINGER_D_POINT_P_MM'])
        points=f.point_data(data,direction,(0,0,-6),(0,0,1))
        expected=[(-44.13609722665777,-23.14693037219348,-6),(-59.23834345932146,2.64776868767,-6)]
        for p,q in zip(points,expected):
            self.assertLess(math.dist(p['point_mm'],q),1e-9)
            self.assertTrue(p['on_segment'])
            a,b=p['line_mm'];self.assertLess(v.norm(v.cross(v.sub(p['point_mm'],a),v.sub(b,a))),1e-8)
        data['D']=e['calculate_finger_d_line'](twist_deg=20)
        changed=f.point_data(data,direction,(0,0,-6),(0,0,1))
        self.assertNotEqual(changed[0]['point_mm'],points[0]['point_mm'])
        self.assertEqual(changed[1]['point_mm'],points[1]['point_mm'])

    def test_parallel_coplanar_and_extension(self):
        for a,b in [((0,0,-6),(1,0,-6)),((0,0,0),(1,0,0)),((0,0,0),(0,0,0))]:
            with self.assertRaises(ValueError):f.intersection(a,b,(0,0,-6),(0,0,1))
        self.assertFalse(f.intersection((0,0,0),(0,0,1),(0,0,-6),(0,0,1))['on_segment'])


if __name__=='__main__':unittest.main()
