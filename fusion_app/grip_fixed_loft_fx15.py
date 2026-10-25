"""Fx15 joins the remaining FxL1 interval to the Fx9/FxL3 boundary up to X."""
import math

ELLIPSE_HINTS = ((-79.596,-35.129,10.492),(-76.795,18.768,10.492))
UPPER_HINT = (-76.006,12.506,29.59)
X_HINT = (-52.459,-28.011,26.224)


def ellipse_section():
    from . import grip_fixed_lines as f
    data=f.ellipse_data()
    ends=(f.point_at(data,0),f.point_at(data,data['start']))
    if any(math.dist(p,q)>.005 for p,q in zip(ends,ELLIPSE_HINTS)):
        raise RuntimeError('Fx15の楕円区間が指定点と一致しません。')
    if not data['start']<0<data['start']+data['sweep']:
        raise RuntimeError('Fx15の楕円区間がFxL1の範囲外です。')
    return data,ends


def create(root,fx9_body,fxl1_sketch,fxl3_sketch,reference_x,revision):
    import adsk.core
    import adsk.fusion
    import importlib
    from . import grip_fixed_lines as f, grip_surface_names
    importlib.reload(grip_surface_names)
    name=grip_surface_names.display_name('Fx15')
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    def local(sketch,p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in p)))
    def check_ends(curve,expected):
        actual=[xyz(p.worldGeometry) for p in (curve.startSketchPoint,curve.endSketchPoint)]
        if any(min(math.dist(p,q) for q in actual)>1e-5 for p in expected):
            raise RuntimeError('Fx15の断面端点が指定区間と一致しません。')
    arcs=fxl3_sketch.sketchCurves.sketchArcs
    if arcs.count!=1:raise RuntimeError('Fx15のFxL3円弧が一意に決まりません。')
    source=arcs.item(0)
    endpoints=[xyz(p.worldGeometry) for p in (source.startSketchPoint,source.endSketchPoint)]
    upper=min(endpoints,key=lambda p:math.dist(p,UPPER_HINT))
    if math.dist(upper,UPPER_HINT)>.005 or not any(
            math.dist(upper,xyz(v.geometry))<1e-5 for v in fx9_body.vertices):
        raise RuntimeError('Fx15の指定上端がFx9の頂点と一致しません。')
    x=xyz(reference_x.worldGeometry)
    if math.dist(x,X_HINT)>.005:raise RuntimeError('Fx15の参考点Xが指定点と一致しません。')
    plane=root.constructionPlanes.itemByName('固定線：FxL3：Fx3＋2mm基準平面')
    if plane is None:raise RuntimeError('Fx15のFxL3基準平面がありません。')
    upper_sketch=root.sketches.add(plane);upper_sketch.name=name+'：Fx9円弧区間'
    c,p,q=[local(upper_sketch,v) for v in (xyz(source.centerSketchPoint.worldGeometry),upper,x)]
    a=(p.x-c.x,p.y-c.y);b=(q.x-c.x,q.y-c.y)
    if max(abs(v.z) for v in (c,p,q))>1e-6 or abs(math.hypot(*a)-math.hypot(*b))>1e-6:
        raise RuntimeError('Fx15の上側端点が同じFxL3円上にありません。')
    sweep=math.atan2(a[0]*b[1]-a[1]*b[0],a[0]*b[0]+a[1]*b[1])
    if abs(sweep)<1e-8:raise RuntimeError('Fx15の上側円弧区間が退化しています。')
    upper_arc=upper_sketch.sketchCurves.sketchArcs.addByCenterStartSweep(c,p,sweep)
    if upper_arc is None:raise RuntimeError('Fx15の上側円弧区間を作成できません。')
    check_ends(upper_arc,(upper,x))
    data,ends=ellipse_section()
    source_ellipses=fxl1_sketch.sketchCurves.sketchEllipticalArcs
    if source_ellipses.count!=1:raise RuntimeError('Fx15のFxL1楕円弧が一意に決まりません。')
    original=source_ellipses.item(0)
    if min(math.dist(ends[1],xyz(v.worldGeometry)) for v in
           (original.startSketchPoint,original.endSketchPoint))>1e-5:
        raise RuntimeError('Fx15の楕円終点がFxL1と一致しません。')
    plane=root.constructionPlanes.itemByName('固定線：FxL1：XY基準平面Z=10.492')
    if plane is None:raise RuntimeError('Fx15のFxL1基準平面がありません。')
    lower_sketch=root.sketches.add(plane);lower_sketch.name=name+'：楕円区間'
    c=local(lower_sketch,data['center'])
    major=c.vectorTo(local(lower_sketch,f.point_at(data,0)))
    minor=c.vectorTo(local(lower_sketch,f.point_at(data,math.pi/2)))
    lower_arc=lower_sketch.sketchCurves.sketchEllipticalArcs.addByAngle(c,major,minor,data['start'],-data['start'])
    if lower_arc is None:raise RuntimeError('Fx15の楕円区間を作成できません。')
    check_ends(lower_arc,ends)
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for curve in (lower_arc,upper_arc):
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:
            raise RuntimeError('Fx15のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=name
    if feature.bodies.count!=1:raise RuntimeError('Fx15が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Fx15の面積または形状を確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in vertices) for p in list(ends)+[upper,x]):
        raise RuntimeError('Fx15の生成面が指定の4頂点に一致しません。')
    body.name=name;body.isLightBulbOn=True
    body.attributes.add('grip_fixed_face','id','Fx15')
    body.attributes.add('grip_fixed_face','revision',revision)
    upper_sketch.isLightBulbOn=False;lower_sketch.isLightBulbOn=False
    fxl1_sketch.isLightBulbOn=True;fxl3_sketch.isLightBulbOn=True
    return body
