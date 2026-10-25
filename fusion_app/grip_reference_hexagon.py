"""Ref8 regular hexagon on the X-axis 135-degree plane at the requested side."""
import math

NAME = '参考線：Ref8：六角形ABCDEF'
SIDE_MM = 10.0
OFFSET_MM = -40.0
HINTS_MM = ((-61.727,-30.443,-26.125),(-71.727,-30.443,-26.125),
            (-76.727,-36.567,-20.002),(-71.727,-42.691,-13.878),
            (-61.727,-42.691,-13.878),(-56.727,-36.567,-20.002))


def hexagon_data():
    # Plane orientation is modulo 180 degrees. Choose the normal that makes
    # the user's negative offset reach the side specified by all six hints.
    n=(0.,math.sqrt(.5),math.sqrt(.5))
    tangent=(0.,math.sqrt(.5),-math.sqrt(.5))
    mean=tuple(sum(p[i] for p in HINTS_MM)/6 for i in range(3))
    signed=sum(mean[i]*n[i] for i in range(3))
    center=tuple(mean[i]+(OFFSET_MM-signed)*n[i] for i in range(3))
    height=math.sqrt(3)*SIDE_MM/2
    local=((SIDE_MM/2,height),(-SIDE_MM/2,height),(-SIDE_MM,0),
           (-SIDE_MM/2,-height),(SIDE_MM/2,-height),(SIDE_MM,0))
    points=[(center[0]+x,center[1]+y*tangent[1],center[2]+y*tangent[2]) for x,y in local]
    if any(math.dist(p,h)>.005 for p,h in zip(points,HINTS_MM)):
        raise ValueError('Ref8の正六角形が指定近似値と一致しません。')
    return dict(center=center,normal=n,points=points)


def create(root):
    import adsk.core
    data=hexagon_data()
    def world(p):return adsk.core.Point3D.create(*(x/10 for x in p))
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    support=root.sketches.add(root.xYConstructionPlane);support.name=NAME+'：基準3点'
    anchors=[]
    for coords in data['points'][:3]:
        point=support.sketchPoints.add(support.modelToSketchSpace(world(coords)))
        if point is None or math.dist(coords,xyz(point.worldGeometry))>1e-5:
            raise RuntimeError('Ref8の基準3点を作成できません。')
        anchors.append(point)
    inp=root.constructionPlanes.createInput()
    if not inp.setByThreePoints(*anchors):raise RuntimeError('Ref8の基準平面を定義できません。')
    plane=root.constructionPlanes.add(inp);plane.name=NAME+'：X軸135度・オフセット−40mm'
    sketch=root.sketches.add(plane);sketch.name=NAME
    points=[]
    for label,coords in zip('ABCDEF',data['points']):
        local=sketch.modelToSketchSpace(world(coords))
        if abs(local.z)>1e-6:raise RuntimeError('Ref8の頂点がスケッチ平面上にありません。')
        point=sketch.sketchPoints.add(local)
        if point is None or math.dist(coords,xyz(point.worldGeometry))>1e-5:
            raise RuntimeError('Ref8の頂点'+label+'が指定位置にありません。')
        point.attributes.add('grip_reference_point','name',label)
        point.attributes.add('grip_reference_point','id','Ref8-'+label)
        points.append(point)
    for i in range(6):
        line=sketch.sketchCurves.sketchLines.addByTwoPoints(points[i],points[(i+1)%6])
        if line is None:raise RuntimeError('Ref8の六角形の辺を作成できません。')
        line.attributes.add('grip_reference_curve','id','Ref8')
    sketch.attributes.add('grip_reference_curve','id','Ref8')
    sketch.isLightBulbOn=True;support.isLightBulbOn=False;plane.isLightBulbOn=False
    return sketch
