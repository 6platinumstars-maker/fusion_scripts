import ast
import math
from pathlib import Path
from types import SimpleNamespace as N
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]

class Faces(list):
    @property
    def count(self):return len(self)

class FilletTests(unittest.TestCase):
    def setUp(self):
        tree=ast.parse((ROOT/'fusion_app/inner_shell_joint_fillet.py').read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        cast=lambda kind:N(cast=lambda value:value if value.kind==kind else None)
        self.env={'math':math,'adsk':N(core=N(Circle3D=cast('circle'),Arc3D=cast('arc'),Plane=cast('plane')))}
        exec(compile(tree,'fillet','exec'),self.env)

    def edge(self, radius=4.6, x=-76.795, fraction=1, count=2):
        geometry=N(kind='circle' if fraction==1 else 'arc',center=N(x=x/10,y=-.7201,z=1.0492),
                   radius=radius/10,normal=N(x=1,y=0,z=0))
        cap=N(geometry=N(kind='plane',origin=N(x=x/10),normal=N(x=1)))
        return N(geometry=geometry,faces=Faces([cap]*count),length=math.tau*radius/10*fraction)

    def test_outer_rim_only_and_split_arcs(self):
        rim=self.edge()
        self.assertEqual(self.env['select_outer_rim'](N(edges=[self.edge(2.5),self.edge(3.5,-73.795),self.edge(x=-73),rim])),[rim])
        arcs=[self.edge(fraction=.5),self.edge(fraction=.5)]
        self.assertEqual(self.env['select_outer_rim'](N(edges=arcs)),arcs)

    def test_missing_incomplete_or_nonmanifold_rim_stops(self):
        for edges in ([],[self.edge(fraction=.5)],[self.edge(count=4)]):
            with self.assertRaises(RuntimeError): self.env['select_outer_rim'](N(edges=edges))

    def test_radius_and_no_tangent_chain(self):
        rim=self.edge();result=N(isSolid=True,volume=10)
        apply=Mock(return_value=N(bodies=N(count=1,item=lambda i:result)))
        self.env.update(inner_shell=N(apply_constant_radius_fillet_to_edges=apply),
                        helpers=N(set_body_identity=Mock()),naming=N(BODY_INNER_SHELL='inner'),
                        write_report=lambda report:'diagnostics')
        root=object()
        self.assertIs(self.env['apply'](root,N(edges=[rim])),result)
        apply.assert_called_once_with(root,[rim],.1,tangent_chain=False)

if __name__=='__main__':unittest.main()
