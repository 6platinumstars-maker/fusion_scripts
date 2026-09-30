"""Extend the inner-shell curved surface to a flat circular joining pad."""
import json
import math
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, inner_shell

NAME = '内殻‐外殻‐グリップ部接合部'
CENTER_MM = (-76.795, -7.201, 10.492)
RADIUS_MM = 4.6


def projection_samples_mm():
    x,y,z = CENTER_MM
    return [CENTER_MM] + [(x, y+RADIUS_MM*math.cos(i*math.tau/32),
                           z+RADIUS_MM*math.sin(i*math.tau/32)) for i in range(32)]


def point_mm(coords):
    return adsk.core.Point3D.create(*(value/10 for value in coords))


def find_target_face(root, body, report):
    target = None
    report['projection_hits_mm'] = []
    for coords in projection_samples_mm():
        hits = adsk.core.ObjectCollection.create()
        faces = root.findBRepUsingRay(point_mm(coords), adsk.core.Vector3D.create(1,0,0),
            adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hits)
        found = None
        for index in range(faces.count):
            face = faces.item(index)
            if face.body == body:
                found = face
                hit = hits.item(index)
                report['projection_hits_mm'].append((hit.x*10,hit.y*10,hit.z*10))
                if hit.x*10 <= CENTER_MM[0]+1e-5:
                    raise RuntimeError('円Aから＋X方向に肉盛りする空間を確認できません。')
                break
        if found is None:
            raise RuntimeError('円Aの一部が＋X方向で内殻に届きません。')
        if target is None:
            target = found
        elif found != target:
            raise RuntimeError('円Aの投影先が複数の面に分かれています。対象曲面の確認が必要です。')
    if adsk.core.Plane.cast(target.geometry) is not None:
        raise RuntimeError('円Aの投影先が曲面ではなく平面です。対象面を確認してください。')
    report['target_surface_type'] = target.geometry.objectType
    return target


def write_report(report):
    path = Path(__file__).resolve().parent.parent/'inner_joint_diagnostics.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def project_reference_circle(projection, target, circle, axis, report):
    before = projection.sketchCurves.count
    returned = projection.projectToSurface([target], [circle],
        adsk.fusion.SurfaceProjectTypes.AlongVectorSurfaceProjectType, axis)
    after = projection.sketchCurves.count
    report['projection_return_type'] = type(returned).__name__
    report['projection_curves_before'] = before
    report['projection_curves_after'] = after
    # Some Fusion builds create the curves but return an empty result array.
    # Inspect the dedicated destination sketch, not the return array's truth value.
    if before != 0 or after == 0:
        raise RuntimeError('専用スケッチ上で参考円A′の生成を確認できませんでした。')
    curves = [projection.sketchCurves.item(i) for i in range(after)]
    report['projected_curve_count'] = len(curves)
    return curves


def add_joint(root, body):
    report = {'stage':'find_surface', 'center_mm':CENTER_MM,
              'diameter_mm':RADIUS_MM*2, 'projection_direction':[1,0,0]}
    try:
        volume_before = body.volume
        target = find_target_face(root, body, report)
        plane = inner_shell.create_offset_plane_from_yz(root, CENTER_MM[0], NAME+'：先端平面')
        sketch = root.sketches.add(plane)
        sketch.name = NAME+'：円A'
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(
            sketch.modelToSketchSpace(point_mm(CENTER_MM)), RADIUS_MM/10)
        helpers.add_named_attribute(circle, NAME+'：円A')
        if sketch.profiles.count != 1:
            raise RuntimeError('接合部の円Aの閉領域を取得できません。')
        report['stage'] = 'project_circle'
        projection = root.sketches.add(plane)
        projection.name = NAME+'：参考円A′'
        curves = project_reference_circle(
            projection, target, circle, root.xConstructionAxis, report)
        write_report(report)
        for index, curve in enumerate(curves):
            helpers.add_named_attribute(curve, NAME+'：参考円A′{}'.format(index+1))
        # Extrude the planar disk to the curved surface, then join this pad
        # explicitly to the inner shell. The visible result is a flat cap at X.
        origin = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
        normal_tip = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
        direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection
                     if normal_tip.x > origin.x else adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes = root.features.extrudeFeatures
        data = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extent = adsk.fusion.ToEntityExtentDefinition.create(target, False)
        data.setOneSideExtent(extent, direction)
        report['stage'] = 'extrude_to_surface'
        write_report(report)
        feature = extrudes.add(data)
        feature.name = NAME+'：曲面まで肉盛り'
        if feature.bodies.count != 1:
            raise RuntimeError('接合部の肉盛りが1ボディになりませんでした。')
        pad = feature.bodies.item(0)
        tools = adsk.core.ObjectCollection.create()
        tools.add(pad)
        combines = root.features.combineFeatures
        join = combines.createInput(body, tools)
        join.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        join.isKeepToolBodies = False
        report['stage'] = 'join_inner_shell'
        write_report(report)
        combined = combines.add(join)
        combined.name = NAME
        if combined.bodies.count != 1:
            raise RuntimeError('接合部を内殻へ結合できませんでした。')
        result = combined.bodies.item(0)
        if not result.isSolid or result.volume <= volume_before+1e-9:
            raise RuntimeError('内殻への肉盛りによる体積増加を確認できません。')
        # Check for the requested planar circular end face.
        cap = None
        for face in result.faces:
            flat = adsk.core.Plane.cast(face.geometry)
            if flat is None or abs(abs(flat.normal.x)-1) > 1e-6:
                continue
            if abs(flat.origin.x*10-CENTER_MM[0]) > 1e-4:
                continue
            if abs(face.area*100-math.pi*RADIUS_MM**2) < 0.01:
                cap = face
                break
        if cap is None:
            raise RuntimeError('X=-76.795 mmの直径9.2 mmの平坦な先端面を確認できません。')
        helpers.add_named_attribute(cap, NAME+'：先端円面')
        helpers.set_body_identity(result, naming.BODY_INNER_SHELL)
        report.update(stage='joint_succeeded', added_volume_mm3=(result.volume-volume_before)*1000)
        write_report(report)
        return result
    except Exception as error:
        report['error'] = str(error)
        path = write_report(report)
        raise RuntimeError('{}\n診断記録: {}'.format(error,path)) from error
