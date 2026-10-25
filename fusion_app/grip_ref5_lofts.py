"""Fx14 and Fx15 using the two intervals of the current tilted Ref5 ellipse."""
import json
import math
from . import grip_reference_ellipse as ellipse

SPLIT_HINT_MM = (-91.65133213863457,-45.62511018271056,12.60031930439956)
FX14_EDGE_HINTS_MM = ((-29.854,-35.,23.639),(-52.459,-28.011,26.224))
UPPER_HINT_MM = (-76.006,12.506,29.59)


def sections(data):
    # This rounded point identifies the new ellipse's exact major-axis endpoint.
    split=ellipse.point_at(data,0)
    if math.dist(split,SPLIT_HINT_MM)>.005:
        raise ValueError('Ref5の分割点が指定近似値と一致しません。')
    offset=(-data['start'])%math.tau
    if not 1e-8<offset<data['sweep']-1e-8:
        raise ValueError('Ref5の分割点が表示区間の途中にありません。')
    pieces=[dict(start=data['start'],sweep=offset),
            dict(start=data['start']+offset,sweep=data['sweep']-offset)]
    result={}
    for piece in pieces:
        ends=(ellipse.point_at(data,piece['start']),ellipse.point_at(data,piece['start']+piece['sweep']))
        if min(math.dist(p,data['points'][2]) for p in ends)<1e-7:
            identifier='Fx14'
        elif min(math.dist(p,data['points'][0]) for p in ends)<1e-7:
            identifier='Fx15'
        else:raise ValueError('Ref5の分割区間の接続先を判断できません。')
        result[identifier]=dict(piece,ends=ends)
    if set(result)!={'Fx14','Fx15'}:raise ValueError('Ref5の2区間を取得できません。')
    # Trim only Fx15's lower boundary to G; keep Fx14 and the source ellipse.
    old=result['Fx15']
    via=data['start']+(data['via']-data['start'])%math.tau
    split_parameter=data['start']+offset
    if not old['start']<via<old['start']+old['sweep']:
        raise ValueError('Fx15のGが変更前の楕円区間内にありません。')
    start=min(via,split_parameter);sweep=abs(split_parameter-via)
    result['Fx15']=dict(start=start,sweep=sweep,
        ends=(ellipse.point_at(data,start),ellipse.point_at(data,start+sweep)))
    return result,split


