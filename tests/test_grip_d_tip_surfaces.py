import math
import unittest
from types import SimpleNamespace as NS
from test_grip_twist import load_grip
from fusion_app import grip_d_tip_surfaces as f, grip_width as w, grip_twist as v, grip_hexagon_fixed_surfaces as h


def body(points):
    return NS(vertices=[NS(geometry=NS(**dict(zip('xyz',(x/10 for x in p))))) for p in points])


class DTipSurfacesTests(unittest.TestCase):
    def test_resolve_only_fx5_actual_vertices(self):
        actual=(-29.844389426562834,-24.822587497948433,-5.999585091460191)
        manifest={'faces':[{'fixed_id':'Fx3'},{'fixed_id':'Fx5'},{'fixed_id':'Fx5'}]}
        resolved=f.resolve_fixed_points(manifest,[body(f.FX5_HINTS_MM),body([actual]),body([f.FX5_HINTS_MM[1]])])
        self.assertLess(math.dist(resolved[0],actual),1e-12)
        self.assertGreater(math.dist(resolved[0],f.FX5_HINTS_MM[0]),.0001)
        with self.assertRaises(RuntimeError):
            f.resolve_fixed_points({'faces':[{'fixed_id':'Fx3'}]},[body(f.FX5_HINTS_MM)])
        with self.assertRaises(RuntimeError):
            f.resolve_fixed_points({'faces':[{'fixed_id':'Fx5'}]},[body([f.FX5_HINTS_MM[1]])])

    def test_shared_edge_and_d_tip_follow_width(self):
        env=load_grip();d=env['calculate_finger_d_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        faces=f.face_data(d,direction,f.FX5_HINTS_MM)
        width={name:p for face in w.output_faces('D',d,direction) for name,p in zip(face['names'],face['corners'])}
        self.assertEqual(faces[0]['corners'],[width['F5'],*f.FX5_HINTS_MM])
        from fusion_app import grip_reference_fx6
        self.assertEqual(faces[1]['corners'],[grip_reference_fx6.tip_point('D',d,direction),width['F5'],f.FX5_HINTS_MM[0]])
        self.assertEqual(faces[0]['corners'][:2],faces[1]['corners'][1:])
        fx20=h.face_data(d,direction)[3]
        self.assertEqual([x['identifier'] for x in faces],['SmV13','SmV14','SmV15'])
        self.assertEqual(faces[2]['corners'],[fx20['corners'][3],fx20['corners'][0],f.FX5_HINTS_MM[1]])
        self.assertEqual(faces[2]['corners'][::2],faces[0]['corners'][::2])
        for face in faces:self.assertGreater(face['area_mm2'],0)
        changed=f.face_data(env['calculate_finger_d_line'](twist_deg=20),direction,f.FX5_HINTS_MM)
        for before,after in zip(faces,changed):
            self.assertEqual(before['corners'][-1],after['corners'][-1])
            self.assertGreater(math.dist(before['corners'][0],after['corners'][0]),.01)
        self.assertEqual(faces[0]['corners'][1],changed[0]['corners'][1])
        self.assertEqual(faces[2]['corners'][1:],changed[2]['corners'][1:])
        with self.assertRaises(ValueError):f.face_data(d,direction,[f.FX5_HINTS_MM[1]]*2)

if __name__=='__main__':unittest.main()
