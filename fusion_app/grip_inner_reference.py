"""Immutable Ref1--Ref3 copies from the FINISHED inner shell, separate from outer inputs."""
import hashlib
import json
import math
import os
from pathlib import Path
import uuid
import adsk.core
import adsk.fusion
from . import isolated_design

TOL_MM = 0.005
HINTS_MM = ((-29.842,-25.679,20.362),(-75.0,5.052,22.698),(-66.67,26.918,-3.0))
CENTER_MM = (-76.795,-7.201,10.492)
INCLUDE_R1 = False
LEGACY_IDS = {'Fx8':'Ref1', 'Fx9':'Ref2', 'Fx10':'Ref3'}
IDS = ('Ref1','Ref2','Ref3')


def cache_root():
    return Path(__file__).resolve().parents[2]/'_grip_inner_fixed_reference'


def xyz(point):
    return tuple(getattr(point,a)*10 for a in 'xyz')


def unit(vector):
    values = tuple(getattr(vector,a) for a in 'xyz')
    length = math.sqrt(sum(v*v for v in values))
    return tuple(v/length for v in values) if length else (0,0,0)


def cylinder_distance(point, origin, axis):
    delta = tuple(p-o for p,o in zip(point,origin))
    along = sum(v*n for v,n in zip(delta,axis))
    return math.sqrt(sum((v-along*n)**2 for v,n in zip(delta,axis)))


def face_matches(face, fixed_id):
    if not math.isfinite(face.area) or face.area*100 <= 1e-8:
        return False
    cylinder = adsk.core.Cylinder.cast(face.geometry)
    if fixed_id in ('Ref1','Ref2') and cylinder is not None:
        ok, origin, axis, radius = cylinder.getData()
        if not ok: return False
        origin, axis, radius = xyz(origin), unit(axis), radius*10
        if axis == (0,0,0): return False
        if fixed_id == 'Ref1':
            return all(abs(cylinder_distance(p,origin,axis)-radius)<=TOL_MM for p in HINTS_MM)
        return (abs(abs(axis[0])-1)<1e-7 and abs(radius-4.6)<=TOL_MM
                and cylinder_distance(CENTER_MM,origin,axis)<=TOL_MM)
    if fixed_id == 'Ref3':
        plane = adsk.core.Plane.cast(face.geometry)
        if plane is None: return False
        bounds = face.boundingBox
        return (abs(abs(unit(plane.normal)[0])-1)<1e-7
                and abs(plane.origin.x*10-CENTER_MM[0])<=TOL_MM
                and all(getattr(bounds.minPoint,a)*10 >= CENTER_MM[i]-3.6-TOL_MM
                        and getattr(bounds.maxPoint,a)*10 <= CENTER_MM[i]+3.6+TOL_MM
                        for i,a in ((1,'y'),(2,'z')))
                and face.loops.count==2)
    return False


def validate_surface(body, expected_area=None, fixed_id='Ref1'):
    if body is None or body.isSolid or body.faces.count!=1:
        raise RuntimeError(fixed_id+'が単一のサーフェスではありません。')
    face=body.faces.item(0)
    if not face_matches(face,fixed_id):
        raise RuntimeError(fixed_id+'の形状が指定と一致しません。')
    area=face.area*100
    if expected_area is not None and abs(area-expected_area)>max(1e-5,expected_area*1e-6):
        raise RuntimeError(fixed_id+'の面積が保存時と一致しません。')
    return area


