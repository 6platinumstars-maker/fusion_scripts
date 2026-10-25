"""Extrude the existing Z=-6 planar face to Z=-6.8, cutting the grip."""
import math

START_Z_MM = -6.0
END_Z_MM = -6.8
NAME = 'グリップ加工：Z-6面切り取り：Z-6.8まで'


def matches_plane(origin_z_cm, normal):
    return (abs(origin_z_cm*10-START_Z_MM)<1e-5 and
            abs(normal.x)<1e-7 and abs(normal.y)<1e-7 and abs(abs(normal.z)-1)<1e-7)


def cut(root,body,report):
    import adsk.core
    import adsk.fusion
    report['stage']='z6_face_cut'
    candidates=[]
    for face in body.faces:
        plane=adsk.core.Plane.cast(face.geometry)
        if plane and matches_plane(plane.origin.z,plane.normal):
            candidates.append(face)
    info=dict(start_z_mm=START_Z_MM,end_z_mm=END_Z_MM,distance_mm=0.8,
              candidate_count=len(candidates),before_volume_mm3=body.volume*1000)
    report['z6_face_cut']=info
    if len(candidates)!=1:
        raise RuntimeError('Z=-6 mmの平面が{}面見つかりました。対象を一意に特定できません。'.format(len(candidates)))
    face=candidates[0]
    info['source_area_mm2']=face.area*100
    before=body.volume
    ok,normal=face.evaluator.getNormalAtPoint(face.pointOnFace)
    if not ok or abs(abs(normal.z)-1)>1e-7:
        raise RuntimeError('Z=-6面の法線を取得できません。')
    info['source_normal_z']=normal.z
    extrudes=root.features.extrudeFeatures
    data=extrudes.createInput(face,adsk.fusion.FeatureOperations.CutFeatureOperation)
    extent=adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('0.8 mm'))
    direction=(adsk.fusion.ExtentDirections.NegativeExtentDirection if normal.z>0
               else adsk.fusion.ExtentDirections.PositiveExtentDirection)
    if not data.setOneSideExtent(extent,direction):
        raise RuntimeError('Z=-6面の切り取り範囲を設定できません。')
    data.participantBodies=[body]
    feature=extrudes.add(data)
    if feature is None:raise RuntimeError('Z=-6面の押し出し切り取りに失敗しました。')
    feature.name=NAME
    bodies=list(root.bRepBodies)
    if len(bodies)!=1 or not bodies[0].isSolid:
        raise RuntimeError('Z=-6面の切り取り後が１個のソリッドではありません。')
    after=bodies[0].volume
    if not math.isfinite(after) or not 0<after<before-1e-9:
        raise RuntimeError('Z=-6面の切り取りで体積が減少していません。')
    ends=list(feature.endFaces)
    end_z=[]
    for end in ends:
        plane=adsk.core.Plane.cast(end.geometry)
        if plane:end_z.append(plane.origin.z*10)
    info['end_face_z_mm']=end_z
    if not end_z or any(abs(z-END_Z_MM)>1e-5 for z in end_z):
        raise RuntimeError('切り取り終端がZ=-6.8 mmに一致しません。出力先の加工を確認してください。')
    info['after_volume_mm3']=after*1000
    return bodies[0]
