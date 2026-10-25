"""Replace the notched Fx4 copy with a loft of its lower/upper conics."""
import math

HINTS = ((-76.795,8.044,-6.), (-29.854,-24.826,-6.),
         (-76.795,5.303,26.985), (-29.844,-27.338,24.270))
NAME = '固定面：Fx4：上下円弧接続曲面'


def sections(center, normal, radius, corners):
    from .grip_fixed_arc import dot, cross
    n = tuple(x/math.sqrt(dot(normal,normal)) for x in normal)
    if n[2] < 0: n = tuple(-x for x in n)
    if n[2] < .9: raise ValueError('Fx4の円柱軸方向が想定と異なります。')
    def radial(p):
        d = tuple(p[i]-center[i] for i in range(3))
        a = dot(d,n)
        r = tuple(d[i]-a*n[i] for i in range(3))
        length = math.sqrt(dot(r,r))
        if abs(length-radius) > .005: raise ValueError('Fx4の指定点が円柱面から離れています。')
        return tuple(x/length for x in r)
    result = []
    for lower, ends in ((True,corners[:2]), (False,corners[2:])):
        u, target = map(radial,ends)
        sweep = math.atan2(dot(cross(u,target),n),dot(u,target))
        v = cross(n,u)
        if not .1 < abs(sweep) < math.pi: raise ValueError('Fx4の円弧区間が不正です。')
        count = math.ceil(abs(sweep)/(math.pi/2))
        controls, weights = [], []
        def point(angle,weight):
            p = tuple(center[i]+radius*(math.cos(angle)*u[i]+math.sin(angle)*v[i])/weight for i in range(3))
            if lower:
                distance = (-6.-p[2])/n[2]
                p = tuple(p[i]+distance*n[i] for i in range(3))
            return p
        for j in range(count):
            a,b = sweep*j/count, sweep*(j+1)/count
            w = math.cos((b-a)/2)
            if j == 0: controls.append(point(a,1)); weights.append(1.)
            controls.extend((point((a+b)/2,w),point(b,1)))
            weights.extend((w,1.))
        if any(math.dist(p,q) > .005 for p,q in zip((controls[0],controls[-1]),ends)):
            raise ValueError('Fx4の円弧への補正が0.005 mmを超えています。')
        knots = [0.]*3 + [float(j) for j in range(1,count) for _ in range(2)] + [float(count)]*3
        result.append(dict(control=controls,weights=weights,knots=knots))
    return result


def resolve(manifest,bodies):
    import adsk.core
    def xyz(p): return tuple(getattr(p,a)*10 for a in 'xyz')
    sources = [b for row,b in zip(manifest['faces'],bodies) if row['fixed_id']=='Fx4']
    if len(sources)!=1: raise RuntimeError('Fx4の元円柱面を一意に取得できません。')
    vertices = [xyz(v.geometry) for v in sources[0].vertices]
    corners = [min(vertices,key=lambda p:math.dist(p,h)) for h in HINTS]
    if any(math.dist(p,h)>.005 for p,h in zip(corners,HINTS)):
        raise RuntimeError('Fx4の指定4頂点を取得できません。')
    for row,body in zip(manifest['faces'],bodies):
        if row['fixed_id']!='Fx3': continue
        for edge in body.edges:
            arc = adsk.core.Arc3D.cast(edge.geometry)
            if arc is not None and abs(arc.radius*10-34.9)<.005 and math.dist(xyz(arc.center),(-41.895,5.303,26.985))<.005:
                return sections(xyz(arc.center),tuple(getattr(arc.normal,a) for a in 'xyz'),arc.radius*10,corners),sources[0]
    raise RuntimeError('Fx4上端に対応するFx3の円弧がありません。')


def replace(root,manifest,bodies):
    import adsk.core
    import adsk.fusion
    data,old = resolve(manifest,bodies)
    def world(p): return adsk.core.Point3D.create(*(x/10 for x in p))
    def xyz(p): return tuple(getattr(p,a)*10 for a in 'xyz')
    curves=[]; sketches=[]
    for label,section in zip(('下側楕円弧','上側円弧'),data):
        support=root.sketches.add(root.xYConstructionPlane);support.name=NAME+'：'+label+'基準点'
        control=section['control']
        anchors=[support.sketchPoints.add(support.modelToSketchSpace(world(p))) for p in (control[0],control[1],control[-1])]
        inp=root.constructionPlanes.createInput()
        if not inp.setByThreePoints(*anchors): raise RuntimeError('Fx4の円弧平面を設定できません。')
        plane=root.constructionPlanes.add(inp);plane.name=NAME+'：'+label+'平面'
        sketch=root.sketches.add(plane);sketch.name=NAME+'：'+label
        local=[sketch.modelToSketchSpace(world(p)) for p in control]
        if max(abs(p.z) for p in local)>1e-6: raise RuntimeError('Fx4の曲線制御点が平面外です。')
        nurbs=adsk.core.NurbsCurve3D.createRational(local,2,section['knots'],section['weights'],False)
        if nurbs is None: raise RuntimeError('Fx4の円弧を定義できません。')
        curve=sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(nurbs)
        if curve is None: raise RuntimeError('Fx4の境界曲線を作成できません。')
        curves.append(curve);sketches.append(sketch)
        support.isLightBulbOn=False;plane.isLightBulbOn=False
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for curve in curves:
        path=adsk.fusion.Path.create(curve,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None: raise RuntimeError('Fx4のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=NAME
    if feature.bodies.count!=1: raise RuntimeError('Fx4が単一ボディになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or body.faces.count!=1 or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Fx4の四角形サーフェスを確認してください。')
    vertices=[xyz(v.geometry) for v in body.vertices]
    for section in data:
        for p in (section['control'][0],section['control'][-1]):
            if not any(math.dist(p,q)<1e-5 for q in vertices): raise RuntimeError('Fx4のロフト端点が一致しません。')
    # Reject a crossed loft: each straight side must join the same end of both arcs.
    for index in (0,-1):
        pair=[s['control'][index] for s in data]
        if not any(all(min(math.dist(p,xyz(v.geometry)) for v in (e.startVertex,e.endVertex))<1e-5 for p in pair)
                   for e in body.edges if e.startVertex and e.endVertex):
            raise RuntimeError('Fx4の左右の接続が一致しません。')
    body.name=NAME;body.isLightBulbOn=True
    body.attributes.add('grip_fixed_face','id','Fx4')
    body.attributes.add('grip_fixed_face','revision',manifest['revision'])
    for sketch in sketches: sketch.isLightBulbOn=False
    if root.features.removeFeatures.add(old) is None: raise RuntimeError('旧Fx4を置き換えられません。')
    return body
