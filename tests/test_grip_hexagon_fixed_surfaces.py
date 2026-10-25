import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_hexagon_fixed_surfaces as f, grip_reference_hexagon as h, grip_width as w, grip_twist as v

class HexagonFixedSurfacesTests(unittest.TestCase):
    def test_cap_and_three_exact_width_connections(self):
        env=load_grip();d=env['calculate_finger_d_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        faces=f.face_data(d,direction);hexagon=dict(zip('ABCDEF',h.hexagon_data()['points']))
        width={name:p for face in w.output_faces('D',d,direction) for name,p in zip(face['names'],face['corners'])}
        self.assertEqual([x['identifier'] for x in faces],['Fx17','Fx18','Fx19','Fx20'])
        self.assertEqual(faces[0]['corners'],h.hexagon_data()['points'])
        self.assertAlmostEqual(faces[0]['area_mm2'],259.8076211353316)
        for face,a,b,first,last in zip(faces[1:],'AAE','BFF',(2,4,4),(3,3,5)):
            self.assertEqual(face['corners'],[hexagon[a],hexagon[b],width['F'+str(first)],width['F'+str(last)]])
            self.assertIsNone(face['area_mm2'])
        self.assertEqual([faces[1]['corners'][0],faces[1]['corners'][3]],
                         [faces[2]['corners'][0],faces[2]['corners'][3]])
        self.assertEqual(faces[2]['corners'][1:3],faces[3]['corners'][1:3])
        changed=f.face_data(env['calculate_finger_d_line'](twist_deg=20),direction)
        self.assertEqual(changed[0],faces[0])
        for before,after in zip(faces[1:],changed[1:]):
            self.assertEqual(before['corners'][:2],after['corners'][:2])
            self.assertGreater(max(math.dist(p,q) for p,q in zip(before['corners'][2:],after['corners'][2:])),.01)

if __name__=='__main__':unittest.main()
