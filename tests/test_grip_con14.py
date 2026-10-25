import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_con14 as f, grip_width as w, grip_twist as v

class Con14Tests(unittest.TestCase):
    def test_dh2_and_shared_con13_shortened_edge(self):
        env=load_grip();data={k:env['calculate_finger_'+k.lower()+'_line']() for k in 'ABCD'}
        for k in 'AB':data[k]['guideline_points_mm']=env['calculate_guideline_points'](k,data[k])[0]
        c,d=data['C'],data['D']
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        points=f.corners(c,d,direction)
        con13=next(face for face in w.connection_faces(data,direction) if face['identifier']=='Con13')
        self.assertEqual(points[2:],[con13['corners'][0],con13['corners'][3]])
        self.assertEqual(points[0],d['points_mm'][1])
        con12=next(face for face in w.connection_faces(data,direction) if face['identifier']=='Con12')
        self.assertEqual(points[:2],[con12['corners'][2],con12['corners'][0]])
        full=next(face for face in w.output_faces('D',d,direction) if face['index']==2)
        self.assertEqual(points[1],dict(zip(full['names'],full['corners']))['H2'])
        changed=f.corners(c,env['calculate_finger_d_line'](twist_deg=20),direction)
        self.assertEqual(points[2:],changed[2:])
        self.assertNotEqual(points[:2],changed[:2])
        self.assertGreater(v.norm(v.cross(v.sub(points[1],points[0]),v.sub(points[2],points[0]))),1e-8)

if __name__=='__main__':unittest.main()
