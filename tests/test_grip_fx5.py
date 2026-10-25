import unittest
from types import SimpleNamespace as NS
from fusion_app import grip_fx5 as f


def body(points):
    return NS(vertices=[NS(geometry=NS(**dict(zip('xyz',(x/10 for x in p))))) for p in points])


class Fx5Tests(unittest.TestCase):
    def test_only_fx5_is_replaced_and_top_vertex_is_shared_with_new_fx4(self):
        points=[(-29.854,-34.9669113466,23.6387905532),(-29.854,-35.,-6.),
                (-29.84438942656,-24.82258749795,-5.99958509146)]
        old_top=(-29.84438942656,-27.33775525755,24.26950896963)
        new_top=(-29.84438942656,-27.3380206,24.2727025)
        old=[body(points[:2]),body(points[2:]+[old_top])]
        unrelated=body(f.HINTS_MM)
        corners,selected=f.resolve({'faces':[{'fixed_id':'Fx5'},{'fixed_id':'Fx22'},{'fixed_id':'Fx5'}]},
                                   [old[0],unrelated,old[1]],body([new_top]))
        self.assertEqual(selected,old)
        for p,q in zip(corners,points+[new_top]):
            for x,y in zip(p,q):self.assertAlmostEqual(x,y,places=10)

    def test_missing_source_or_distant_top_fails_before_removal(self):
        with self.assertRaises(RuntimeError):f.resolve({'faces':[]},[],body(f.HINTS_MM))
        with self.assertRaises(RuntimeError):
            f.resolve({'faces':[{'fixed_id':'Fx5'}]},[body(f.HINTS_MM)],body([(0,0,0)]))


if __name__=='__main__':unittest.main()
