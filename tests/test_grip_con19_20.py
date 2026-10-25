import unittest
from test_grip_twist import load_grip
from fusion_app import grip_con19_20 as f, grip_width as w, grip_reference_closest as r, grip_twist as v

class Con19Con20Tests(unittest.TestCase):
    def test_con3_ref13_and_shortened_ag2_prime(self):
        env=load_grip();data={k:env['calculate_finger_'+k.lower()+'_line']() for k in 'ABCD'}
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        ref=r.point_data(data['A'],data['C'],direction)['point_mm']
        fallback=f.face_data(data,direction,ref)
        for k in 'AB':data[k]['guideline_points_mm']=env['calculate_guideline_points'](k,data[k])[0]
        faces=f.face_data(data,direction,ref)
        self.assertEqual(faces,fallback)
        con3=next(x for x in w.connection_faces(data,direction) if x['identifier']=='Con3')
        self.assertEqual(faces[0]['corners'],[con3['corners'][1],con3['corners'][0],ref])
        quarter=w.quarter_l1_points('A',data['A'],direction)
        ag2_prime=v.mul(v.add(quarter["AF1'"],quarter["AH1'"]),.5)
        self.assertEqual(faces[1]['names'],('Ref13','AH2',"AG2'"))
        self.assertEqual(faces[1]['corners'],[ref,con3['corners'][0],ag2_prime])
        ag2=data['A']['points_mm'][2];ag1_prime=data['A']['guideline_points_mm'][1]
        self.assertAlmostEqual(v.norm(v.sub(ag2_prime,ag2)),3.75,places=8)
        self.assertLess(v.norm(v.sub(ag2_prime,v.add(ag2,v.mul(v.sub(ag1_prime,ag2),.25)))),1e-8)
        for face in faces:self.assertGreater(face['area_mm2'],0)
        with self.assertRaises(ValueError):f.face_data(data,direction,con3['corners'][1])

if __name__=='__main__':unittest.main()
