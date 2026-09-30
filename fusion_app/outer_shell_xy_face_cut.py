"""Cut outer-shell XY faces at Z=-3.2 mm towards world -Z."""
import json
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell_rectangle_cut

START_Z_MM = -3.2
DEPTH_MM = 0.5
NAME = '３Dプリント用微調整：1 外殻XY面Z-3.2：-Z0.5mm切取り'


def select_faces(bodies):
    faces = adsk.core.ObjectCollection.create()
    for body in bodies:
        for face in body.faces:
            plane = adsk.core.Plane.cast(face.geometry)
            if plane is None:
                continue
            normal = plane.normal
            if (abs(normal.x) <= 1e-6 and abs(normal.y) <= 1e-6
                    and abs(abs(normal.z) - 1.0) <= 1e-6
                    and abs(plane.origin.z * 10 - START_Z_MM) <= 0.001):
                faces.add(face)
    return faces


def cut(root, outer_results):
    report = {'start_z_mm': START_Z_MM, 'end_z_mm': START_Z_MM - DEPTH_MM,
              'displacement_mm': [0, 0, -DEPTH_MM], 'stage': 'select_faces'}
    path = Path(__file__).resolve().parent.parent / 'outer_xy_face_cut_diagnostics.json'
    try:
        originals = list(outer_results.values())
        before = sum(body.volume for body in originals)
        faces = select_faces(originals)
        report['face_count'] = faces.count
        if faces.count == 0:
            raise RuntimeError('外殻上のZ=-3.2 mmのXY平面を検出できません。')
        normal = adsk.core.Plane.cast(faces.item(0).geometry).normal
        direction = (adsk.fusion.ExtentDirections.NegativeExtentDirection
                     if normal.z > 0 else adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extrudes = root.features.extrudeFeatures
        data = extrudes.createInput(faces, adsk.fusion.FeatureOperations.CutFeatureOperation)
        data.participantBodies = originals
        extent = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(DEPTH_MM / 10))
        data.setOneSideExtent(extent, direction)
        report['stage'] = 'cut_negative_z'
        feature = extrudes.add(data)
        feature.name = NAME
        bodies = outer_shell_rectangle_cut.remaining_bodies(originals, feature)
        if not bodies or any(not body.isSolid for body in bodies):
            raise RuntimeError('XY面切取り後の外殻ソリッドを確認できません。')
        after = sum(body.volume for body in bodies)
        if after >= before - 1e-9:
            raise RuntimeError('XY面切取りで外殻の合計体積が減少していません。')
        results = {}
        for index, body in enumerate(sorted(bodies, key=lambda b: b.volume, reverse=True)):
            name = naming.BODY_OUTER_SHELL if index == 0 else '{}：XY面切取り後{}'.format(
                naming.BODY_OUTER_SHELL, index + 1)
            helpers.set_body_identity(body, name)
            body.isLightBulbOn = True
            results[name] = body
        report.update(stage='succeeded', removed_volume_mm3=(before - after) * 1000,
                      result_body_count=len(bodies))
        return results
    except Exception as error:
        report['error'] = str(error)
        raise RuntimeError('{}\n診断記録: {}'.format(error, path)) from error
    finally:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
