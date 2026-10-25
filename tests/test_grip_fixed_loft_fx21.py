import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_fixed_loft_fx21 as f, grip_reference_ellipse as ellipse, grip_twist as v

class Fx21Tests(unittest.TestCase):
    def data(self):
        env=load_grip()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        return ellipse.from_a_lower(env['calculate_finger_a_line'](),direction)

    def test_correct_subarc_and_actual_major_endpoint(self):
        data=self.data();piece=f.section(data)
        self.assertLess(math.dist(piece['split'],f.SPLIT_HINT_MM),.001)
        self.assertLess(min(math.dist(p,f.END_MM) for p in piece['ends']),1e-7)
        self.assertLess(min(math.dist(p,piece['split']) for p in piece['ends']),1e-7)
        self.assertGreater(piece['sweep'],0)
        self.assertLess(piece['sweep'],data['sweep'])
        for i in range(21):
            t=piece['start']+piece['sweep']*i/20
            self.assertLessEqual((t-data['start'])%math.tau,data['sweep']+1e-8)
        # Ref7's G is outside this trimmed endpoint-to-major-tip interval.
        self.assertGreater((data['via']-piece['start'])%math.tau,piece['sweep'])

    def test_reject_wrong_ellipse_or_missing_interval(self):
        data=self.data()
        with self.assertRaises(ValueError):f.section(dict(data,center=(0,0,0)))
        with self.assertRaises(ValueError):f.section(dict(data,start=.1,sweep=.2))
        with self.assertRaises(ValueError):f.section(dict(data,points=(*data['points'][:2],(0,0,0))))

if __name__=='__main__':unittest.main()
