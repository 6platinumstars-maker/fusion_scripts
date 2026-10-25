"""Apply exact R2 to the free circular end of the joined 4 mm pin."""
import math
from . import grip_solid_pin as pin
RADIUS_MM = 2.0


def apply(root,body,report):
    import adsk.core
    report['stage']='pin_end_fillet'
    center=(pin.END_X_MM,pin.CENTER_MM[1],pin.CENTER_MM[2])
    edges=[]
    for edge in body.edges:
        circle=adsk.core.Circle3D.cast(edge.geometry)
        if circle is None:continue
        xyz=tuple(getattr(circle.center,a)*10 for a in 'xyz')
        if math.dist(xyz,center)<1e-5 and abs(circle.radius*10-pin.DIAMETER_MM/2)<1e-5:
            if abs(abs(circle.normal.x)-1)<1e-7:
                edges.append(edge)
    data=dict(radius_mm=RADIUS_MM,center_mm=center,edge_count=len(edges),before_volume_mm3=body.volume*1000)
    report['pin_end_fillet']=data
    if len(edges)!=1:
        raise RuntimeError('円柱自由端X=-71.795 mmの円周を一意に取得できません。候補：{}'.format(len(edges)))
    if abs(edges[0].length*10-math.pi*pin.DIAMETER_MM)>1e-4:
        raise RuntimeError('円柱自由端の円周が完全な円ではありません。')
    entities=adsk.core.ObjectCollection.create()
    entities.add(edges[0])
    fillets=root.features.filletFeatures
    inp=fillets.createInput()
    inp.edgeSetInputs.addConstantRadiusEdgeSet(entities,adsk.core.ValueInput.createByString('2 mm'),False)
    try:
        feature=fillets.add(inp)
    except Exception as error:
        raise RuntimeError('円柱自由端のR2.0 mmフィレットを作成できませんでした。半径は変更していません。'+str(error)) from error
    if feature is None:raise RuntimeError('円柱自由端のR2フィレットが作成されませんでした。')
    feature.name='グリップ加工：円柱自由端R2.0'
    bodies=list(root.bRepBodies)
    if len(bodies)!=1 or not bodies[0].isSolid or bodies[0].lumps.count!=1:
        raise RuntimeError('R2フィレット後が連続した１ソリッドではありません。')
    after=bodies[0].volume*1000
    if not math.isfinite(after) or not 0<after<data['before_volume_mm3']-1e-6:
        raise RuntimeError('R2フィレット後の体積減少を確認できません。')
    data['after_volume_mm3']=after
    return bodies[0]
