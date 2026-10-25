import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_reference_ellipse as f, grip_fixed_lines as old, grip_twist as v

class ReferenceEllipseTests(unittest.TestCase):
    def test_three_points_projected_axes_ratio_and_via_interval(self):
        env=load_grip();finger=env['calculate_finger_a_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        d=f.from_finger(finger,direction);reference=old.ellipse_data()
        from fusion_app import grip_width
        al1=grip_width.output_faces('A',finger,direction)[0]
        self.assertEqual(d['points'][0],al1['corners'][al1['names'].index('F1')])
        for p,t in zip(d['points'],d['angles']):
            self.assertLess(math.dist(p,f.point_at(d,t)),1e-9)
            self.assertAlmostEqual(v.dot(v.sub(p,d['center']),d['normal']),0,places=9)
        projected=v.unit(v.sub(tuple(reference['u'])+(0.,),v.mul(d['normal'],v.dot(tuple(reference['u'])+(0.,),d['normal']))))
        self.assertLess(math.dist(d['u'],projected),1e-10)
        self.assertAlmostEqual(v.dot(d['u'],d['v']),0,places=12)
        self.assertAlmostEqual(d['major']/d['minor'],reference['major']/reference['minor'],places=12)
        self.assertLess((d['via']-d['start'])%math.tau,d['sweep'])
        ends=[f.point_at(d,t) for t in (d['start'],d['start']+d['sweep'])]
        for p in (d['points'][0],d['points'][2]):self.assertLess(min(math.dist(p,q) for q in ends),1e-9)
        self.assertEqual(d['points'][2],(-29.854,-35.0,10.492))
        changed=f.from_finger(env['calculate_finger_a_line'](twist_deg=10),direction)
        self.assertGreater(math.dist(d['points'][0],changed['points'][0]),.01)
        self.assertEqual(d['points'][1:],changed['points'][1:])

    def test_ref6_uses_current_cg1_dg1_and_preserves_ratio(self):
        env=load_grip();c=env['calculate_finger_c_line']();d=env['calculate_finger_d_line']()
        data=f.from_cd(c,d);old_data=old.ellipse_data()
        self.assertEqual(data['points'],(c['points_mm'][1],d['points_mm'][1],(-29.854,-35.,-6.)))
        for p,t in zip(data['points'],data['angles']):
            self.assertLess(math.dist(p,f.point_at(data,t)),1e-9)
        self.assertAlmostEqual(data['major']/data['minor'],old_data['major']/old_data['minor'],places=12)
        projected=v.unit(v.sub(tuple(old_data['u'])+(0.,),v.mul(data['normal'],v.dot(tuple(old_data['u'])+(0.,),data['normal']))))
        self.assertLess(math.dist(data['u'],projected),1e-10)
        self.assertAlmostEqual(v.dot(data['u'],data['v']),0,places=12)
        self.assertLess((data['via']-data['start'])%math.tau,data['sweep'])
        ends=[f.point_at(data,data['start']),f.point_at(data,data['start']+data['sweep'])]
        for p in (c['points_mm'][1],f.REF6_END_MM):
            self.assertLess(min(math.dist(p,q) for q in ends),1e-9)
        changed=f.from_cd(env['calculate_finger_c_line'](twist_deg=5),d)
        self.assertGreater(math.dist(changed['points'][0],data['points'][0]),.01)
        self.assertEqual(changed['points'][1:],data['points'][1:])

    def test_ref7_uses_af1_and_g_but_lower_endpoint(self):
        env=load_grip();a=env['calculate_finger_a_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        ref5=f.from_finger(a,direction);data=f.from_a_lower(a,direction)
        self.assertEqual(data['points'][:2],ref5['points'][:2])
        self.assertEqual(data['points'][2],(-29.854,-35.,-6.))
        self.assertEqual(ref5['points'][2],(-29.854,-35.,10.492))
        self.assertAlmostEqual(data['major']/data['minor'],ref5['major']/ref5['minor'],places=12)
        for p,t in zip(data['points'],data['angles']):
            self.assertLess(math.dist(p,f.point_at(data,t)),1e-9)
        self.assertLess((data['via']-data['start'])%math.tau,data['sweep'])
        ends=[f.point_at(data,data['start']),f.point_at(data,data['start']+data['sweep'])]
        for p in (data['points'][0],data['points'][2]):
            self.assertLess(min(math.dist(p,q) for q in ends),1e-9)

    def test_hexagon_curves_pass_cg1_dg1_and_exact_hexagon_vertices(self):
        from fusion_app import grip_reference_hexagon as hexagon
        env=load_grip();c=env['calculate_finger_c_line']();d=env['calculate_finger_d_line']()
        curves=f.from_cd_hexagon(c,d);vertices=hexagon.hexagon_data()['points'];reference=old.ellipse_data()
        self.assertEqual(set(curves),{'Ref9','Ref10','Ref11'})
        for identifier,label,index in f.HEXAGON_CURVES:
            data=curves[identifier]
            self.assertEqual(data['points'],(c['points_mm'][1],d['points_mm'][1],vertices[index]))
            for p,t in zip(data['points'],data['angles']):
                self.assertLess(math.dist(p,f.point_at(data,t)),1e-8)
            self.assertAlmostEqual(data['major']/data['minor'],reference['major']/reference['minor'],places=12)
            self.assertLess((data['via']-data['start'])%math.tau,data['sweep'])
            projected=v.unit(v.sub(tuple(reference['u'])+(0.,),v.mul(data['normal'],v.dot(tuple(reference['u'])+(0.,),data['normal']))))
            self.assertLess(math.dist(data['u'],projected),1e-10)
            ends=[f.point_at(data,data['start']),f.point_at(data,data['start']+data['sweep'])]
            for p in (data['points'][0],data['points'][2]):
                self.assertLess(min(math.dist(p,q) for q in ends),1e-8)
        changed=f.from_cd_hexagon(c,env['calculate_finger_d_line'](twist_deg=20))
        for identifier in curves:
            self.assertEqual(curves[identifier]['points'][0],changed[identifier]['points'][0])
            self.assertEqual(curves[identifier]['points'][2],changed[identifier]['points'][2])
            self.assertGreater(math.dist(curves[identifier]['points'][1],changed[identifier]['points'][1]),.01)

    def test_hexagon_curves_follow_cg1_changes(self):
        env=load_grip();c=env['calculate_finger_c_line']();d=env['calculate_finger_d_line']()
        before=f.from_cd_hexagon(c,d)
        after=f.from_cd_hexagon(env['calculate_finger_c_line'](twist_deg=5),d)
        for key in before:
            self.assertGreater(math.dist(before[key]['points'][0],after[key]['points'][0]),.01)
            self.assertEqual(before[key]['points'][1:],after[key]['points'][1:])

    def test_collinear_points_rejected(self):
        with self.assertRaises(ValueError):f.fit_ellipse(((0,0,0),(1,1,1),(2,2,2)))

if __name__=='__main__':unittest.main()
