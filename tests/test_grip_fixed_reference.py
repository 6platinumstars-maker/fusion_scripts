import ast
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace as N
import unittest
from unittest.mock import Mock
import uuid

ROOT=Path(__file__).resolve().parents[1]
class Collection(list):
    @property
    def count(self):return len(self)
    def item(self,i):return self[i]

class FixedReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        tree=ast.parse((ROOT/'fusion_app/grip_fixed_reference.py').read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        self.files={}
        def export(bodies,path):
            self.files[path]=bodies[0];Path(path).write_text('surface');return True
        self.manager=N(copy=lambda f:self.body(f),exportToFile=export,createFromFile=lambda path:Collection([self.files[path]]))
        self.e=dict(hashlib=hashlib,json=json,math=math,os=os,Path=Path,uuid=uuid,
                    isolated_design=N(code_revision=lambda:'code'),__package__='fusion_app',
                    adsk=N(core=N(Plane=N(cast=lambda g:g if g.kind=='plane' else None),
                                         Cylinder=N(cast=lambda g:g if g.kind=='cylinder' else None)),
                           fusion=N(TemporaryBRepManager=N(get=lambda:self.manager),DesignTypes=N(ParametricDesignType=1))))
        exec(compile(tree,'fixed','exec'),self.e)
        self.e['cache_root']=lambda:Path(self.temp.name)

    def face(self,x=-76.795,normal=(1,0,0),area=2,kind='plane',loops=2,z=-6.0,x_bounds=None,y=0):
        return N(geometry=N(kind=kind,origin=N(x=x/10,y=y/10,z=z/10),normal=N(x=normal[0],y=normal[1],z=normal[2])),
                 area=area,pointOnFace=N(y=0,z=0),body=N(name='outer'),loops=Collection([None]*loops),
                 boundingBox=N(minPoint=N(x=(x_bounds[0] if x_bounds else x)/10,y=y/10),
                               maxPoint=N(x=(x_bounds[1] if x_bounds else x)/10,y=y/10)))
    def body(self,face):return N(isSolid=False,faces=Collection([face]),attributes=N(add=Mock()))

    def outer(self):
        return {'outer':N(faces=[self.face(),self.face(x=-30,normal=(0,0,-1),area=3),self.face(x=-29.854,area=4),self.face(y=32.2,normal=(0,1,0)),self.fx3_face(),self.fx4_face()])}

    def fx4_face(self, radius=34.9, offset=0, reverse=False):
        face=self.face(kind='cylinder')
        sign=-1 if reverse else 1
        face.geometry.getData=lambda:(True,N(x=(-41.895+offset)/10,y=.5303,z=2.6985),
            N(x=0,y=sign*-.08280820751220438,z=sign*.9965655024977614),radius/10)
        return face

    def test_fx4_matches_cylinder_and_rejects_inner_radius_and_offset(self):
        for face in (self.fx4_face(),self.fx4_face(reverse=True)):
            self.assertTrue(self.e['face_matches'](face,'Fx4'))
        for face in (self.fx4_face(radius=33.3),self.fx4_face(offset=.2),self.fx3_face()):
            self.assertFalse(self.e['face_matches'](face,'Fx4'))

    def test_missing_fx4_keeps_previous_reference(self):
        self.e['publish'](self.outer(),'inner-ref')
        path=Path(self.temp.name)/'latest.json';before=path.read_bytes()
        outer=self.outer();outer['outer'].faces.pop()
        with self.assertRaisesRegex(RuntimeError,'Fx4'):self.e['publish'](outer,'inner-ref')
        self.assertEqual(path.read_bytes(),before)

    def fx3_face(self, offset=0, reverse=False):
        sign=-1 if reverse else 1
        return self.face(x=-59.35288145028793,y=-1.3669067829940815,
                         z=26.4307356319431+offset,
                         normal=(0,sign*-.08280820751220438,sign*.9965655024977614))

    def test_fx3_selects_actual_slope_and_excludes_parallel_inner_plane(self):
        a=self.fx3_face();b=self.fx3_face(reverse=True)
        rejected=[self.fx3_face(offset=.2),self.face(normal=(0,0,1),z=29.223),
                  self.face(kind='cylinder')]
        self.assertEqual(self.e['select_faces']({'outer':N(faces=[a,b]+rejected)},'Fx3'),[a,b])

    def test_missing_fx3_keeps_previous_reference(self):
        self.e['publish'](self.outer(),'inner-ref')
        path=Path(self.temp.name)/'latest.json';before=path.read_bytes()
        outer=self.outer();outer['outer'].faces.pop(-2)
        with self.assertRaisesRegex(RuntimeError,'Fx3'):self.e['publish'](outer,'inner-ref')
        self.assertEqual(path.read_bytes(),before)

    def test_fx2_preserves_both_xz_levels_and_rejects_other_directions(self):
        a=self.face(y=32.2,normal=(0,-1,0),area=3)
        b=self.face(y=32.2330977806,normal=(0,1,0))
        others=[self.face(y=32.25,normal=(0,1,0)),self.face(y=32.2),
                self.face(y=32.22,normal=(0,.08,1)),
                self.face(y=32.2,normal=(0,1,0),kind='cylinder')]
        self.assertEqual(self.e['select_faces']({'outer':N(faces=[a,b]+others)},'Fx2'),[a,b])

    def test_missing_fx2_keeps_previous_reference(self):
        self.e['publish'](self.outer(),'inner-ref')
        path=Path(self.temp.name)/'latest.json';before=path.read_bytes()
        outer=self.outer();outer['outer'].faces.pop(-3)
        with self.assertRaisesRegex(RuntimeError,'Fx2'):self.e['publish'](outer,'inner-ref')
        self.assertEqual(path.read_bytes(),before)

    def test_diagnostics_include_rejected_curved_and_out_of_range_faces(self):
        faces=[self.face(x=-29.854),self.face(x=-29.8),
               self.face(x=-29.85,kind='cylinder')]
        self.e['write_selection_diagnostics']({'outer':N(faces=faces)},'source')
        report=json.loads((Path(self.temp.name)/'fx5_selection_diagnostics.json').read_text())
        self.assertEqual(report['source_reference_revision'],'source')
        self.assertEqual([f['selected_fx5'] for f in report['faces']],[True,False,False])
        self.assertFalse(report['faces'][2]['planar'])
        self.assertAlmostEqual(report['faces'][1]['max_mm']['x'],-29.8)
        self.assertFalse((Path(self.temp.name)/'latest.json').exists())

    def test_fx5_selection_preserves_split_faces_and_rejects_other_planes(self):
        a=self.face(x=-29.854,area=4);b=self.face(x=-29.853,normal=(-1,0,0),area=1)
        outer={'outer':N(faces=[a,b,self.face(),self.face(x=-29.82),
                               self.face(x=-29.854,normal=(0,0,1)),self.face(x=-29.854,kind='cylinder')])}
        self.assertEqual(self.e['select_faces'](outer,'Fx5'),[a,b])

    def test_fx5_accepts_new_extent_and_slight_tilt_without_moving_face(self):
        flat=self.face(x=-29.844)
        tilted=self.face(x=0,normal=(1,0.001,0),x_bounds=(-29.854,-29.844))
        self.assertTrue(self.e['face_matches'](flat,'Fx5'))
        self.assertTrue(self.e['face_matches'](tilted,'Fx5'))
        self.assertFalse(self.e['face_matches'](tilted,'Fx1'))
        for face in (self.face(x=-29.854,x_bounds=(-30,-29.844)),
                     self.face(x=-29.854,x_bounds=(-29.854,-29.8)),
                     self.face(x=-29.85,normal=(1,.1,0))):
            self.assertFalse(self.e['face_matches'](face,'Fx5'))

    def test_old_fx5_selection_requires_refresh(self):
        manifest=self.e['publish'](self.outer(),'inner-ref')
        manifest['phase']='completed_outer_shell_fx1_fx6_fx5'
        (Path(self.temp.name)/'latest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(RuntimeError,'2を実行'):self.e['read_snapshot']()

    def test_missing_fx5_preserves_published_reference(self):
        self.e['publish'](self.outer(),'inner-ref')
        path=Path(self.temp.name)/'latest.json';before=path.read_bytes()
        with self.assertRaisesRegex(RuntimeError,'Fx5'):
            self.e['publish']({'outer':N(faces=[self.face(),self.face(normal=(0,0,1))])},'inner-ref')
        self.assertEqual(path.read_bytes(),before)

    def test_fx1_fx6_only_snapshot_requires_refresh(self):
        manifest=self.e['publish'](self.outer(),'inner-ref')
        manifest['phase']='completed_outer_shell_fx1_fx6'
        manifest['planes'].pop('Fx5')
        manifest['faces']=[f for f in manifest['faces'] if f['fixed_id']!='Fx5']
        (Path(self.temp.name)/'latest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(RuntimeError,'2を実行'):self.e['read_snapshot']()

    def test_fx6_selection_rejects_wrong_height_and_curved_faces(self):
        a=self.face(normal=(0,0,1));b=self.face(normal=(0,0,-1),area=1)
        outer={'outer':N(faces=[a,b,self.face(),self.face(normal=(0,0,1),z=-3.7),self.face(kind='cylinder')])}
        self.assertEqual(self.e['select_faces'](outer,'Fx6'),[a,b])

    def test_legacy_fx1_only_snapshot_requires_refresh(self):
        path=Path(self.temp.name)/'latest.json'
        path.write_text(json.dumps({'schema':1,'phase':'completed_outer_shell_fx1','x_mm':-76.795,'faces':[{}]}))
        with self.assertRaisesRegex(RuntimeError,'2を実行'):self.e['read_snapshot']()

    def test_missing_fx6_does_not_replace_previous_reference(self):
        self.e['publish'](self.outer(),'inner-ref')
        path=Path(self.temp.name)/'latest.json';before=path.read_bytes()
        with self.assertRaisesRegex(RuntimeError,'Fx6'):
            self.e['publish']({'outer':N(faces=[self.face()])},'inner-ref')
        self.assertEqual(path.read_bytes(),before)

    def test_plane_selection_preserves_all_matching_fragments(self):
        a=self.face();b=self.face(normal=(-1,0,0),area=1)
        root={'outer':N(faces=[self.face(x=-76.7),a,self.face(kind='cylinder'),b,self.face(normal=(0,1,0)),self.face(area=0)])}
        self.assertEqual(self.e['select_faces'](root),[a,b])
        with self.assertRaises(RuntimeError):self.e['select_faces']({'outer':N(faces=[self.face(x=0)])})

    def test_round_trip_and_loop_identity(self):
        m=self.e['publish'](self.outer(), 'inner-ref')
        read,bodies=self.e['read_snapshot']()
        self.assertEqual(read,m);self.assertEqual(read['faces'][0]['loop_count'],2)
        self.assertEqual(read['source_reference_revision'],'inner-ref')
        self.assertEqual(bodies[0].faces.count,1)
        self.assertEqual([f['fixed_id'] for f in read['faces']],['Fx1','Fx6','Fx5','Fx2','Fx3','Fx4'])
        self.assertEqual(len(bodies),6)

    def test_missing_and_corrupted_cache_stops(self):
        with self.assertRaises(RuntimeError):self.e['read_snapshot']()
        m=self.e['publish'](self.outer(), 'inner-ref')
        (Path(self.temp.name)/m['revision']/m['faces'][0]['file']).write_text('changed')
        with self.assertRaises(RuntimeError):self.e['read_snapshot']()

    def test_failed_export_keeps_last_published_snapshot(self):
        self.e['publish'](self.outer(), 'inner-ref')
        before=(Path(self.temp.name)/'latest.json').read_bytes()
        self.manager.exportToFile=lambda *_:False
        with self.assertRaises(RuntimeError):self.e['publish'](self.outer(), 'inner-ref')
        self.assertEqual((Path(self.temp.name)/'latest.json').read_bytes(),before)

    def test_install_does_not_count_or_rename_existing_grip_bodies(self):
        for mode in (0,1):
            face=self.face();body=self.body(face);fx6=self.body(self.face(normal=(0,0,1),area=3));fx5=self.body(self.face(x=-29.854,area=4))
            originals=[N(name='guide-surface-'+str(i)) for i in range(19)]
            base=N(bodies=Collection(),startEdit=Mock(return_value=True),finishEdit=Mock(return_value=True))
            class Bodies(Collection):
                def add(self,b,feature=None):
                    self.append(b)
                    if feature:feature.bodies.append(b)
                    return b
            root=N(bRepBodies=Bodies(originals),features=N(baseFeatures=N(add=lambda:base)))
            design=N(rootComponent=root,designType=mode,attributes=N(add=Mock()))
            m={'revision':'a'*32,'faces':[{'area_mm2':200,'name':'Fx1','fixed_id':'Fx1'},{'area_mm2':300,'name':'Fx6','fixed_id':'Fx6'},{'area_mm2':400,'name':'Fx5','fixed_id':'Fx5'}]}
            installed=self.e['install'](design,m,[body,fx6,fx5])
            self.assertEqual(installed,[body,fx6,fx5]);self.assertEqual(body.name,'固定面：Fx1：外殻X=-76.795面');self.assertEqual(fx6.name,'固定面：Fx6：外殻Z=-6.0面');self.assertEqual(fx5.name,'固定面：Fx5：外殻コの字面')
            self.assertEqual(len(root.bRepBodies),22)
            self.assertEqual([b.name for b in originals],['guide-surface-'+str(i) for i in range(19)])
            self.assertEqual(base.finishEdit.call_count,mode)

    def test_outer_export_after_final_cut_and_read_before_grip_mutation(self):
        outer=(ROOT/'fusion_app/outer_shell_structure.py').read_text()
        self.assertLess(outer.index('outer_shell_corner_split.split_and_remove'),outer.index('grip_fixed_reference.publish'))
        grip=(ROOT/'fusion_app/grip_structure.py').read_text()
        self.assertLess(grip.index('grip_fixed_reference.read_snapshot'),grip.index('grip.build_grip'))

if __name__=='__main__':unittest.main()
