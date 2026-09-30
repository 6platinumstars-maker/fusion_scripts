"""Diameter 7 mm second-stage bore along +X in the inner-shell joining pad."""
import json
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, inner_shell

CENTER_MM = (-73.795, -7.201, 10.492)
RADIUS_MM = 3.5
DEPTH_MM = 30.0
NAME = '内殻‐外殻‐グリップ部接合部：円C穴あけ'


def write_report(report):
    path = Path(__file__).resolve().parent.parent/'inner_joint_bore_c_diagnostics.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def cut(root, body):
    report = {'stage':'create_circle_C', 'center_mm':CENTER_MM,
              'diameter_mm':RADIUS_MM*2, 'displacement_mm':[DEPTH_MM,0,0],
              'end_x_mm':CENTER_MM[0]+DEPTH_MM}
    try:
        before = body.volume
        plane = inner_shell.create_offset_plane_from_yz(root, CENTER_MM[0], NAME+'：平面')
        sketch = root.sketches.add(plane)
        sketch.name = NAME+'：スケッチ'
        center = adsk.core.Point3D.create(*(value/10 for value in CENTER_MM))
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(
            sketch.modelToSketchSpace(center), RADIUS_MM/10)
        helpers.add_named_attribute(circle, '内殻接合部：円C')
        if sketch.profiles.count != 1:
            raise RuntimeError('穴あけ用円Cの閉領域を取得できません。')
        origin = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
        normal_tip = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
        direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection
                     if normal_tip.x > origin.x else adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes = root.features.extrudeFeatures
        data = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        extent = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(DEPTH_MM/10))
        data.setOneSideExtent(extent, direction)
        data.participantBodies = [body]
        report['stage'] = 'cut_positive_x'
        write_report(report)
        feature = extrudes.add(data)
        feature.name = NAME+'：+X30mm'
        report['result_body_count'] = feature.bodies.count
        if feature.bodies.count != 1:
            raise RuntimeError('円C穴あけ後の内殻が1ボディになりませんでした。形状を確認してください。')
        result = feature.bodies.item(0)
        report['volume_before_mm3'] = before*1000
        report['volume_after_mm3'] = result.volume*1000
        if not result.isSolid or result.volume >= before-1e-9:
            raise RuntimeError('円C穴あけによる内殻の体積減少を確認できません。')
        helpers.set_body_identity(result, naming.BODY_INNER_SHELL)
        sketch.isLightBulbOn = False
        plane.isLightBulbOn = False
        report.update(stage='bore_succeeded', removed_volume_mm3=(before-result.volume)*1000)
        write_report(report)
        return result
    except Exception as error:
        report['error'] = str(error)
        path = write_report(report)
        raise RuntimeError('{}\n診断記録: {}'.format(error,path)) from error
