import ast
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fusion_app import grip_twist as t


def load_grip():
    tree = ast.parse((ROOT/'fusion_app/grip.py').read_text())
    tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.Assign))]
    env = {'math': math, '__package__': 'fusion_app'}
    exec(compile(tree, 'grip.py', 'exec'), env)
    return env


class TwistTests(unittest.TestCase):
    finger = "a"
    degrees = 20
    lengths = (12,25,17,11,14)
    def setUp(self):
        self.e = load_grip()
        self.old = self.e[f'calculate_finger_{self.finger}_line'](twist_deg=0)
        self.new = self.e[f'calculate_finger_{self.finger}_line']()

    def test_closure_lengths_and_preserved_angles(self):
        pts = self.new['points_mm']
        self.assertEqual(pts[0], self.old['points_mm'][0])
        self.assertEqual(pts[-1], self.old['points_mm'][-1])
        for i, length in enumerate(self.lengths):
            self.assertAlmostEqual(t.norm(t.sub(pts[i+1], pts[i])), length, places=8)
        for i in (1,3,4):
            self.assertAlmostEqual(self.new['angles_deg'][i], self.old['angles_deg'][i], places=8)
        self.assertNotAlmostEqual(self.new['angles_deg'][2], self.old['angles_deg'][2], places=3)

    def test_two_planes_and_twist(self):
        p = self.new['points_mm']
        u = t.unit(t.sub(p[2], p[1]))
        n1 = t.unit(t.cross(t.sub(p[1],p[0]), u))
        n2 = t.unit(t.cross(u, t.sub(p[3],p[2])))
        self.assertAlmostEqual(t.angle(n1,n2),self.degrees,places=8)
        self.assertAlmostEqual(t.dot(t.sub(p[2],p[0]),n1),0,places=8)
        for i in (1,4,5):
            self.assertAlmostEqual(t.dot(t.sub(p[i],p[2]),n2),0,places=8)
        self.assertEqual(self.new["twist_joint_index"],2)
        self.assertLess(self.new['direction_point_b_plane_distance_after_mm'], self.new['direction_point_b_plane_distance_before_mm'])

    def test_other_fingers_unchanged(self):
        for f in 'BCD':
            e=self.e
            old=e['calculate_finger_line'](e[f'GRIP_FINGER_{f}_POINT_P_MM'],e[f'GRIP_FINGER_{f}_POINT_P_PRIME_MM'],e[f'GRIP_FINGER_{f}_LENGTHS_MM'],e[f'GRIP_FINGER_{f}_ANGLES_DEG'],prefer_far_from_o=f!='D')
            actual = e[f'calculate_finger_{f.lower()}_line'](**({} if f == 'B' else {'twist_deg': 0}))
            self.assertEqual(old['points_mm'], actual['points_mm'])
            self.assertEqual(old['angles_deg'], actual['angles_deg'])

    def test_invalid_angle(self):
        for angle in (-1,180,float('nan')):
            with self.assertRaises(ValueError): self.e[f'calculate_finger_{self.finger}_line'](twist_deg=angle)

class CTwistTests(TwistTests):
    finger = 'c'
    degrees = 10
    lengths = (30,10,15,18,16)


class DTwistTests(TwistTests):
    finger = 'd'
    degrees = 30
    lengths = (37,14,10,10,15)


class ConfirmedATests(unittest.TestCase):
    def test_restored_axis_reproduces_original_a(self):
        e = load_grip()
        data = e['calculate_finger_a_line'](twist_deg=0)
        g = e['GRIP_REFERENCE_POINT_G_MM']
        b = t.sub(e['GRIP_FINGER_B_POINT_P_MM'],g)
        bn = t.cross(b,t.cross(b,t.sub(e['GRIP_FINGER_B_POINT_P_PRIME_MM'],g)))
        an = t.cross(t.sub(e['GRIP_FINGER_A_POINT_P_MM'],g),t.sub(e['GRIP_FINGER_A_POINT_P_PRIME_MM'],g))
        actual = e['calculate_finger_a_line']()['points_mm']
        expected = [(-90.,0.,23.),(-93.74675215018132,8.145771724031084,30.975478126425227),
                    (-82.98429248934364,30.707652184512884,31.337434112383857),
                    (-70.88952614083018,42.25748844140277,28.28490902421532),
                    (-61.20340689176109,41.036555525044825,23.216534856243182),(-52.5,32.2,16.723)]
        for a,b in zip(actual,expected):
            self.assertLess(t.norm(t.sub(a,b)),1e-9)


if __name__=='__main__': unittest.main()