def publish(body):
    groups={key:[face for face in body.faces if face_matches(face,key)] for key in IDS}
    missing=[key for key,faces in groups.items() if not faces]
    if missing:
        rows=[]
        for face in body.faces:
            row=dict(surface_type=getattr(face.geometry,'objectType','unknown'),area_mm2=face.area*100)
            cylinder=adsk.core.Cylinder.cast(face.geometry)
            if cylinder is not None:
                ok,origin,axis,radius=cylinder.getData()
                if ok:
                    row.update(origin_mm=xyz(origin),axis=unit(axis),radius_mm=radius*10,
                        ref1_distances_mm=[abs(cylinder_distance(p,xyz(origin),unit(axis))-radius*10) for p in HINTS_MM])
            rows.append(row)
        cache_root().mkdir(parents=True,exist_ok=True)
        report=cache_root()/'selection_diagnostics.json'
        report.write_text(json.dumps(dict(missing=missing,faces=rows),ensure_ascii=False,indent=2),encoding='utf-8')
        raise RuntimeError('完成内殻から参考面を取得できません：'+', '.join(missing)+'\n診断記録: '+str(report))
    revision=uuid.uuid4().hex
    folder=cache_root()/revision
    folder.mkdir(parents=True,exist_ok=False)
    manager=adsk.fusion.TemporaryBRepManager.get()
    manifest=dict(schema=1,phase='finished_inner_shell',revision=revision,
                  source_code_revision=isolated_design.code_revision(),include_r1=INCLUDE_R1,surface_role='reference',faces=[])
    for key,faces in groups.items():
        for index,face in enumerate(sorted(faces,key=lambda f:-f.area)):
            copy=manager.copy(face)
            area=validate_surface(copy,face.area*100,key)
            filename='{}_{}.smt'.format(key,index+1);path=folder/filename
            if not manager.exportToFile([copy],str(path)):
                raise RuntimeError(key+'を保存できません。')
            loaded=manager.createFromFile(str(path))
            if loaded is None or loaded.count!=1: raise RuntimeError(key+'の保存を検証できません。')
            validate_surface(loaded.item(0),area,key)
            if loaded.item(0).faces.item(0).loops.count!=face.loops.count:
                raise RuntimeError(key+'の内外周が一致しません。')
            manifest['faces'].append(dict(fixed_id=key,file=filename,area_mm2=area,
                loop_count=face.loops.count,name=key if len(faces)==1 else '{}：{}'.format(key,index+1),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    payload=json.dumps(manifest,ensure_ascii=False,indent=2)
    (folder/'manifest.json').write_text(payload,encoding='utf-8')
    temp=cache_root()/('latest-'+revision+'.tmp');temp.write_text(payload,encoding='utf-8')
    os.replace(str(temp),str(cache_root()/'latest.json'))
    return manifest


def read_snapshot():
    path=cache_root()/'latest.json'
    if not path.exists():raise RuntimeError('内殻参考面Ref1〜Ref3がありません。更新後の1を空のデザインで実行してから3を実行してください。')
    manifest=json.loads(path.read_text(encoding='utf-8'))
    # Migrate labels in memory; geometry files and their hashes stay unchanged.
    for item in manifest.get('faces', []):
        old = item.get('fixed_id')
        if old in LEGACY_IDS:
            new = LEGACY_IDS[old]
            item['fixed_id'] = new
            item['name'] = new + item.get('name', old)[len(old):]
    manifest['surface_role'] = 'reference'
    if (manifest.get('schema')!=1 or manifest.get('phase')!='finished_inner_shell'
            or manifest.get('include_r1')!=INCLUDE_R1
            or {f.get('fixed_id') for f in manifest.get('faces',[])}!=set(IDS)):
        raise RuntimeError('内殻参考面の形式が異なります。更新後の1を実行してください。')
    revision=manifest['revision']
    if len(revision)!=32 or any(c not in '0123456789abcdef' for c in revision):
        raise RuntimeError('内殻参考面の参照版が不正です。')
    manager=adsk.fusion.TemporaryBRepManager.get();bodies=[]
    for item in manifest['faces']:
        if Path(item['file']).name!=item['file']:raise RuntimeError('参照ファイル名が不正です。')
        path=cache_root()/revision/item['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise RuntimeError('内殻参考面の参照が変化しています。1を実行し直してください。')
        loaded=manager.createFromFile(str(path))
        if loaded is None or loaded.count!=1:raise RuntimeError('内殻参考面を読み込めません。')
        body=loaded.item(0);validate_surface(body,item['area_mm2'],item['fixed_id'])
        if body.faces.item(0).loops.count!=item['loop_count']:raise RuntimeError('内殻参考面の内外周が一致しません。')
        bodies.append(body)
    return manifest,bodies


def install(design,manifest,bodies):
    from . import grip_fixed_reference
    return grip_fixed_reference.install(design,manifest,bodies,validator=validate_surface,
        label='グリップ内殻参考面：Ref1・Ref2・Ref3',revision_key='inner_reference_revision',attribute_group='grip_reference_face')
