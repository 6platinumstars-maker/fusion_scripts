"""Cut the lower-notch closed contour, using the confirmed circle sketch."""
import json
import math
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell_lower_notch as geometry

CONTOUR_HINTS_MM = {
    'P1': (-80.00, 32.233, 29.223),
    'P2': (-80.00, -34.967, 23.639),
    'P3': (-29.854, -34.967, 23.639),
    'D': (-29.854, -27.312, 24.275),
}
DEPTH_MM = 40.0


def circle_point_and_sweep(center, hint, end, radius):
    delta = geometry.subtract(hint, center)
    direction = geometry.unit(delta)
    start = tuple(center[i]+radius*direction[i] for i in range(2))
    a = math.atan2(start[1]-center[1], start[0]-center[0])
    b = math.atan2(end[1]-center[1], end[0]-center[0])
    sweep = (b-a+math.pi) % (2*math.pi)-math.pi
    return start, sweep


def write_report(report):
    path = Path(__file__).resolve().parent.parent/'lower_notch_cut_diagnostics.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def collect_cut_results(feature, volume_before, report):
    bodies = [feature.bodies.item(i) for i in range(feature.bodies.count)]
    report['result_body_count'] = len(bodies)
    report['result_bodies'] = [
        {'name': body.name, 'is_solid': body.isSolid, 'volume_mm3': body.volume*1000}
        for body in bodies
    ]
    if not bodies:
        raise RuntimeError('下部切かけの結果ボディを取得できませんでした。')
    if any(not body.isSolid or body.volume <= 0 for body in bodies):
        raise RuntimeError('下部切かけの結果に正常なソリッドではないボディがあります。')
    volume_after = sum(body.volume for body in bodies)
    if volume_after >= volume_before-1e-9:
        raise RuntimeError('下部切かけで外殻の合計体積が減少していません。')
    # Keep every resulting solid. Largest-first ordering is only for naming;
    # no fragment is silently deleted, merged, or excluded from the result.
    bodies.sort(key=lambda body: body.volume, reverse=True)
    results = {}
    for index, body in enumerate(bodies):
        name = (naming.BODY_OUTER_SHELL if index == 0 else
                '{}：下部切かけ後{}'.format(naming.BODY_OUTER_SHELL, index+1))
        helpers.set_body_identity(body, name)
        body.isLightBulbOn = True
        results[name] = body
    report['result_bodies'] = [
        {'name': body.name, 'is_solid': body.isSolid, 'volume_mm3': body.volume*1000}
        for body in bodies
    ]
    report.update(stage='cut_succeeded', removed_volume_mm3=(volume_before-volume_after)*1000)
    return results


