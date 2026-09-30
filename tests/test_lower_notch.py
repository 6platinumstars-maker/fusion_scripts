"""Pure geometry and face-selection checks; no Fusion kernel."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace as N
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'fusion_app/outer_shell_lower_notch.py'


class LowerNotchTests(unittest.TestCase):
    def setUp(self):
        tree=ast.parse(SOURCE.read_text())
        tree.body=[node for node in tree.body if not isinstance(node,(ast.Import,ast.ImportFrom))]
        self.ns={'math':math,'adsk':N(core=N(Plane=N(cast=lambda value:value))),
                 'naming':N(ATTRIBUTE_GROUP='g',ATTRIBUTE_NAME_KEY='name')}
        exec(compile(tree,str(SOURCE),'exec'),self.ns)

    def face(self, offset=0, name='known slope', area=1):
        normal=self.ns['hint_normal']()
        origin=self.ns['PLANE_HINTS_MM'][0]
        p=tuple((origin[i]+offset*normal[i])/10 for i in range(3))
        plane=N(origin=N(x=p[0],y=p[1],z=p[2]),normal=N(x=normal[0],y=normal[1],z=normal[2]))
        return N(geometry=plane,area=area,attributes=N(itemByName=lambda *args:N(value=name) if name else None))

    def test_tangent_on_actual_plane_near_requested_C(self):
        ns=self.ns; origin=ns['PLANE_HINTS_MM'][0]; normal=ns['hint_normal']()
        # An orthonormal basis for the tilted model plane.
        nx,ny,nz=normal
        u=ns['unit']((ny,-nx,0))
        v=(ny*u[2]-nz*u[1],nz*u[0]-nx*u[2],nx*u[1]-ny*u[0])
        coords={key:(ns['dot'](ns['subtract'](point,origin),u),ns['dot'](ns['subtract'](point,origin),v)) for key,point in ns['POINTS_MM'].items()}
        a,b=coords['A'],coords['B']
        c=ns['closest_tangent'](a,b,coords['C'],34.9)
        ac=ns['subtract'](c,a);bc=ns['subtract'](b,c)
        self.assertAlmostEqual(math.sqrt(ns['dot'](ac,ac)),34.9,places=10)
        self.assertAlmostEqual(ns['dot'](ac,bc),0,places=9)
        actual=tuple(origin[i]+c[0]*u[i]+c[1]*v[i] for i in range(3))
        self.assertLess(math.dist(actual,ns['POINTS_MM']['C']),0.1)
        self.assertAlmostEqual(ns['dot'](ns['subtract'](actual,origin),normal),0,places=10)

    def test_internal_B_rejected(self):
        with self.assertRaises(RuntimeError): self.ns['closest_tangent']((0,0),(1,0),(0,2),2)

    def test_named_face_reused(self):
        face=self.face();report={}
        chosen,name=self.ns['select_face'](N(constructionPlanes=[]),N(faces=[face]),report)
        self.assertIs(chosen,face);self.assertEqual(name,'known slope')

    def test_distinct_nearby_planes_rejected(self):
        with self.assertRaises(RuntimeError):
            self.ns['select_face'](N(constructionPlanes=[]),N(faces=[self.face(),self.face(.01)]),{})

    def test_coplanar_patches_and_unnamed_fallback(self):
        face=self.face(name='',area=2)
        chosen,name=self.ns['select_face'](N(constructionPlanes=[]),N(faces=[face,self.face(name='',area=1)]),{})
        self.assertIs(chosen,face);self.assertEqual(name,'外殻蓋部斜面')

    def test_distant_face_rejected(self):
        with self.assertRaises(RuntimeError):
            self.ns['select_face'](N(constructionPlanes=[]),N(faces=[self.face(1)]),{})


if __name__=='__main__': unittest.main()
