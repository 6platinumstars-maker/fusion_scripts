"""Regression checks for selecting the circle/starting-face intersection."""
import ast
from pathlib import Path
from types import SimpleNamespace as N
import unittest


class Collection(list):
    @property
    def count(self):
        return len(self)

    def item(self, index):
        return self[index]

    def add(self, value):
        self.append(value)


class CircleOverlapTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'fusion_app/outer_shell_circle_cut.py'
        tree = ast.parse(path.read_text())
        tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
        self.env = {'adsk': N(core=N(ObjectCollection=N(create=Collection)))}
        exec(compile(tree, str(path), 'exec'), self.env)
        self.cx, self.cy, self.z = [v / 10 for v in self.env['CENTER_MM']]

    def profile(self, x, y):
        # Deliberately do not provide a centroid; it is unsuitable for holes
        # and concave profiles. Coordinates below are in sketch space.
        return N(face=N(pointOnFace=N(x=x, y=y, z=0)))

    def sketch(self, profiles):
        return N(profiles=Collection(profiles), sketchToModelSpace=lambda p:
                 N(x=self.cx+p.x, y=self.cy+p.y, z=self.z))

    def test_only_overlap_kept_not_circle_only_or_model_only(self):
        overlap = self.profile(.5, 0)
        circle_only = self.profile(-.5, 0)
        model_only = self.profile(2.0, 0)
        face = N(isPointOnFace=lambda p, tol: p.x > 0 and p.z == 0)
        result = self.env['select_overlap_profiles'](
            self.sketch([overlap, circle_only, model_only]), [face])
        self.assertEqual(result, [overlap])

    def test_gap_between_disconnected_outer_regions_excluded(self):
        left, hole, right = self.profile(-1, 0), self.profile(0, 0), self.profile(1, 0)
        faces = [N(isPointOnFace=lambda p, tol: p.x < -.5),
                 N(isPointOnFace=lambda p, tol: p.x > .5)]
        result = self.env['select_overlap_profiles'](self.sketch([left, hole, right]), faces)
        self.assertEqual(result, [left, right])

    def test_inner_hole_included_using_only_filled_outer_loop(self):
        outer = N(isOuter=True, edges=[])
        inner = N(isOuter=False, edges=[])
        source_face = N(loops=[outer, inner], isPointOnFace=lambda p, tol: False)
        filled = N(isPointOnFace=lambda p, tol: abs(p.x) < 1.5)
        region = N(faces=Collection([filled]))
        copied = []
        wire = N()

        def copy(loop):
            copied.append(loop)
            return wire

        def fill(wires):
            self.assertEqual(wires, [wire])
            return region

        self.env['adsk'].fusion = N(TemporaryBRepManager=N(get=lambda:
            N(copy=copy, createFaceFromPlanarWires=fill)))
        loops = self.env['outer_loops']([source_face])
        regions = self.env['filled_outer_regions'](loops)
        hole = self.profile(0, 0)
        outside = self.profile(1.7, 0)  # In circle, but outside model outer boundary.
        result = self.env['select_overlap_profiles'](
            self.sketch([hole, outside]), [r.faces.item(0) for r in regions])
        self.assertEqual(copied, [outer])
        self.assertEqual(result, [hole])

    def test_whole_body_projection_includes_buried_footprint(self):
        body = N(name='outer')
        outline_face = N(loops=[N(isOuter=True)])
        curve = N(isConstruction=True)
        calls = []
        def project(bodies, linked):
            calls.append((bodies, linked))
            return [curve]
        sketch = N(project2=project, profiles=Collection([N(face=outline_face)]))
        filled = N(isPointOnFace=lambda p, tol: -.2 < p.x < 1.5)
        region = N(faces=Collection([filled]))
        self.env['adsk'].fusion = N(SketchCurve=N(cast=lambda value:value))
        self.env['filled_outer_regions'] = lambda loops: [region]
        regions = self.env['project_body_outline'](sketch, [body])
        buried = self.profile(.8, 0)
        outside = self.profile(-.5, 0)
        result = self.env['select_overlap_profiles'](
            self.sketch([buried, outside]), [r.faces.item(0) for r in regions])
        self.assertEqual(result, [buried])
        self.assertEqual(calls, [([body], True)])
        self.assertFalse(curve.isConstruction)

    def test_no_overlap_fails_instead_of_using_full_circle(self):
        with self.assertRaisesRegex(RuntimeError, '重なる領域'):
            self.env['select_overlap_profiles'](
                self.sketch([self.profile(0, 0)]), [N(isPointOnFace=lambda p, tol: False)])

    def test_unknown_profile_geometry_fails(self):
        with self.assertRaisesRegex(RuntimeError, '内部点'):
            self.env['select_overlap_profiles'](self.sketch([N(face=None)]), [])


if __name__ == '__main__':
    unittest.main()
