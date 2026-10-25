"""Fx16: loft the existing Ref5 and Ref7 intervals from G to their fixed ends."""
import json
import math
from . import grip_reference_ellipse as ellipse


def end_to_via_section(data):
    offset=(data['via']-data['start'])%math.tau
    if not 1e-8<offset<data['sweep']-1e-8:
        raise ValueError('Fx16のGが参照楕円区間の途中にありません。')
    end=data['points'][2]
    if math.dist(ellipse.point_at(data,data['start']+data['sweep']),end)<1e-7:
        start=data['start']+offset;sweep=data['sweep']-offset
    elif math.dist(ellipse.point_at(data,data['start']),end)<1e-7:
        start=data['start'];sweep=offset
    else:raise ValueError('Fx16の指定終点が参照楕円弧の端点と一致しません。')
    return dict(start=start,sweep=sweep,ends=(tuple(data['points'][1]),tuple(end)))


def create(root,ref5_sketch,ref7_sketch,revision):
    import adsk.core
    import adsk.fusion
    import importlib
    from . import grip_surface_names
    importlib.reload(grip_surface_names)
    name=grip_surface_names.display_name('Fx16')
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    sections=[]
    for source,identifier,z in ((ref5_sketch,'Ref5',10.492),(ref7_sketch,'Ref7',-6.0)):
        if source is None:raise RuntimeError('Fx16の参照楕円'+identifier+'がありません。')
        tag=source.attributes.itemByName('grip_reference_curve','ellipse_data_mm')
        if tag is None:raise RuntimeError(identifier+'の楕円計算値がありません。')
        data=json.loads(tag.value);piece=end_to_via_section(data)
        if math.dist(piece['ends'][1],(-29.854,-35.,z))>1e-5:
            raise RuntimeError('Fx16の'+identifier+'終点が指定座標と一致しません。')
        sections.append((source,identifier,data,piece))
    if math.dist(sections[0][3]['ends'][0],sections[1][3]['ends'][0])>1e-5:
        raise RuntimeError('Fx16の2曲線のGが一致しません。')
    curves=[];sketches=[];corners=[]
    for source,identifier,data,piece in sections:
        plane=root.constructionPlanes.itemByName(source.name+'：傾斜基準平面')
        if plane is None:raise RuntimeError('Fx16の'+identifier+'基準平面がありません。')
        sketch=root.sketches.add(plane);sketch.name=name+'：'+identifier+'区間'
        def local(p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in p)))
        c=local(data['center']);a=local(ellipse.point_at(data,0));b=local(ellipse.point_at(data,math.pi/2))
        if max(abs(p.z) for p in (c,a,b))>1e-6:raise RuntimeError('Fx16の楕円断面が平面上にありません。')
        arc=sketch.sketchCurves.sketchEllipticalArcs.addByAngle(c,c.vectorTo(a),c.vectorTo(b),piece['start'],piece['sweep'])
        if arc is None:raise RuntimeError('Fx16の'+identifier+'区間を作成できません。')
        ends=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
        if any(min(math.dist(p,q) for q in ends)>1e-5 for p in piece['ends']):
            raise RuntimeError('Fx16の楕円断面端点がGと指定終点に一致しません。')
        curves.append(arc);sketches.append(sketch);corners.extend(piece['ends'])
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for curve in curves:
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:
            raise RuntimeError('Fx16のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=name
    if feature.bodies.count!=1:raise RuntimeError('Fx16が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Fx16の面積または形状を確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in vertices) for p in corners):
        raise RuntimeError('Fx16の生成面がGと指定終点に一致しません。')
    body.name=name;body.isLightBulbOn=True
    body.attributes.add('grip_fixed_face','id','Fx16')
    body.attributes.add('grip_fixed_face','revision',revision)
    for sketch in sketches:sketch.isLightBulbOn=False
    ref5_sketch.isLightBulbOn=True;ref7_sketch.isLightBulbOn=True
    return body
