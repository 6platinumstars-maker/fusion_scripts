import ast
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace as N
import unittest
import uuid
from test_grip_fixed_reference import Collection

ROOT=Path(__file__).resolve().parents[1]

class InnerFixedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        tree=ast.parse((ROOT/'fusion_app/grip_inner_reference.py').read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        files={}
        def export(bodies,path):files[path]=bodies[0];Path(path).write_text('surface');return True
        manager=N(copy=lambda f:N(isSolid=False,faces=Collection([f])),exportToFile=export,
                  createFromFile=lambda path:Collection([files[path]]))
        core=N(**{name:N(cast=lambda g,kind=name:g if g.kind==kind else None) for name in ('Cylinder','Plane')})
        self.e=dict(hashlib=hashlib,json=json,math=math,os=os,Path=Path,uuid=uuid,
                    isolated_design=N(code_revision=lambda:'code'),
                    adsk=N(core=core,fusion=N(TemporaryBRepManager=N(get=lambda:manager))))
        exec(compile(tree,'inner-fixed','exec'),self.e)
        self.e['cache_root']=lambda:Path(self.temp.name)

    def cylinder(self,origin,axis,radius):
        return N(area=2,loops=Collection([None]),geometry=N(kind='Cylinder',getData=lambda:
            (True,N(**dict(zip('xyz',[v/10 for v in origin]))),N(**dict(zip('xyz',axis))),radius/10)))

    def outer_side(self):
        # Construct an independent cylinder passing through the three hints.
        (x1,y1,_),(x2,y2,_),(x3,y3,_)=self.e['HINTS_MM']
        a,b=2*(x2-x1),2*(y2-y1);c,d=2*(x3-x1),2*(y3-y1)
        e=x2*x2+y2*y2-x1*x1-y1*y1;f=x3*x3+y3*y3-x1*x1-y1*y1
        x=(e*d-b*f)/(a*d-b*c);y=(a*f-e*c)/(a*d-b*c)
        return self.cylinder((x,y,0),(0,0,1),math.hypot(x-x1,y-y1))

    def cap(self):
        return N(area=.21,loops=Collection([None,None]),
                 geometry=N(kind='Plane',origin=N(x=-7.6795),normal=N(x=1,y=0,z=0)),
                 boundingBox=N(minPoint=N(y=-1.0801,z=.6892),maxPoint=N(y=-.3601,z=1.4092)))

    def body(self):
        return N(faces=Collection([self.outer_side(),self.cylinder(self.e['CENTER_MM'],(1,0,0),4.6),self.cap()]))

    def test_selection_excludes_bore_and_fillet(self):
        body=self.body()
        for face,key in zip(body.faces,self.e['IDS']):self.assertTrue(self.e['face_matches'](face,key))
        for radius in (2.5,3.5):
            self.assertFalse(self.e['face_matches'](self.cylinder(self.e['CENTER_MM'],(1,0,0),radius),'Ref2'))
        self.assertFalse(self.e['face_matches'](N(area=1,geometry=N(kind='Torus')),'Ref2'))
        cap=self.cap();cap.loops=Collection([None])
        self.assertFalse(self.e['face_matches'](cap,'Ref3'))

    def test_snapshot_roundtrip_preserves_ring_and_failed_selection_keeps_previous(self):
        manifest=self.e['publish'](self.body());read,bodies=self.e['read_snapshot']()
        self.assertEqual(manifest,read);self.assertEqual(len(bodies),3)
        self.assertEqual(read['faces'][2]['loop_count'],2)
        path=Path(self.temp.name)/'latest.json';before=path.read_bytes()
        body=self.body();body.faces.pop()
        with self.assertRaisesRegex(RuntimeError,'Ref3'):self.e['publish'](body)
        self.assertEqual(path.read_bytes(),before)
        source=Path(self.temp.name)/manifest['revision']/manifest['faces'][0]['file']
        source.write_text('modified')
        with self.assertRaises(RuntimeError):self.e['read_snapshot']()

    def test_legacy_names_load_without_regenerating_geometry(self):
        manifest=self.e['publish'](self.body())
        legacy={'Ref1':'Fx8','Ref2':'Fx9','Ref3':'Fx10'}
        for item in manifest['faces']:
            item['name']=legacy[item['fixed_id']]
            item['fixed_id']=legacy[item['fixed_id']]
        path=Path(self.temp.name)/'latest.json'
        path.write_text(json.dumps(manifest));before=path.read_bytes()
        read,bodies=self.e['read_snapshot']()
        self.assertEqual([f['name'] for f in read['faces']],['Ref1','Ref2','Ref3'])
        self.assertEqual(read['surface_role'],'reference')
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(len(bodies),3)

    def test_finished_inner_and_early_read(self):
        inner=(ROOT/'fusion_app/inner_shell_structure.py').read_text()
        self.assertLess(inner.index('inner_shell_joint_fillet.apply'),inner.index('grip_inner_reference.publish'))
        grip=(ROOT/'fusion_app/grip_structure.py').read_text()
        self.assertLess(grip.index('grip_inner_reference.read_snapshot'),grip.index('grip.build_grip'))
        with self.assertRaisesRegex(RuntimeError,'1を'):self.e['read_snapshot']()

if __name__=='__main__':unittest.main()