def cut(root, body, source_sketch):
    report = {'stage': 'prepare_contour', 'input_points_mm': CONTOUR_HINTS_MM,
              'depth_mm': -DEPTH_MM}
    try:
        source = json.loads(source_sketch.attributes.itemByName(
            naming.ATTRIBUTE_GROUP, 'lower_notch_spec').value)
        report['source_plane'] = source['selected_plane']
        # A clean coplanar sketch avoids automatically projected face edges and
        # the complete circle splitting the requested contour into extra regions.
        # Query the current body, not Sketch.referencePlane: Fusion requires
        # rolling the timeline back to access a face-backed sketch reference.
        support_face, _ = geometry.select_face(root, body, report)
        selected = report['selected_plane']
        original = source['selected_plane']
        if not geometry.same_plane(
                (selected['origin_mm'], selected['normal']),
                (original['origin_mm'], original['normal'])):
            raise RuntimeError('切取り面が確認済みスケッチの平面と一致しません。')
        planes = root.constructionPlanes
        plane_input = planes.createInput()
        plane_input.setByOffset(support_face,
                               adsk.core.ValueInput.createByReal(0))
        plane = planes.add(plane_input)
        plane.name = '下部切かけ：切取り平面'
        sketch = root.sketches.add(plane)
        sketch.name = '下部切かけ：切取り領域'

        def local(coords):
            p = sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in coords)))
            return (p.x, p.y)

        def point(coords):
            return adsk.core.Point3D.create(*coords, 0)

        coords = {key: local(value) for key, value in CONTOUR_HINTS_MM.items()}
        for key in ('A', 'B', 'C'):
            coords[key] = local(source['actual_points_mm'][key])
        coords['D'], sweep = circle_point_and_sweep(
            coords['A'], coords['D'], coords['C'], geometry.RADIUS_MM/10)
        report['arc_sweep_deg'] = math.degrees(sweep)
        report['actual_points_mm'] = {}
        report['correction_mm'] = {}
        for key, value in coords.items():
            p = sketch.sketchToModelSpace(point(value))
            actual = (p.x*10, p.y*10, p.z*10)
            report['actual_points_mm'][key] = actual
            if key in CONTOUR_HINTS_MM:
                difference = geometry.subtract(actual, CONTOUR_HINTS_MM[key])
                report['correction_mm'][key] = math.sqrt(geometry.dot(difference, difference))
        if max(report['correction_mm'].values()) > geometry.MAX_POINT_ADJUSTMENT_MM:
            raise RuntimeError('切取り輪郭の補正が0.1 mmを超えました。診断記録を確認してください。')
        arcs = sketch.sketchCurves.sketchArcs
        arc = arcs.addByCenterStartSweep(point(coords['A']), point(coords['D']), sweep)
        # Fusion stores arcs counterclockwise even for a negative input sweep.
        endpoints = (arc.startSketchPoint, arc.endSketchPoint)
        def distance_to_D(p):
            return (p.geometry.x-coords['D'][0])**2+(p.geometry.y-coords['D'][1])**2
        d_vertex = min(endpoints, key=distance_to_D)
        c_vertex = max(endpoints, key=distance_to_D)
        lines = sketch.sketchCurves.sketchLines
        first = lines.addByTwoPoints(point(coords['P1']), point(coords['P2']))
        second = lines.addByTwoPoints(first.endSketchPoint, point(coords['P3']))
        lines.addByTwoPoints(second.endSketchPoint, d_vertex)
        tangent = lines.addByTwoPoints(c_vertex, point(coords['B']))
        lines.addByTwoPoints(tangent.endSketchPoint, first.startSketchPoint)
        if sketch.profiles.count != 1:
            raise RuntimeError('切取り領域が単一の閉領域になりませんでした。')

        # Negative along the confirmed upward-facing slope normal, regardless of
        # whether the newly created sketch's local Z is reversed.
        normal = source['selected_plane']['normal']
        if normal[2] < 0:
            normal = [-v for v in normal]
        origin = sketch.sketchToModelSpace(adsk.core.Point3D.create(0, 0, 0))
        z_point = sketch.sketchToModelSpace(adsk.core.Point3D.create(0, 0, 1))
        z_direction = (z_point.x-origin.x, z_point.y-origin.y, z_point.z-origin.z)
        directions = adsk.fusion.ExtentDirections
        direction = (directions.NegativeExtentDirection if geometry.dot(z_direction, normal) > 0
                     else directions.PositiveExtentDirection)
        report['displacement_mm'] = [-DEPTH_MM*v for v in normal]
        report['stage'] = 'extrude_cut'
        write_report(report)
        volume_before = body.volume
        extrudes = root.features.extrudeFeatures
        cut_input = extrudes.createInput(sketch.profiles.item(0),
                                        adsk.fusion.FeatureOperations.CutFeatureOperation)
        extent = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(DEPTH_MM/10))
        cut_input.setOneSideExtent(extent, direction)
        cut_input.participantBodies = [body]
        feature = extrudes.add(cut_input)
        feature.name = '下部切かけ：-40mm切取り'
        results = collect_cut_results(feature, volume_before, report)
        write_report(report)
        source_sketch.isLightBulbOn = False
        sketch.isLightBulbOn = False
        plane.isLightBulbOn = False
        return results
    except Exception as error:
        report['error'] = str(error)
        path = write_report(report)
        raise RuntimeError('{}\n診断記録: {}'.format(error, path)) from error
