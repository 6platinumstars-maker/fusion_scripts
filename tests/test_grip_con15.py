import unittest
from test_grip_twist import load_grip
from fusion_app import grip_con15 as f, grip_reference_bezier as b, grip_width as w, grip_twist as v

class Con15Tests(unittest.TestCase):
    def test_exact_ref12_and_con13_connections(self):
        env=load_grip();a=env['calculate_finger_a_line']();c=env['calculate_finger_c_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        points=f.corners(a,c,direction);control=b.curve_data(a)['control_points_mm']
        self.assertEqual(points,[control[0],w.quarter_l1_points('C',c,direction)["CH1'"],control[2]])
        f.validate_arc_ends(points,[control[0],control[2]])
        f.validate_arc_ends(points,[control[2],control[0]])
        with self.assertRaises(ValueError):f.validate_arc_ends(points,[control[0],a['points_mm'][2]])
        changed=f.corners(a,env['calculate_finger_c_line'](twist_deg=5),direction)
        self.assertEqual(points[::2],changed[::2]);self.assertNotEqual(points[1],changed[1])

if __name__=='__main__':unittest.main()
