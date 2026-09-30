"""No Fusion kernel: check orchestration and snapshot lifecycle only."""
import ast
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace as N
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location('split_test.' + name, ROOT/'fusion_app'/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Collection(list):
    @property
    def count(self): return len(self)
    def item(self, index): return self[index]
    def add(self, body, base=None):
        result = N(name='', isSolid=True)
        self.append(result)
        if base: base.bodies.append(result)
        return result


class SeparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.manager = N(copy=lambda b:b,
            exportToFile=self.export,
            createFromFile=lambda path:Collection([N(name=Path(path).read_text())]))
        fusion = ModuleType('adsk.fusion')
        fusion.TemporaryBRepManager = N(get=lambda:self.manager)
        fusion.DesignTypes = N(ParametricDesignType=1)
        adsk = ModuleType('adsk'); adsk.fusion = fusion
        package = ModuleType('split_test'); package.__path__ = []
        package.helpers = N(set_body_identity=lambda body,name:setattr(body,'name',name))
        package.isolated_design = N(code_revision=lambda:'code-hash', record=Mock())
        self.modules = patch.dict(sys.modules, {'adsk':adsk,'adsk.fusion':fusion,'split_test':package})
        self.modules.start(); self.addCleanup(self.modules.stop)
        self.snapshot = load_module('reference_snapshot')
        self.snapshot.cache_root = lambda:Path(self.temp.name)
        self.guard = load_module('isolated_design')

    def export(self, bodies, path):
        Path(path).write_text(bodies[0].name)
        return True

    def test_stage_does_not_publish_and_old_snapshot_survives(self):
        first = self.snapshot.stage(N(bRepBodies=[N(name='inner')]))
        with self.assertRaises(RuntimeError): self.snapshot.read_snapshot()
        self.snapshot.publish(first)
        self.snapshot.stage(N(bRepBodies=[N(name='unfinished-new-inner')]))
        manifest, bodies = self.snapshot.read_snapshot()
        self.assertEqual(manifest['revision'],first['revision'])
        self.assertEqual(bodies[0].name,'inner')

    def test_corrupted_geometry_rejected(self):
        first = self.snapshot.stage(N(bRepBodies=[N(name='inner')]))
        self.snapshot.publish(first)
        (Path(self.temp.name)/first['revision']/'0.smt').write_text('changed')
        with self.assertRaises(RuntimeError): self.snapshot.read_snapshot()

    def test_install_parametric_and_direct(self):
        for mode in (1,0):
            base = N(name='', bodies=Collection(), startEdit=Mock(return_value=True), finishEdit=Mock(return_value=True))
            root = N(bRepBodies=Collection(), features=N(baseFeatures=N(add=lambda:base)))
            design = N(designType=mode, rootComponent=root)
            manifest={'revision':'reference-id','bodies':[{'name':'inner'},{'name':'other'}]}
            self.snapshot.install(design,manifest,[N(),N()])
            self.assertEqual([b.name for b in root.bRepBodies],['inner','other'])
            self.assertEqual(base.finishEdit.call_count,1 if mode==1 else 0)

    def test_existing_design_rejected_without_mutation(self):
        root=N(**{key:Collection() for key in ('bRepBodies','occurrences','sketches','constructionPlanes','constructionAxes','constructionPoints')})
        design=N(rootComponent=root,timeline=Collection())
        self.guard.require_empty(design)
        for key in ('bRepBodies','occurrences','sketches','constructionPlanes','constructionAxes','constructionPoints'):
            getattr(root,key).append(N())
            with self.assertRaises(RuntimeError): self.guard.require_empty(design)
            self.assertEqual(getattr(root,key).count,1)
            getattr(root,key).clear()

    def test_outer_pipeline_preserved_and_builders_unchanged(self):
        old=(ROOT/'fusion_app/assembly_left_hand_grip.py').read_text()
        new=(ROOT/'fusion_app/outer_shell_structure.py').read_text()
        def calls(source):
            tree=ast.parse(source)
            fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('build_inner_and_outer','build_for_preview'))
            return [ast.dump(n) for n in ast.walk(fn) if isinstance(n,ast.Call)
                    and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name)
                    and n.func.value.id=='outer_shell']
        self.assertEqual(calls(old),calls(new))
        for filename in ('outer_shell_structure','grip_structure'):
            source=(ROOT/'fusion_app'/(filename+'.py')).read_text()
            self.assertNotIn('inner_shell.build_',source)
            self.assertNotIn('assembly_left_hand_grip',source)


if __name__=='__main__': unittest.main()
