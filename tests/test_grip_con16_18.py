import math
import unittest
from types import SimpleNamespace as NS
from test_grip_twist import load_grip
from fusion_app import grip_con16_18 as f, grip_con15, grip_con19_20, grip_reference_closest, grip_width as w, grip_twist as v

class NewConnectionsTests(unittest.TestCase):
    def test_shared_edges_and_fixed_vertex_resolution(self):
        env=load_grip();data={k:env['calculate_finger_'+k.lower()+'_line']() for k in 'ABC'}
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        faces=f.moving_faces(data,direction);con15=grip_con15.corners(data['A'],data['C'],direction)
        ref=grip_reference_closest.point_data(data['A'],data['C'],direction)['point_mm']
        self.assertEqual(faces[0]['corners'][:2],[con15[1],ref])
        con19=grip_con19_20.face_data(data,direction,ref)[0]
        self.assertEqual(faces[0]['corners'][1:3],[con19['corners'][2],con19['corners'][0]])
        self.assertIn('Con2',w.SUSPENDED_CONNECTION_FACES)
        self.assertEqual(faces[0]['names'],("CH1'",'Ref13','BH2','BF2'))
        width={k:{n:p for item in w.output_faces(k,data[k],direction) for n,p in zip(item['names'],item['corners'])} for k in 'ABC'}
        self.assertEqual(faces[0]['corners'][2:],[width['B']['H2'],width['B']['F2']])
        self.assertEqual(faces[1]['corners'],[con15[1],width['C']['H2'],width['B']['F2']])
        fixed=[(-70.07549714398385,21.518309932535725,28.332350498192813),(-76.002831,12.50624,29.59025)]
        body=NS(vertices=[NS(geometry=NS(**dict(zip('xyz',(x/10 for x in p))))) for p in fixed])
        triangle=f.fixed_face(data['A'],direction,body)
        self.assertEqual(triangle['corners'][0],width['A']['F2'])
        for p,q in zip(triangle['corners'][1:],fixed):self.assertLess(math.dist(p,q),1e-10)
        self.assertGreater(triangle['area_mm2'],0)
        with self.assertRaises(ValueError):f.fixed_face(data['A'],direction,NS(vertices=[]))

if __name__=='__main__':unittest.main()
