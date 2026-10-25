import unittest
import math
from types import SimpleNamespace as NS
from test_grip_twist import load_grip
from fusion_app import grip_smv16 as f, grip_reference_hexagon as h, grip_reference_ellipse as e, grip_twist as v


def vertex(p):return NS(geometry=NS(**dict(zip('xyz',(x/10 for x in p)))))
def edge(a,b):return NS(startVertex=vertex(a),endVertex=vertex(b))


class SmV16Tests(unittest.TestCase):
    def test_actual_edge_reused_and_current_g(self):
        env=load_grip();g=env['GRIP_REFERENCE_POINT_G_MM']
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        split=e.point_at(e.from_a_lower(env['calculate_finger_a_line'](),direction),0)
        d=h.hexagon_data()['points'][3]
        selected=edge(split,d)
        body=NS(edges=[edge(d,h.hexagon_data()['points'][4]),selected])
        actual,corners=f.resolve_boundary(body,g)
        self.assertIs(actual,selected)
        for p,q in zip(corners,[d,split,g]):self.assertLess(v.norm(v.sub(p,q)),1e-10)
        changed=(g[0],g[1]+1,g[2])
        self.assertEqual(f.resolve_boundary(body,changed)[1][2],changed)

    def test_ref7_split_to_g_arc(self):
        env=load_grip();g=env['GRIP_REFERENCE_POINT_G_MM']
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        data=e.from_a_lower(env['calculate_finger_a_line'](),direction)
        split=e.point_at(data,0);piece=f.ellipse_section(data,split,g)
        ends=[e.point_at(data,piece['start']),e.point_at(data,piece['start']+piece['sweep'])]
        for p in (split,g):self.assertLess(min(math.dist(p,q) for q in ends),1e-8)
        for i in range(21):
            t=piece['start']+piece['sweep']*i/20
            self.assertLess((t-data['start'])%math.tau,data['sweep'])
        midpoint=e.point_at(data,piece['start']+piece['sweep']/2)
        chord=v.sub(g,split)
        distance=v.norm(v.cross(v.sub(midpoint,split),chord))/v.norm(chord)
        self.assertGreater(distance,.1)
        with self.assertRaises(ValueError):f.ellipse_section(data,split,(0,0,0))
        with self.assertRaises(ValueError):f.ellipse_section(data,(0,0,0),g)
        with self.assertRaises(ValueError):f.ellipse_section(dict(data,sweep=.01),split,g)

    def test_missing_ambiguous_or_degenerate_boundary_rejected(self):
        g=(-90,0,23);selected=edge(*f.HINTS_MM)
        for edges in ([],[selected,selected]):
            with self.assertRaises(RuntimeError):f.resolve_boundary(NS(edges=edges),g)
        with self.assertRaises(ValueError):
            f.resolve_boundary(NS(edges=[selected]),f.HINTS_MM[0])

if __name__=='__main__':unittest.main()
