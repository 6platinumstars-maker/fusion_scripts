"""SmV12: hexagon C-D and the actual Fx21 ellipse endpoint."""
from . import grip_reference_hexagon, grip_smv16, grip_twist as v

NAME='半変動面：SmV12：六角形C–D・Fx21楕円端点三角面'


def face_data(split):
    points=grip_reference_hexagon.hexagon_data()['points'][2:4]+[tuple(split)]
    area=v.norm(v.cross(v.sub(points[1],points[0]),v.sub(points[2],points[0])))/2
    if area<1e-8:raise ValueError('SmV12の三角面が退化しています。')
    return points,area


def create(root,fx21_body,point_g):
    from . import grip_width
    _,ends=grip_smv16.resolve_boundary(fx21_body,point_g)
    points,area=face_data(ends[1])
    body=grip_width.create_patch(root,NAME,points,('六角形C','六角形D','Fx21楕円端点'),area)
    body.attributes.add('grip_semi_variable_face','id','SmV12')
    return body
