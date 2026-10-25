"""Con14: DG1-DH2-CF2-CF1-prime straight-boundary surface."""
from . import grip_width

NAME='グリップ接続面：Con14：DG1–DH2–CF2–CF1′'
NAMES=('DG1','DH2','CF2',"CF1'")


def corners(finger_c,finger_d,direction):
    d_face=next(f for f in grip_width.output_faces('D',finger_d,direction) if f['index']==2)
    dh2=dict(zip(d_face['names'],d_face['corners']))['H2']
    c_face=next(f for f in grip_width.output_faces('C',finger_c,direction) if f['index']==2)
    cf2=dict(zip(c_face['names'],c_face['corners']))['F2']
    cf1_prime=grip_width.quarter_l1_points('C',finger_c,direction)["CF1'"]
    return [finger_d['points_mm'][1],dh2,cf2,cf1_prime]


def create(root,finger_c,finger_d,direction):
    body=grip_width.create_patch(root,NAME,corners(finger_c,finger_d,direction),NAMES)
    body.attributes.add('grip_connection_face','id','Con14')
    return body
