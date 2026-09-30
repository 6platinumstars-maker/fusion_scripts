"""Lower-notch sketch on the actual outer-shell face; no solid modification."""
import json
import math
from pathlib import Path
import adsk.core
from . import helpers, naming

PLANE_HINTS_MM = ((-80.0, 32.233, 29.223),
                  (-80.0, -34.967, 23.639),
                  (-29.854, -35.0, 23.639))
POINTS_MM = {'A': (-41.895, 5.303, 26.985),
             'B': (-76.795, 32.322, 29.223),
             'C': (-76.795, 5.303, 26.985)}
RADIUS_MM = 34.9
FACE_DISTANCE_TOL_MM = 0.05
FACE_ANGLE_TOL_DEG = 0.1
MAX_POINT_ADJUSTMENT_MM = 0.1
SKETCH_NAME = '下部切かけ：円A・接線BC'


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x-y for x, y in zip(a, b))


def unit(v):
    length = math.sqrt(dot(v, v))
    if length < 1e-12:
        raise RuntimeError('平面の方向を計算できません。')
    return tuple(x/length for x in v)


def hint_normal():
    u = subtract(PLANE_HINTS_MM[1], PLANE_HINTS_MM[0])
    v = subtract(PLANE_HINTS_MM[2], PLANE_HINTS_MM[0])
    return unit((u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]))


def plane_data(plane):
    return ((plane.origin.x*10, plane.origin.y*10, plane.origin.z*10),
            unit((plane.normal.x, plane.normal.y, plane.normal.z)))


def plane_error(origin, normal):
    distances = [abs(dot(subtract(p, origin), normal)) for p in PLANE_HINTS_MM]
    angle = math.degrees(math.acos(min(1.0, abs(dot(normal, hint_normal())))))
    return max(distances), angle


def same_plane(a, b):
    return (abs(dot(a[1], b[1])) > 1-1e-10
            and abs(dot(subtract(a[0], b[0]), b[1])) < 1e-5)


def select_face(root, body, report):
    candidates = []
    report['planar_faces'] = []
    for face in body.faces:
        plane = adsk.core.Plane.cast(face.geometry)
        if plane is None:
            continue
        data = plane_data(plane)
        distance, angle = plane_error(*data)
        attribute = face.attributes.itemByName(naming.ATTRIBUTE_GROUP, naming.ATTRIBUTE_NAME_KEY)
        name = attribute.value if attribute else ''
        row = {'name': name, 'max_hint_distance_mm': distance, 'angle_deg': angle}
        report['planar_faces'].append(row)
        if distance <= FACE_DISTANCE_TOL_MM and angle <= FACE_ANGLE_TOL_DEG:
            candidates.append((face, data, name))
    if not candidates:
        raise RuntimeError('指定位置に近い外殻の斜面がありません。診断記録の候補面を確認してください。')
    # Multiple coplanar face patches describe the same sketch plane.
    if any(not same_plane(candidates[0][1], item[1]) for item in candidates[1:]):
        raise RuntimeError('近い斜面が複数あります。面を特定するまでスケッチを作成しません。')
    face, data, name = max(candidates, key=lambda item: (bool(item[2]), item[0].area))
    if not name:
        for construction in root.constructionPlanes:
            plane = adsk.core.Plane.cast(construction.geometry)
            if plane is not None and same_plane(data, plane_data(plane)):
                name = construction.name
                break
    if not name:
        name = '外殻蓋部斜面'
    report['selected_plane'] = {'name': name, 'origin_mm': data[0], 'normal': data[1]}
    return face, name


def closest_tangent(center, start, hint, radius):
    v = subtract(start, center)
    d2 = dot(v, v)
    if d2 <= radius*radius:
        raise RuntimeError('点Bが円の内側または円上のため接線BCを作成できません。')
    factor = radius*math.sqrt(d2-radius*radius)/d2
    middle = tuple(center[i]+radius*radius*v[i]/d2 for i in range(2))
    perpendicular = (-v[1], v[0])
    candidates = [tuple(middle[i]+sign*factor*perpendicular[i] for i in range(2))
                  for sign in (-1, 1)]
    return min(candidates, key=lambda point: dot(subtract(point, hint), subtract(point, hint)))


def write_report(report):
    path = Path(__file__).resolve().parent.parent/'lower_notch_sketch_diagnostics.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def create_sketch(root, body):
    report = {'stage': 'select_face', 'plane_hints_mm': PLANE_HINTS_MM,
              'input_points_mm': POINTS_MM, 'radius_mm': RADIUS_MM}
    sketch = None
    try:
        face, face_name = select_face(root, body, report)
        report['stage'] = 'project_points'
        sketch = root.sketches.add(face)
        sketch.name = SKETCH_NAME
        # Work in the face's sketch coordinates and explicitly project onto z=0.
        projected = {}
        for key, coords in POINTS_MM.items():
            model = adsk.core.Point3D.create(*(value/10 for value in coords))
            local = sketch.modelToSketchSpace(model)
            projected[key] = (local.x, local.y)
        center, start = projected['A'], projected['B']
        end = closest_tangent(center, start, projected['C'], RADIUS_MM/10)
        actual = {}
        correction = {}
        for key, coords in [('A', center), ('B', start), ('C', end)]:
            model = sketch.sketchToModelSpace(adsk.core.Point3D.create(*coords, 0))
            actual[key] = (model.x*10, model.y*10, model.z*10)
            diff = subtract(actual[key], POINTS_MM[key])
            correction[key] = math.sqrt(dot(diff, diff))
        report.update(actual_points_mm=actual, correction_mm=correction)
        if max(correction.values()) > MAX_POINT_ADJUSTMENT_MM:
            raise RuntimeError('点の補正量が0.1 mmを超えています。座標と対象面を確認してください。')
        report['stage'] = 'draw_circle_and_line'
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(*center, 0), RADIUS_MM/10)
        line = sketch.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create(*start, 0), adsk.core.Point3D.create(*end, 0))
        # Preserve the computed geometry without solver-induced coordinate changes.
        circle.isFixed = True
        line.isFixed = True
        helpers.add_named_attribute(circle, '下部切かけ：円A')
        helpers.add_named_attribute(circle.centerSketchPoint, '下部切かけ：中心A')
        helpers.add_named_attribute(line, '下部切かけ：接線BC')
        helpers.add_named_attribute(line.startSketchPoint, '下部切かけ：B')
        helpers.add_named_attribute(line.endSketchPoint, '下部切かけ：C')
        helpers.add_named_attribute(face, face_name)
        report['stage'] = 'sketch_created_no_cut'
        sketch.attributes.add(naming.ATTRIBUTE_GROUP, 'lower_notch_spec',
                              json.dumps(report, ensure_ascii=False))
        write_report(report)
        sketch.isLightBulbOn = True
        return sketch
    except Exception as error:
        report['error'] = str(error)
        if sketch is not None:
            sketch.deleteMe()
        path = write_report(report)
        raise RuntimeError('{}\n診断記録: {}'.format(error, path)) from error
