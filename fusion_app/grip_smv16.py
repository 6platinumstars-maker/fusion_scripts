"""SmV16 lofts Ref7 endpoint-to-G and Ref10 hexagon-C-to-DG1 arcs."""
import math
import json
from . import grip_reference_ellipse as ellipse
from . import grip_twist as v
from . import grip_hexagon_curved_surfaces, grip_reference_hexagon

NAME='半変動面：SmV16：Ref7端点–G・六角形C–DG1楕円間ロフト面'
HINTS_MM=((-71.727,-42.691,-13.878),(-93.19139979761287,-46.57812082776331,6.270520878966186))


def xyz(point):
    return tuple(getattr(point,a)*10 for a in 'xyz')


def resolve_boundary(body,point_g):
    from .grip_semi_variable import resolve_boundary_edge
    edge=resolve_boundary_edge({'faces':[{'fixed_id':'Fx21'}]},[body],'Fx21',HINTS_MM,'SmV16')
    ends=[xyz(vertex.geometry) for vertex in (edge.startVertex,edge.endVertex)]
    if math.dist(ends[0],HINTS_MM[0])>math.dist(ends[1],HINTS_MM[0]):ends.reverse()
    corners=ends+[tuple(point_g)]
    if any(not math.isfinite(x) for p in corners for x in p):
        raise ValueError('SmV16の頂点座標が不正です。')
    if v.norm(v.cross(v.sub(ends[1],ends[0]),v.sub(point_g,ends[0])))<1e-8:
        raise ValueError('SmV16の3頂点が退化しています。')
    return edge,corners


def ellipse_section(data,split,point_g):
    split_offset=(-data['start'])%math.tau
    g_offset=(data['via']-data['start'])%math.tau
    if not all(1e-8<t<data['sweep']-1e-8 for t in (split_offset,g_offset)):
        raise ValueError('SmV16の楕円端点またはGがRef7表示区間内にありません。')
    if math.dist(ellipse.point_at(data,0),split)>1e-5 or math.dist(ellipse.point_at(data,data['via']),point_g)>1e-5:
        raise ValueError('SmV16のRef7区間がFx21端点・Gと一致しません。')
    start=data['start']+min(split_offset,g_offset)
    sweep=abs(g_offset-split_offset)
    if sweep<1e-8:raise ValueError('SmV16の楕円区間が退化しています。')
    return dict(start=start,sweep=sweep,ends=(tuple(split),tuple(point_g)))


def create_ref7_arc(root,ref7_sketch,data,piece):
    import adsk.core
    plane=root.constructionPlanes.itemByName(ref7_sketch.name+'：傾斜基準平面')
    if plane is None:raise RuntimeError('SmV16のRef7基準平面がありません。')
    arc_sketch=root.sketches.add(plane);arc_sketch.name=NAME+'：Ref7端点–G区間'
    def local(p):return arc_sketch.modelToSketchSpace(adsk.core.Point3D.create(*(x/10 for x in p)))
    c,a,b=[local(p) for p in (data['center'],ellipse.point_at(data,0),ellipse.point_at(data,math.pi/2))]
    if max(abs(p.z) for p in (c,a,b))>1e-6:raise RuntimeError('SmV16の楕円が基準平面上にありません。')
    arc=arc_sketch.sketchCurves.sketchEllipticalArcs.addByAngle(c,c.vectorTo(a),c.vectorTo(b),piece['start'],piece['sweep'])
    if arc is None:raise RuntimeError('SmV16の楕円区間を作成できません。')
    ends=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
    if any(min(math.dist(p,q) for q in ends)>1e-5 for p in piece['ends']):
        raise RuntimeError('SmV16の楕円境界端点が一致しません。')
    arc_sketch.isLightBulbOn=False
    return arc


def sections(ref7,ref10,split,point_g):
    first=ellipse_section(ref7,split,point_g)
    second=grip_hexagon_curved_surfaces.section(ref10)
    d=grip_reference_hexagon.hexagon_data()['points'][2]
    if math.dist(second['ends'][1],d)>1e-5:
        raise ValueError('SmV16のRef10終点が六角形Cと一致しません。')
    return first,second


def create(root,ref7_sketch,fx21_body,point_g):
    import adsk.fusion
    _,corners=resolve_boundary(fx21_body,point_g)
    sources=[s for s in root.sketches if s.attributes.itemByName('grip_reference_curve','id') is not None
             and s.attributes.itemByName('grip_reference_curve','id').value=='Ref10']
    if len(sources)!=1:raise RuntimeError('SmV16のRef10参照スケッチが一意に決まりません。')
    data=[]
    for source in (ref7_sketch,sources[0]):
        tag=source.attributes.itemByName('grip_reference_curve','ellipse_data_mm')
        if tag is None:raise RuntimeError('SmV16の参照楕円計算値がありません。')
        data.append(json.loads(tag.value))
    first,second=sections(*data,corners[1],point_g)
    create_ref7_arc(root,ref7_sketch,data[0],first)
    helper_names=(NAME+'：Ref7端点–G区間','半変動面：SmV11・SmV12：Ref10のDG1–C区間')
    curves=[]
    for name,piece in zip(helper_names,(first,second)):
        sketch=root.sketches.itemByName(name)
        if sketch is None or sketch.sketchCurves.sketchEllipticalArcs.count!=1:
            raise RuntimeError('SmV16の既存部分楕円弧がありません：'+name)
        arc=sketch.sketchCurves.sketchEllipticalArcs.item(0)
        ends=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
        if any(min(math.dist(p,q) for q in ends)>1e-5 for p in piece['ends']):
            raise RuntimeError('SmV16の既存楕円区間端点が指定位置と一致しません。')
        curves.append(arc)
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for curve in curves:
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:
            raise RuntimeError('SmV16のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=NAME
    if feature.bodies.count!=1:raise RuntimeError('SmV16が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('SmV16の面積または形状を確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in vertices) for p in first['ends']+second['ends']):
        raise RuntimeError('SmV16の4頂点が指定位置と一致しません。')
    for start,end in ((first['ends'][0],second['ends'][1]),(first['ends'][1],second['ends'][0])):
        if not any(edge.startVertex is not None and edge.endVertex is not None and
                   any(math.dist(xyz(a.geometry),start)<1e-5 and math.dist(xyz(b.geometry),end)<1e-5
                       for a,b in ((edge.startVertex,edge.endVertex),(edge.endVertex,edge.startVertex)))
                   for edge in body.edges):
            raise RuntimeError('SmV16の端点対応（楕円端点–C、G–DG1）を確認してください。')
    body.name=NAME;body.isLightBulbOn=True
    body.attributes.add('grip_semi_variable_face','id','SmV16')
    return body
