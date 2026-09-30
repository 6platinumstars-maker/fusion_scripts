import unittest
from test_grip_twist import load_grip
from fusion_app import grip_width as w
from fusion_app import grip_twist as v


class WidthTests(unittest.TestCase):
    def setUp(self):
        self.e=load_grip()
        self.direction=v.sub(self.e["GRIP_FINGER_A_POINT_P_MM"],self.e["GRIP_FINGER_D_POINT_P_MM"])

    def test_all_twenty_rectangles_width_center_area_and_planarity(self):
        for f in 'ABCD':
            data=self.e[f'calculate_finger_{f.lower()}_line']()
            points=data['points_mm']
            faces=w.rectangles(points,self.direction)
            self.assertEqual(len(faces),5)
            for i,face in enumerate(faces):
                a,b,c,d=face['corners']
                self.assertAlmostEqual(v.norm(v.sub(a,d)),10,places=8)
                self.assertAlmostEqual(v.norm(v.sub(b,c)),10,places=8)
                self.assertLess(v.norm(v.sub(v.mul(v.add(a,d),.5),points[i])),1e-8)
                self.assertLess(v.norm(v.sub(v.mul(v.add(b,c),.5),points[i+1])),1e-8)
                cross=v.cross(v.sub(b,a),v.sub(d,a))
                self.assertAlmostEqual(v.norm(cross),data['lengths_mm'][i]*10,places=7)
                self.assertAlmostEqual(v.dot(v.unit(cross),v.sub(c,a)),0,places=8)
                self.assertAlmostEqual(v.dot(v.sub(a,d),v.sub(b,a)),0,places=8)
                for first,second in ((0,3),(1,2)):
                    idx=first if face['names'][first].startswith('H') else second
                    other=second if idx==first else first
                    h_dir=v.unit(v.sub(face['corners'][idx],face['corners'][other]))
                    if i < 2:
                        self.assertGreater(v.dot(h_dir,self.direction),0)
                    else:
                        front=faces[0]
                        front_h=front['corners'][0] if front['names'][0].startswith('H') else front['corners'][3]
                        front_dir=v.unit(v.sub(front_h,points[0]))
                        self.assertAlmostEqual(v.angle(front_dir,h_dir),dict(A=20,B=0,C=10,D=30)[f],places=6)

    def test_width_direction_and_unjoined_transition(self):
        for f,angle in [('A',20),('B',0),('C',10),('D',30)]:
            data=self.e[f'calculate_finger_{f.lower()}_line']()
            faces=w.rectangles(data['points_mm'],self.direction)
            front=faces[1];back=faces[2]
            self.assertAlmostEqual(v.angle(front['normal'],back['normal']),angle,places=6)
            for i in (0,1):self.assertLess(v.norm(v.sub(faces[i]['normal'],front['normal'])),1e-8)
            for i in (0,2,3):
                a=faces[i]['corners'];b=faces[i+1]['corners']
                self.assertEqual(a[1],b[0]);self.assertEqual(a[2],b[3])
            for i in (2,3,4):self.assertLess(v.norm(v.sub(faces[i]['normal'],back['normal'])),1e-8)
            self.assertTrue(all('_前半' in front['names'][i] for i in (1,2)))
            self.assertTrue(all('_後半' in back['names'][i] for i in (0,3)))
            self.assertTrue(any('2_前半' in name for name in front['names']))
            self.assertTrue(any('2_後半' in name for name in back['names']))
            ends=[v.norm(v.sub(front['corners'][1],back['corners'][j])) for j in (0,3)]
            if f=='B':self.assertLess(min(ends),1e-8)
            else:self.assertGreater(min(ends),.1)

    def test_midpoints_shared_and_only_adjacent_faces_change(self):
        expected_widths = dict(A=9.84807753012208, B=10., C=9.961946980917448, D=9.659258262890676)
        for f in 'ABCD':
            data=self.e[f'calculate_finger_{f.lower()}_line']()
            points=data['points_mm']; origin=self.direction
            old=w.rectangles(points,origin)
            new=w.connected_faces(points,origin)
            self.assertEqual(len(new),5)
            for i in (0,3,4):self.assertEqual(new[i],old[i])
            endpoints=[]
            for side in ('H','F'):
                key=side+'2'
                a=old[1]['corners'][old[1]['names'].index(key+'_前半')]
                b=old[2]['corners'][old[2]['names'].index(key+'_後半')]
                midpoint=v.mul(v.add(a,b),.5)
                for i in (1,2):
                    self.assertEqual(new[i]['corners'][new[i]['names'].index(key)],midpoint)
                endpoints.append(midpoint)
            self.assertLess(v.norm(v.sub(v.mul(v.add(*endpoints),.5),points[2])),1e-8)
            self.assertAlmostEqual(v.norm(v.sub(*endpoints)),expected_widths[f],places=8)
            self.assertEqual(set(new[1]['names']),{'H1','F1','H2','F2'})
            self.assertEqual(set(new[2]['names']),{'H2','F2','H3','F3'})
            self.assertIsNone(new[1]['area_mm2'])
            self.assertIsNone(new[2]['area_mm2'])

    def test_a_back_h_keeps_identity_even_when_global_projection_reverses(self):
        points=self.e['calculate_finger_a_line']()['points_mm']
        faces=w.rectangles(points,self.direction)
        front,back=faces[1],faces[2]
        h_front=front['corners'][front['names'].index('H2_前半')]
        h_back=back['corners'][back['names'].index('H2_後半')]
        self.assertGreater(v.dot(v.sub(h_front,points[2]),self.direction),0)
        self.assertLess(v.dot(v.sub(h_back,points[2]),self.direction),0)
        self.assertAlmostEqual(v.angle(v.sub(h_front,points[2]),v.sub(h_back,points[2])),20,places=8)

    def test_ambiguous_front_direction_stops(self):
        points=self.e['calculate_finger_b_line']()['points_mm']
        with self.assertRaises(ValueError):
            w.rectangles(points,v.sub(points[1],points[0]))

    def test_invalid_width_rejected(self):
        data=self.e['calculate_finger_b_line']()
        for width in (0,-10,float('inf'),float('nan')):
            with self.assertRaises(ValueError):w.rectangles(data['points_mm'],(0,0,0),width)

if __name__=='__main__':unittest.main()
