"""Remove the rectangular remnant before the minor-sector cut."""
import math
POINTS_MM=((-76.795,18.768,-6.0),(-77.595,18.768,-6.0),
           (-77.595,8.044,-6.0),(-76.795,8.044,-6.0))
NAME='グリップ加工：長方形残部・Z-6.0～-6.8切り取り'


def cut(root,body,report):
    import adsk.core
    import adsk.fusion
    before=body.volume*1000
    info=dict(points_mm=POINTS_MM,start_z_mm=-6.0,end_z_mm=-6.8,before_volume_mm3=before)
    report['rectangle_cleanup']=info;report['stage']='rectangle_cleanup'
    inp=root.constructionPlanes.createInput()
    if not inp.setByOffset(root.xYConstructionPlane,adsk.core.ValueInput.createByString('-6 mm')):
        raise RuntimeError('長方形切り取りの基準平面を作成できません。')
    plane=root.constructionPlanes.add(inp);plane.name=NAME+'：平面'
    sketch=root.sketches.add(plane);sketch.name=NAME+'：スケッチ'
    points=[]
    for xyz in POINTS_MM:
        p=sketch.modelToSketchSpace(adsk.core.Point3D.create(*(x/10 for x in xyz)))
        if abs(p.z)>1e-7:raise RuntimeError('長方形の頂点が基準平面に一致しません。')
        points.append(sketch.sketchPoints.add(p))
    for i,p in enumerate(points):
        sketch.sketchCurves.sketchLines.addByTwoPoints(p,points[(i+1)%4])
    if sketch.profiles.count!=1:raise RuntimeError('長方形が１つの閉じた領域になりません。')
    profile=sketch.profiles.item(0)
    area=profile.areaProperties().area*100
    if abs(area-0.8*10.724)>1e-5:raise RuntimeError('長方形の面積が指定座標に一致しません。')
    p0=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
    p1=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
    nz=p1.z-p0.z
    if abs(abs(nz)-1)>1e-7:raise RuntimeError('長方形の押し出し軸がZ方向に一致しません。')
    direction=adsk.fusion.ExtentDirections.NegativeExtentDirection if nz>0 else adsk.fusion.ExtentDirections.PositiveExtentDirection
    extrudes=root.features.extrudeFeatures
    data=extrudes.createInput(profile,adsk.fusion.FeatureOperations.CutFeatureOperation)
    extent=adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('0.8 mm'))
    if not data.setOneSideExtent(extent,direction):raise RuntimeError('長方形の押し出し範囲を設定できません。')
    data.participantBodies=[body]
    feature=extrudes.add(data)
    if feature is None:raise RuntimeError('長方形残部の切り取りに失敗しました。')
    feature.name=NAME
    bodies=list(root.bRepBodies)
    if len(bodies)!=1 or not bodies[0].isSolid or bodies[0].lumps.count!=1:
        raise RuntimeError('長方形切り取り後が連続した１ソリッドではありません。')
    after=bodies[0].volume*1000
    if not math.isfinite(after) or not 0<after<before-1e-6:
        raise RuntimeError('長方形切り取り後の体積減少を確認できません。')
    if before-after>area*0.8+1e-3:
        raise RuntimeError('長方形切り取り量が指定した工具体積を超えています。')
    info['after_volume_mm3']=after
    sketch.isLightBulbOn=False;plane.isLightBulbOn=False
    return bodies[0]
