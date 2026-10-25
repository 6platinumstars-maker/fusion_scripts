"""Minor circular sector cut from Z=-6.8 to -6.0 mm."""
import math
CENTER_MM=(-42.019,7.755,-6.8)
RADIUS_MM=35.565
HINTS_MM=((-26.365,-24.180,-6.8),(-76.988,14.136,-6.8))
END_Z_MM=-6.0
NAME='グリップ加工：半径35.565扇形・Z-6.8～-6.0切り取り'


def sector_data():
    ends=[]
    for hint in HINTS_MM:
        dx,dy=hint[0]-CENTER_MM[0],hint[1]-CENTER_MM[1]
        length=math.hypot(dx,dy)
        if length<1e-9:raise ValueError('扇形の端点が中心に一致しています。')
        ends.append((CENTER_MM[0]+RADIUS_MM*dx/length,CENTER_MM[1]+RADIUS_MM*dy/length,CENTER_MM[2]))
    a,b=[math.atan2(p[1]-CENTER_MM[1],p[0]-CENTER_MM[0]) for p in ends]
    sweep=(b-a+math.pi)%(2*math.pi)-math.pi
    if abs(sweep)<1e-8:raise ValueError('扇形の角度がありません。')
    return dict(center_mm=CENTER_MM,radius_mm=RADIUS_MM,ends_mm=ends,
                sweep_radians=sweep,area_mm2=RADIUS_MM**2*abs(sweep)/2)


def cut(root,body,report):
    import adsk.core
    import adsk.fusion
    geometry=sector_data()
    info=dict(geometry,start_z_mm=CENTER_MM[2],end_z_mm=END_Z_MM,before_volume_mm3=body.volume*1000)
    report['sector_cut']=info;report['stage']='sector_cut_sketch'
    inp=root.constructionPlanes.createInput()
    if not inp.setByOffset(root.xYConstructionPlane,adsk.core.ValueInput.createByString('-6.8 mm')):
        raise RuntimeError('扇形のZ=-6.8平面を作成できません。')
    plane=root.constructionPlanes.add(inp);plane.name=NAME+'：平面'
    sketch=root.sketches.add(plane);sketch.name=NAME+'：スケッチ'
    def local(p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(x/10 for x in p)))
    c=local(CENTER_MM);a,b=[local(p) for p in geometry['ends_mm']]
    if max(abs(p.z) for p in (c,a,b))>1e-7:raise RuntimeError('扇形の指定点がスケッチ平面上にありません。')
    theta1=math.atan2(a.y-c.y,a.x-c.x);theta2=math.atan2(b.y-c.y,b.x-c.x)
    sweep=(theta2-theta1+math.pi)%(2*math.pi)-math.pi
    arc=sketch.sketchCurves.sketchArcs.addByCenterStartSweep(c,a,sweep)
    if arc is None:raise RuntimeError('扇形の円弧を作成できません。')
    anchor=sketch.sketchPoints.add(c)
    sketch.sketchCurves.sketchLines.addByTwoPoints(anchor,arc.startSketchPoint)
    sketch.sketchCurves.sketchLines.addByTwoPoints(arc.endSketchPoint,anchor)
    if sketch.profiles.count!=1:raise RuntimeError('扇形が１つの閉じた領域になりません。')
    profile=sketch.profiles.item(0)
    area=profile.areaProperties().area*100
    if abs(area-geometry['area_mm2'])>max(1e-4,geometry['area_mm2']*1e-6):
        raise RuntimeError('扇形の面積が短い円弧の計算値に一致しません。')
    p0=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
    p1=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
    nz=p1.z-p0.z
    if abs(abs(nz)-1)>1e-7:raise RuntimeError('扇形の押し出し軸がZ方向に一致しません。')
    extent=adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('0.8 mm'))
    direction=adsk.fusion.ExtentDirections.PositiveExtentDirection if nz>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
    extrudes=root.features.extrudeFeatures
    data=extrudes.createInput(profile,adsk.fusion.FeatureOperations.CutFeatureOperation)
    if not data.setOneSideExtent(extent,direction):raise RuntimeError('扇形の押し出し距離を設定できません。')
    data.participantBodies=[body]
    report['stage']='sector_cut_extrude'
    feature=extrudes.add(data)
    if feature is None:raise RuntimeError('扇形の押し出し切り取りに失敗しました。')
    feature.name=NAME
    bodies=list(root.bRepBodies)
    if len(bodies)!=1 or not bodies[0].isSolid or bodies[0].lumps.count!=1:
        raise RuntimeError('扇形切り取り後が連続した１ソリッドではありません。')
    volume=bodies[0].volume*1000
    if not math.isfinite(volume) or not 0<volume<info['before_volume_mm3']-1e-6:
        raise RuntimeError('扇形切り取り後の体積減少を確認できません。')
    info['after_volume_mm3']=volume
    sketch.isLightBulbOn=False;plane.isLightBulbOn=False
    return bodies[0]
