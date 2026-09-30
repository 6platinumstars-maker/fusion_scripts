"""Join an extrusion of outer-shell YZ faces at X=0 mm towards world +X."""
import json
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell_rectangle_cut

START_X_MM = 0.0
DEPTH_MM = 0.5
NAME = '３Dプリント用微調整：2 外殻YZ面X0：+X0.5mm押し出し'


def select_faces(bodies):
    faces = adsk.core.ObjectCollection.create()
    for body in bodies:
        for face in body.faces:
            plane = adsk.core.Plane.cast(face.geometry)
            if plane is None:
                continue
            normal = plane.normal
            if (abs(normal.z) <= 1e-6 and abs(normal.y) <= 1e-6
                    and abs(abs(normal.x) - 1.0) <= 1e-6
                    and abs(plane.origin.x * 10 - START_X_MM) <= 0.001):
                faces.add(face)
    return faces


def extrude(root, outer_results):
    report = {'start_x_mm': START_X_MM, 'end_x_mm': START_X_MM + DEPTH_MM,
              'displacement_mm': [DEPTH_MM, 0, 0], 'stage': 'select_faces'}
    path = Path(__file__).resolve().parent.parent / 'outer_yz_face_extrude_diagnostics.json'
    try:
        originals = list(outer_results.values())
        before = sum(body.volume for body in originals)
        faces = select_faces(originals)
        report['face_count'] = faces.count
        if faces.count == 0:
            raise RuntimeError('外殻上のX=0 mmのYZ平面を検出できません。')
        normal = adsk.core.Plane.cast(faces.item(0).geometry).normal
        direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection
                     if normal.x > 0 else adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes = root.features.extrudeFeatures
        data = extrudes.createInput(faces, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extent = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(DEPTH_MM / 10))
        data.setOneSideExtent(extent, direction)
        report['stage'] = 'join_positive_x'
        feature = extrudes.add(data)
        feature.name = NAME
        bodies = outer_shell_rectangle_cut.remaining_bodies(originals, feature)
        if not bodies or any(not body.isSolid for body in bodies):
            raise RuntimeError('YZ面押し出し後の外殻ソリッドを確認できません。')
        after = sum(body.volume for body in bodies)
        if after <= before + 1e-9:
            raise RuntimeError('YZ面押し出しで外殻の合計体積が増加していません。')
        results = {}
        for index, body in enumerate(sorted(bodies, key=lambda b: b.volume, reverse=True)):
            name = naming.BODY_OUTER_SHELL if index == 0 else '{}：YZ面押し出し後{}'.format(
                naming.BODY_OUTER_SHELL, index + 1)
            helpers.set_body_identity(body, name)
            body.isLightBulbOn = True
            results[name] = body
        report.update(stage='succeeded', added_volume_mm3=(after - before) * 1000,
                      result_body_count=len(bodies))
        return results
    except Exception as error:
        report['error'] = str(error)
        raise RuntimeError('{}\n診断記録: {}'.format(error, path)) from error
    finally:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
