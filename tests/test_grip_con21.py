import unittest
from types import SimpleNamespace as NS
from test_grip_twist import load_grip
from fusion_app import grip_con21 as f, grip_width as w, grip_twist as v

def vertex(p):return NS(geometry=NS(**dict(zip('xyz',(x/10 for x in p)))))
def edge(a,b):return NS(startVertex=vertex(a),endVertex=vertex(b))

class Con21Tests(unittest.TestCase):
    def test_reuses_only_con18_af2_to_fixed_vertex_edge(self):
        env=load_grip();a=env['calculate_finger_a_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        width=next(item for item in w.output_faces('A',a,direction) if item['index']==2)
        af2=dict(zip(width['names'],width['corners']))['F2']
        fixed=(-76.002831,12.50624,29.59025);other=(-70.075497,21.51831,28.33235)
        selected=edge(fixed,af2)
        actual,ends=f.resolve_edge(NS(edges=[edge(af2,other),edge(other,fixed),selected]),a,direction)
        self.assertIs(actual,selected)
        for p,q in zip(ends,(af2,fixed)):self.assertLess(v.norm(v.sub(p,q)),1e-10)
        with self.assertRaises(RuntimeError):f.resolve_edge(NS(edges=[edge(af2,other)]),a,direction)
        with self.assertRaises(RuntimeError):f.resolve_edge(NS(edges=[selected,selected]),a,direction)

if __name__=='__main__':unittest.main()
