"""Ref5: tilted ellipse through current AF1, G and FxL1's (-29.854, -35.0, 10.492) endpoint."""
import math
import json
from . import grip_twist as v
from . import grip_fixed_lines as fixed

NAME = '参考線：Ref5：AF1′–G–指定終点楕円弧'


def fit_ellipse(points, reference=None):
    reference=fixed.ellipse_data() if reference is None else reference
    a,g,e=points
    normal=v.unit(v.cross(v.sub(g,a),v.sub(e,a)))
    old_u=tuple(reference['u'])+(0.,)
    u=v.unit(v.sub(old_u,v.mul(normal,v.dot(old_u,normal))))
    minor_direction=v.unit(v.cross(normal,u))
    ratio=reference['major']/reference['minor']
    # Scaling the long-axis coordinate reduces the fixed-ratio ellipse to a circle.
    scaled=[(v.dot(v.sub(p,a),u)/ratio,v.dot(v.sub(p,a),minor_direction)) for p in points]
    cx,cy,k=fixed.solve3([(2*x,2*y,1.,x*x+y*y) for x,y in scaled])
    radius2=cx*cx+cy*cy+k
    if not math.isfinite(radius2) or radius2<=1e-12:
        raise ValueError('Ref5の楕円半径を計算できません。')
    minor=math.sqrt(radius2);major=ratio*minor
    center=v.add(a,v.add(v.mul(u,ratio*cx),v.mul(minor_direction,cy)))
    angles=[math.atan2(y-cy,x-cx) for x,y in scaled]
    start,via,end=angles
    sweep=(end-start)%math.tau
    if (via-start)%math.tau>sweep:
        start,end=end,start
        sweep=(end-start)%math.tau
    return dict(center=center,u=u,v=minor_direction,normal=normal,major=major,minor=minor,
                start=start,sweep=sweep,via=via,angles=angles,points=tuple(points))


def point_at(data,t):
    return v.add(data['center'],v.add(v.mul(data['u'],data['major']*math.cos(t)),
                                     v.mul(data['v'],data['minor']*math.sin(t))))


def from_finger(data,a_side_direction):
    from . import grip_width
    al1=next(face for face in grip_width.output_faces('A',data,a_side_direction) if face['index']==1)
    af1=al1['corners'][al1['names'].index('F1')]
    return fit_ellipse((af1,data['points_mm'][0],fixed.START_MM))


def create(root,finger_data,a_side_direction):
    return create_data(root,from_finger(finger_data,a_side_direction),NAME,'Ref5')


def create_data(root,data,name,identifier):
    import adsk.core
    def world(p):return adsk.core.Point3D.create(*(x/10 for x in p))
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    support=root.sketches.add(root.xYConstructionPlane);support.name=name+'：基準3点'
    points=[]
    for coords in data['points']:
        point=support.sketchPoints.add(support.modelToSketchSpace(world(coords)))
        if point is None or math.dist(xyz(point.worldGeometry),coords)>1e-5:
            raise RuntimeError(identifier+'の基準点を正しい3D位置に作成できません。')
        points.append(point)
    inp=root.constructionPlanes.createInput()
    if not inp.setByThreePoints(*points):raise RuntimeError(identifier+'の3点平面を定義できません。')
    plane=root.constructionPlanes.add(inp);plane.name=name+'：傾斜基準平面'
    sketch=root.sketches.add(plane);sketch.name=name
    def local(p):return sketch.modelToSketchSpace(world(p))
    c=local(data['center']);a=local(point_at(data,0));b=local(point_at(data,math.pi/2))
    if max(abs(p.z) for p in (c,a,b))>1e-6:
        raise RuntimeError(identifier+'の楕円が基準平面上にありません。')
    ellipse=sketch.sketchCurves.sketchEllipses.add(c,a,b)
    if ellipse is None:raise RuntimeError(identifier+'の基準楕円を作成できません。')
    ellipse.isConstruction=True
    arc=sketch.sketchCurves.sketchEllipticalArcs.addByAngle(
        c,c.vectorTo(a),c.vectorTo(b),data['start'],data['sweep'])
    if arc is None:raise RuntimeError(identifier+'の楕円弧を作成できません。')
    ends=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
    if any(min(math.dist(p,q) for q in ends)>1e-5 for p in (data['points'][0],data['points'][2])):
        raise RuntimeError(identifier+'の楕円弧端点が指定点と一致しません。')
    sketch.sketchPoints.add(local(data['points'][1]))
    arc.attributes.add('grip_reference_curve','id',identifier)
    sketch.attributes.add('grip_reference_curve','id',identifier)
    sketch.attributes.add('grip_reference_curve','ellipse_data_mm',json.dumps(data))
    sketch.isLightBulbOn=True;support.isLightBulbOn=False;plane.isLightBulbOn=False
    return sketch


REF6_NAME = '参考線：Ref6：CG1–DG1–指定終点楕円弧'
REF6_END_MM = (-29.854,-35.0,-6.0)


def from_cd(finger_c,finger_d):
    return fit_ellipse((finger_c['points_mm'][1],finger_d['points_mm'][1],REF6_END_MM))


def create_ref6(root,finger_c,finger_d):
    return create_data(root,from_cd(finger_c,finger_d),REF6_NAME,'Ref6')


REF7_NAME = '参考線：Ref7：AF1′–G–Z=-6指定終点楕円弧'
REF7_END_MM = (-29.854,-35.0,-6.0)


def from_a_lower(finger_a,a_side_direction):
    from . import grip_width
    al1=next(face for face in grip_width.output_faces('A',finger_a,a_side_direction) if face['index']==1)
    af1=al1['corners'][al1['names'].index('F1')]
    return fit_ellipse((af1,finger_a['points_mm'][0],REF7_END_MM))


def create_ref7(root,finger_a,a_side_direction):
    return create_data(root,from_a_lower(finger_a,a_side_direction),REF7_NAME,'Ref7')


HEXAGON_CURVES = (('Ref9','B',1),('Ref10','C',2),('Ref11','D',3))


def from_cd_hexagon(finger_c,finger_d):
    from . import grip_reference_hexagon
    vertices=grip_reference_hexagon.hexagon_data()['points']
    return {identifier:fit_ellipse((finger_c['points_mm'][1],finger_d['points_mm'][1],vertices[index]))
            for identifier,label,index in HEXAGON_CURVES}


def create_hexagon_curves(root,finger_c,finger_d):
    from . import grip_reference_hexagon
    import importlib
    importlib.reload(grip_reference_hexagon)
    curves=from_cd_hexagon(finger_c,finger_d)
    return [create_data(root,curves[identifier],
                        '参考線：'+identifier+'：CG1–DG1–六角形'+label+'楕円弧',identifier)
            for identifier,label,index in HEXAGON_CURVES]
