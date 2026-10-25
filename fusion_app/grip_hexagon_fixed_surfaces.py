"""Fx17 hexagon cap and Fx18-Fx20 connections to the current D width edges."""
import math
from . import grip_twist as v


def face_data(finger_d,a_side_direction):
    from . import grip_reference_hexagon as hexagon, grip_width
    hex_points=hexagon.hexagon_data()['points']
    points=dict(zip('ABCDEF',hex_points))
    for face in grip_width.output_faces('D',finger_d,a_side_direction):
        for name,p in zip(face['names'],face['corners']):
            key='D'+name
            if key in points and math.dist(points[key],p)>1e-8:
                raise ValueError('指Dの共有幅端点が一致しません：'+key)
            points[key]=p
    # Share A-DF3 and F-DF4 between neighboring faces; retain the F-side labels.
    definitions=(('Fx17',tuple('ABCDEF')),
                 ('Fx18',('A','B','DF2','DF3')),
                 ('Fx19',('A','F','DF4','DF3')),
                 ('Fx20',('E','F','DF4','DF5')))
    result=[]
    for identifier,names in definitions:
        corners=[points[name] for name in names]
        if any(not math.isfinite(x) for p in corners for x in p):
            raise ValueError(identifier+'の頂点座標が不正です。')
        if min(math.dist(a,b) for a,b in zip(corners,corners[1:]+corners[:1]))<1e-8:
            raise ValueError(identifier+'の境界辺が退化しています。')
        fan_area=sum(v.norm(v.cross(v.sub(corners[i],corners[0]),v.sub(corners[i+1],corners[0])))
                     for i in range(1,len(corners)-1))/2
        if fan_area<=1e-8:raise ValueError(identifier+'の面積がありません。')
        expected=3*math.sqrt(3)*hexagon.SIDE_MM**2/2 if identifier=='Fx17' else None
        result.append(dict(identifier=identifier,names=names,corners=corners,area_mm2=expected))
    return result


def create(root,finger_d,a_side_direction):
    from . import grip_reference_hexagon, grip_surface_names, grip_width
    import importlib
    importlib.reload(grip_reference_hexagon)
    importlib.reload(grip_surface_names)
    bodies=[]
    for face in face_data(finger_d,a_side_direction):
        body=grip_width.create_patch(root,grip_surface_names.display_name(face['identifier']),
                                    face['corners'],face['names'],face['area_mm2'])
        body.attributes.add('grip_fixed_face','id',face['identifier'])
        bodies.append(body)
    return bodies
