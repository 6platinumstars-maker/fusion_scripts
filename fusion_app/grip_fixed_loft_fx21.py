"""Fx21: current Ref7 endpoint-to-major-tip arc lofted to hexagon DE."""
import json
import math
from . import grip_reference_ellipse as ellipse

END_MM=(-29.854,-35.,-6.)
SPLIT_HINT_MM=(-93.19139979761287,-46.57812082776331,6.270520878966186)


def section(data):
    split=ellipse.point_at(data,0)
    if math.dist(split,SPLIT_HINT_MM)>.005 or math.dist(data['points'][2],END_MM)>1e-5:
        raise ValueError('Fx21のRef7端点または分割点が指定近似値と一致しません。')
    offset=(-data['start'])%math.tau
    if not 1e-8<offset<data['sweep']-1e-8:
        raise ValueError('Fx21の分割点がRef7の表示区間内にありません。')
    for start,sweep in ((data['start'],offset),(data['start']+offset,data['sweep']-offset)):
        ends=[ellipse.point_at(data,start),ellipse.point_at(data,start+sweep)]
        if min(math.dist(p,END_MM) for p in ends)<1e-7:
            return dict(start=start,sweep=sweep,ends=ends,split=split)
    raise ValueError('Fx21のRef7区間を取得できません。')


def create(root,ref7_sketch,hexagon_sketch,revision):
    import adsk.core
    import adsk.fusion
    from . import grip_surface_names, grip_reference_hexagon
    import importlib
    importlib.reload(grip_surface_names)
    name=grip_surface_names.display_name('Fx21')
    if ref7_sketch is None or hexagon_sketch is None:
        raise RuntimeError('Fx21の参照スケッチがありません。')
    tag=ref7_sketch.attributes.itemByName('grip_reference_curve','ellipse_data_mm')
    if tag is None:raise RuntimeError('Fx21のRef7計算値がありません。')
    data=json.loads(tag.value);piece=section(data)
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    d,e=grip_reference_hexagon.hexagon_data()['points'][3:5]
    candidates=[]
    for line in hexagon_sketch.sketchCurves.sketchLines:
        ends=[xyz(p.worldGeometry) for p in (line.startSketchPoint,line.endSketchPoint)]
        if all(min(math.dist(p,q) for q in ends)<1e-5 for p in (d,e)):candidates.append(line)
    if len(candidates)!=1:raise RuntimeError('Fx21の六角形D–E辺を一意に取得できません。')
    plane=root.constructionPlanes.itemByName(ref7_sketch.name+'：傾斜基準平面')
    if plane is None:raise RuntimeError('Fx21のRef7基準平面がありません。')
    sketch=root.sketches.add(plane);sketch.name=name+'：Ref7楕円区間'
    def local(p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(x/10 for x in p)))
    c,a,b=[local(p) for p in (data['center'],ellipse.point_at(data,0),ellipse.point_at(data,math.pi/2))]
    if max(abs(p.z) for p in (c,a,b))>1e-6:raise RuntimeError('Fx21の楕円が基準平面上にありません。')
    arc=sketch.sketchCurves.sketchEllipticalArcs.addByAngle(c,c.vectorTo(a),c.vectorTo(b),piece['start'],piece['sweep'])
    if arc is None:raise RuntimeError('Fx21の楕円区間を作成できません。')
    actual=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
    if any(min(math.dist(p,q) for q in actual)>1e-5 for p in piece['ends']):
        raise RuntimeError('Fx21の楕円区間端点が一致しません。')
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for curve in (arc,candidates[0]):
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:raise RuntimeError('Fx21のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=name
    if feature.bodies.count!=1:raise RuntimeError('Fx21が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:raise RuntimeError('Fx21の面積または形状を確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    if any(min(math.dist(p,q) for q in vertices)>1e-5 for p in piece['ends']+[d,e]):
        raise RuntimeError('Fx21の4頂点が指定位置と一致しません。')
    # Check the two joining edges so a twisted endpoint correspondence is not accepted.
    for first,last in ((END_MM,e),(piece['split'],d)):
        if not any(edge.startVertex is not None and edge.endVertex is not None and
                   any(math.dist(xyz(a.geometry),first)<1e-5 and math.dist(xyz(b.geometry),last)<1e-5
                       for a,b in ((edge.startVertex,edge.endVertex),(edge.endVertex,edge.startVertex)))
                   for edge in body.edges):
            raise RuntimeError('Fx21の楕円端点と六角形D・Eの対応を確認してください。')
    body.name=name;body.isLightBulbOn=True
    body.attributes.add('grip_fixed_face','id','Fx21')
    body.attributes.add('grip_fixed_face','revision',revision)
    sketch.isLightBulbOn=False
    return body
