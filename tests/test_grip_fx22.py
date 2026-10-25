import math
import unittest
from types import SimpleNamespace as NS
from fusion_app import grip_fixed_surfaces as f

ACTUAL=((-29.849277135859897,-31.039252434246514,21.8),
        (-29.851876117255035,-31.039252671582176,-3.7),
        (-29.844389426562834,-25.013668283876033,-3.7),
        (-29.844389426562834,-27.132554886180387,21.8))
def body(points):return NS(vertices=[NS(geometry=NS(**dict(zip('xyz',(x/10 for x in p))))) for p in points])

class Fx22Tests(unittest.TestCase):
    def test_actual_fx5_vertices_in_requested_order(self):
        manifest={'faces':[{'fixed_id':'Fx3'},{'fixed_id':'Fx5'},{'fixed_id':'Fx5'}]}
        points=f.resolve_fx22(manifest,[body(f.FX22_HINTS_MM),body(ACTUAL[:2]),body(ACTUAL[2:])])
        for p,q in zip(points,ACTUAL):self.assertLess(math.dist(p,q),1e-10)
        self.assertNotEqual(points[0][0],points[2][0])
        with self.assertRaises(RuntimeError):f.resolve_fx22({'faces':[{'fixed_id':'Fx3'}]},[body(ACTUAL)])
        with self.assertRaises(RuntimeError):f.resolve_fx22({'faces':[{'fixed_id':'Fx5'}]},[body(ACTUAL[:3])])

if __name__=='__main__':unittest.main()
