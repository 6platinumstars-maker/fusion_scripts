"""Extend the pin to the first negative-X contact with the grip and join."""
import math

CENTER_MM = (-76.795, -8.201, 10.492)
DIAMETER_MM = 4.0
END_X_MM = -71.795
NAME = 'グリップ追加円柱：直径4.0・−X側を本体まで延長'
OVERLAP_MM = 0.1


def extension_end(body,report):
    import adsk.core
    import adsk.fusion
    manager=adsk.fusion.TemporaryBRepManager.get()
    def cylinder(end):
        return manager.createCylinderOrCone(
            adsk.core.Point3D.create(END_X_MM/10,CENTER_MM[1]/10,CENTER_MM[2]/10),DIAMETER_MM/20,
            adsk.core.Point3D.create(end/10,CENTER_MM[1]/10,CENTER_MM[2]/10),DIAMETER_MM/20)
    limit=body.boundingBox.minPoint.x*10-1.0
    if limit>=CENTER_MM[0]:raise RuntimeError('円柱の−X側に本体がありません。')
    probe=cylinder(limit)
    if probe is None or not manager.booleanOperation(probe,body,adsk.fusion.BooleanTypes.IntersectionBooleanType):
        raise RuntimeError('円柱と本体の接触位置を計算できません。')
    if probe.faces.count==0 or not probe.isSolid or probe.volume<=1e-10:
        raise RuntimeError('直径4.0 mmの円柱を−Xに延ばしても本体に接しません。')
    contact=probe.boundingBox.maxPoint.x*10
    end=min(CENTER_MM[0],contact-OVERLAP_MM)
    overlap=cylinder(end)
    if overlap is None or not manager.booleanOperation(overlap,body,adsk.fusion.BooleanTypes.IntersectionBooleanType):
        raise RuntimeError('円柱と本体の結合部分を確認できません。')
    if overlap.faces.count==0 or overlap.volume<=1e-10:
        raise RuntimeError('円柱と本体に体積を持つ重なりがありません。')
    report['pin_contact']=dict(contact_x_mm=contact,end_x_mm=end,
        direction='-X',fixed_positive_end_x_mm=END_X_MM,
        overlap_distance_mm=OVERLAP_MM,overlap_volume_mm3=overlap.volume*1000)
    return end


def create(root, body, report):
    import adsk.core
    import adsk.fusion
    before = body.volume
    report['stage']='pin_contact_search'
    end_x = extension_end(body,report)
    report['stage'] = 'cylindrical_pin'
    report['cylindrical_pin'] = dict(center_mm=CENTER_MM, diameter_mm=DIAMETER_MM,
        start_x_mm=END_X_MM, end_x_mm=end_x,
        distance_mm=END_X_MM-end_x, before_volume_mm3=before*1000)
    planes = root.constructionPlanes
    inp = planes.createInput()
    if not inp.setByOffset(root.yZConstructionPlane,adsk.core.ValueInput.createByReal(END_X_MM/10)):
        raise RuntimeError('追加円柱のYZ基準面を作成できません。')
    plane = planes.add(inp)
    plane.name = NAME+'：基準平面'
    sketch = root.sketches.add(plane)
    sketch.name = NAME+'：円スケッチ'
    sketch_center = (END_X_MM,CENTER_MM[1],CENTER_MM[2])
    world = adsk.core.Point3D.create(*(x/10 for x in sketch_center))
    local = sketch.modelToSketchSpace(world)
    if abs(local.z)>1e-7:
        raise RuntimeError('指定円中心がYZスケッチ平面上にありません。')
    circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(local,DIAMETER_MM/20)
    actual = circle.centerSketchPoint.worldGeometry
    if math.dist(tuple(getattr(actual,a)*10 for a in 'xyz'),sketch_center)>1e-6:
        raise RuntimeError('追加円の中心位置が一致しません。')
    if sketch.profiles.count != 1:
        raise RuntimeError('追加円のプロファイルが１個ではありません。')
    # Check sketch normal in world coordinates, rather than assuming its sign.
    p0=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,0))
    p1=sketch.sketchToModelSpace(adsk.core.Point3D.create(0,0,1))
    normal=(p1.x-p0.x,p1.y-p0.y,p1.z-p0.z)
    if abs(normal[1])>1e-7 or abs(normal[2])>1e-7 or abs(abs(normal[0])-1)>1e-7:
        raise RuntimeError('円柱スケッチの法線がX軸に一致しません。')
    direction=(adsk.fusion.ExtentDirections.PositiveExtentDirection if normal[0]<0
               else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    extrudes=root.features.extrudeFeatures
    data=extrudes.createInput(sketch.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extent=adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal((END_X_MM-end_x)/10))
    if not data.setOneSideExtent(extent,direction):
        raise RuntimeError('追加円柱の押し出し範囲を設定できません。')
    feature=extrudes.add(data)
    if feature is None:raise RuntimeError('追加円柱を作成できません。')
    feature.name=NAME
    result=list(feature.bodies)
    if len(result)!=1 or not result[0].isSolid:
        raise RuntimeError('追加円柱が１個のソリッドではありません。')
    pin=result[0]
    expected=math.pi*(DIAMETER_MM/2)**2*(END_X_MM-end_x)
    volume=pin.volume*1000
    if not math.isfinite(volume) or abs(volume-expected)>max(1e-5,expected*1e-6):
        raise RuntimeError('追加円柱の体積が指定寸法に一致しません。')
    bounds=pin.boundingBox
    if abs(bounds.minPoint.x*10-end_x)>1e-5 or abs(bounds.maxPoint.x*10-END_X_MM)>1e-5:
        raise RuntimeError('追加円柱のX方向の始点・終点が一致しません。')
    if abs(body.volume-before)>1e-8 or root.bRepBodies.count!=2:
        raise RuntimeError('追加後のボディ構成または元グリップの体積が一致しません。')
    pin.name=NAME
    pin.isLightBulbOn=True
    pin.attributes.add('grip_solid','part','cylindrical_pin')
    report['cylindrical_pin']['volume_mm3']=volume
    tools=adsk.core.ObjectCollection.create()
    tools.add(pin)
    combine=root.features.combineFeatures
    join_input=combine.createInput(body,tools)
    join_input.operation=adsk.fusion.FeatureOperations.JoinFeatureOperation
    join_input.isKeepToolBodies=False
    joined=combine.add(join_input)
    if joined is not None:joined.name='グリップ加工：円柱と本体の結合'
    bodies=list(root.bRepBodies)
    if len(bodies)!=1 or not bodies[0].isSolid or bodies[0].lumps.count!=1:
        raise RuntimeError('円柱と本体が連続した１ソリッドになっていません。')
    final_volume=bodies[0].volume*1000
    expected_join=before*1000+volume-report['pin_contact']['overlap_volume_mm3']
    if not math.isfinite(final_volume) or final_volume<=before*1000 or abs(final_volume-expected_join)>max(0.001,expected_join*1e-6):
        raise RuntimeError('円柱結合後の体積が計算値に一致しません。')
    report['cylindrical_pin']['operation']='join'
    report['cylindrical_pin']['joined_volume_mm3']=final_volume
    sketch.isLightBulbOn=False
    plane.isLightBulbOn=False
    return bodies[0]
