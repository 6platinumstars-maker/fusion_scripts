"""Ref13: closest point on the infinite CH1-prime/AG2-prime line to AH2/AH1."""
import math
import json
from . import grip_twist as v, grip_width, grip_reference_bezier

NAME='参考点：Ref13：CH1′–AG2′直線とAH2–AH1直線の最接近点'


def closest_lines(p,q,r,end):
    if any(not math.isfinite(x) for point in (p,q,r,end) for x in point):
        raise ValueError('Ref13の直線座標が不正です。')
    u=v.sub(q,p);direction=v.sub(end,r);offset=v.sub(p,r)
    a=v.dot(u,u);b=v.dot(u,direction);c=v.dot(direction,direction)
    d=v.dot(u,offset);e=v.dot(direction,offset)
    determinant=a*c-b*b
    if a<1e-12 or c<1e-12 or determinant<=1e-12*a*c:
        raise ValueError('Ref13の直線が退化または平行のため最接近点が一意に決まりません。')
    s=(b*e-c*d)/determinant;t=(a*e-b*d)/determinant
    point=v.add(p,v.mul(u,s));other=v.add(r,v.mul(direction,t))
    return dict(point_mm=point,other_point_mm=other,distance_mm=math.dist(point,other),
                first_parameter=s,second_parameter=t,line1_mm=(p,q),line2_mm=(r,end))


def point_data(finger_a,finger_c,direction):
    ch1=grip_width.quarter_l1_points('C',finger_c,direction)["CH1'"]
    ag2=grip_reference_bezier.curve_data(finger_a)['control_points_mm'][2]
    al1=next(f for f in grip_width.output_faces('A',finger_a,direction) if f['index']==1)
    points=dict(zip(al1['names'],al1['corners']))
    return closest_lines(ch1,ag2,points['H2'],points['H1'])


def create(root,finger_a,finger_c,direction):
    import adsk.core
    data=point_data(finger_a,finger_c,direction)
    sketch=root.sketches.add(root.xYConstructionPlane);sketch.name=NAME
    world=adsk.core.Point3D.create(*(x/10 for x in data['point_mm']))
    point=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
    if point is None or math.dist(tuple(getattr(point.worldGeometry,a)*10 for a in 'xyz'),data['point_mm'])>1e-5:
        raise RuntimeError('Ref13を指定の最接近位置に作成できません。')
    point.attributes.add('grip_reference_point','id','Ref13')
    point.attributes.add('grip_reference_point','name','Ref13')
    sketch.attributes.add('grip_reference_point','id','Ref13')
    sketch.attributes.add('grip_reference_point','closest_lines_data_mm',json.dumps(data))
    sketch.isLightBulbOn=True
    return point
