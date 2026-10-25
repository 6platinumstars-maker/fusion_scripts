"""SmV13/14/15 connect the current D tip width to actual Fx5 vertices."""
import math
from . import grip_twist as v

FX5_HINTS_MM = ((-29.844,-24.823,-6.0),(-29.854,-35.0,-6.0))


def resolve_fixed_points(manifest,bodies):
    from . import grip_semi_variable
    return grip_semi_variable.resolve_smv1(manifest,bodies,FX5_HINTS_MM,'SmV13・SmV14・SmV15','Fx5')


def face_data(finger_d,a_side_direction,fixed_points):
    from . import grip_width, grip_reference_hexagon, grip_reference_fx6
    tip=next(face for face in grip_width.output_faces('D',finger_d,a_side_direction) if face['index']==4)
    points={'D'+name:p for name,p in zip(tip['names'],tip['corners'])}
    points["DH5'"]=grip_reference_fx6.tip_point('D',finger_d,a_side_direction)
    points.update(zip(('Fx5-P1','Fx5-P2'),fixed_points))
    points['E']=grip_reference_hexagon.hexagon_data()['points'][4]
    result=[]
    for identifier,names,description in (
        ('SmV13',('DF5','Fx5-P1','Fx5-P2'),'DF5とFx5の2頂点の接続面'),
        ('SmV14',("DH5'",'DF5','Fx5-P1'),'DH5′–DF5とFx5頂点の接続面'),
        ('SmV15',('DF5','E','Fx5-P2'),'Fx20の六角形E–DF5辺とFx5頂点の接続面')):
        corners=[points[name] for name in names]
        if any(not math.isfinite(x) for p in corners for x in p):
            raise ValueError(identifier+'の頂点座標が不正です。')
        area=v.norm(v.cross(v.sub(corners[1],corners[0]),v.sub(corners[2],corners[0])))/2
        if area<=1e-8:raise ValueError(identifier+'の三角面が退化しています。')
        result.append(dict(identifier=identifier,name='半変動面：'+identifier+'：'+description,
                           names=names,corners=corners,area_mm2=area))
    return result


def create(root,finger_d,a_side_direction,fixed_points):
    from . import grip_width
    bodies=[]
    for face in face_data(finger_d,a_side_direction,fixed_points):
        body=grip_width.create_patch(root,face['name'],face['corners'],face['names'],face['area_mm2'])
        body.attributes.add('grip_semi_variable_face','id',face['identifier'])
        bodies.append(body)
    return bodies
