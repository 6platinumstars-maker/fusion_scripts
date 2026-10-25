"""Con19/20 join Con3 width endpoints and Ref12 AG2-prime to Ref13."""
import math
from . import grip_width, grip_reference_bezier, grip_twist as v


def face_data(finger_data,direction,ref13):
    points={'Ref13':tuple(ref13)}
    for finger in 'AB':
        face=next(f for f in grip_width.output_faces(finger,finger_data[finger],direction) if f['index']==2)
        points.update((finger+n,p) for n,p in zip(face['names'],face['corners']))
    points["AG2'"]=grip_reference_bezier.curve_data(finger_data['A'])['control_points_mm'][2]
    result=[]
    for identifier,names in (('Con19',('BH2','AH2','Ref13')),('Con20',('Ref13','AH2',"AG2'"))):
        corners=[points[n] for n in names]
        if any(not math.isfinite(x) for p in corners for x in p):raise ValueError(identifier+'の頂点座標が不正です。')
        area=v.norm(v.cross(v.sub(corners[1],corners[0]),v.sub(corners[2],corners[0])))/2
        if area<1e-8:raise ValueError(identifier+'の三角面が退化しています。')
        result.append(dict(identifier=identifier,names=names,corners=corners,area_mm2=area))
    return result


def create(root,finger_data,direction,reference_point):
    ref13=tuple(getattr(reference_point.worldGeometry,a)*10 for a in 'xyz')
    bodies=[]
    for data in face_data(finger_data,direction,ref13):
        name='グリップ接続面：'+data['identifier']+'：'+'–'.join(data['names'])
        body=grip_width.create_patch(root,name,data['corners'],data['names'],data['area_mm2'])
        body.attributes.add('grip_connection_face','id',data['identifier'])
        bodies.append(body)
    return bodies
