"""Fixed ellipse arc fitted through the requested endpoints and via point."""
import math

CENTER_MM = (-35.928,8.326,10.492)
START_MM = (-29.854,-35.0,10.492)
VIA_MM = (-79.723,-35.0,10.492)
END_MM = (-76.795,18.768,10.492)
ORIGINAL_MINOR_MM = (-8.709,-19.188,10.492)
NAME = '固定線：FxL1：Z=10.492楕円弧'


def solve3(rows):
    rows=[list(row) for row in rows]
    for j in range(3):
        k=max(range(j,3),key=lambda i:abs(rows[i][j]))
        rows[j],rows[k]=rows[k],rows[j]
        pivot=rows[j][j]
        if abs(pivot)<1e-12:raise ValueError('指定3点から楕円を一意に計算できません。')
        rows[j]=[v/pivot for v in rows[j]]
        for i in range(3):
            if i!=j:
                factor=rows[i][j]
                rows[i]=[a-factor*b for a,b in zip(rows[i],rows[j])]
    return [row[3] for row in rows]


def ellipse_data(z_mm=CENTER_MM[2]):
    # With fixed center, the three curve points determine the symmetric conic.
    rows=[]
    for p in (START_MM,VIA_MM,END_MM):
        x,y=p[0]-CENTER_MM[0],p[1]-CENTER_MM[1]
        rows.append((x*x,2*x*y,y*y,1.0))
    a,b,d=solve3(rows)
    discriminant=math.hypot(a-d,2*b)
    low,high=(a+d-discriminant)/2,(a+d+discriminant)/2
    if not 0<low<=high:raise ValueError('指定3点と中心から楕円を作成できません。')
    u=(b,low-a)
    length=math.hypot(*u)
    if length<1e-12:u=(1.,0.) if a<=d else (0.,1.)
    else:u=tuple(v/length for v in u)
    if sum(u[i]*(VIA_MM[i]-CENTER_MM[i]) for i in range(2))<0:u=tuple(-v for v in u)
    v=(-u[1],u[0]);major=1/math.sqrt(low);minor=1/math.sqrt(high)
    def parameter(point):
        delta=[point[i]-CENTER_MM[i] for i in range(2)]
        return math.atan2(sum(delta[i]*v[i] for i in range(2))/minor,
                          sum(delta[i]*u[i] for i in range(2))/major)
    start,via,end=map(parameter,(START_MM,VIA_MM,END_MM))
    sweep=(end-start)%math.tau
    if (via-start)%math.tau>sweep:
        start,end=end,start
        sweep=(end-start)%math.tau
    return dict(center=(CENTER_MM[0],CENTER_MM[1],z_mm),major=major,minor=minor,u=u,v=v,
                start=start,sweep=sweep,via=via,coefficients=(a,b,d))


def point_at(data, t):
    return tuple(data['center'][i]+data['major']*math.cos(t)*data['u'][i]
                 +data['minor']*math.sin(t)*data['v'][i] for i in range(2))+(data['center'][2],)


def create(root, identifier="FxL1", z_mm=CENTER_MM[2], show_via=False):
    import adsk.core
    data=ellipse_data(z_mm)
    plane_input=root.constructionPlanes.createInput()
    plane_input.setByOffset(root.xYConstructionPlane,adsk.core.ValueInput.createByReal(z_mm/10))
    plane=root.constructionPlanes.add(plane_input)
    plane.name=f'固定線：{identifier}：XY基準平面Z={z_mm:g}'
    sketch=root.sketches.add(plane);sketch.name=f'固定線：{identifier}：Z={z_mm:g}楕円弧'
    def local(coords):return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v/10 for v in coords)))
    center=local(data['center'])
    major_point=local(point_at(data,0))
    minor_point=local(point_at(data,math.pi/2))
    major_axis=center.vectorTo(major_point)
    minor_axis=center.vectorTo(minor_point)
    ellipse=sketch.sketchCurves.sketchEllipses.add(center,major_point,minor_point)
    if ellipse is None:raise RuntimeError(f'{identifier}の基準楕円を作成できません。')
    ellipse.isConstruction=True
    arc=sketch.sketchCurves.sketchEllipticalArcs.addByAngle(
        center,major_axis,minor_axis,data['start'],data['sweep'])
    if arc is None:raise RuntimeError(f'{identifier}の楕円弧を作成できません。')
    actual=[tuple(getattr(p.worldGeometry,a)*10 for a in 'xyz')
            for p in (arc.startSketchPoint,arc.endSketchPoint)]
    if not all(min(math.dist(p,q) for q in actual)<1e-5 for p in (START_MM[:2]+(z_mm,),END_MM[:2]+(z_mm,))):
        raise RuntimeError(f'{identifier}の楕円弧端点が指定座標と一致しません。')
    arc.attributes.add('grip_fixed_line','id',identifier)
    sketch.attributes.add('grip_fixed_line','id',identifier)
    if show_via:
        via=VIA_MM[:2]+(z_mm,)
        point=sketch.sketchPoints.add(local(via))
        if point is None:
            raise RuntimeError(f'{identifier}の途中参考点を作成できません。')
        actual_via=tuple(getattr(point.worldGeometry,a)*10 for a in 'xyz')
        if math.dist(actual_via,via)>1e-5:
            raise RuntimeError(f'{identifier}の途中参考点が指定座標と一致しません。')
        point.attributes.add('grip_fixed_line','id',identifier)
        point.attributes.add('grip_fixed_line','role','via')
    sketch.isLightBulbOn=True
    plane.isLightBulbOn=False
    return sketch
