"""Unite Fx6/Fx23 and subtract the requested planar five-corner region."""
import json
import math

NAME='固定面：Fx6：統合・指定5頂点切り取り面'
FIXED_START=((-29.854,29.638,-6.),(-29.854,-24.826,-6.))
FIXED_END=(-51.8,28.,-6.)


def cut_corners(dh5,ch5):
    points=[*FIXED_START,tuple(dh5),tuple(ch5),FIXED_END]
    if any(not math.isfinite(x) for p in points for x in p):raise ValueError('Fx6切取点が不正です。')
    if any(abs(p[2]+6)>1e-5 for p in points):raise ValueError('Fx6切取点がZ=-6平面外です。')
    if any(math.dist(a,b)<1e-6 for i,a in enumerate(points) for b in points[i+1:]):
        raise ValueError('Fx6切取点が重複しています。')
    area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2
    if area<1e-8:raise ValueError('Fx6切取領域の面積がありません。')
    def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    edges=list(zip(points,points[1:]+points[:1]))
    for i,(a,b) in enumerate(edges):
        for j,(c,d) in enumerate(edges):
            if j<=i or j==i+1 or (i==0 and j==len(edges)-1):continue
            if orient(a,b,c)*orient(a,b,d)<0 and orient(c,d,a)*orient(c,d,b)<0:
                raise ValueError('Fx6切取領域が自己交差しています。')
    return points,area


def reference_point(root,identifier):
    found=[]
    for sketch in root.sketches:
        tag=sketch.attributes.itemByName('grip_reference_point','id')
        if not tag or tag.value!=identifier:continue
        for point in sketch.sketchPoints:
            tag=point.attributes.itemByName('grip_reference_point','id')
            if tag and tag.value==identifier:
                found.append(tuple(getattr(point.worldGeometry,a)*10 for a in 'xyz'))
    if len(found)!=1:raise RuntimeError('Fx6切取用の'+identifier+'を一意に取得できません。')
    return found[0]


def create(root,revision):
    import adsk.core
    import adsk.fusion
    sources={}
    for body in root.bRepBodies:
        tag=body.attributes.itemByName('grip_fixed_face','id')
        if tag and tag.value in ('Fx6','Fx23'):sources.setdefault(tag.value,[]).append(body)
    if any(len(sources.get(key,[]))!=1 for key in ('Fx6','Fx23')):
        raise RuntimeError('統合元のFx6・Fx23を一意に取得できません。')
    fx6,fx23=sources['Fx6'][0],sources['Fx23'][0]
    corners,area=cut_corners(reference_point(root,'Ref14'),reference_point(root,'Ref15'))
    manager=adsk.fusion.TemporaryBRepManager.get()
    result=manager.copy(fx6);addition=manager.copy(fx23)
    if result is None or addition is None:raise RuntimeError('Fx6統合用のコピーを作成できません。')
    if not manager.booleanOperation(result,addition,adsk.fusion.BooleanTypes.UnionBooleanType):
        raise RuntimeError('Fx6とFx23の統合に失敗しました。')
    united_area=result.area*100
    if not math.isfinite(united_area) or not max(fx6.area,fx23.area)*100-1e-4<=united_area<=(fx6.area+fx23.area)*100+1e-4:
        raise RuntimeError('Fx6統合後の面積が不正です。')
    def point(p):return adsk.core.Point3D.create(*(x/10 for x in p))
    curves=[adsk.core.Line3D.create(point(a),point(b)) for a,b in zip(corners,corners[1:]+corners[:1])]
    wire,_=manager.createWireFromCurves(curves)
    if wire is None:raise RuntimeError('Fx6切取輪郭を作成できません。')
    cutter=manager.createFaceFromPlanarWires([wire])
    if cutter is None or abs(cutter.area*100-area)>1e-4:
        raise RuntimeError('Fx6切取用の５角形面を作成できません。')
    if not manager.booleanOperation(result,cutter,adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError('Fx6の指定領域の切り取りに失敗しました。')
    after=result.area*100
    if result.isSolid or not math.isfinite(after) or not 1e-8<after<united_area-1e-5:
        raise RuntimeError('Fx6の面積が切り取りで減少していません。')
    if united_area-after>area+1e-4:raise RuntimeError('Fx6の切取面積が指定領域を超えています。')
    if result.lumps.count!=1:raise RuntimeError('切り取り後のFx6が複数の離れた領域になりました。')
    base=root.features.baseFeatures.add();base.name=NAME
    if not base.startEdit():raise RuntimeError('Fx6の編集を開始できません。')
    try:
        if root.bRepBodies.add(result,base) is None:raise RuntimeError('Fx6の生成に失敗しました。')
    finally:
        if not base.finishEdit():raise RuntimeError('Fx6の編集を終了できません。')
    if base.bodies.count!=1:raise RuntimeError('Fx6が１つのボディになりませんでした。')
    body=base.bodies.item(0);body.name=NAME;body.isLightBulbOn=True
    body.attributes.add('grip_fixed_face','id','Fx6')
    body.attributes.add('grip_fixed_face','revision',revision)
    body.attributes.add('grip_fixed_face','cut_data_mm',json.dumps(dict(corners=corners,
        union_area_mm2=united_area,result_area_mm2=after,removed_area_mm2=united_area-after)))
    for source in (fx6,fx23):
        if root.features.removeFeatures.add(source) is None:raise RuntimeError('統合前Fx6・Fx23の除去に失敗しました。')
    return body
