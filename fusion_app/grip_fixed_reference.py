"""Copy Fx1 through Fx6 from the completed outer shell; preserve original trimmed faces."""
import hashlib
import json
import math
import os
from pathlib import Path
import uuid
import adsk.core
import adsk.fusion
from . import isolated_design

X_MM = -76.795
TOL_MM = 0.005
PHASE = 'completed_outer_shell_fx1_fx6_fx5_fx2_fx3_fx4'
FX4_HINTS_MM = ((-76.795, 5.303, 26.985),
                (-29.844, -27.133, 21.80),
                (-73.757, -7.201, 5.495))
FX4_RADIUS_MM = 34.9
FX3_HINTS_MM = ((-76.795, 32.233, 29.223),
                (-29.415, -24.646, 24.496),
                (-70.075, 21.518, 28.332))
FX2_Y_RANGE_MM = (32.20, 32.233)
FX5_X_RANGE_MM = (-29.854, -29.844)
FX5_MAX_TILT_DEG = 0.5
SPECS = {'Fx1': ('x', X_MM), 'Fx6': ('z', -6.0), 'Fx5': ('x', -29.854), 'Fx2': ('y', 32.20), 'Fx3': ('slope', 0.0), 'Fx4': ('cylinder', 34.9)}


def cache_root():
    return Path(__file__).resolve().parents[2] / '_grip_fixed_reference'


def face_matches(face, fixed_id='Fx1'):
    axis, coordinate = SPECS[fixed_id]
    if fixed_id == 'Fx4':
        cylinder = adsk.core.Cylinder.cast(face.geometry)
        if cylinder is None:
            return False
        ok, origin, direction, radius = cylinder.getData()
        if not ok or abs(radius*10-FX4_RADIUS_MM) > TOL_MM:
            return False
        length = math.sqrt(sum(getattr(direction, a)**2 for a in 'xyz'))
        if length == 0:
            return False
        unit = [getattr(direction, a)/length for a in 'xyz']
        for point in FX4_HINTS_MM:
            delta = [v-getattr(origin, a)*10 for a, v in zip('xyz', point)]
            along = sum(v*n for v, n in zip(delta, unit))
            radial = math.sqrt(sum((v-along*n)**2 for v, n in zip(delta, unit)))
            if abs(radial-radius*10) > TOL_MM:
                return False
        return math.isfinite(face.area) and face.area*100 > 1e-8
    plane = adsk.core.Plane.cast(face.geometry)
    if plane is None:
        return False
    if fixed_id == 'Fx3':
        # Match the actual plane against all three non-collinear rounded hints.
        # Copy its trimmed faces; never rebuild a plane through approximate points.
        n = plane.normal
        length = math.sqrt(n.x*n.x + n.y*n.y + n.z*n.z)
        if length == 0:
            return False
        distances = [abs(sum(getattr(n, axis)*(value-getattr(plane.origin, axis)*10)
                             for axis, value in zip('xyz', point)))/length
                     for point in FX3_HINTS_MM]
        return (max(distances) <= TOL_MM
                and math.isfinite(face.area) and face.area*100 > 1e-8)
    normal = plane.normal
    length = math.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
    off_axis = math.sqrt(sum(getattr(normal,a)**2 for a in 'xyz' if a != axis))
    if length == 0:
        return False
    if fixed_id == 'Fx2':
        if off_axis/length > 1e-7:
            return False
        bounds = face.boundingBox
        if (bounds.minPoint.y*10 < FX2_Y_RANGE_MM[0]-TOL_MM or
                bounds.maxPoint.y*10 > FX2_Y_RANGE_MM[1]+TOL_MM):
            return False
    elif fixed_id == 'Fx5':
        # A slightly tilted plane's geometry origin need not be on the trimmed face.
        # Require the entire trimmed face to lie within the requested X slab.
        if off_axis/length > math.sin(math.radians(FX5_MAX_TILT_DEG)):
            return False
        bounds = face.boundingBox
        if (bounds.minPoint.x*10 < FX5_X_RANGE_MM[0]-TOL_MM or
                bounds.maxPoint.x*10 > FX5_X_RANGE_MM[1]+TOL_MM):
            return False
    else:
        if off_axis/length > 1e-7:
            return False
        if abs(getattr(plane.origin,axis)*10-coordinate) > TOL_MM:
            return False
    return math.isfinite(face.area) and face.area*100 > 1e-8


def face_is_fx1(face):
    return face_matches(face, 'Fx1')


def select_faces(outer_results, fixed_id='Fx1'):
    faces = [face for body in outer_results.values() for face in body.faces
             if face_matches(face, fixed_id)]
    if not faces:
        axis, coordinate = SPECS[fixed_id]
        raise RuntimeError('完成外殻に{}（{}={} mmの面）が見つかりません。'.format(fixed_id,axis.upper(),coordinate))
    return sorted(faces, key=lambda f: (-f.area, f.pointOnFace.y, f.pointOnFace.z))


