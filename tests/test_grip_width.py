import unittest
from test_grip_twist import load_grip
from fusion_app import grip_width as w
from fusion_app import grip_twist as v


class WidthTests(unittest.TestCase):
    def setUp(self):
        self.e=load_grip()
        self.direction=v.sub(self.e["GRIP_FINGER_A_POINT_P_MM"],self.e["GRIP_FINGER_D_POINT_P_MM"])

    def test_restored_bl3_keeps_g3_edge_and_uses_one_fifth_length(self):
        data=self.e['calculate_finger_b_line']()
        original=w.connected_faces(data['points_mm'],self.direction)[3]
        output=w.output_faces('B',data,self.direction)
        self.assertEqual([f['index'] for f in output],[2,3])
        face=output[1]
        self.assertEqual(face['length_fraction'],0.2)
        self.assertEqual(face['corners'][0],original['corners'][0])
        self.assertEqual(face['corners'][3],original['corners'][3])
        self.assertEqual(set(face['names']),{'H3','F3',"H4'","F4'"})
        self.assertAlmostEqual(v.norm(v.sub(face['corners'][1],face['corners'][0])),3.6)
        self.assertAlmostEqual(v.norm(v.sub(face['corners'][2],face['corners'][1])),10)
        self.assertAlmostEqual(face['area_mm2'],36)
        self.assertAlmostEqual(v.norm(v.sub(data['points_mm'][4],data['points_mm'][3])),18)
        a=self.e['calculate_finger_a_line']()
        al3=next(f for f in w.output_faces('A',a,self.direction) if f['index']==3)
        self.assertEqual(al3['length_fraction'],0.25)
        self.assertAlmostEqual(al3['area_mm2'],27.5)

    def test_ab_connection_quad_uses_both_shortened_ends(self):
        data={f:self.e[f'calculate_finger_{f.lower()}_line']() for f in 'ABCD'}
        for f in 'AB':
            data[f]['guideline_points_mm']=self.e['calculate_guideline_points'](f,data[f])[0]
        connections=w.connection_faces(data,self.direction)
        names=('AH3',"AH4'","BH4'",'BH3')
        face=next(f for f in connections if f['names']==names)
        a=next(f for f in w.output_faces('A',data['A'],self.direction) if f['index']==3)
        b=next(f for f in w.output_faces('B',data['B'],self.direction) if f['index']==3)
        ap=dict(zip(a['names'],a['corners']));bp=dict(zip(b['names'],b['corners']))
        self.assertEqual(face['corners'],[ap['H3'],ap["H4'"],bp["H4'"],bp['H3']])
        self.assertIsNone(face['area_mm2'])
        self.assertEqual(len(connections),13)

    def test_connection_numbers_and_new_bc_quad(self):
        data={f:self.e[f'calculate_finger_{f.lower()}_line']() for f in 'ABCD'}
        for f in 'AB':
            data[f]['guideline_points_mm']=self.e['calculate_guideline_points'](f,data[f])[0]
        faces=w.connection_faces(data,self.direction)
        self.assertEqual([f['identifier'] for f in faces],['Con'+str(i) for i in range(1,14)])
        new=faces[10]
        self.assertEqual(new['names'],('BF3','BF2','CH2','CH3'))
        b=next(f for f in w.output_faces('B',data['B'],self.direction) if f['index']==2)
        c=next(f for f in w.output_faces('C',data['C'],self.direction) if f['index']==2)
        bp=dict(zip(b['names'],b['corners']));cp=dict(zip(c['names'],c['corners']))
        self.assertEqual(new['corners'],[bp['F3'],bp['F2'],cp['H2'],cp['H3']])
        self.assertIsNone(new['area_mm2'])
        self.assertEqual(faces[4]['names'],('AH3',"AH4'","BH4'",'BH3'))

    def test_all_twenty_rectangles_width_center_area_and_planarity(self):
        for f in 'ABCD':
            data=self.e[f'calculate_finger_{f.lower()}_line']()
            points=data['points_mm']
            k=data.get('twist_joint_index',2)
            faces=w.rectangles(points,self.direction,joint_index=k,front_normal=data.get('front_plane_normal'))
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
                    if i < k:
                        self.assertGreater(v.dot(h_dir,self.direction),0)
                    else:
                        front=faces[0]
                        front_h=front['corners'][0] if front['names'][0].startswith('H') else front['corners'][3]
                        front_dir=v.unit(v.sub(front_h,points[0]))
                        self.assertAlmostEqual(v.angle(front_dir,h_dir),dict(A=20,B=0,C=10,D=30)[f],places=6)

    def test_width_direction_and_unjoined_transition(self):
        for f,angle in [('A',20),('B',0),('C',10),('D',30)]:
            data=self.e[f'calculate_finger_{f.lower()}_line']()
            k=data.get('twist_joint_index',2)
            faces=w.rectangles(data['points_mm'],self.direction,joint_index=k,front_normal=data.get('front_plane_normal'))
            front=faces[k-1];back=faces[k]
            self.assertAlmostEqual(v.angle(front['normal'],back['normal']),angle,places=6)
            for i in range(k):self.assertLess(v.norm(v.sub(faces[i]['normal'],front['normal'])),1e-8)
            for i in (j for j in range(4) if j!=k-1):
                a=faces[i]['corners'];b=faces[i+1]['corners']
                self.assertEqual(a[1],b[0]);self.assertEqual(a[2],b[3])
            for i in range(k,5):self.assertLess(v.norm(v.sub(faces[i]['normal'],back['normal'])),1e-8)
            self.assertTrue(all('_前半' in front['names'][i] for i in (1,2)))
            self.assertTrue(all('_後半' in back['names'][i] for i in (0,3)))
            self.assertTrue(any(str(k)+'_前半' in name for name in front['names']))
            self.assertTrue(any(str(k)+'_後半' in name for name in back['names']))
            ends=[v.norm(v.sub(front['corners'][1],back['corners'][j])) for j in (0,3)]
            if f=='B':self.assertLess(min(ends),1e-8)
            else:self.assertGreater(min(ends),.1)

    def test_midpoints_shared_and_only_adjacent_faces_change(self):
        expected_widths = dict(A=9.84807753012208, B=10., C=9.961946980917448, D=9.659258262890676)
        for f in 'ABCD':
            data=self.e[f'calculate_finger_{f.lower()}_line']()
            points=data['points_mm']; origin=self.direction
            k=data.get('twist_joint_index',2)
            normal=data.get('front_plane_normal')
            old=w.rectangles(points,origin,joint_index=k,front_normal=normal)
            new=w.connected_faces(points,origin,joint_index=k,front_normal=normal)
            self.assertEqual(len(new),5)
            for i in (j for j in range(5) if j not in (k-1,k)):self.assertEqual(new[i],old[i])
            endpoints=[]
            for side in ('H','F'):
                key=side+str(k)
                a=old[k-1]['corners'][old[k-1]['names'].index(key+'_前半')]
                b=old[k]['corners'][old[k]['names'].index(key+'_後半')]
                midpoint=v.mul(v.add(a,b),.5)
                for i in (k-1,k):
                    self.assertEqual(new[i]['corners'][new[i]['names'].index(key)],midpoint)
                endpoints.append(midpoint)
            self.assertLess(v.norm(v.sub(v.mul(v.add(*endpoints),.5),points[k])),1e-8)
            self.assertAlmostEqual(v.norm(v.sub(*endpoints)),expected_widths[f],places=8)
            self.assertEqual(set(new[k-1]['names']),{side+str(i) for side in 'HF' for i in (k-1,k)})
            self.assertEqual(set(new[k]['names']),{side+str(i) for side in 'HF' for i in (k,k+1)})
            self.assertIsNone(new[k-1]['area_mm2'])
            self.assertIsNone(new[k]['area_mm2'])

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

    def test_d_restored_g2_midpoint_and_shared_edges(self):
        for finger in 'D':
            data=self.e[f'calculate_finger_{finger.lower()}_line']()
            with self.assertRaises(ValueError):
                w.rectangles(data['points_mm'],self.direction,joint_index=1)
            faces=w.output_faces(finger,data,self.direction)
            self.assertEqual([f['index'] for f in faces],[2,3,4])
            for face in faces:
                self.assertEqual(face.get('midpoint_boundary',False),face['index']==2)
                expected=10*__import__('math').cos(__import__('math').radians(15)) if face['index']==2 else 10
                self.assertAlmostEqual(v.norm(v.sub(face['corners'][0],face['corners'][3])),expected,places=8)
            for first,second in zip(faces,faces[1:]):
                self.assertEqual(first['corners'][1],second['corners'][0])
                self.assertEqual(first['corners'][2],second['corners'][3])

    def test_restored_al1_center_and_unchanged_g2(self):
        data=self.e['calculate_finger_a_line']()
        original=w.connected_faces(data['points_mm'],self.direction)
        guideline=self.e['calculate_guideline_points']('A',data)[0]
        data['guideline_points_mm']=guideline
        faces=w.output_faces('A',data,self.direction)
        self.assertEqual([f['index'] for f in faces],[1,2,3])
        p=dict(zip(faces[0]['names'],faces[0]['corners']))
        old=dict(zip(original[1]['names'],original[1]['corners']))
        self.assertLess(v.norm(v.sub(v.mul(v.add(p['H1'],p['F1']),.5),guideline[1])),1e-10)
        self.assertAlmostEqual(v.norm(v.sub(p['H1'],p['F1'])),10,places=10)
        self.assertAlmostEqual(v.dot(v.sub(p['H1'],p['F1']),v.sub(guideline[2],guideline[1])),0,places=9)
        self.assertEqual(p['H2'],old['H2']);self.assertEqual(p['F2'],old['F2'])
        self.assertEqual(faces[1],original[2])
        plain=dict(data);plain.pop('guideline_points_mm')
        self.assertEqual(w.output_faces('A',plain,self.direction),faces)

    def test_con4_uses_bg1_prime_and_new_ah1(self):
        data={f:self.e[f'calculate_finger_{f.lower()}_line']() for f in 'ABCD'}
        for f in 'AB':data[f]['guideline_points_mm']=self.e['calculate_guideline_points'](f,data[f])[0]
        faces=w.connection_faces(data,self.direction)
        a=w.output_faces('A',data['A'],self.direction)[0]
        b=w.output_faces('B',data['B'],self.direction)[0]
        ap=dict(zip(a['names'],a['corners']));bp=dict(zip(b['names'],b['corners']))
        self.assertEqual(faces[3]['names'],("BG1'",'AH1','AH2','BH2'))
        self.assertEqual(faces[3]['corners'],[data['B']['guideline_points_mm'][1],ap['H1'],ap['H2'],bp['H2']])
        self.assertEqual(len(faces),13)

    def test_cd_g1_triangle_connections_share_width_edges(self):
        data={f:self.e[f'calculate_finger_{f.lower()}_line']() for f in 'ABCD'}
        for f in 'AB':data[f]['guideline_points_mm']=self.e['calculate_guideline_points'](f,data[f])[0]
        faces=w.connection_faces(data,self.direction)
        for finger,face in zip('D',faces[-2:-1]):
            width=next(item for item in w.output_faces(finger,data[finger],self.direction) if item['index']==2)
            points=dict(zip(width['names'],width['corners']))
            self.assertEqual(face['names'],(finger+'H2',finger+'F2',finger+'G1'))
            self.assertEqual(face['corners'],[points['H2'],points['F2'],data[finger]['points_mm'][1]])
            self.assertGreater(face['area_mm2'],0)
        changed=dict(data)
        changed['D']=self.e['calculate_finger_d_line'](twist_deg=20)
        updated=w.connection_faces(changed,self.direction)
        self.assertNotEqual(faces[-2]['corners'],updated[-2]['corners'])
        self.assertEqual(faces[-1],updated[-1])

    def test_quarter_l1_connections_and_con4_suspension(self):
        from unittest.mock import patch, MagicMock
        data={f:self.e[f'calculate_finger_{f.lower()}_line']() for f in 'ABCD'}
        for f in 'AB':data[f]['guideline_points_mm']=self.e['calculate_guideline_points'](f,data[f])[0]
        faces=w.connection_faces(data,self.direction)
        con1=faces[0]
        self.assertEqual(con1['names'],("AG2'",'AF2','AH2'))
        ag1=data['A']['guideline_points_mm'][1];ag2=data['A']['points_mm'][2]
        shortened=v.add(ag2,v.mul(v.sub(ag1,ag2),.25))
        self.assertLess(v.norm(v.sub(con1['corners'][0],shortened)),1e-10)
        self.assertAlmostEqual(v.norm(v.sub(con1['corners'][0],ag2)),3.75,places=8)
        from fusion_app import grip_reference_bezier
        self.assertEqual(con1['corners'][0],grip_reference_bezier.curve_data(data['A'])['control_points_mm'][2])
        al2=next(item for item in w.output_faces('A',data['A'],self.direction) if item['index']==2)
        apoints=dict(zip(al2['names'],al2['corners']))
        self.assertEqual(con1['corners'][1:],[apoints['F2'],apoints['H2']])
        self.assertGreater(con1['area_mm2'],0)
        for finger,index,length in (('B',1,5.),('C',12,7.5)):
            face=faces[index]
            self.assertEqual(face['names'],(finger+'F2',finger+'H2',finger+"H1'",finger+"F1'"))
            width=next(item for item in w.output_faces(finger,data[finger],self.direction) if item['index']==2)
            points=dict(zip(width['names'],width['corners']))
            self.assertEqual(face['corners'][:2],[points['F2'],points['H2']])
            near=v.mul(v.add(*face['corners'][:2]),.5)
            far=v.mul(v.add(*face['corners'][2:]),.5)
            self.assertAlmostEqual(v.norm(v.sub(near,far)),length,places=8)
            g1=data[finger].get('guideline_points_mm',data[finger]['points_mm'])[1]
            self.assertLess(v.norm(v.sub(far,v.add(near,v.mul(v.sub(g1,near),.25)))),1e-8)
            self.assertIsNone(face['area_mm2'])
        with patch.object(w,'create_patch',side_effect=lambda *args:MagicMock()) as create:
            w.create_connections(None,data,self.direction)
            names=[call.args[1].split('：')[1] for call in create.call_args_list]
            self.assertEqual(names,['Con'+str(i) for i in range(1,14) if i not in (2,4)])
        self.assertIn(('A',1),w.SUSPENDED_WIDTH_FACES)

    def test_invalid_width_rejected(self):
        data=self.e['calculate_finger_b_line']()
        for width in (0,-10,float('inf'),float('nan')):
            with self.assertRaises(ValueError):w.rectangles(data['points_mm'],(0,0,0),width)

if __name__=='__main__':unittest.main()
