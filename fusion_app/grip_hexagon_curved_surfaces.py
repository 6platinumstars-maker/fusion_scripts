"""SmV11/12 bounded by Ref9/10/11 ellipse intervals and hexagon straight sides."""
import json
import math
from . import grip_reference_ellipse as ellipse


def section(data):
    offset=(data['via']-data['start'])%math.tau
    if not 1e-8<offset<data['sweep']-1e-8:
        raise ValueError('DG1が参照楕円区間の途中にありません。')
    end=data['points'][2]
    if math.dist(ellipse.point_at(data,data['start']+data['sweep']),end)<1e-7:
        start=data['start']+offset;sweep=data['sweep']-offset
    elif math.dist(ellipse.point_at(data,data['start']),end)<1e-7:
        start=data['start'];sweep=offset
    else:raise ValueError('六角形頂点が参照楕円の端点と一致しません。')
    return dict(start=start,sweep=sweep,ends=(tuple(data['points'][1]),tuple(end)))


def create(root,finger_d,source_sketches):
    import adsk.core
    import adsk.fusion
    from . import grip_reference_hexagon
    vertices=grip_reference_hexagon.hexagon_data()['points']
    dg1=finger_d['points_mm'][1]
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    def local(sketch,p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in p)))
    sources={}
    for sketch in source_sketches:
        tag=sketch.attributes.itemByName('grip_reference_curve','id')
        if tag is not None:sources[tag.value]=sketch
    curves={};helpers=[]
    for identifier,label,index in ellipse.HEXAGON_CURVES:
        source=sources.get(identifier)
        if source is None:raise RuntimeError('半変動面の参照曲線'+identifier+'がありません。')
        attr=source.attributes.itemByName('grip_reference_curve','ellipse_data_mm')
        if attr is None:raise RuntimeError(identifier+'の楕円計算値がありません。')
        data=json.loads(attr.value);piece=section(data)
        if math.dist(piece['ends'][0],dg1)>1e-5 or math.dist(piece['ends'][1],vertices[index])>1e-5:
            raise RuntimeError(identifier+'の区間がDG1・六角形頂点と一致しません。')
        plane=root.constructionPlanes.itemByName(source.name+'：傾斜基準平面')
        if plane is None:raise RuntimeError(identifier+'の基準平面がありません。')
        sketch=root.sketches.add(plane);sketch.name='半変動面：SmV11・SmV12：'+identifier+'のDG1–'+label+'区間'
        c=local(sketch,data['center']);a=local(sketch,ellipse.point_at(data,0));b=local(sketch,ellipse.point_at(data,math.pi/2))
        arc=sketch.sketchCurves.sketchEllipticalArcs.addByAngle(c,c.vectorTo(a),c.vectorTo(b),piece['start'],piece['sweep'])
        if arc is None:raise RuntimeError(identifier+'の部分楕円弧を作成できません。')
        ends=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
        if any(min(math.dist(p,q) for q in ends)>1e-5 for p in piece['ends']):
            raise RuntimeError(identifier+'の部分楕円弧端点が一致しません。')
        curves[label]=arc;helpers.append(sketch)
    result=[]
    for identifier,first,second,i,j in (('SmV11','B','C',1,2),):
        name='半変動面：'+identifier+'：六角形'+first+'–'+second+'とDG1の楕円境界面'
        sketch=root.sketches.add(root.xYConstructionPlane);sketch.name=name+'：六角形辺'
        points=[]
        for p in (vertices[i],vertices[j]):
            point=sketch.sketchPoints.add(local(sketch,p))
            if point is None or math.dist(xyz(point.worldGeometry),p)>1e-5:
                raise RuntimeError(identifier+'の六角形辺端点を作成できません。')
            points.append(point)
        line=sketch.sketchCurves.sketchLines.addByTwoPoints(*points)
        if line is None:raise RuntimeError(identifier+'の六角形辺を作成できません。')
        boundary=adsk.core.ObjectCollection.create()
        for curve in (line,curves[second],curves[first]):boundary.add(curve)
        patches=root.features.patchFeatures
        feature=patches.add(patches.createInput(boundary,adsk.fusion.FeatureOperations.NewBodyFeatureOperation))
        feature.name=name
        if feature.bodies.count!=1:raise RuntimeError(identifier+'が1つのサーフェスになりませんでした。')
        body=feature.bodies.item(0)
        if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
            raise RuntimeError(identifier+'の曲面形状を確認してください。')
        actual=[xyz(v.geometry) for v in body.vertices]
        if any(not any(math.dist(p,q)<1e-5 for q in actual) for p in (vertices[i],vertices[j],dg1)):
            raise RuntimeError(identifier+'の3頂点が指定点と一致しません。')
        body.name=name;body.isLightBulbOn=True
        body.attributes.add('grip_semi_variable_face','id',identifier)
        result.append(body);helpers.append(sketch)
    for sketch in helpers:sketch.isLightBulbOn=False
    return result
