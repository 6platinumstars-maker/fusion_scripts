import unittest
from types import SimpleNamespace as N
from fusion_app import grip_semi_variable as s
from test_grip_twist import load_grip


class SemiVariableTests(unittest.TestCase):
    def body(self,points):
        return N(vertices=[N(geometry=N(x=x/10,y=y/10,z=z/10)) for x,y,z in points])

    def test_fixed_points_only_from_fx3(self):
        exact=[(-70.07549714398385,21.518309932535725,28.332350498192813),
               (-57.97620390287997,24.794183823112572,28.604554627509753)]
        manifest={'faces':[{'fixed_id':'Fx1'},{'fixed_id':'Fx3'}]}
        points=s.resolve_smv1(manifest,[self.body(s.SMV1_HINTS_MM),self.body(exact)])
        for p,q in zip(points,exact):
            for a,b in zip(p,q):self.assertAlmostEqual(a,b,places=12)
        with self.assertRaises(RuntimeError):
            s.resolve_smv1(manifest,[self.body(s.SMV1_HINTS_MM),self.body([])])

    def test_smv2_uses_only_requested_fx3_edge_in_either_direction(self):
        def vertex(p):return N(geometry=N(x=p[0]/10,y=p[1]/10,z=p[2]/10))
        first,second=s.SMV2_HINTS_MM
        edge=N(startVertex=vertex(second),endVertex=vertex(first))
        unrelated=N(startVertex=vertex(first),endVertex=vertex((0,0,0)))
        manifest={'faces':[{'fixed_id':'Fx1'},{'fixed_id':'Fx3'}]}
        bodies=[N(edges=[edge]),N(edges=[unrelated,edge])]
        self.assertIs(s.resolve_smv2_edge(manifest,bodies),edge)
        bodies[1].edges=[unrelated]
        with self.assertRaises(RuntimeError):s.resolve_smv2_edge(manifest,bodies)
        bodies[1].edges=[edge,edge]
        with self.assertRaises(RuntimeError):s.resolve_smv2_edge(manifest,bodies)

    def test_smv3_uses_shortened_al3_and_shares_smv2_fixed_endpoint(self):
        from fusion_app import grip_width
        env=load_grip();data=env['calculate_finger_a_line']()
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        corners=s.smv3_corners(data,s.SMV3_HINTS_MM,direction)
        al3=next(f for f in grip_width.output_faces('A',data,direction) if f['index']==3)
        points=dict(zip(al3['names'],al3['corners']))
        self.assertEqual(corners,[points["F4'"],s.SMV3_HINTS_MM[1],s.SMV3_HINTS_MM[0]])
        self.assertAlmostEqual(__import__('math').dist(points['F3'],corners[0]),data['lengths_mm'][3]/4)
        self.assertLess(__import__('math').dist(s.SMV3_HINTS_MM[0],s.SMV2_HINTS_MM[1]),0.005)
        exact=[(-57.055708919420326,28.128594841163775,28.881622816850232),
               (-58.36646444312956,32.2,24.703770768847487)]
        manifest={'faces':[{'fixed_id':'Fx3'},{'fixed_id':'Fx2'}]}
        resolved=s.resolve_smv3(manifest,[self.body([exact[0]]),self.body([exact[1]])])
        with self.assertRaises(RuntimeError):
            s.resolve_smv3(manifest,[self.body(exact),self.body([])])
        for p,q in zip(resolved,exact):
            for a,b in zip(p,q):self.assertAlmostEqual(a,b,places=12)

    def test_smv4_uses_shortened_width_end_and_fx2_curve(self):
        from fusion_app import grip_width
        env=load_grip();data=env['calculate_finger_a_line']()
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        al3=next(f for f in grip_width.output_faces('A',data,direction) if f['index']==3)
        points=dict(zip(al3['names'],al3['corners']))
        self.assertEqual(s.smv4_endpoints(data,direction),(points["F4'"],points["H4'"]))
        self.assertEqual(s.SMV4_HINTS_MM[0],s.SMV3_HINTS_MM[1])
        def vertex(p):return N(geometry=N(x=p[0]/10,y=p[1]/10,z=p[2]/10))
        a,b=s.SMV4_HINTS_MM
        edge=N(startVertex=vertex(b),endVertex=vertex(a))
        self.assertIs(s.resolve_smv4_edge({'faces':[{'fixed_id':'Fx2'}]},[N(edges=[edge])]),edge)
        with self.assertRaises(RuntimeError):
            s.resolve_smv4_edge({'faces':[{'fixed_id':'Fx3'}]},[N(edges=[edge])])

    def test_smv5_uses_bh4_prime_and_shares_smv4_boundary(self):
        from fusion_app import grip_width
        env=load_grip()
        data={'A':env['calculate_finger_a_line'](),'B':env['calculate_finger_b_line']()}
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        corners=s.smv5_corners(data,s.SMV5_HINTS_MM,direction)
        al3=next(f for f in grip_width.output_faces('A',data['A'],direction) if f['index']==3)
        bl3=next(f for f in grip_width.output_faces('B',data['B'],direction) if f['index']==3)
        self.assertEqual(corners[0],bl3['corners'][bl3['names'].index("H4'")])
        self.assertEqual(corners[1],al3['corners'][al3['names'].index("H4'")])
        self.assertEqual(corners[1],s.smv4_endpoints(data['A'],direction)[1])
        self.assertEqual(corners[2],s.SMV4_HINTS_MM[1])
        self.assertEqual(corners[3],s.SMV5_HINTS_MM[1])
        with self.assertRaises(RuntimeError):
            s.resolve_smv5({'faces':[{'fixed_id':'Fx3'}]},[self.body(s.SMV5_HINTS_MM)])
        result=s.resolve_smv5({'faces':[{'fixed_id':'Fx2'}]},[self.body(s.SMV5_HINTS_MM)])
        for p,q in zip(result,s.SMV5_HINTS_MM):
            for a,b in zip(p,q):self.assertAlmostEqual(a,b)

    def test_smv6_uses_shortened_bl3_end_and_shares_smv5_boundary(self):
        from fusion_app import grip_width
        env=load_grip();data=env['calculate_finger_b_line']()
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        bl3=next(f for f in grip_width.output_faces('B',data,direction) if f['index']==3)
        points=dict(zip(bl3['names'],bl3['corners']))
        self.assertEqual(s.smv6_endpoints(data,direction),(points["H4'"],points["F4'"]))
        self.assertEqual(s.SMV6_HINTS_MM[0],s.SMV5_HINTS_MM[1])
        def vertex(p):return N(geometry=N(x=p[0]/10,y=p[1]/10,z=p[2]/10))
        a,b=s.SMV6_HINTS_MM
        edge=N(startVertex=vertex(b),endVertex=vertex(a))
        self.assertIs(s.resolve_smv6_edge({'faces':[{'fixed_id':'Fx2'}]},[N(edges=[edge])]),edge)
        with self.assertRaises(RuntimeError):
            s.resolve_smv6_edge({'faces':[{'fixed_id':'Fx3'}]},[N(edges=[edge])])

    def test_smv7_keeps_bf3_after_smv6_moves_to_bf4_prime(self):
        env=load_grip();data=env['calculate_finger_b_line']()
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        fixed=s.resolve_smv7({'faces':[{'fixed_id':'Fx2'}]},[self.body(s.SMV7_HINTS_MM)])
        corners=s.smv7_corners(data,fixed,direction)
        self.assertEqual(len(corners),4)
        self.assertEqual(corners[0],s.bl2_endpoints(data,direction)[1])
        self.assertNotEqual(corners[0],s.smv6_endpoints(data,direction)[1])
        self.assertEqual(corners[1],s.smv6_endpoints(data,direction)[1])
        for a,b in zip(corners[2],s.SMV6_HINTS_MM[1]):self.assertAlmostEqual(a,b)
        for a,b in zip(corners[3],s.SMV7_HINTS_MM[1]):self.assertAlmostEqual(a,b)
        with self.assertRaises(RuntimeError):
            s.resolve_smv7({'faces':[{'fixed_id':'Fx3'}]},[self.body(s.SMV7_HINTS_MM)])

    def test_smv8_uses_cl3_h_side_and_smv7_fixed_vertex(self):
        from fusion_app import grip_width
        env=load_grip();calc=env['calculate_finger_c_line'];data=calc()
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        manifest={'faces':[{'fixed_id':'Fx2'}]};bodies=[self.body(s.SMV7_HINTS_MM)]
        fixed=s.resolve_smv8(manifest,bodies)
        self.assertEqual(fixed,s.resolve_smv7(manifest,bodies)[1])
        corners=s.smv8_corners(data,fixed,direction)
        face=next(f for f in grip_width.output_faces('C',data,direction) if f['index']==3)
        points=dict(zip(face['names'],face['corners']))
        self.assertEqual(corners,[points['H4'],points['H3'],fixed])
        changed=s.smv8_corners(calc(twist_deg=20),fixed,direction)
        self.assertEqual(changed[2],fixed)
        self.assertNotEqual(changed[:2],corners[:2])
        with self.assertRaises(RuntimeError):
            s.resolve_smv8({'faces':[{'fixed_id':'Fx3'}]},bodies)

    def test_smv9_shares_edges_with_smv7_and_smv8(self):
        env=load_grip()
        data={'B':env['calculate_finger_b_line'](),'C':env['calculate_finger_c_line']()}
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        fixed=s.SMV8_HINT_MM
        corners=s.smv9_corners(data,fixed,direction)
        seven=s.smv7_corners(data['B'],s.SMV7_HINTS_MM,direction)
        eight=s.smv8_corners(data['C'],fixed,direction)
        self.assertEqual(corners,[seven[0],eight[1],fixed])
        self.assertEqual(corners[2],seven[3])
        self.assertEqual(corners[2],eight[2])
        changed=dict(data,C=env['calculate_finger_c_line'](twist_deg=20))
        updated=s.smv9_corners(changed,fixed,direction)
        self.assertEqual(updated[0],corners[0])
        self.assertNotEqual(updated[1],corners[1])
        self.assertEqual(updated[2],fixed)

    def test_smv10_uses_cl4_and_shares_ch4_edge_with_smv8(self):
        from fusion_app import grip_width
        env=load_grip();data=env['calculate_finger_c_line']()
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        fixed=s.SMV8_HINT_MM
        corners=s.smv10_corners(data,fixed,direction)
        cl4=grip_width.tip_surface('C',data,direction)
        points=dict(zip(cl4['names'],cl4['corners']))
        self.assertEqual(corners,[fixed,s.SMV10_FX6_POINT_MM,points["H5'"],points['H4']])
        eight=s.smv8_corners(data,fixed,direction)
        self.assertEqual([corners[3],corners[0]], [eight[0],eight[2]])
        changed=s.smv10_corners(env['calculate_finger_c_line'](twist_deg=20),fixed,direction)
        self.assertNotEqual(changed[2:],corners[2:])
        self.assertEqual(changed[:2],corners[:2])
        from fusion_app.grip_fixed_surfaces import FX23_CORNERS_MM
        self.assertEqual(tuple(corners[:2]),(FX23_CORNERS_MM[1],FX23_CORNERS_MM[2]))
        a,b,c=FX23_CORNERS_MM
        self.assertAlmostEqual(abs((b[1]-a[1])*(c[0]-a[0]))/2,12.6)

    def test_revised_smv2_four_corners_and_smv3_triangle_share_boundary(self):
        from fusion_app import grip_width
        env=load_grip();data=env['calculate_finger_a_line']()
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        af3,af4=s.smv2_endpoints(data,direction)
        historical=s.smv2_endpoints(env['calculate_finger_a_line'](lengths_mm=(12,25,17,11,14)),direction)
        self.assertLess(__import__('math').dist(historical[0],(-68.737,41.161,32.663)),0.005)
        self.assertLess(__import__('math').dist(historical[1],(-66.316,40.855,31.395)),0.005)
        al3=next(f for f in grip_width.output_faces('A',data,direction) if f['index']==3)
        current=dict(zip(al3['names'],al3['corners']))
        self.assertEqual((af3,af4),(current['F3'],current["F4'"]))
        tri=s.smv3_corners(data,s.SMV3_HINTS_MM,direction)
        self.assertEqual(len(tri),3)
        self.assertEqual(tri[0],af4)
        self.assertEqual(tri[2],s.SMV2_HINTS_MM[1])
        changed=s.smv2_endpoints(env['calculate_finger_a_line'](twist_deg=10),direction)
        self.assertNotEqual(changed,(af3,af4))

    def test_only_finger_side_changes_with_twist(self):
        env=load_grip()
        calc=env['calculate_finger_a_line']
        direction=tuple(a-b for a,b in zip(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM']))
        fixed=s.SMV1_HINTS_MM
        a,b=calc(twist_deg=20),calc(twist_deg=10)
        first,second=s.smv1_corners(a,fixed,direction),s.smv1_corners(b,fixed,direction)
        from fusion_app import grip_width
        face=next(f for f in grip_width.output_faces('A',a,direction) if f['index']==2)
        points=dict(zip(face['names'],face['corners']))
        self.assertEqual(first[:2],[points['F2'],points['F3']])
        self.assertNotEqual(first[:2],a['points_mm'][2:4])
        self.assertEqual(first[2:],[fixed[1],fixed[0]])
        self.assertEqual(first[2:],second[2:])
        self.assertNotEqual(first[:2],second[:2])

if __name__=='__main__':unittest.main()


class HexagonTriangleTests(unittest.TestCase):
    def test_shared_edge_and_only_dg1_moves(self):
        from fusion_app import grip_reference_hexagon as h
        env=load_grip();d=env['calculate_finger_d_line']()
        faces=s.hexagon_triangle_faces(d);points=h.hexagon_data()['points']
        self.assertEqual([f['identifier'] for f in faces],['SmV11','SmV12'])
        self.assertEqual(faces[0]['corners'],[points[1],points[2],d['points_mm'][1]])
        self.assertEqual(faces[1]['corners'],[points[2],points[3],d['points_mm'][1]])
        self.assertEqual(faces[0]['corners'][1:], [faces[1]['corners'][0],faces[1]['corners'][2]])
        changed=s.hexagon_triangle_faces(env['calculate_finger_d_line'](twist_deg=20))
        for before,after in zip(faces,changed):
            self.assertEqual(before['corners'][:2],after['corners'][:2])
            self.assertNotEqual(before['corners'][2],after['corners'][2])
            self.assertGreater(before['area_mm2'],0)
        with self.assertRaises(ValueError):
            s.hexagon_triangle_faces({'points_mm':[(0,0,0),points[2]]})
