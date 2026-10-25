import unittest
from test_grip_twist import load_grip
from fusion_app import grip_con22_23 as f, grip_con14, grip_width as w, grip_twist as v

class Con22Con23Tests(unittest.TestCase):
    def test_exact_con13_con14_shared_edges_and_g(self):
        env=load_grip();data={k:env['calculate_finger_'+k.lower()+'_line']() for k in 'ABCD'}
        for k in 'AB':data[k]['guideline_points_mm']=env['calculate_guideline_points'](k,data[k])[0]
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        c,d=data['C'],data['D'];faces=f.face_data(c,d,direction);g=env['GRIP_REFERENCE_POINT_G_MM']
        con13=next(x for x in w.connection_faces(data,direction) if x['identifier']=='Con13')
        con14=grip_con14.corners(c,d,direction)
        self.assertEqual(faces[0]['corners'],con13['corners'][2:]+[g])
        self.assertEqual(faces[1]['corners'],[con14[3],con14[0],g])
        self.assertEqual(faces[0]['corners'][1:],faces[1]['corners'][::2])
        for face in faces:self.assertGreater(face['area_mm2'],0)
        changed=f.face_data(c,env['calculate_finger_d_line'](twist_deg=20),direction)
        self.assertEqual(faces[0],changed[0]);self.assertNotEqual(faces[1]['corners'][1],changed[1]['corners'][1])

if __name__=='__main__':unittest.main()
