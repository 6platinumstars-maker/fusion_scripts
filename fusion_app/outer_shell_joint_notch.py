"""Joint notch: circle/rectangle/triangle union cut along world +X."""
import json
import math
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell, outer_shell_rectangle_cut

NAME = '接合部切かけ'
X_MM = -76.795
DEPTH_MM = 40.0
RADIUS_MM = 5.0
POINTS_MM = {
    'A': (X_MM, -7.201, 10.495),
    'B': (X_MM, -7.201, 15.495),
    'C': (X_MM, -29.201, 15.495),
    'D': (X_MM, -29.201, 5.495),
    'E': (X_MM, -7.201, 5.495),
    'F': (X_MM, -13.725, -3.20),
}


def expected_area_mm2():
    # Left half of the circle is contained in the rectangle. Triangle shares DE.
    width = POINTS_MM['E'][1] - POINTS_MM['D'][1]
    rectangle = width * (POINTS_MM['B'][2] - POINTS_MM['E'][2])
    triangle = width * (POINTS_MM['E'][2] - POINTS_MM['F'][2]) / 2
    return rectangle + triangle + math.pi * RADIUS_MM**2 / 2


def write_report(report):
    path = Path(__file__).resolve().parent.parent/'joint_notch_diagnostics.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def cut(root, outer_results):
    report = {'stage': 'create_sketch', 'points_mm': POINTS_MM,
              'radius_mm': RADIUS_MM, 'displacement_mm': [DEPTH_MM, 0, 0],
              'end_x_mm': X_MM + DEPTH_MM}
    try:
        originals = list(outer_results.values())
        if not originals:
            raise RuntimeError('接合部切かけの対象外殻がありません。')
        before = sum(body.volume for body in originals)
        plane = outer_shell.create_offset_plane_from_yz(root, X_MM, NAME+'：YZ平面')
        sketch = root.sketches.add(plane)
        sketch.name = NAME+'：円A・長方形BCDE・三角形EDF'
        points = {key: sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in xyz)))
                  for key, xyz in POINTS_MM.items()}
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(points['A'], RADIUS_MM/10)
        lines = sketch.sketchCurves.sketchLines
        bc = lines.addByTwoPoints(points['B'], points['C'])
        cd = lines.addByTwoPoints(bc.endSketchPoint, points['D'])
        de = lines.addByTwoPoints(cd.endSketchPoint, points['E'])
        lines.addByTwoPoints(de.endSketchPoint, bc.startSketchPoint)
        # DE belongs to both closed shapes; do not create a duplicate edge ED.
        df = lines.addByTwoPoints(de.startSketchPoint, points['F'])
        lines.addByTwoPoints(df.endSketchPoint, de.endSketchPoint)
        helpers.add_named_attribute(circle, NAME+'：円A')
        vertices = {'A':circle.centerSketchPoint,'B':bc.startSketchPoint,
                    'C':bc.endSketchPoint,'D':de.startSketchPoint,
                    'E':de.endSketchPoint,'F':df.endSketchPoint}
        for key, vertex in vertices.items():
            helpers.add_named_attribute(vertex, NAME+'：'+key)
        # Every profile in this clean sketch belongs to the requested union.
        profiles = adsk.core.ObjectCollection.create()
        area = 0.0
        for index in range(sketch.profiles.count):
            profile = sketch.profiles.item(index)
            profiles.add(profile)
            area += profile.areaProperties().area*100
        report.update(profile_count=profiles.count, area_mm2=area,
                      expected_area_mm2=expected_area_mm2())
        if profiles.count == 0 or abs(area-expected_area_mm2()) > 0.01:
            raise RuntimeError('円・長方形・三角形の合成領域の面積が一致しません。スケッチを確認してください。')
        origin = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
        normal_tip = sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
        direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection
                     if normal_tip.x > origin.x else adsk.fusion.ExtentDirections.NegativeExtentDirection)
        report['stage'] = 'cut_positive_x'
        write_report(report)
        extrudes = root.features.extrudeFeatures
        data = extrudes.createInput(profiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extent = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(DEPTH_MM/10))
        data.setOneSideExtent(extent, direction)
        data.participantBodies = originals
        feature = extrudes.add(data)
        feature.name = NAME+'：+X40mm切取り'
        bodies = outer_shell_rectangle_cut.remaining_bodies(originals, feature)
        report['result_body_count'] = len(bodies)
        report['result_bodies'] = [{'name':b.name, 'volume_mm3':b.volume*1000, 'is_solid':b.isSolid}
                                  for b in bodies]
        if not bodies or any(not b.isSolid for b in bodies):
            raise RuntimeError('接合部切かけ後の外殻ソリッドを確認できません。')
        after = sum(b.volume for b in bodies)
        if after >= before-1e-9:
            raise RuntimeError('接合部切かけで外殻の合計体積が減少していません。')
        results = {}
        for index, body in enumerate(sorted(bodies, key=lambda b:b.volume, reverse=True)):
            name = naming.BODY_OUTER_SHELL if index == 0 else '{}：切かけ後{}'.format(naming.BODY_OUTER_SHELL,index+1)
            helpers.set_body_identity(body, name)
            body.isLightBulbOn = True
            results[name] = body
        sketch.isLightBulbOn = False
        plane.isLightBulbOn = False
        report.update(stage='cut_succeeded', removed_volume_mm3=(before-after)*1000)
        write_report(report)
        return results
    except Exception as error:
        report['error'] = str(error)
        path = write_report(report)
        raise RuntimeError('{}\n診断記録: {}'.format(error,path)) from error
