"""Con16/17 connect current finger points; Con18 joins AF2 to Fx9 vertices."""
import math
from . import grip_width, grip_reference_closest, grip_twist as v

FX9_HINTS_MM=((-70.075,21.518,28.332),(-76.003,12.506,29.59))


def face(identifier,names,points):
    area=None
    if any(not math.isfinite(x) for p in points for x in p):raise ValueError(identifier+'の頂点座標が不正です。')
    if len(points)==3:
        area=v.norm(v.cross(v.sub(points[1],points[0]),v.sub(points[2],points[0])))/2
        if area<1e-8:raise ValueError(identifier+'の三角面が退化しています。')
    return dict(identifier=identifier,names=names,corners=points,area_mm2=area)


def moving_faces(finger_data,direction,ref13=None):
    points={}
    for finger in 'ABC':
        for item in grip_width.output_faces(finger,finger_data[finger],direction):
            points.update((finger+n,p) for n,p in zip(item['names'],item['corners']))
    points.update(grip_width.quarter_l1_points('C',finger_data['C'],direction))
    points["Ref13"]=tuple(ref13) if ref13 is not None else grip_reference_closest.point_data(finger_data['A'],finger_data['C'],direction)['point_mm']
    definitions=(('Con16',("CH1'","Ref13",'BH2','BF2')),('Con17',("CH1'",'CH2','BF2')))
    return [face(identifier,names,[points[n] for n in names]) for identifier,names in definitions]


def fixed_face(finger_a,direction,fx9_body):
    width=next(item for item in grip_width.output_faces('A',finger_a,direction) if item['index']==2)
    af2=dict(zip(width['names'],width['corners']))['F2']
    vertices=[tuple(getattr(vertex.geometry,a)*10 for a in 'xyz') for vertex in fx9_body.vertices]
    points=[af2]
    for hint in FX9_HINTS_MM:
        if not vertices:raise ValueError('Con18のFx9に頂点がありません。')
        nearest=min(vertices,key=lambda p:math.dist(p,hint))
        if math.dist(nearest,hint)>.005:raise ValueError('Con18の指定点に一致するFx9頂点がありません。')
        points.append(nearest)
    return face('Con18',('AF2','Fx9-Fx3端点','Fx9-FxL3端点'),points)


def create_face(root,data):
    name='グリップ接続面：'+data['identifier']+'：'+'–'.join(data['names'])
    body=grip_width.create_patch(root,name,data['corners'],data['names'],data['area_mm2'])
    body.attributes.add('grip_connection_face','id',data['identifier'])
    return body


def create_moving(root,finger_data,direction,reference_point):
    ref13=tuple(getattr(reference_point.worldGeometry,a)*10 for a in 'xyz')
    return [create_face(root,data) for data in moving_faces(finger_data,direction,ref13)]


def create_fixed(root,finger_a,direction,fx9_body):
    return create_face(root,fixed_face(finger_a,direction,fx9_body))
