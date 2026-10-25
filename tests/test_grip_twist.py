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
    lengths = (15,20,17,11,14)
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
        if self.finger in ('a','c','d'):
            self.assertNotAlmostEqual(self.new['angles_deg'][2], self.old['angles_deg'][2], places=3)

    def test_two_planes_and_twist(self):
        p = self.new['points_mm']
        k=self.new['twist_joint_index']
        u=t.unit(t.sub(p[k],p[k-1]))
        n1=(self.new['front_plane_normal'] if k==1 else t.unit(t.cross(t.sub(p[1],p[0]),u)))
        n2=t.unit(t.cross(t.sub(p[4],p[3]),t.sub(p[5],p[4])))
        self.assertAlmostEqual(t.angle(n1,n2),self.degrees,places=8)
        for i in range(k+1):
            self.assertAlmostEqual(t.dot(t.sub(p[i],p[0]),n1),0,places=8)
        for i in range(k,6):
            self.assertAlmostEqual(t.dot(t.sub(p[i],p[k]),n2),0,places=8)
        self.assertAlmostEqual(t.dot(u,n1),0,places=8)
        self.assertEqual(k,2)
        self.assertGreater(max(t.norm(t.sub(a,b)) for a,b in zip(p,self.old['points_mm'])),.1)
        self.assertLess(self.new['direction_point_b_plane_distance_after_mm'], self.new['direction_point_b_plane_distance_before_mm'])

    def test_other_fingers_unchanged(self):
        for f in 'BCD':
            e=self.e
            old=e['calculate_finger_line'](e[f'GRIP_FINGER_{f}_POINT_P_MM'],e[f'GRIP_FINGER_{f}_POINT_P_PRIME_MM'],e[f'GRIP_FINGER_{f}_LENGTHS_MM'],e[f'GRIP_FINGER_{f}_ANGLES_DEG'],prefer_far_from_o=f!='D',max_total_turn_deg=e['GRIP_FINGER_C_MAX_TOTAL_TURN_DEG'] if f=='C' else 180.0)
            actual = e[f'calculate_finger_{f.lower()}_line'](**({} if f == 'B' else {'twist_deg': 0}))
            self.assertEqual(old['points_mm'], actual['points_mm'])
            self.assertEqual(old['angles_deg'], actual['angles_deg'])

    def test_invalid_angle(self):
        for angle in (-1,180,float('nan')):
            with self.assertRaises(ValueError): self.e[f'calculate_finger_{self.finger}_line'](twist_deg=angle)

class CTwistTests(TwistTests):
    finger = 'c'
    degrees = 10
    lengths = (15,30,15,18,16)


class DTwistTests(TwistTests):
    finger = 'd'
    degrees = 30
    lengths = (30,23,15,15,15)


class CExtendedTurnTests(unittest.TestCase):
    def test_c_requires_extension_and_preserves_requested_lengths_and_endpoint(self):
        e=load_grip()
        args=(e['GRIP_FINGER_C_POINT_P_MM'],e['GRIP_FINGER_C_POINT_P_PRIME_MM'],
              (15,30,15,18,16),e['GRIP_FINGER_C_ANGLES_DEG'])
        with self.assertRaises(ValueError):e['calculate_finger_line'](*args)
        flat=e['calculate_finger_c_line'](twist_deg=0)
        total=sum(180-a for a in flat['angles_deg'][1:])
        self.assertAlmostEqual(total,202.00427386208938,places=8)
        self.assertLess(total,e['GRIP_FINGER_C_MAX_TOTAL_TURN_DEG'])
        self.assertEqual(flat['points_mm'][-1],e['GRIP_FINGER_C_POINT_P_MM'])
        extended=e['calculate_finger_line'](*args,max_total_turn_deg=210)
        self.assertEqual(flat['points_mm'],extended['points_mm'])

    def test_extension_keeps_existing_under_180_solutions(self):
        e=load_grip()
        for finger in 'ABD':
            args=(e[f'GRIP_FINGER_{finger}_POINT_P_MM'],e[f'GRIP_FINGER_{finger}_POINT_P_PRIME_MM'],
                  e[f'GRIP_FINGER_{finger}_LENGTHS_MM'],e[f'GRIP_FINGER_{finger}_ANGLES_DEG'])
            self.assertEqual(e['calculate_finger_line'](*args),e['calculate_finger_line'](*args,max_total_turn_deg=210))

class UpdatedABLengthsTests(unittest.TestCase):
    def test_displayed_parallelogram_lengths_and_fixed_endpoints(self):
        env=load_grip()
        for finger,expected in (('A',(20,15,17,11,14)),('B',(15,20,21,18,13))):
            data=env['calculate_finger_'+finger.lower()+'_line']()
            points,names=env['calculate_guideline_points'](finger,data)
            self.assertEqual(names[1],finger+"G1'")
            for a,b,length in zip(points,points[1:],expected):
                self.assertAlmostEqual(math.dist(a,b),length,places=8)
            self.assertEqual(points[0],env['GRIP_REFERENCE_POINT_G_MM'])
            self.assertEqual(points[-1],env['GRIP_FINGER_'+finger+'_POINT_P_MM'])

class ConfirmedATests(unittest.TestCase):
    def test_restored_axis_reproduces_original_a(self):
        e = load_grip()
        data = e['calculate_finger_a_line'](lengths_mm=(12,25,17,11,14),twist_deg=0)
        g = e['GRIP_REFERENCE_POINT_G_MM']
        b = t.sub(e['GRIP_FINGER_B_POINT_P_MM'],g)
        bn = t.cross(b,t.cross(b,t.sub(e['GRIP_FINGER_B_POINT_P_PRIME_MM'],g)))
        an = t.cross(t.sub(e['GRIP_FINGER_A_POINT_P_MM'],g),t.sub(e['GRIP_FINGER_A_POINT_P_PRIME_MM'],g))
        actual = e['calculate_finger_a_line'](lengths_mm=(12,25,17,11,14))['points_mm']
        expected = [(-90.,0.,23.),(-93.74675215018132,8.145771724031084,30.975478126425227),
                    (-82.98429248934364,30.707652184512884,31.337434112383857),
                    (-70.88952614083018,42.25748844140277,28.28490902421532),
                    (-61.20340689176109,41.036555525044825,23.216534856243182),(-52.5,32.2,16.723)]
        for a,b in zip(actual,expected):
            self.assertLess(t.norm(t.sub(a,b)),1e-9)


if __name__=='__main__': unittest.main()