def validate_surface(body, expected_area=None, fixed_id='Fx1'):
    if body is None or body.isSolid or body.faces.count != 1:
        raise RuntimeError(fixed_id+'が単一面のサーフェスとして取得できません。')
    face = body.faces.item(0)
    if not face_matches(face, fixed_id):
        raise RuntimeError(fixed_id+'の位置・面の形状が指定と一致しません。')
    area = face.area*100
    if expected_area is not None and abs(area-expected_area) > max(1e-5, expected_area*1e-6):
        raise RuntimeError(fixed_id+'の面積が保存時と一致しません。')
    return area


def write_selection_diagnostics(outer_results, source_reference_revision):
    """Record selected AND rejected faces without changing geometry or selection."""
    def xyz(point, scale=10):
        return {axis: getattr(point, axis, None)*scale
                if getattr(point, axis, None) is not None else None for axis in 'xyz'}

    rows = []
    for name, body in outer_results.items():
        for index, face in enumerate(body.faces):
            row = dict(source_body=name, face_index=index)
            try:
                geometry = face.geometry
                plane = adsk.core.Plane.cast(geometry)
                bounds = face.boundingBox
                row.update(surface_type=getattr(geometry, 'objectType', type(geometry).__name__),
                           area_mm2=face.area*100, point_mm=xyz(face.pointOnFace),
                           min_mm=xyz(bounds.minPoint), max_mm=xyz(bounds.maxPoint),
                           planar=plane is not None, selected_fx5=face_matches(face, 'Fx5'),
                           vertices_mm=[xyz(v.geometry) for v in getattr(face, 'vertices', ())])
                if plane is not None:
                    row['normal'] = xyz(plane.normal, 1)
                    row['plane_origin_mm'] = xyz(plane.origin)
                    normal = plane.normal
                    row['x_normal_tilt_deg'] = math.degrees(math.atan2(
                        math.hypot(normal.y, normal.z), abs(normal.x)))
            except Exception as error:
                row['diagnostic_error'] = str(error)
            rows.append(row)
    payload = dict(source_reference_revision=source_reference_revision,
                   source_code_revision=isolated_design.code_revision(),
                   phase=PHASE, x_range_mm=list(FX5_X_RANGE_MM),
                   tolerance_mm=TOL_MM, max_tilt_deg=FX5_MAX_TILT_DEG, faces=rows)
    folder = cache_root()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/'fx5_selection_diagnostics.json'
    temp = folder/('diagnostics-'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(str(temp), str(path))


def publish(outer_results, source_reference_revision):
    try:
        write_selection_diagnostics(outer_results, source_reference_revision)
    except Exception as error:
        # Diagnostic I/O must not prevent an otherwise valid outer-shell build.
        print('Fx5診断記録を保存できませんでした: '+str(error))
    groups = {fixed_id: select_faces(outer_results, fixed_id) for fixed_id in SPECS}
    revision = uuid.uuid4().hex
    folder = cache_root()/revision
    folder.mkdir(parents=True, exist_ok=False)
    manager = adsk.fusion.TemporaryBRepManager.get()
    manifest = dict(schema=2, phase=PHASE, revision=revision,
                    source_reference_revision=source_reference_revision,
                    source_code_revision=isolated_design.code_revision(),
                    planes={key: list(spec) for key,spec in SPECS.items()}, tolerance_mm=TOL_MM,
                    fx5_x_range_mm=list(FX5_X_RANGE_MM), fx5_max_tilt_deg=FX5_MAX_TILT_DEG,
                    fx2_y_range_mm=list(FX2_Y_RANGE_MM),
                    fx3_hints_mm=[list(p) for p in FX3_HINTS_MM],
                    fx4_hints_mm=[list(p) for p in FX4_HINTS_MM],
                    fx4_radius_mm=FX4_RADIUS_MM, faces=[])
    for fixed_id, faces in groups.items():
        for i, face in enumerate(faces):
            body = manager.copy(face)
            area = validate_surface(body, face.area*100, fixed_id)
            filename = '{}_{}.smt'.format(fixed_id,i+1)
            path = folder/filename
            if not manager.exportToFile([body], str(path)):
                raise RuntimeError('固定面の保存に失敗しました。')
            # Verify the serialized copy before replacing the published reference.
            loaded = manager.createFromFile(str(path))
            if loaded is None or loaded.count != 1:
                raise RuntimeError('保存した固定面を検証できません。')
            validate_surface(loaded.item(0), area, fixed_id)
            manifest['faces'].append(dict(fixed_id=fixed_id, file=filename, area_mm2=area,
                name=fixed_id if len(faces)==1 else '{}：{}'.format(fixed_id,i+1),
                source_body=face.body.name, loop_count=face.loops.count,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            if fixed_id == 'Fx5':
                bounds = face.boundingBox
                manifest['faces'][-1]['x_bounds_mm'] = [bounds.minPoint.x*10, bounds.maxPoint.x*10]
            if loaded.item(0).faces.item(0).loops.count != face.loops.count:
                raise RuntimeError('固定面の内外周数がコピー元と一致しません。')
    payload = json.dumps(manifest, ensure_ascii=False, indent=2)
    (folder/'manifest.json').write_text(payload, encoding='utf-8')
    temp = cache_root()/('latest-'+revision+'.tmp')
    temp.write_text(payload, encoding='utf-8')
    os.replace(str(temp), str(cache_root()/'latest.json'))
    return manifest


def read_snapshot():
    path = cache_root()/'latest.json'
    if not path.exists():
        raise RuntimeError('Fx1・Fx6・Fx5・Fx2・Fx3・Fx4の参照データがありません。更新後の2を新しい空のデザインで実行し、完了後に別の空のデザインで3を実行してください。')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if (manifest.get('schema') != 2 or manifest.get('phase') != PHASE
            or manifest.get('planes') != {key: list(spec) for key,spec in SPECS.items()} or not manifest.get('faces')
            or manifest.get('fx5_x_range_mm') != list(FX5_X_RANGE_MM)
            or manifest.get('fx5_max_tilt_deg') != FX5_MAX_TILT_DEG
            or manifest.get('fx2_y_range_mm') != list(FX2_Y_RANGE_MM)
            or manifest.get('fx3_hints_mm') != [list(p) for p in FX3_HINTS_MM]
            or manifest.get('fx4_hints_mm') != [list(p) for p in FX4_HINTS_MM]
            or manifest.get('fx4_radius_mm') != FX4_RADIUS_MM):
        raise RuntimeError('Fx1・Fx6・Fx5・Fx2・Fx3・Fx4の参照形式が異なります。2を実行し直してください。')
    if {item.get('fixed_id') for item in manifest['faces']} != set(SPECS):
        raise RuntimeError('Fx1・Fx6・Fx5・Fx2・Fx3・Fx4すべての参照が必要です。更新後の2を実行してください。')
    revision = manifest['revision']
    if len(revision) != 32 or any(c not in '0123456789abcdef' for c in revision):
        raise RuntimeError('Fx1・Fx6・Fx5・Fx2・Fx3・Fx4の参照版が不正です。')
    manager = adsk.fusion.TemporaryBRepManager.get()
    bodies = []
    for item in manifest['faces']:
        if Path(item['file']).name != item['file']:
            raise RuntimeError('Fx1・Fx6・Fx5・Fx2・Fx3・Fx4の参照ファイル名が不正です。')
        source = cache_root()/revision/item['file']
        if hashlib.sha256(source.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError('Fx1・Fx6・Fx5・Fx2・Fx3・Fx4の参照データが保存時から変化しています。2を実行し直してください。')
        loaded = manager.createFromFile(str(source))
        if loaded is None or loaded.count != 1:
            raise RuntimeError('固定面を読み込めません。')
        body = loaded.item(0)
        validate_surface(body, item['area_mm2'], item.get('fixed_id', 'Fx1'))
        if body.faces.item(0).loops.count != item['loop_count']:
            raise RuntimeError('固定面の内外周数が保存時と一致しません。')
        bodies.append(body)
    return manifest, bodies


def install(design, manifest, bodies, validator=None, label=None, revision_key=None, attribute_group='grip_fixed_face'):
    validator = validator or validate_surface
    root = design.rootComponent
    base = None
    added_bodies = []
    if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
        base = root.features.baseFeatures.add()
        base.name = (label or 'グリップ固定面：Fx1・Fx6・Fx5・Fx2・Fx3・Fx4')+'：'+manifest['revision'][:8]
        if not base.startEdit():
            raise RuntimeError('固定面のベースフィーチャ編集を開始できません。')
    try:
        for body in bodies:
            added = root.bRepBodies.add(body, base) if base else root.bRepBodies.add(body)
            if added is None:
                raise RuntimeError('固定面をデザインへ追加できません。')
            added_bodies.append(added)
    finally:
        if base and not base.finishEdit():
            raise RuntimeError('固定面のベースフィーチャ編集を終了できません。')
    installed = [base.bodies.item(i) for i in range(base.bodies.count)] if base else added_bodies
    if len(installed) != len(manifest['faces']):
        raise RuntimeError('固定面の構成面数が一致しません。')
    from .grip_surface_names import display_name
    counts = {}
    seen = {}
    for item in manifest['faces']:
        identifier = item.get('fixed_id', 'Fx1')
        counts[identifier] = counts.get(identifier, 0) + 1
    for body, item in zip(installed, manifest['faces']):
        validator(body, item['area_mm2'], item.get('fixed_id', 'Fx1'))
        identifier = item.get('fixed_id', 'Fx1')
        seen[identifier] = seen.get(identifier, 0) + 1
        body.name = display_name(identifier, seen[identifier] if counts[identifier] > 1 else None)
        body.isLightBulbOn = True
        body.attributes.add(attribute_group, 'id', item.get('fixed_id', 'Fx1'))
        body.attributes.add(attribute_group, 'revision', manifest['revision'])
    design.attributes.add('fusion_scripts_build', revision_key or 'fixed_reference_revision', manifest['revision'])
    return installed
