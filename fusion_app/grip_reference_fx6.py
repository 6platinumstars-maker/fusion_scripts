"""Ref14/DH5-prime and Ref15/CH5-prime at actual Fx6 plane crossings."""
import json
import math
from . import grip_width, grip_twist as v


def intersection(a,b,origin,normal):
    direction=v.sub(b,a)
    denominator=v.dot(direction,normal)
    scale=v.norm(direction)*v.norm(normal)
    if scale<1e-12 or abs(denominator)<1e-12*scale:
        raise ValueError('Fx6との交点が一意に決まりません（直線が退化または平行）。')
    t=v.dot(v.sub(origin,a),normal)/denominator
    point=v.add(a,v.mul(direction,t))
    if not all(math.isfinite(x) for x in point):raise ValueError('Fx6交点の座標が不正です。')
    return dict(point_mm=point,line_parameter=t,on_segment=(-1e-9<=t<=1+1e-9),line_mm=(a,b))


def tip_intersection(finger,data,direction,origin=(0,0,-6.),normal=(0,0,1.)):
    # Always intersect the original width guideline, not the shortened face.
    width=grip_width.connected_faces(data['points_mm'],direction,10.,
        data.get('twist_joint_index',2),data.get('front_plane_normal'))[4]
    points=dict(zip(width['names'],width['corners']))
    return intersection(points['H4'],points['H5'],origin,normal)


def tip_point(finger,data,direction):
    if 'fx6_h5_prime_mm' in data:return tuple(data['fx6_h5_prime_mm'])
    return tip_intersection(finger,data,direction)['point_mm']


def point_data(finger_data,direction,origin,normal):
    result=[]
    for finger,identifier in (('D','Ref14'),('C','Ref15')):
        data=tip_intersection(finger,finger_data[finger],direction,origin,normal)
        data.update(identifier=identifier,label=finger+'H5′')
        result.append(data)
    return result


def create(root,finger_data,direction):
    import adsk.core
    faces=[]
    for body in root.bRepBodies:
        tag=body.attributes.itemByName('grip_fixed_face','id')
        if tag and tag.value=='Fx6':faces.extend(list(body.faces))
    if len(faces)!=1:raise RuntimeError('参照点の基準Fx6を一意に取得できません。')
    face=faces[0];plane=adsk.core.Plane.cast(face.geometry)
    if plane is None:raise RuntimeError('Fx6が平面ではありません。')
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    origin=xyz(plane.origin);normal=tuple(getattr(plane.normal,a) for a in 'xyz')
    data=point_data(finger_data,direction,origin,normal)
    for item in data:
        world=adsk.core.Point3D.create(*(x/10 for x in item['point_mm']))
        if not face.isPointOnFace(world,.0005):
            raise RuntimeError(item['label']+'はFx6の支持平面上ですが、面の範囲外です。')
        finger_data[item['label'][0]]['fx6_h5_prime_mm']=tuple(item['point_mm'])
        name='参考点：{}：{}（{}H4–{}H5とFx6の交点）'.format(item['identifier'],item['label'],item['label'][0],item['label'][0])
        sketch=root.sketches.add(root.xYConstructionPlane);sketch.name=name
        point=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
        if point is None or math.dist(xyz(point.worldGeometry),item['point_mm'])>1e-5:
            raise RuntimeError(item['label']+'を計算位置に作成できません。')
        point.attributes.add('grip_reference_point','id',item['identifier'])
        point.attributes.add('grip_reference_point','name',item['label'])
        sketch.attributes.add('grip_reference_point','id',item['identifier'])
        sketch.attributes.add('grip_reference_point','intersection_data_mm',json.dumps(item))
        sketch.isLightBulbOn=True
    return data
