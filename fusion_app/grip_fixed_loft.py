"""Fixed loft surfaces between reference sketch curves and copied shell edges."""
import math

FX9_EDGE_HINTS_MM = ((-70.075,21.518,28.332), (-29.415,-24.646,24.496))


def resolve_fx9_edge(manifest, bodies):
    from .grip_semi_variable import resolve_boundary_edge
    return resolve_boundary_edge(manifest,bodies,'Fx3',FX9_EDGE_HINTS_MM,'Fx9')


def create_fx9(root, manifest, bodies, sketch):
    import adsk.fusion
    import importlib
    from . import grip_surface_names
    importlib.reload(grip_surface_names)
    name=grip_surface_names.display_name('Fx9')
    edge=resolve_fx9_edge(manifest,bodies)
    # The selected boundary is identified by its source face and both endpoints.
    # Keep its native BRepEdge geometry; a loft Path does not require Arc3D.
    arcs=sketch.sketchCurves.sketchArcs
    if arcs.count!=1:
        raise RuntimeError('Fx9の接続先FxL3円弧を一意に取得できません。')
    arc=arcs.item(0)
    tag=arc.attributes.itemByName('grip_fixed_line','id')
    if tag is None or tag.value!='FxL3':
        raise RuntimeError('Fx9の参照線がFxL3ではありません。')
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    corners=[xyz(v.geometry) for v in (edge.startVertex,edge.endVertex)]
    corners += [xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False
    inp.isClosed=False
    for curve in (edge,arc):
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:
            raise RuntimeError('Fx9のロフト断面を設定できません。')
    feature=lofts.add(inp)
    feature.name=name
    if feature.bodies.count!=1:
        raise RuntimeError('Fx9が1つのサーフェスボディになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Fx9のロフト面の面積または形状を確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    if any(not any(math.dist(c,p)<1e-5 for p in vertices) for c in corners):
        raise RuntimeError('Fx9のロフト面が指定円弧の端点に一致しません。')
    body.name=name
    body.attributes.add('grip_fixed_face','id','Fx9')
    body.attributes.add('grip_fixed_face','revision',manifest['revision'])
    body.isLightBulbOn=True
    sketch.isLightBulbOn=True
    return body


FX12_LINE_HINTS_MM = ((-29.854,-35.0,23.639),(-35.235,-29.004,26.141))


def create_fx12(root, fx11_body, fxl3_sketch, reference_x, revision):
    import adsk.core
    import adsk.fusion
    import importlib
    from .grip_semi_variable import resolve_boundary_edge
    from . import grip_surface_names
    importlib.reload(grip_surface_names)
    name=grip_surface_names.display_name('Fx12')
    edge=resolve_boundary_edge({'faces':[{'fixed_id':'Fx11'}]},[fx11_body],
                               'Fx11',FX12_LINE_HINTS_MM,'Fx12')
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    ends=[xyz(v.geometry) for v in (edge.startVertex,edge.endVertex)]
    shared=min(ends,key=lambda p:math.dist(p,FX12_LINE_HINTS_MM[1]))
    arcs=fxl3_sketch.sketchCurves.sketchArcs
    if arcs.count!=1:raise RuntimeError('Fx12のFxL3円弧が一意に決まりません。')
    source=arcs.item(0)
    if min(math.dist(shared,xyz(p.worldGeometry)) for p in
           (source.startSketchPoint,source.endSketchPoint))>1e-5:
        raise RuntimeError('Fx12のFx11辺とFxL3円弧が共通端点を持ちません。')
    x=xyz(reference_x.worldGeometry)
    plane=root.constructionPlanes.itemByName('固定線：FxL3：Fx3＋2mm基準平面')
    if plane is None:raise RuntimeError('Fx12のFxL3基準平面がありません。')
    sketch=root.sketches.add(plane);sketch.name=name+'：円弧区間'
    def local(p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in p)))
    c,p,q=map(local,(xyz(source.centerSketchPoint.worldGeometry),shared,x))
    if max(abs(v.z) for v in (c,p,q))>1e-6:
        raise RuntimeError('Fx12の円弧端点がFxL3平面上にありません。')
    a=(p.x-c.x,p.y-c.y);b=(q.x-c.x,q.y-c.y)
    if abs(math.hypot(*a)-math.hypot(*b))>1e-6:
        raise RuntimeError('Fx12の接点XがFxL3の円上にありません。')
    sweep=math.atan2(a[0]*b[1]-a[1]*b[0],a[0]*b[0]+a[1]*b[1])
    if abs(sweep)<1e-8:raise RuntimeError('Fx12の円弧区間の長さがありません。')
    arc=sketch.sketchCurves.sketchArcs.addByCenterStartSweep(c,p,sweep)
    if arc is None:raise RuntimeError('Fx12の円弧区間を作成できません。')
    endpoints=[xyz(v.worldGeometry) for v in (arc.startSketchPoint,arc.endSketchPoint)]
    if any(min(math.dist(p,q) for q in endpoints)>1e-5 for p in (shared,x)):
        raise RuntimeError('Fx12の円弧端点が指定区間と一致しません。')
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for curve in (edge,arc):
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:
            raise RuntimeError('Fx12のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=name
    if feature.bodies.count!=1:raise RuntimeError('Fx12が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Fx12のロフト面の面積または形状を確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in vertices) for p in ends+[x]):
        raise RuntimeError('Fx12のロフト面が指定の3頂点に一致しません。')
    body.name=name;body.isLightBulbOn=True
    body.attributes.add('grip_fixed_face','id','Fx12')
    body.attributes.add('grip_fixed_face','revision',revision)
    sketch.isLightBulbOn=False
    fxl3_sketch.isLightBulbOn=True
    return body


FX14_ELLIPSE_HINTS_MM = ((-79.596,-35.129,10.492),(-29.854,-35.0,10.492))
FX14_EDGE_HINTS_MM = ((-29.854,-35.0,23.639),(-52.459,-28.011,26.224))


def fx14_ellipse_section():
    from . import grip_fixed_lines as lines
    data=lines.ellipse_data()
    # The first rounded hint is the confirmed ellipse's major-axis endpoint.
    first=lines.point_at(data,0.)
    delta=[lines.START_MM[i]-data['center'][i] for i in range(2)]
    end=math.atan2(sum(delta[i]*data['v'][i] for i in range(2))/data['minor'],
                   sum(delta[i]*data['u'][i] for i in range(2))/data['major'])
    last=lines.point_at(data,end)
    if any(math.dist(p,q)>.005 for p,q in zip((first,last),FX14_ELLIPSE_HINTS_MM)):
        raise RuntimeError('Fx14の指定区間がFxL1楕円と一致しません。')
    if not data['start']<=0<end<=data['start']+data['sweep']+1e-10:
        raise RuntimeError('Fx14の楕円区間が現在のFxL1の範囲外です。')
    return data,end,(first,last)


def create_fx14(root, fx12_body, fxl1_sketch, revision):
    import adsk.core
    import adsk.fusion
    import importlib
    from . import grip_surface_names, grip_fixed_lines
    from .grip_semi_variable import resolve_boundary_edge
    importlib.reload(grip_surface_names)
    name=grip_surface_names.display_name('Fx14')
    edge=resolve_boundary_edge({'faces':[{'fixed_id':'Fx12'}]},[fx12_body],
                               'Fx12',FX14_EDGE_HINTS_MM,'Fx14')
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    data,sweep,ends=fx14_ellipse_section()
    source_arcs=fxl1_sketch.sketchCurves.sketchEllipticalArcs
    if source_arcs.count!=1:raise RuntimeError('Fx14の元のFxL1楕円弧が一意に決まりません。')
    source=source_arcs.item(0)
    if min(math.dist(ends[1],xyz(p.worldGeometry)) for p in
           (source.startSketchPoint,source.endSketchPoint))>1e-5:
        raise RuntimeError('Fx14の端点が元のFxL1端点と一致しません。')
    plane=root.constructionPlanes.itemByName('固定線：FxL1：XY基準平面Z=10.492')
    if plane is None:raise RuntimeError('Fx14のFxL1基準平面がありません。')
    sketch=root.sketches.add(plane);sketch.name=name+'：楕円区間'
    def local(p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in p)))
    c=local(data['center'])
    major=c.vectorTo(local(grip_fixed_lines.point_at(data,0)))
    minor=c.vectorTo(local(grip_fixed_lines.point_at(data,math.pi/2)))
    arc=sketch.sketchCurves.sketchEllipticalArcs.addByAngle(c,major,minor,0,sweep)
    if arc is None:raise RuntimeError('Fx14の楕円区間を作成できません。')
    actual=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
    if any(min(math.dist(p,q) for q in actual)>1e-5 for p in ends):
        raise RuntimeError('Fx14の楕円区間の端点が一致しません。')
    corners=list(ends)+[xyz(v.geometry) for v in (edge.startVertex,edge.endVertex)]
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for curve in (arc,edge):
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:
            raise RuntimeError('Fx14のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=name
    if feature.bodies.count!=1:raise RuntimeError('Fx14が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Fx14のロフト面の面積または形状を確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in vertices) for p in corners):
        raise RuntimeError('Fx14のロフト面が指定の4頂点に一致しません。')
    body.name=name;body.isLightBulbOn=True
    body.attributes.add('grip_fixed_face','id','Fx14')
    body.attributes.add('grip_fixed_face','revision',revision)
    sketch.isLightBulbOn=False;fxl1_sketch.isLightBulbOn=True
    return body
