import ast
from pathlib import Path
from types import SimpleNamespace as N
import unittest

ROOT=Path(__file__).resolve().parents[1]

class RectangleCutTests(unittest.TestCase):
    def setUp(self):
        tree=ast.parse((ROOT/'fusion_app/outer_shell_rectangle_cut.py').read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        self.ns={}
        exec(compile(tree,'rectangle','exec'),self.ns)

    def test_rectangle_and_depth(self):
        points=self.ns['corners_mm']()
        self.assertEqual(set(points),{(-80,-35,-6),(-29.854,-35,-6),(-29.854,-32.504,-6),(-80,-32.504,-6)})
        for a,b in zip(points,points[1:]+points[:1]):
            self.assertEqual(sum(x!=y for x,y in zip(a,b)),1)
        self.assertEqual(self.ns['START_Z_MM']+self.ns['DEPTH_MM'],34)

    def test_direction_is_world_positive_z_for_either_sketch_orientation(self):
        tree=ast.parse((ROOT/'fusion_app/outer_shell_rectangle_cut.py').read_text())
        assignment=next(node for node in ast.walk(tree) if isinstance(node,ast.Assign)
                        and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='direction')
        for normal_z,expected in ((1,'positive'),(-1,'negative')):
            env={'adsk':N(fusion=N(ExtentDirections=N(PositiveExtentDirection='positive',NegativeExtentDirection='negative'))),
                 'origin':N(z=0),'normal_tip':N(z=normal_z)}
            exec(compile(ast.Module(body=[assignment],type_ignores=[]),'<direction>','exec'),env)
            self.assertEqual(env['direction'],expected)

    def test_survivors_new_fragments_and_consumed_body(self):
        untouched=N(name='untouched',isValid=True)
        modified=N(name='modified',isValid=True)
        consumed=N(name='consumed',isValid=False)
        new=N(name='new',isValid=True)
        feature=N(bodies=N(count=2,item=lambda i:[modified,new][i]))
        result=self.ns['remaining_bodies']([untouched,modified,consumed],feature)
        self.assertEqual(result,[untouched,modified,new])
        feature=N(bodies=N(count=0))
        self.assertEqual(self.ns['remaining_bodies']([untouched,consumed],feature),[untouched])

if __name__=='__main__': unittest.main()
