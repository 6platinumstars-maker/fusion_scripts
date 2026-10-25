"""Tangent point on FxL3 after orthogonal projection of the Fx5 source point."""
import math

SOURCE_HINT_MM = (-29.854,-35.0,23.639)
NAME = '参考点：Ref4：X（FxL3投影接点）'


def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def tangent_point(center,start,end,source):
    u=sub(start,center);v=sub(end,center)
    radius=math.sqrt(dot(u,u))
    n=cross(u,v);length=math.sqrt(dot(n,n))
    if radius<1e-8 or length<1e-10:
        raise ValueError('Xの参照円弧の平面を計算できません。')
    n=tuple(x/length for x in n)
    if abs(math.sqrt(dot(v,v))-radius)>1e-5:
        raise ValueError('Xの参照円弧の半径が一致しません。')
    # FxL3 is the confirmed minor arc; its endpoints define this interval.
    sweep=math.atan2(dot(cross(u,v),n),dot(u,v))
    offset=dot(sub(source,center),n)
    projected=tuple(source[i]-offset*n[i] for i in range(3))
    d=sub(projected,center);d2=dot(d,d)
    if d2<=radius*radius+1e-10:
        raise ValueError('Fx5の投影点が円の外側にないため接線を計算できません。')
    side=cross(n,d);scale=radius*math.sqrt(d2-radius*radius)/d2
    candidates=[]
    for sign in (-1,1):
        point=tuple(center[i]+radius*radius/d2*d[i]+sign*scale*side[i] for i in range(3))
        w=sub(point,center)
        angle=math.atan2(dot(cross(u,w),n),dot(u,w)) % math.tau
        if angle<=sweep+1e-9 or abs(angle-math.tau)<1e-9:
            candidates.append(point)
    if len(candidates)!=1:
        raise ValueError('現在のFxL3区間内の接点Xが一意に決まりません。候補数：'+str(len(candidates)))
    return candidates[0],projected


def create(root,manifest,bodies,fxl3_sketch):
    import adsk.core
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    vertices=[xyz(v.geometry) for item,body in zip(manifest['faces'],bodies)
              if item['fixed_id']=='Fx5' for v in body.vertices]
    if not vertices:raise RuntimeError('Xの基準となるFx5頂点がありません。')
    source=min(vertices,key=lambda p:math.dist(p,SOURCE_HINT_MM))
    if math.dist(source,SOURCE_HINT_MM)>.005:
        raise RuntimeError('Xの指定基準点に一致するFx5頂点がありません。')
    arcs=fxl3_sketch.sketchCurves.sketchArcs
    if arcs.count!=1:raise RuntimeError('Xの対象となるFxL3円弧が一意に決まりません。')
    arc=arcs.item(0)
    tag=arc.attributes.itemByName('grip_fixed_line','id')
    if tag is None or tag.value!='FxL3':raise RuntimeError('Xの対象円弧がFxL3ではありません。')
    point,projected=tangent_point(xyz(arc.centerSketchPoint.worldGeometry),
        xyz(arc.startSketchPoint.worldGeometry),xyz(arc.endSketchPoint.worldGeometry),source)
    sketch=root.sketches.add(root.xYConstructionPlane);sketch.name=NAME
    world=adsk.core.Point3D.create(*(x/10 for x in point))
    result=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
    if result is None or math.dist(xyz(result.worldGeometry),point)>1e-5:
        raise RuntimeError('参考点Xを指定の3D位置に作成できませんでした。')
    result.attributes.add('grip_reference_point','id','Ref4')
    result.attributes.add('grip_reference_point','name','X')
    sketch.attributes.add('grip_reference_point','id','Ref4')
    sketch.attributes.add('grip_reference_point','projected_source_mm',','.join(map(str,projected)))
    sketch.isLightBulbOn=True
    return result
