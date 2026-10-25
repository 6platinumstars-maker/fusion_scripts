"""Ref12: quadratic Bezier tangent to the displayed G-AG1-prime-AG2-prime lines."""
import json
import math
from . import grip_twist as v

NAME='参考線：Ref12：G–AG2′内接曲線（AG1′制御点）'


def curve_data(finger_a):
    source=finger_a['points_mm']
    points=finger_a.get('guideline_points_mm')
    if points is None:
        points=[source[0],v.sub(v.add(source[0],source[2]),source[1]),source[2]]
    # The new end is the center of Con1's quarter-length free boundary.
    ag2_prime=v.add(points[2],v.mul(v.sub(points[1],points[2]),.25))
    control=[tuple(points[0]),tuple(points[1]),tuple(ag2_prime)]
    if any(not math.isfinite(x) for p in control for x in p):
        raise ValueError('Ref12の制御点座標が不正です。')
    if v.norm(v.cross(v.sub(control[1],control[0]),v.sub(control[2],control[0])))<1e-8:
        raise ValueError('Ref12の3点が同一直線上にあります。')
    return dict(control_points_mm=control,degree=2,knots=[0.,0.,0.,1.,1.,1.])


def point_at(data,t):
    a,b,c=data['control_points_mm']
    return tuple((1-t)**2*a[i]+2*t*(1-t)*b[i]+t*t*c[i] for i in range(3))


def create(root,finger_a):
    import adsk.core
    data=curve_data(finger_a)
    def world(p):return adsk.core.Point3D.create(*(x/10 for x in p))
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    support=root.sketches.add(root.xYConstructionPlane);support.name=NAME+'：基準3点'
    anchors=[]
    for p in data['control_points_mm']:
        point=support.sketchPoints.add(support.modelToSketchSpace(world(p)))
        if point is None or math.dist(xyz(point.worldGeometry),p)>1e-5:
            raise RuntimeError('Ref12の基準点を指定位置に作成できません。')
        anchors.append(point)
    inp=root.constructionPlanes.createInput()
    if not inp.setByThreePoints(*anchors):raise RuntimeError('Ref12の基準平面を定義できません。')
    plane=root.constructionPlanes.add(inp);plane.name=NAME+'：基準平面'
    sketch=root.sketches.add(plane);sketch.name=NAME
    control=[sketch.modelToSketchSpace(world(p)) for p in data['control_points_mm']]
    if max(abs(p.z) for p in control)>1e-6:raise RuntimeError('Ref12の制御点が平面上にありません。')
    nurbs=adsk.core.NurbsCurve3D.createNonRational(control,2,data['knots'],False)
    if nurbs is None:raise RuntimeError('Ref12の二次ベジェ曲線を定義できません。')
    curve=sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(nurbs)
    if curve is None:raise RuntimeError('Ref12のスプラインを作成できません。')
    actual=[xyz(p.worldGeometry) for p in (curve.startSketchPoint,curve.endSketchPoint)]
    if any(math.dist(p,q)>1e-5 for p,q in zip(actual,(data['control_points_mm'][0],data['control_points_mm'][2]))):
        raise RuntimeError('Ref12の端点がG・AG2′と一致しません。')
    curve.endSketchPoint.attributes.add('grip_reference_point','name',"AG2'")
    curve.endSketchPoint.attributes.add('grip_reference_point','id',"Ref12-AG2'")
    curve.attributes.add('grip_reference_curve','id','Ref12')
    sketch.attributes.add('grip_reference_curve','id','Ref12')
    sketch.attributes.add('grip_reference_curve','bezier_data_mm',json.dumps(data))
    support.isLightBulbOn=False;plane.isLightBulbOn=False;sketch.isLightBulbOn=True
    return sketch
