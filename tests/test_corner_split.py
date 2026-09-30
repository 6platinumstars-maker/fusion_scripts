import ast
import math
from pathlib import Path
from types import SimpleNamespace as N
import unittest


class CornerSplitTests(unittest.TestCase):
    def setUp(self):
        p=Path(__file__).resolve().parents[1]/'fusion_app/outer_shell_corner_split.py'
        tree=ast.parse(p.read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        self.env={'math':math,'adsk':N(core=N(Point3D=N(create=lambda x,y,z:N(x=x,y=y,z=z))))}
        exec(compile(tree,str(p),'exec'),self.env)

    def test_plane_contains_all_three_points(self):
        for p in self.env['POINTS_MM']:
            self.assertAlmostEqual(self.env['distance_mm'](p),0,places=10)
        self.assertAlmostEqual(sum(v*v for v in self.env['plane_normal']()),1)

    def test_corner_and_main_body_on_opposite_sides(self):
        self.assertGreater(self.env['distance_mm'](self.env['REMOVE_SIDE_POINT_MM']),0)
        self.assertLess(self.env['distance_mm']((-40,0,0)),0)

    def test_centimeter_conversion(self):
        p=self.env['REMOVE_SIDE_POINT_MM']
        self.assertAlmostEqual(self.env['removal_distance'](N(x=p[0]/10,y=p[1]/10,z=p[2]/10)),
                               self.env['distance_mm'](p))

    def test_nonintersecting_body_prescreen(self):
        box=N(minPoint=N(x=-4,y=-1,z=0),maxPoint=N(x=-3,y=1,z=1))
        self.assertFalse(self.env['bounds_cross_plane'](N(boundingBox=box)))
        box=N(minPoint=N(x=-8,y=1,z=-.6),maxPoint=N(x=-5,y=3.3,z=3))
        self.assertTrue(self.env['bounds_cross_plane'](N(boundingBox=box)))


if __name__=='__main__':
    unittest.main()
