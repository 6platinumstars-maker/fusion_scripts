"""FxL3: circular Fx3 boundary translated 2 mm along the upward normal."""
import math

OFFSET_MM = 2.0
ORIGINAL_SWEEP_DEG = 129.98
CENTER_HINT = (-41.895, 5.138, 28.978)
ORIGINAL_START_HINT = (-72.426, 21.988, 30.378)
START_HINT = (-76.002, 12.506, 29.591)
END_HINT = (-35.835, -29.114, 26.132)
NAME = '固定線：FxL3：Fx3＋2mm円弧'


def dot(a, b):
    return sum(x*y for x,y in zip(a,b))


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def arc_data(source_center, normal, radius):
    length=math.sqrt(dot(normal,normal))
    n=tuple(v/length for v in normal)
    if n[2]<0:n=tuple(-v for v in n)
    center=tuple(source_center[i]+OFFSET_MM*n[i] for i in range(3))
    def radial(hint):
        d=tuple(hint[i]-center[i] for i in range(3))
        projection=dot(d,n)
        d=tuple(d[i]-projection*n[i] for i in range(3))
        norm=math.sqrt(dot(d,d))
        if norm<1e-10:raise ValueError('FxL3の端点方向を計算できません。')
        return tuple(v/norm for v in d)
    u=radial(ORIGINAL_START_HINT);target=radial(END_HINT)
    sign=1 if dot(cross(u,target),n)>0 else -1
    v=tuple(sign*x for x in cross(n,u))
    sweep=math.radians(ORIGINAL_SWEEP_DEG)
    start=tuple(center[i]+radius*u[i] for i in range(3))
    end=tuple(center[i]+radius*(math.cos(sweep)*u[i]+math.sin(sweep)*v[i]) for i in range(3))
    # Preserve the previously confirmed opposite endpoint; trim only this end.
    new_u=radial(START_HINT)
    end_u=tuple((end[i]-center[i])/radius for i in range(3))
    sweep=math.atan2(sign*dot(cross(new_u,end_u),n),dot(new_u,end_u)) % math.tau
    if not 0 < sweep < math.pi:
        raise ValueError('FxL3の変更端点が想定する短い円弧区間にありません。')
    start=tuple(center[i]+radius*new_u[i] for i in range(3))
    return dict(center=center,normal=n,radius=radius,start=start,end=end,sweep=sweep)


def create(root, manifest, bodies):
    import adsk.core
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    candidates=[]
    for item,body in zip(manifest['faces'],bodies):
        if item['fixed_id']!='Fx3':continue
        for face in body.faces:
            plane=adsk.core.Plane.cast(face.geometry)
            if plane is None:continue
            for edge in face.edges:
                arc=adsk.core.Arc3D.cast(edge.geometry)
                if arc is None or abs(arc.radius*10-34.9)>0.005:continue
                data=arc_data(xyz(arc.center),tuple(getattr(plane.normal,a) for a in 'xyz'),arc.radius*10)
                if math.dist(data['center'],CENTER_HINT)<0.005:
                    candidates.append((face,plane,data))
    if not candidates:raise RuntimeError('FxL3に対応するFx3の円弧がありません。')
    face,source_plane,data=candidates[0]
    if any(math.dist(other['center'],data['center'])>1e-5 or abs(other['radius']-data['radius'])>1e-5
           for _,_,other in candidates):
        raise RuntimeError('FxL3の参照円弧が一意に決まりません。')
    # Check offset side against the actual resulting construction-plane geometry.
    plane=None
    for offset in (OFFSET_MM,-OFFSET_MM):
        inp=root.constructionPlanes.createInput()
        if not inp.setByOffset(face,adsk.core.ValueInput.createByReal(offset/10)):
            raise RuntimeError('FxL3のオフセット平面を定義できません。')
        trial=root.constructionPlanes.add(inp)
        delta=tuple(xyz(trial.geometry.origin)[i]-xyz(source_plane.origin)[i] for i in range(3))
        if abs(dot(delta,data['normal'])-OFFSET_MM)<1e-5:
            plane=trial;break
        trial.deleteMe()
    if plane is None:raise RuntimeError('FxL3の＋2mm方向を確認できません。')
    plane.name='固定線：FxL3：Fx3＋2mm基準平面'
    sketch=root.sketches.add(plane);sketch.name=NAME
    def local(p):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(x/10 for x in p)))
    c,s,e=(local(data[k]) for k in ('center','start','end'))
    if max(abs(p.z) for p in (c,s,e))>1e-6:
        raise RuntimeError('FxL3の円弧がスケッチ平面上にありません。')
    determinant=(s.x-c.x)*(e.y-c.y)-(s.y-c.y)*(e.x-c.x)
    sweep=data['sweep']*(1 if determinant>0 else -1)
    arc=sketch.sketchCurves.sketchArcs.addByCenterStartSweep(c,s,sweep)
    if arc is None:raise RuntimeError('FxL3の円弧を作成できません。')
    actual=[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)]
    if any(min(math.dist(data[key],p) for p in actual)>1e-5 for key in ('start','end')):
        raise RuntimeError('FxL3の生成端点が計算結果と一致しません。')
    arc.attributes.add('grip_fixed_line','id','FxL3')
    sketch.attributes.add('grip_fixed_line','id','FxL3')
    sketch.isLightBulbOn=True;plane.isLightBulbOn=False
    return sketch
