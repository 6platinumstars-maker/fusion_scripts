"""Cut a rectangular region from Z=-6 to Z=34 mm in outer-shell results only."""
import json
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell

X_MIN_MM, X_MAX_MM = -80.0, -29.854
Y_MIN_MM, Y_MAX_MM = -35.0, -32.504
START_Z_MM, DEPTH_MM = -6.0, 40.0
NAME = '下部切かけ：余剰部長方形切取り'


def corners_mm():
    # Perimeter order; the user's listing is not perimeter order.
    return [(X_MIN_MM, Y_MIN_MM, START_Z_MM),
            (X_MAX_MM, Y_MIN_MM, START_Z_MM),
            (X_MAX_MM, Y_MAX_MM, START_Z_MM),
            (X_MIN_MM, Y_MAX_MM, START_Z_MM)]


def remaining_bodies(originals, feature):
    # Include untouched outer fragments; omit fully consumed ones. Keep new splits.
    result = []
    for body in list(originals) + [feature.bodies.item(i) for i in range(feature.bodies.count)]:
        if body.isValid and not any(body == known for known in result):
            result.append(body)
    return result


def write_report(report):
    path = Path(__file__).resolve().parent.parent/'lower_rectangle_cut_diagnostics.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def cut(root, outer_results):
    report = {'stage': 'create_rectangle', 'corners_mm': corners_mm(),
              'displacement_mm': [0, 0, DEPTH_MM]}
    try:
        originals = list(outer_results.values())
        if not originals:
            raise RuntimeError('長方形切取りの対象となる外殻がありません。')
        before = sum(body.volume for body in originals)
        report['input_bodies'] = [{'name':body.name,'volume_mm3':body.volume*1000}
                                  for body in originals]
        plane = outer_shell.create_offset_plane_from_xy(root, START_Z_MM, NAME+'：平面')
        sketch = root.sketches.add(plane)
        sketch.name = NAME+'：輪郭'
        pts = [sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in coords)))
               for coords in corners_mm()]
        lines = sketch.sketchCurves.sketchLines
        first = lines.addByTwoPoints(pts[0], pts[1])
        second = lines.addByTwoPoints(first.endSketchPoint, pts[2])
        third = lines.addByTwoPoints(second.endSketchPoint, pts[3])
        lines.addByTwoPoints(third.endSketchPoint, first.startSketchPoint)
        if sketch.profiles.count != 1:
            raise RuntimeError('長方形が単一の閉領域になりませんでした。')
        origin = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
        normal_tip = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
        direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection
                     if normal_tip.z > origin.z else adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes = root.features.extrudeFeatures
        data = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        extent = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(DEPTH_MM/10))
        data.setOneSideExtent(extent, direction)
        data.participantBodies = originals
        report['stage'] = 'rectangle_cut'
        write_report(report)
        feature = extrudes.add(data)
        feature.name = NAME
        bodies = remaining_bodies(originals, feature)
        report['result_body_count'] = len(bodies)
        report['result_bodies'] = [{'name':b.name,'is_solid':b.isSolid,'volume_mm3':b.volume*1000}
                                   for b in bodies]
        if not bodies or any(not body.isSolid for body in bodies):
            raise RuntimeError('長方形切取り後の外殻ソリッドを確認できません。')
        after = sum(body.volume for body in bodies)
        if after >= before-1e-9:
            raise RuntimeError('長方形切取りで外殻の合計体積が減少していません。')
        results = {}
        for index, body in enumerate(sorted(bodies, key=lambda b:b.volume, reverse=True)):
            name = naming.BODY_OUTER_SHELL if index == 0 else '{}：下部切かけ後{}'.format(naming.BODY_OUTER_SHELL,index+1)
            helpers.set_body_identity(body, name)
            body.isLightBulbOn = True
            results[name] = body
        sketch.isLightBulbOn = False
        plane.isLightBulbOn = False
        report.update(stage='rectangle_cut_succeeded', removed_volume_mm3=(before-after)*1000)
        write_report(report)
        return results
    except Exception as error:
        report['error'] = str(error)
        path = write_report(report)
        raise RuntimeError('{}\n診断記録: {}'.format(error,path)) from error