def create(root,ref5_sketch,fx12_body,fx9_body,fxl3_sketch,reference_x,revision):
    import adsk.core
    import adsk.fusion
    import importlib
    from . import grip_surface_names
    from .grip_semi_variable import resolve_boundary_edge
    importlib.reload(grip_surface_names)
    if ref5_sketch is None:raise RuntimeError('Fx14・Fx15の参照楕円Ref5がありません。')
    attribute=ref5_sketch.attributes.itemByName('grip_reference_curve','ellipse_data_mm')
    if attribute is None:raise RuntimeError('Ref5の楕円計算値がありません。')
    data=json.loads(attribute.value)
    pieces,split=sections(data)
    plane=root.constructionPlanes.itemByName(ellipse.NAME+'：傾斜基準平面')
    if plane is None:raise RuntimeError('Ref5の傾斜平面がありません。')
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    def local(sketch,p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in p)))
    def check_ends(curve,ends):
        actual=[xyz(p.worldGeometry) for p in (curve.startSketchPoint,curve.endSketchPoint)]
        if any(min(math.dist(p,q) for q in actual)>1e-5 for p in ends):
            raise RuntimeError('Ref5ロフト断面の端点が指定区間と一致しません。')
    # Locate Fx12's actual P-to-X edge. Its geometry is not reconstructed.
    edge=resolve_boundary_edge({'faces':[{'fixed_id':'Fx12'}]},[fx12_body],
                               'Fx12',FX14_EDGE_HINTS_MM,'Fx14')
    x=xyz(reference_x.worldGeometry)
    edge_ends=[xyz(v.geometry) for v in (edge.startVertex,edge.endVertex)]
    if min(math.dist(p,x) for p in edge_ends)>1e-5:
        raise RuntimeError('Fx14の上側辺が参考点Xに接続していません。')
    # Reuse the exact circle underlying the Fx9/FxL3 boundary, trimmed at X.
    sources=fxl3_sketch.sketchCurves.sketchArcs
    if sources.count!=1:raise RuntimeError('Fx15のFxL3円弧が一意に決まりません。')
    source=sources.item(0)
    upper=min((xyz(source.startSketchPoint.worldGeometry),xyz(source.endSketchPoint.worldGeometry)),
              key=lambda p:math.dist(p,UPPER_HINT_MM))
    if math.dist(upper,UPPER_HINT_MM)>.005 or not any(
            math.dist(upper,xyz(v.geometry))<1e-5 for v in fx9_body.vertices):
        raise RuntimeError('Fx15の上側端点がFx9と一致しません。')
    upper_plane=root.constructionPlanes.itemByName('固定線：FxL3：Fx3＋2mm基準平面')
    if upper_plane is None:raise RuntimeError('Fx15のFxL3基準平面がありません。')
    upper_sketch=root.sketches.add(upper_plane)
    upper_sketch.name=grip_surface_names.display_name('Fx15')+'：Fx9円弧区間'
    c,p,q=[local(upper_sketch,v) for v in (xyz(source.centerSketchPoint.worldGeometry),upper,x)]
    a=(p.x-c.x,p.y-c.y);b=(q.x-c.x,q.y-c.y)
    if max(abs(v.z) for v in (c,p,q))>1e-6 or abs(math.hypot(*a)-math.hypot(*b))>1e-6:
        raise RuntimeError('Fx15の上側区間がFxL3円上にありません。')
    sweep=math.atan2(a[0]*b[1]-a[1]*b[0],a[0]*b[0]+a[1]*b[1])
    upper_arc=upper_sketch.sketchCurves.sketchArcs.addByCenterStartSweep(c,p,sweep)
    if upper_arc is None:raise RuntimeError('Fx15の上側円弧を作成できません。')
    check_ends(upper_arc,(upper,x))
    results=[]
    for identifier,top,top_ends in (('Fx14',edge,edge_ends),('Fx15',upper_arc,(upper,x))):
        piece=pieces[identifier];name=grip_surface_names.display_name(identifier)
        sketch=root.sketches.add(plane);sketch.name=name+'：Ref5楕円区間'
        c=local(sketch,data['center'])
        major=c.vectorTo(local(sketch,ellipse.point_at(data,0)))
        minor=c.vectorTo(local(sketch,ellipse.point_at(data,math.pi/2)))
        arc=sketch.sketchCurves.sketchEllipticalArcs.addByAngle(c,major,minor,piece['start'],piece['sweep'])
        if arc is None:raise RuntimeError(identifier+'の楕円区間を作成できません。')
        check_ends(arc,piece['ends'])
        lofts=root.features.loftFeatures
        inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        inp.isSolid=False;inp.isClosed=False
        for curve in (arc,top):
            path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
            if path is None or inp.loftSections.add(path) is None:
                raise RuntimeError(identifier+'のロフト断面を設定できません。')
        feature=lofts.add(inp);feature.name=name
        if feature.bodies.count!=1:raise RuntimeError(identifier+'が1つのサーフェスになりませんでした。')
        body=feature.bodies.item(0)
        if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
            raise RuntimeError(identifier+'の面積または形状を確認してください。')
        vertices=[xyz(v.geometry) for v in body.vertices]
        if any(not any(math.dist(p,q)<1e-5 for q in vertices) for p in list(piece['ends'])+list(top_ends)):
            raise RuntimeError(identifier+'の生成面が指定の4頂点に一致しません。')
        if identifier=='Fx15':
            for a,b in ((tuple(data['points'][1]),upper),(split,x)):
                if not any(e.startVertex and e.endVertex and
                           min(math.dist(a,xyz(e.startVertex.geometry))+math.dist(b,xyz(e.endVertex.geometry)),
                               math.dist(b,xyz(e.startVertex.geometry))+math.dist(a,xyz(e.endVertex.geometry)))<2e-5
                           for e in body.edges):
                    raise RuntimeError('Fx15の接続方向（G–FxL3端点、分割点–X）が一致しません。')
        body.name=name;body.isLightBulbOn=True
        body.attributes.add('grip_fixed_face','id',identifier)
        body.attributes.add('grip_fixed_face','revision',revision)
        sketch.isLightBulbOn=False
        results.append(body)
    upper_sketch.isLightBulbOn=False
    ref5_sketch.isLightBulbOn=True;fxl3_sketch.isLightBulbOn=True
    return results
