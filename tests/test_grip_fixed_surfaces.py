import unittest
from types import SimpleNamespace as N
from fusion_app import grip_fixed_surfaces as fixed


class Fx7Tests(unittest.TestCase):
    def bodies(self, points):
        return [N(vertices=[N(geometry=N(x=x/10, y=y/10, z=z/10)) for x,y,z in points])]

    def test_uses_exact_existing_vertices_in_requested_order(self):
        points=[(-76.78957297718996,32.233097780612916,29.222680710656515),
                (-76.795,18.768,-6),(-57.8,32.2,-6)]
        corners, area=fixed.resolve_fx7(self.bodies(points[::-1]+points))
        for actual, expected in zip(corners,points):
            for a,b in zip(actual,expected):self.assertAlmostEqual(a,b,places=12)
        self.assertGreater(area,400)
        self.assertLess(area,500)

    def test_fx8_snaps_three_confirmed_points_and_keeps_order(self):
        points=[(-61.19980364795056,32.233097780612916,29.222680710656515),
                (-57.055708919420326,28.128594841163775,28.881622816850232),
                (-58.36646444312956,32.2,24.703770768847487)]
        corners,area=fixed.resolve_fx8(self.bodies(points[::-1]))
        for p,q in zip(corners,points):
            for a,b in zip(p,q):self.assertAlmostEqual(a,b,places=12)
        self.assertGreater(area,0)
        with self.assertRaises(RuntimeError):fixed.resolve_fx8(self.bodies(points[:2]))

    def test_missing_or_distant_vertex_stops_before_build(self):
        with self.assertRaises(RuntimeError):fixed.resolve_fx7([])
        points=list(fixed.FX7_HINTS_MM)
        points[0]=(-76.7,32.233,29.223)
        with self.assertRaises(RuntimeError):fixed.resolve_fx7(self.bodies(points))

class Fx10Tests(unittest.TestCase):
    def test_base_vertices_need_not_share_one_existing_edge(self):
        def vertex(p):return N(geometry=N(x=p[0]/10,y=p[1]/10,z=p[2]/10))
        apex=(-35.2344,-29.0037,26.1412)
        a=(-29.854,-25.9,24.392192787605936)
        b=(-29.414548413939432,-24.645588812696168,24.496426319314125)
        nearby=(-29.854,-25.86692386459134,24.3949412025147)
        manifest={'faces':[{'fixed_id':'Fx2'},{'fixed_id':'Fx3'}]}
        bodies=[N(vertices=[vertex(p) for p in fixed.FX10_EDGE_HINTS_MM]),
                N(vertices=[vertex(p) for p in (b,nearby,a)])]
        fx9=N(vertices=[vertex(apex),vertex(a),vertex(b)])
        corners,area=fixed.resolve_fx10(manifest,bodies,fx9)
        for p,q in zip(corners,[apex,a,b]):
            for x,y in zip(p,q):self.assertAlmostEqual(x,y,places=12)
        self.assertGreater(area,0)
        with self.assertRaises(RuntimeError):
            fixed.resolve_fx10(manifest,[bodies[0],N(vertices=[])],fx9)
        with self.assertRaises(RuntimeError):
            fixed.resolve_fx10(manifest,bodies,N(vertices=[vertex(a),vertex(b)]))
        with self.assertRaises(RuntimeError):
            fixed.resolve_fx10(manifest,[bodies[0],N(vertices=[vertex(nearby),vertex(b)])],fx9)

class Fx11Tests(unittest.TestCase):
    def test_shares_fx10_edge_and_uses_fx5_not_nearby_vertex(self):
        def vertex(p):return N(geometry=N(x=p[0]/10,y=p[1]/10,z=p[2]/10))
        def body(points):return N(vertices=[vertex(p) for p in points])
        apex=(-35.2344,-29.0037,26.1412)
        shared=(-29.854,-25.9,24.392192787605936)
        end=(-29.854,-35.,23.639)
        manifest={'faces':[{'fixed_id':'Fx3'},{'fixed_id':'Fx5'}]}
        bodies=[body([shared,fixed.FX10_EDGE_HINTS_MM[1]]),
                body([(-29.854,-25.9,24.395),end,shared,shared])]
        fx9=body([apex])
        first,_=fixed.resolve_fx10(manifest,bodies,fx9)
        second,area=fixed.resolve_fx11(manifest,bodies,fx9)
        self.assertEqual(first[:2],second[:2])
        for a,b in zip(second[2],end):self.assertAlmostEqual(a,b,places=12)
        self.assertGreater(area,0)
        with self.assertRaises(RuntimeError):
            fixed.resolve_fx11(manifest,[bodies[0],body([])],fx9)

if __name__=='__main__':unittest.main()
