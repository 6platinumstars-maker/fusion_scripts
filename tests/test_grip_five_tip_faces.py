import copy
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_width as w,grip_reference_fx6 as ref,grip_twist as v,grip_d_tip_surfaces as tip


class FiveTipFaceTests(unittest.TestCase):
    def test_requested_vertices_share_reference_points_and_keep_guidelines(self):
        e=load_grip();data={f:e['calculate_finger_'+f.lower()+'_line']() for f in 'ABCD'}
        for f in 'AB':data[f]['guideline_points_mm']=e['calculate_guideline_points'](f,data[f])[0]
        direction=v.sub(e['GRIP_FINGER_A_POINT_P_MM'],e['GRIP_FINGER_D_POINT_P_MM'])
        before=copy.deepcopy(data)
        points={f:ref.tip_point(f,data[f],direction) for f in 'CD'}
        width={f:w.tip_surface(f,data[f],direction) for f in 'CD'}
        for f in 'CD':
            self.assertEqual(width[f]['names'],["H5'",'F5','F4','H4'])
            self.assertEqual(width[f]['corners'][0],points[f])
            original=next(x for x in w.output_faces(f,data[f],direction) if x['index']==4)
            old=dict(zip(original['names'],original['corners']))
            self.assertEqual(width[f]['corners'][1:],[old['F5'],old['F4'],old['H4']])
        connections={f['identifier']:f for f in w.connection_faces(data,direction)}
        c,d=width['C']['corners'],width['D']['corners']
        self.assertEqual(connections['Con8']['names'],('CF4','DH4',"DH5'",'CF5'))
        self.assertEqual(connections['Con8']['corners'],[c[2],d[3],d[0],c[1]])
        self.assertEqual(connections['Con9']['corners'],[c[1],c[0],d[0]])
        smv14=tip.face_data(data['D'],direction,tip.FX5_HINTS_MM)[1]
        self.assertEqual(smv14['corners'],[d[0],d[1],tip.FX5_HINTS_MM[0]])
        self.assertNotEqual(set(connections['Con8']['corners']),set(d))
        self.assertEqual(data,before)

    def test_actual_fx6_intersection_is_used_by_every_consumer(self):
        e=load_grip();d=e['calculate_finger_d_line']()
        direction=v.sub(e['GRIP_FINGER_A_POINT_P_MM'],e['GRIP_FINGER_D_POINT_P_MM'])
        d['fx6_h5_prime_mm']=(-44.,-23.,-6.)
        self.assertEqual(w.tip_surface('D',d,direction)['corners'][0],d['fx6_h5_prime_mm'])
        self.assertEqual(tip.face_data(d,direction,tip.FX5_HINTS_MM)[1]['corners'][0],d['fx6_h5_prime_mm'])


if __name__=='__main__':unittest.main()
