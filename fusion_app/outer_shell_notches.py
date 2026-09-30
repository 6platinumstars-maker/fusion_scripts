"""Notches applied only by the standalone outer-shell entry (2)."""
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell, outer_shell_rectangle_cut

UPPER_NOTCH_POINTS_MM = {
    'T': (-76.795, 32.233, 29.233),
    'A': (-76.795, 18.768, -6.00),
    'B': (-76.795, 32.20, -6.00),
    'C': (-67.298, 32.20, -6.00),
}
UPPER_NOTCH_NAME = '上部切かけ'


def point_on_sketch(sketch, point_mm):
    point = adsk.core.Point3D.create(*(coordinate / 10.0 for coordinate in point_mm))
    return sketch.modelToSketchSpace(point)


def cut_upper_notch(root_comp, outer_results):
    originals = list(outer_results.values())
    if not originals:
        raise RuntimeError('上部切かけの対象となる外殻がありません。')
    volume_before = sum(body.volume for body in originals)
    points = UPPER_NOTCH_POINTS_MM
    base_plane = outer_shell.create_offset_plane_from_xy(
        root_comp, points['A'][2], UPPER_NOTCH_NAME + '：底面平面',
    )
    base_sketch = root_comp.sketches.add(base_plane)
    base_sketch.name = UPPER_NOTCH_NAME + '：三角形ABC'
    lines = base_sketch.sketchCurves.sketchLines
    vertices = [point_on_sketch(base_sketch, points[key]) for key in ('A', 'B', 'C')]
    for index in range(3):
        lines.addByTwoPoints(vertices[index], vertices[(index + 1) % 3])
    if base_sketch.profiles.count != 1:
        raise RuntimeError('上部切かけの三角形ABCを作成できませんでした。')

    apex_plane = outer_shell.create_offset_plane_from_xy(
        root_comp, points['T'][2], UPPER_NOTCH_NAME + '：頂点平面',
    )
    apex_sketch = root_comp.sketches.add(apex_plane)
    apex_sketch.name = UPPER_NOTCH_NAME + '：頂点T'
    apex = apex_sketch.sketchPoints.add(point_on_sketch(apex_sketch, points['T']))

    lofts = root_comp.features.loftFeatures
    loft_input = lofts.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
    loft_input.isSolid = True
    # Free end conditions: straight triangular sides, without tangent rounding.
    loft_input.loftSections.add(base_sketch.profiles.item(0))
    loft_input.loftSections.add(apex)
    # Never cut the frozen inner-shell reference stored in this design.
    loft_input.participantBodies = originals
    feature = lofts.add(loft_input)
    feature.name = UPPER_NOTCH_NAME
    helpers.add_named_attribute(feature, UPPER_NOTCH_NAME)
    bodies = outer_shell_rectangle_cut.remaining_bodies(originals, feature)
    if not bodies or any(not body.isSolid for body in bodies):
        raise RuntimeError('上部切かけ後の外殻ソリッドを確認できません。')
    volume_after = sum(body.volume for body in bodies)
    if volume_after >= volume_before - 1e-9:
        raise RuntimeError('上部切かけで外殻の合計体積が減っていません。指定位置と形状を確認してください。')
    results = {}
    for index, body in enumerate(sorted(bodies, key=lambda b: b.volume, reverse=True)):
        name = (naming.BODY_OUTER_SHELL if index == 0 else
                '{}：切かけ後{}'.format(naming.BODY_OUTER_SHELL, index+1))
        helpers.set_body_identity(body, name)
        body.isLightBulbOn = True
        results[name] = body
    for entity in (base_sketch, apex_sketch, base_plane, apex_plane):
        entity.isLightBulbOn = False
    return results
