import ast
import math
from pathlib import Path
from types import SimpleNamespace as N
import unittest

ROOT=Path(__file__).resolve().parents[1]


class LowerCutTests(unittest.TestCase):
    def test_arc_radius_branch_and_projection_size(self):
        def load(name, env):
            tree=ast.parse((ROOT/'fusion_app'/name).read_text())
            tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
            exec(compile(tree,name,'exec'),env)
            return env
        geom=load('outer_shell_lower_notch.py',{'math':math})
        module=load('outer_shell_lower_cut.py',{'math':math,'geometry':N(**geom)})
        origin=(-59.35288145028793,-1.3669067829940815,26.4307356319431)
        normal=(0,-0.08280820751220438,0.9965655024977614)
        u=(1,0,0);v=(0,normal[2],-normal[1])
        def local(p):
            d=geom['subtract'](p,origin)
            return geom['dot'](d,u),geom['dot'](d,v)
        a=local(geom['POINTS_MM']['A']); b=local(geom['POINTS_MM']['B'])
        c=geom['closest_tangent'](a,b,local(geom['POINTS_MM']['C']),34.9)
        d,sweep=module['circle_point_and_sweep'](a,local(module['CONTOUR_HINTS_MM']['D']),c,34.9)
        self.assertAlmostEqual(math.dist(a,d),34.9)
        self.assertGreater(abs(math.degrees(sweep)),100)
        self.assertLess(abs(math.degrees(sweep)),120)
        def world(p): return tuple(origin[i]+p[0]*u[i]+p[1]*v[i] for i in range(3))
        self.assertLess(math.dist(world(d),module['CONTOUR_HINTS_MM']['D']),.1)
        for key in ('P1','P2','P3'):
            hint=module['CONTOUR_HINTS_MM'][key]
            self.assertLess(math.dist(world(local(hint)),hint),.1)

    def test_face_backed_sketch_reference_is_not_accessed(self):
        import json
        from unittest.mock import Mock
        tree=ast.parse((ROOT/'fusion_app/outer_shell_lower_cut.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='cut')
        body=next(n for n in fn.body if isinstance(n,ast.Try)).body
        stop=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign)
                  and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='plane')
        fragment=ast.Module(body=body[:stop+1],type_ignores=[])
        plane_data={'origin_mm':[0,0,0],'normal':[0,0,1]}
        class Source:
            attributes=N(itemByName=lambda *args:N(value=json.dumps({'selected_plane':plane_data})))
            @property
            def referencePlane(self):
                raise AssertionError('Fusion requires timeline rollback here')
        face=object()
        def select(root,body,report):
            report['selected_plane']=plane_data
            return face,'slope'
        plane_input=N(setByOffset=Mock())
        planes=N(createInput=lambda:plane_input,add=lambda value:N())
        env={'json':json,'source_sketch':Source(),'naming':N(ATTRIBUTE_GROUP='g'),
             'report':{},'root':N(constructionPlanes=planes),'body':object(),
             'geometry':N(select_face=select,same_plane=lambda a,b:a==b),
             'adsk':N(core=N(ValueInput=N(createByReal=lambda value:value)))}
        exec(compile(fragment,'<plane regression>','exec'),env)
        plane_input.setByOffset.assert_called_once_with(face,0)

    def test_all_result_solids_preserved_and_invalid_results_rejected(self):
        tree=ast.parse((ROOT/'fusion_app/outer_shell_lower_cut.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='collect_cut_results')
        env={'naming':N(BODY_OUTER_SHELL='outer'),
             'helpers':N(set_body_identity=lambda body,name:setattr(body,'name',name))}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<results>','exec'),env)
        collect=env['collect_cut_results']
        def feature(bodies): return N(bodies=N(count=len(bodies),item=lambda i:bodies[i]))
        small=N(name='small',volume=1,isSolid=True)
        large=N(name='large',volume=7,isSolid=True)
        report={}
        result=collect(feature([small,large]),10,report)
        self.assertEqual(list(result.values()),[large,small])
        self.assertTrue(small.isLightBulbOn and large.isLightBulbOn)
        self.assertEqual(report['result_body_count'],2)
        self.assertEqual(report['removed_volume_mm3'],2000)
        for bodies in ([],[N(name='surface',volume=1,isSolid=False)],
                       [N(name='uncut',volume=10,isSolid=True)]):
            with self.assertRaises(RuntimeError): collect(feature(bodies),10,{})

    def test_cut_scope_depth_and_upper_notch_order(self):
        source=(ROOT/'fusion_app/outer_shell_lower_cut.py').read_text()
        self.assertIn('cut_input.participantBodies = [body]',source)
        self.assertIn('DEPTH_MM = 40.0',source)
        entry=(ROOT/'fusion_app/outer_shell_structure.py').read_text()
        self.assertLess(entry.index('outer_shell_rectangle_cut.cut(root_comp, outer_results)'),
                        entry.index('outer_shell_notches.cut_upper_notch(root_comp, outer_results)'))
        self.assertIn('outer_shell_lower_cut.cut(root_comp, outer_shell_body, lower_sketch)',entry)


if __name__=='__main__': unittest.main()
