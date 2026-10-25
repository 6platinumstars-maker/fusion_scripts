import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_smv16 as f, grip_reference_ellipse as e, grip_reference_hexagon as h, grip_twist as v

class SmV16LoftTests(unittest.TestCase):
    def test_exact_shared_ellipse_intervals(self):
        env=load_grip();g=env['GRIP_REFERENCE_POINT_G_MM']
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        ref7=e.from_a_lower(env['calculate_finger_a_line'](),direction)
        ref10=e.from_cd_hexagon(env['calculate_finger_c_line'](),env['calculate_finger_d_line']())['Ref10']
        split=e.point_at(ref7,0)
        first,second=f.sections(ref7,ref10,split,g)
        self.assertEqual(first['ends'],(split,g))
        self.assertEqual(second['ends'],(tuple(ref10['points'][1]),h.hexagon_data()['points'][2]))
        for data,piece in ((ref7,first),(ref10,second)):
            ends=[e.point_at(data,piece['start']),e.point_at(data,piece['start']+piece['sweep'])]
            for point in piece['ends']:self.assertLess(min(math.dist(point,q) for q in ends),1e-7)
            self.assertGreater(piece['sweep'],0)
            self.assertLess(piece['sweep'],data['sweep'])
        self.assertGreater((ref10['angles'][0]-second['start'])%math.tau,second['sweep'])
        wrong=e.from_cd_hexagon(env['calculate_finger_c_line'](),env['calculate_finger_d_line']())['Ref11']
        with self.assertRaises(ValueError):f.sections(ref7,wrong,split,g)
        old=e.from_cd_hexagon(env['calculate_finger_c_line'](),env['calculate_finger_d_line']())['Ref9']
        with self.assertRaises(ValueError):f.sections(ref7,old,split,g)

if __name__=='__main__':unittest.main()
