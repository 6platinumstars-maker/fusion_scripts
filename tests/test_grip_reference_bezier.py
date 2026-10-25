import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_reference_bezier as f, grip_twist as v, grip_width as w

class ReferenceBezierTests(unittest.TestCase):
    def test_displayed_guideline_endpoints_tangents_and_inside(self):
        env=load_grip();a=env['calculate_finger_a_line']()
        guide,_=env['calculate_guideline_points']('A',a)
        original=list(guide)
        guide[2]=v.add(original[2],v.mul(v.sub(original[1],original[2]),.25))
        data=f.curve_data(a)
        self.assertEqual(data['control_points_mm'],guide[:3])
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        shortened=w.quarter_l1_points('A',a,direction)
        center=v.mul(v.add(shortened["AF1'"],shortened["AH1'"]),.5)
        self.assertLess(math.dist(center,guide[2]),1e-9)
        self.assertAlmostEqual(math.dist(original[2],guide[2]),3.75,places=8)
        self.assertEqual(f.point_at(data,0),guide[0]);self.assertEqual(f.point_at(data,1),guide[2])
        h=1e-6
        for tangent,expected in ((v.sub(f.point_at(data,h),guide[0]),v.sub(guide[1],guide[0])),
                                 (v.sub(guide[2],f.point_at(data,1-h)),v.sub(guide[2],guide[1]))):
            self.assertLess(v.norm(v.sub(v.unit(tangent),v.unit(expected))),1e-5)
        normal=v.unit(v.cross(v.sub(guide[1],guide[0]),v.sub(guide[2],guide[0])))
        for i in range(1,100):
            p=f.point_at(data,i/100)
            self.assertAlmostEqual(v.dot(v.sub(p,guide[0]),normal),0,places=8)
            for start,end in zip(guide[:3],(guide[1],guide[2],guide[0])):
                self.assertGreater(v.dot(v.cross(v.sub(end,start),v.sub(p,start)),normal),0)
        a['guideline_points_mm']=original
        self.assertEqual(data,f.curve_data(a))
        changed=f.curve_data(env['calculate_finger_a_line'](lengths_mm=(16,20,17,11,14)))
        self.assertNotEqual(data['control_points_mm'][1:],changed['control_points_mm'][1:])
        with self.assertRaises(ValueError):f.curve_data({'points_mm':[(0,0,0),(1,0,0),(2,0,0)]})

if __name__=='__main__':unittest.main()
