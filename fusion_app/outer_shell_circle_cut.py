"""Cut the R19 circle clipped to the whole-body XY silhouette, including buried areas."""
import json
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell_rectangle_cut

CENTER_MM = (-22.452, -10.879, -3.7)
RADIUS_MM = 19.0
DEPTH_MM = 13.3
NAME = '３Dプリント用微調整：3 外殻XY面Z-3.7：R19円+Z13.3mm切取り'


def select_support_faces(bodies):
    candidates = []
    for body in bodies:
        for face in body.faces:
            plane = adsk.core.Plane.cast(face.geometry)
            if plane is None:
                continue
            normal = plane.normal
            if (abs(normal.x) <= 1e-6 and abs(normal.y) <= 1e-6
                    and abs(abs(normal.z) - 1.0) <= 1e-6
                    and abs(plane.origin.z * 10 - CENTER_MM[2]) <= 0.001):
                candidates.append(face)
    if not candidates:
        raise RuntimeError('外殻上のZ=-3.7 mmのXY平面を検出できません。')
    return candidates


def outer_loops(faces):
    loops = [loop for face in faces for loop in face.loops if loop.isOuter]
    if not loops:
        raise RuntimeError('モデル面の外周を取得できません。')
    return loops


def filled_outer_regions(loops):
    # One outer loop per temporary face: intentionally omit all inner loops.
    # Keep the bodies alive while their faces are used for point containment.
    manager = adsk.fusion.TemporaryBRepManager.get()
    regions = []
    for loop in loops:
        wire = manager.copy(loop)
        if wire is None:
            raise RuntimeError('モデル面の外周を複製できません。')
        region = manager.createFaceFromPlanarWires([wire])
        if region is None or region.faces.count != 1:
            raise RuntimeError('モデル外周内部の領域を作成できません。')
        regions.append(region)
    return regions


def project_body_outline(sketch, bodies):
    # A body projection includes geometry above/below the starting plane.
    # Projecting just the starting face loses the buried wall footprint.
    curves = sketch.project2(list(bodies), True)
    if not curves:
        raise RuntimeError('外殻全体のXY投影輪郭を取得できません。')
    for entity in curves:
        curve = adsk.fusion.SketchCurve.cast(entity)
        if curve is not None:
            curve.isConstruction = False
    if sketch.profiles.count == 0:
        raise RuntimeError('外殻全体の投影輪郭が閉じていません。')
    # Capture filled outline regions before the circle subdivides the sketch.
    # These temporary faces are in SKETCH coordinates and preserve concavities.
    faces = [sketch.profiles.item(i).face for i in range(sketch.profiles.count)]
    if any(face is None for face in faces):
        raise RuntimeError('投影輪郭の面を取得できません。')
    return filled_outer_regions(outer_loops(faces))


def select_overlap_profiles(sketch, filled_faces):
    selected = adsk.core.ObjectCollection.create()
    radius_cm = RADIUS_MM / 10
    center_x, center_y = CENTER_MM[0] / 10, CENTER_MM[1] / 10
    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        # A centroid can be outside a concave region or inside a hole.
        # Profile.face is in sketch space; pointOnFace is strictly interior.
        profile_face = profile.face
        if profile_face is None:
            raise RuntimeError('分割領域の内部点を取得できません。')
        local_point = profile_face.pointOnFace
        point = sketch.sketchToModelSpace(local_point)
        inside_circle = ((point.x - center_x) ** 2 + (point.y - center_y) ** 2
                         < radius_cm ** 2)
        if inside_circle and any(face.isPointOnFace(local_point, 1e-7) for face in filled_faces):
            selected.add(profile)
    if selected.count == 0:
        raise RuntimeError('円とモデル全体のXY投影外周内部が重なる領域を検出できません。')
    return selected


def cut(root, outer_results):
    report = {'center_mm': CENTER_MM, 'radius_mm': RADIUS_MM,
              'end_z_mm': CENTER_MM[2] + DEPTH_MM, 'displacement_mm': [0, 0, DEPTH_MM], 'stage': 'select_faces'}
    path = Path(__file__).resolve().parent.parent / 'outer_circle_cut_diagnostics.json'
    try:
        originals = list(outer_results.values())
        before = sum(body.volume for body in originals)
        faces = select_support_faces(originals)
        face = max(faces, key=lambda candidate: candidate.area)
        report.update(support_face_count=len(faces),
                      selection='circle_intersection_whole_body_xy_silhouette')
        planes = root.constructionPlanes
        plane_input = planes.createInput()
        plane_input.setByOffset(face, adsk.core.ValueInput.createByReal(0))
        plane = planes.add(plane_input)
        plane.name = NAME + '：面参照平面'
        sketch = root.sketches.add(plane)
        sketch.name = NAME + '：円とモデル全体XY投影の共通領域'
        regions = project_body_outline(sketch, originals)
        filled_faces = [region.faces.item(0) for region in regions]
        report['outline_region_count'] = len(regions)
        center = adsk.core.Point3D.create(*(value / 10 for value in CENTER_MM))
        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            sketch.modelToSketchSpace(center), RADIUS_MM / 10)
        profiles = select_overlap_profiles(sketch, filled_faces)
        report.update(profile_count=sketch.profiles.count, selected_profile_count=profiles.count,
                      selected_area_mm2=sum(profiles.item(i).areaProperties().area * 100
                                            for i in range(profiles.count)))
        origin = sketch.sketchToModelSpace(adsk.core.Point3D.create(0, 0, 0))
        tip = sketch.sketchToModelSpace(adsk.core.Point3D.create(0, 0, 1))
        direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection
                     if tip.z > origin.z else adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes = root.features.extrudeFeatures
        data = extrudes.createInput(profiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
        data.participantBodies = originals
        extent = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(DEPTH_MM / 10))
        data.setOneSideExtent(extent, direction)
        report['stage'] = 'cut_positive_z'
        feature = extrudes.add(data)
        feature.name = NAME
        bodies = outer_shell_rectangle_cut.remaining_bodies(originals, feature)
        if not bodies or any(not body.isSolid for body in bodies):
            raise RuntimeError('円切取り後の外殻ソリッドを確認できません。')
        after = sum(body.volume for body in bodies)
        if after >= before - 1e-9:
            raise RuntimeError('円切取りで外殻の合計体積が減少していません。')
        results = {}
        for index, body in enumerate(sorted(bodies, key=lambda b: b.volume, reverse=True)):
            name = naming.BODY_OUTER_SHELL if index == 0 else '{}：円切取り後{}'.format(
                naming.BODY_OUTER_SHELL, index + 1)
            helpers.set_body_identity(body, name)
            body.isLightBulbOn = True
            results[name] = body
        sketch.isLightBulbOn = False
        plane.isLightBulbOn = False
        report.update(stage='succeeded', removed_volume_mm3=(before - after) * 1000,
                      result_body_count=len(bodies))
        return results
    except Exception as error:
        report['error'] = str(error)
        raise RuntimeError('{}\n診断記録: {}'.format(error, path)) from error
    finally:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
