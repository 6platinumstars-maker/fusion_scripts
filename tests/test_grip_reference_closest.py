import unittest
from test_grip_twist import load_grip
from fusion_app import grip_reference_closest as f, grip_twist as v, grip_width as w

class ClosestReferenceTests(unittest.TestCase):
    def test_current_h_side_point_and_perpendicular_distance(self):
        env=load_grip();a=env['calculate_finger_a_line']();c=env['calculate_finger_c_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        result=f.point_data(a,c,direction)
        self.assertTrue(0<result['first_parameter']<1)
        face=next(face for face in w.output_faces('A',a,direction) if face['index']==1)
        width=dict(zip(face['names'],face['corners']))
        self.assertEqual(result['line2_mm'],(width['H2'],width['H1']))
        self.assertTrue(0<result['second_parameter']<1)
        delta=v.sub(result['point_mm'],result['other_point_mm'])
        for key in ('line1_mm','line2_mm'):
            p,q=result[key];self.assertAlmostEqual(v.dot(delta,v.unit(v.sub(q,p))),0,places=9)
        self.assertAlmostEqual(result['distance_mm'],.5539492441099727,places=8)
        self.assertLess(v.norm(v.sub(result['point_mm'],(-85.17634481847304,25.55447165918472,23.376336213932674))),1e-8)
        reverse=f.closest_lines(*result['line2_mm'],*result['line1_mm'])
        self.assertAlmostEqual(reverse['distance_mm'],result['distance_mm'],places=10)
        self.assertLess(v.norm(v.sub(reverse['other_point_mm'],result['point_mm'])),1e-8)

    def test_crossing_parallel_and_degenerate(self):
        d=f.closest_lines((0,0,0),(1,0,0),(2,-1,0),(2,1,0))
        self.assertEqual(d['point_mm'],(2,0,0));self.assertEqual(d['distance_mm'],0)
        with self.assertRaises(ValueError):f.closest_lines((0,0,0),(1,0,0),(0,1,0),(1,1,0))
        with self.assertRaises(ValueError):f.closest_lines((0,0,0),(0,0,0),(0,1,0),(1,1,0))

if __name__=='__main__':unittest.main()
