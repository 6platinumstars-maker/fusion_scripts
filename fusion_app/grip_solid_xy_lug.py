"""Six-point XY extrusion joined to grip, with R2 on the vertical A edge."""
import math
POINTS_MM=((-28.982,-28.801,0.),(-31.982,-28.796,0.),
           (-31.987,-31.793,0.),(-29.852,-31.797,0.),
           (-29.850,-30.800,0.),(-28.985,-30.801,0.))
START_Z_MM=-3.546
END_Z_MM=21.480
RADIUS_MM=2.0


def is_a_edge(start,end):
    a=POINTS_MM[0]
    return (all(math.hypot(p[0]-a[0],p[1]-a[1])<1e-5 for p in (start,end))
            and abs(min(start[2],end[2])-START_Z_MM)<1e-5
            and abs(max(start[2],end[2])-END_Z_MM)<1e-5)


def single_solid(root):
    bodies=list(root.bRepBodies)
    if len(bodies)!=1 or not bodies[0].isSolid or bodies[0].lumps.count!=1:
        raise RuntimeError('六点輪郭の加工結果が連続した１ソリッドではありません。')
    return bodies[0]


def create(root,body,report):
    import adsk.core
    import adsk.fusion
    report['stage']='xy_lug_extrude'
    info=dict(points_mm=POINTS_MM,start_z_mm=START_Z_MM,end_z_mm=END_Z_MM,radius_mm=RADIUS_MM)
    report['xy_lug']=info
    before=body.volume
    sketch=root.sketches.add(root.xYConstructionPlane)
    sketch.name='グリップ加工：六点輪郭A～F（XY・Z0）'
    points=[sketch.sketchPoints.add(sketch.modelToSketchSpace(
        adsk.core.Point3D.create(*(x/10 for x in p)))) for p in POINTS_MM]
    for i,p in enumerate(points):
        sketch.sketchCurves.sketchLines.addByTwoPoints(p,points[(i+1)%len(points)])
    if sketch.profiles.count!=1:raise RuntimeError('六点輪郭が１つの閉じた領域になりません。')
    extrudes=root.features.extrudeFeatures
    data=extrudes.createInput(sketch.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    positive=adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('21.480 mm'))
    negative=adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('3.546 mm'))
    if not data.setTwoSidesExtent(positive,negative):raise RuntimeError('六点輪郭の押し出し範囲を設定できません。')
    feature=extrudes.add(data)
    if feature is None or feature.bodies.count!=1:raise RuntimeError('六点輪郭の押し出しに失敗しました。')
    feature.name='グリップ加工：六点輪郭Z-3.546～21.480'
    lug=feature.bodies.item(0)
    bounds=lug.boundingBox
    if abs(bounds.minPoint.z*10-START_Z_MM)>1e-5 or abs(bounds.maxPoint.z*10-END_Z_MM)>1e-5:
        raise RuntimeError('六点輪郭の押し出し始点・終点が一致しません。')
    info['addition_volume_mm3']=lug.volume*1000
    tools=adsk.core.ObjectCollection.create();tools.add(lug)
    combines=root.features.combineFeatures
    join=combines.createInput(body,tools)
    join.operation=adsk.fusion.FeatureOperations.JoinFeatureOperation
    join.isKeepToolBodies=False
    report['stage']='xy_lug_join'
    result=combines.add(join)
    if result is not None:result.name='グリップ加工：六点押し出し結合'
    joined=single_solid(root)
    joined_volume=joined.volume
    if not math.isfinite(joined_volume) or joined_volume<=before:
        raise RuntimeError('六点押し出し結合後の体積増加を確認できません。')
    info['before_volume_mm3']=before*1000
    info['joined_volume_mm3']=joined_volume*1000
    report['stage']='xy_lug_a_fillet'
    candidates=[]
    def xyz(point):return tuple(getattr(point,a)*10 for a in 'xyz')
    for edge in joined.edges:
        if adsk.core.Line3D.cast(edge.geometry) is None:continue
        if edge.startVertex and edge.endVertex and is_a_edge(xyz(edge.startVertex.geometry),xyz(edge.endVertex.geometry)):
            candidates.append(edge)
    info['a_edge_count']=len(candidates)
    if len(candidates)!=1:
        raise RuntimeError('点Aを通るZ方向の辺を一意に取得できません。候補：{}'.format(len(candidates)))
    entities=adsk.core.ObjectCollection.create();entities.add(candidates[0])
    fillets=root.features.filletFeatures
    fillet_input=fillets.createInput()
    fillet_input.edgeSetInputs.addConstantRadiusEdgeSet(entities,adsk.core.ValueInput.createByString('2 mm'),False)
    try:
        fillet=fillets.add(fillet_input)
    except Exception as error:
        raise RuntimeError('点AのZ方向辺にR2 mmを作成できません。半径や輪郭は変更していません。'+str(error)) from error
    if fillet is None:raise RuntimeError('点AのR2フィレットを作成できません。')
    fillet.name='グリップ加工：点AのZ方向辺R2'
    final=single_solid(root)
    after=final.volume
    if not math.isfinite(after) or not 0<after<joined_volume:
        raise RuntimeError('点AのR2加工後の体積減少を確認できません。')
    info['after_volume_mm3']=after*1000
    sketch.isLightBulbOn=False
    return final
