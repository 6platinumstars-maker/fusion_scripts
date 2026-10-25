"""YZ circular cut, from X=-76.795 to X=-60 mm."""
import math

CENTER_MM = (-76.795, -8.201, 10.492)
DIAMETER_MM = 10.8
END_X_MM = -60.0
NAME = 'グリップ加工：円筒切り取り：直径10.8・X-76.795～-60'


def cut(root, body, report):
    import adsk.core
    import adsk.fusion
    before = body.volume
    report['stage'] = 'yz_circular_cut'
    report['yz_circular_cut'] = dict(center_mm=CENTER_MM, diameter_mm=DIAMETER_MM,
        start_x_mm=CENTER_MM[0], end_x_mm=END_X_MM,
        distance_mm=END_X_MM-CENTER_MM[0], before_volume_mm3=before*1000)
    planes = root.constructionPlanes
    inp = planes.createInput()
    if not inp.setByOffset(root.yZConstructionPlane,adsk.core.ValueInput.createByString('-76.795 mm')):
        raise RuntimeError('円筒切り取りのYZ基準面を作成できません。')
    plane = planes.add(inp)
    plane.name = NAME+'：基準平面'
    sketch = root.sketches.add(plane)
    sketch.name = NAME+'：円スケッチ'
    world = adsk.core.Point3D.create(*(x/10 for x in CENTER_MM))
    local = sketch.modelToSketchSpace(world)
    if abs(local.z)>1e-7:
        raise RuntimeError('指定円中心がYZスケッチ平面上にありません。')
    circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(local,DIAMETER_MM/20)
    actual = circle.centerSketchPoint.worldGeometry
    if math.dist(tuple(getattr(actual,a)*10 for a in 'xyz'),CENTER_MM)>1e-6:
        raise RuntimeError('切り取り円の中心位置が一致しません。')
    if sketch.profiles.count != 1:
        raise RuntimeError('切り取り円のプロファイルが１個ではありません。')
    # Check sketch normal in world coordinates, rather than assuming its sign.
    p0=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
    p1=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
    normal=(p1.x-p0.x,p1.y-p0.y,p1.z-p0.z)
    if abs(normal[1])>1e-7 or abs(normal[2])>1e-7 or abs(abs(normal[0])-1)>1e-7:
        raise RuntimeError('切り取りスケッチの法線がX軸に一致しません。')
    direction=(adsk.fusion.ExtentDirections.PositiveExtentDirection if normal[0]>0
               else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    extrudes=root.features.extrudeFeatures
    data=extrudes.createInput(sketch.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
    extent=adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal((END_X_MM-CENTER_MM[0])/10))
    if not data.setOneSideExtent(extent,direction):
        raise RuntimeError('円筒切り取りの押し出し範囲を設定できません。')
    data.participantBodies=[body]
    feature=extrudes.add(data)
    if feature is None:raise RuntimeError('円筒切り取りを作成できません。')
    feature.name=NAME
    result=list(root.bRepBodies)
    if len(result)!=1 or not result[0].isSolid:
        raise RuntimeError('円筒切り取り後が１個のソリッドではありません。出力先の形状を確認してください。')
    after=result[0].volume
    if not math.isfinite(after) or not 0<after<before-1e-9:
        raise RuntimeError('円筒切り取り後の体積減少を確認できません。')
    report['yz_circular_cut']['after_volume_mm3']=after*1000
    sketch.isLightBulbOn=False
    plane.isLightBulbOn=False
    return result[0]
