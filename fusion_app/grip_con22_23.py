"""Con22/23 connect the existing Con13/14 shortened edges to G."""
import math
from . import grip_width, grip_twist as v


def face_data(finger_c,finger_d,direction):
    points=grip_width.quarter_l1_points('C',finger_c,direction)
    points['G']=finger_c['points_mm'][0]
    if math.dist(points['G'],finger_d['points_mm'][0])>1e-8:
        raise ValueError('Con22・Con23の指C・DのGが一致しません。')
    points['DG1']=finger_d['points_mm'][1]
    result=[]
    for identifier,names in (('Con22',("CH1'","CF1'",'G')),('Con23',("CF1'",'DG1','G'))):
        corners=[points[n] for n in names]
        area=v.norm(v.cross(v.sub(corners[1],corners[0]),v.sub(corners[2],corners[0])))/2
        if not math.isfinite(area) or area<1e-8:raise ValueError(identifier+'の三角面が退化しています。')
        result.append(dict(identifier=identifier,names=names,corners=corners,area_mm2=area))
    return result


def create(root,finger_c,finger_d,direction):
    bodies=[]
    for data in face_data(finger_c,finger_d,direction):
        name='グリップ接続面：'+data['identifier']+'：'+'–'.join(data['names'])
        body=grip_width.create_patch(root,name,data['corners'],data['names'],data['area_mm2'])
        body.attributes.add('grip_connection_face','id',data['identifier'])
        bodies.append(body)
    return bodies
