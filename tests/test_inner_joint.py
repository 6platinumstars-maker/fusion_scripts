import ast
import math
from pathlib import Path
from types import SimpleNamespace as N
import unittest

ROOT=Path(__file__).resolve().parents[1]

class Collection(list):
    @property
    def count(self): return len(self)
    def item(self,index): return self[index]
    def add(self,value): self.append(value)

class InnerJointTests(unittest.TestCase):
    def setUp(self):
        tree=ast.parse((ROOT/'fusion_app/inner_shell_joint.py').read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        self.env={'math':math,'adsk':N(core=N(Point3D=N(create=lambda x,y,z:N(x=x,y=y,z=z)),
            Vector3D=N(create=lambda x,y,z:(x,y,z)),ObjectCollection=N(create=Collection),
            Plane=N(cast=lambda geometry:None)),fusion=N(BRepEntityTypes=N(BRepFaceEntityType='face')))}
        exec(compile(tree,'inner_joint','exec'),self.env)

    def test_circle_dimensions(self):
        points=self.env['projection_samples_mm']()
        self.assertEqual(points[0],(-76.795,-7.201,10.492))
        self.assertEqual(len(points),33)
        for p in points[1:]:
            self.assertEqual(p[0],-76.795)
            self.assertAlmostEqual(math.dist(p,points[0]),4.6)

    def test_nearest_inner_face_and_coverage(self):
        body=object();foreign=object()
        face=N(body=body,geometry=N(objectType='cylinder'))
        other=N(body=foreign)
        def ray(origin,direction,kind,tol,visible,hits):
            self.assertEqual(direction,(1,0,0))
            self.assertFalse(visible)
            hits.add(N(x=-7.6,y=origin.y,z=origin.z))
            hits.add(N(x=-7.2,y=origin.y,z=origin.z))
            return Collection([other,face])
        report={}
        result=self.env['find_target_face'](N(findBRepUsingRay=ray),body,report)
        self.assertIs(result,face)
        self.assertEqual(len(report['projection_hits_mm']),33)

    def test_missing_or_multiple_surfaces_stop(self):
        body=object()
        with self.assertRaises(RuntimeError):
            self.env['find_target_face'](N(findBRepUsingRay=lambda *args:Collection()),body,{})
        count=[0]
        def ray(origin,direction,kind,tol,visible,hits):
            count[0]+=1
            hits.add(N(x=-7.2,y=origin.y,z=origin.z))
            return Collection([N(body=body,geometry=N(objectType=str(count[0])))])
        with self.assertRaises(RuntimeError):
            self.env['find_target_face'](N(findBRepUsingRay=ray),body,{})

    def test_empty_api_return_with_created_curves_is_success(self):
        self.env['adsk'].fusion.SurfaceProjectTypes=N(AlongVectorSurfaceProjectType='along')
        created=Collection()
        curve=object()
        def project(faces,curves,mode,axis):
            self.assertEqual(mode,'along')
            created.add(curve)
            return []
        report={}
        result=self.env['project_reference_circle'](N(sketchCurves=created,projectToSurface=project),
                                                    object(),object(),object(),report)
        self.assertEqual(result,[curve])
        self.assertEqual(report['projected_curve_count'],1)

    def test_projection_without_created_geometry_stops(self):
        self.env['adsk'].fusion.SurfaceProjectTypes=N(AlongVectorSurfaceProjectType='along')
        projection=N(sketchCurves=Collection(),projectToSurface=lambda *args:[])
        with self.assertRaises(RuntimeError):
            self.env['project_reference_circle'](projection,object(),object(),object(),{})

    def test_outer_reference_captured_before_joint_and_published_after_success(self):
        entry=(ROOT/'fusion_app/inner_shell_structure.py').read_text()
        self.assertLess(entry.index('reference_snapshot.stage(root)'),entry.index('inner_shell_joint.add_joint(root, body)'))
        self.assertLess(entry.index('inner_shell_joint.add_joint(root, body)'),entry.index('reference_snapshot.publish(pending)'))
        outer=(ROOT/'fusion_app/outer_shell_structure.py').read_text()
        self.assertNotIn('inner_shell_joint',outer)

if __name__=='__main__': unittest.main()
