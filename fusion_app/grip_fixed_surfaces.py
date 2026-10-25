"""Additional fixed grip surfaces built from the copied outer-shell vertices."""
import math

FX7_HINTS_MM = ((-76.79, 32.233, 29.223),
                (-76.795, 18.768, -6.0),
                (-57.80, 32.20, -6.0))
VERTEX_TOL_MM = 0.005
FX23_CORNERS_MM = ((-57.8,28.0,-6.0),(-57.8,32.2,-6.0),(-51.8,28.0,-6.0))


def create_fx23(root, revision):
    import adsk.core
    from . import grip_width
    from .grip_surface_names import display_name
    faces=[]
    for body in root.bRepBodies:
        tag=body.attributes.itemByName('grip_fixed_face','id')
        if tag and tag.value=='Fx6':faces.extend(list(body.faces))
    if not faces:raise RuntimeError('Fx23の基準面Fx6がありません。')
    for corner in FX23_CORNERS_MM:
        p=adsk.core.Point3D.create(*(v/10 for v in corner))
        if not any(face.isPointOnFace(p,.0005) for face in faces):
            raise RuntimeError('Fx23の指定頂点がFx6上にありません。')
    body=grip_width.create_patch(root,display_name('Fx23'),FX23_CORNERS_MM,
                                ('Fx23-P1','Fx23-P2','Fx23-P3'),12.6)
    body.attributes.add('grip_fixed_face','id','Fx23')
    body.attributes.add('grip_fixed_face','revision',revision)
    return body


def resolve_triangle(bodies, hints, identifier):
    vertices = [tuple(getattr(vertex.geometry, a)*10 for a in 'xyz')
                for body in bodies for vertex in body.vertices]
    corners = []
    for index, hint in enumerate(hints):
        if not vertices:
            raise RuntimeError(identifier+'の接続先となる固定面の頂点がありません。')
        point = min(vertices, key=lambda p: math.dist(p, hint))
        if math.dist(point, hint) > VERTEX_TOL_MM:
            raise RuntimeError(identifier+'の点{}に一致する固定面の頂点がありません。'.format(index+1))
        corners.append(point)
    a, b, c = corners
    u = [b[i]-a[i] for i in range(3)]
    v = [c[i]-a[i] for i in range(3)]
    cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    area = math.sqrt(sum(x*x for x in cross))/2
    if not math.isfinite(area) or area <= 1e-8:
        raise RuntimeError(identifier+'の3点から三角形を作成できません。')
    return corners, area


def create_fx7(root, corners, area, revision):
    from . import grip_width
    from .grip_surface_names import display_name
    body = grip_width.create_patch(root, display_name('Fx7'), corners,
                                   ('Fx7-P1', 'Fx7-P2', 'Fx7-P3'), area)
    body.attributes.add('grip_fixed_face', 'id', 'Fx7')
    body.attributes.add('grip_fixed_face', 'revision', revision)
    return body


FX8_HINTS_MM = ((-61.20,32.233,29.223),
                (-57.056,28.129,28.882),
                (-58.366,32.20,24.704))


def resolve_fx7(bodies):
    return resolve_triangle(bodies,FX7_HINTS_MM,'Fx7')


def resolve_fx8(bodies):
    return resolve_triangle(bodies,FX8_HINTS_MM,'Fx8')


def create_fx8(root, corners, area, revision):
    from . import grip_width, grip_surface_names
    import importlib
    importlib.reload(grip_surface_names)
    body=grip_width.create_patch(root,grip_surface_names.display_name('Fx8'),corners,
                                ('Fx8-P1','Fx8-P2','Fx8-P3'),area)
    body.attributes.add('grip_fixed_face','id','Fx8')
    body.attributes.add('grip_fixed_face','revision',revision)
    return body


FX10_APEX_HINT_MM = (-35.235,-29.004,26.141)
FX10_EDGE_HINTS_MM = ((-29.854,-25.90,24.395),(-29.415,-24.646,24.496))


def resolve_fx9_triangle(manifest, bodies, fx9_body, fixed_id, hints, identifier):
    def xyz(v):return tuple(getattr(v.geometry,a)*10 for a in 'xyz')
    candidates=[xyz(v) for v in fx9_body.vertices
                if math.dist(xyz(v),FX10_APEX_HINT_MM)<=VERTEX_TOL_MM]
    if len(candidates)!=1:
        raise RuntimeError(identifier+'の頂点をFx9上で一意に取得できません。')
    # The requested straight segment need not be one pre-existing BRepEdge.
    # Resolve its two ends independently, only from the requested fixed face's actual vertices.
    vertices=[xyz(v) for item,body in zip(manifest['faces'],bodies)
              if item['fixed_id']==fixed_id for v in body.vertices]
    ends=[]
    for hint in hints:
        if not vertices:
            raise RuntimeError(identifier+'の底辺頂点が'+fixed_id+'上にありません。')
        point=min(vertices,key=lambda p:math.dist(p,hint))
        if math.dist(point,hint)>VERTEX_TOL_MM:
            raise RuntimeError(identifier+'の指定底辺点に一致する'+fixed_id+'頂点がありません。')
        ends.append(point)
    corners=[candidates[0]]+ends
    u=[corners[1][i]-corners[0][i] for i in range(3)]
    v=[corners[2][i]-corners[0][i] for i in range(3)]
    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    area=math.sqrt(sum(x*x for x in cross))/2
    if not math.isfinite(area) or area<=1e-8:
        raise RuntimeError(identifier+'の3頂点から三角面を作成できません。')
    return corners,area


def resolve_fx10(manifest, bodies, fx9_body):
    return resolve_fx9_triangle(manifest,bodies,fx9_body,'Fx3',FX10_EDGE_HINTS_MM,'Fx10')

def create_fx10(root, manifest, bodies, fx9_body):
    from . import grip_width, grip_surface_names
    import importlib
    importlib.reload(grip_surface_names)
    corners,area=resolve_fx10(manifest,bodies,fx9_body)
    body=grip_width.create_patch(root,grip_surface_names.display_name('Fx10'),corners,
                                ('Fx10-Fx9頂点','Fx10-Fx3始点','Fx10-Fx3終点'),area)
    body.attributes.add('grip_fixed_face','id','Fx10')
    body.attributes.add('grip_fixed_face','revision',manifest['revision'])
    return body


FX11_EDGE_HINTS_MM = ((-29.854,-25.90,24.392),(-29.854,-35.0,23.639))


def resolve_fx11(manifest, bodies, fx9_body):
    return resolve_fx9_triangle(manifest,bodies,fx9_body,'Fx5',FX11_EDGE_HINTS_MM,'Fx11')


def create_fx11(root, manifest, bodies, fx9_body):
    from . import grip_width, grip_surface_names
    import importlib
    importlib.reload(grip_surface_names)
    corners,area=resolve_fx11(manifest,bodies,fx9_body)
    body=grip_width.create_patch(root,grip_surface_names.display_name('Fx11'),corners,
                                ('Fx11-Fx9頂点','Fx11-Fx5始点','Fx11-Fx5終点'),area)
    body.attributes.add('grip_fixed_face','id','Fx11')
    body.attributes.add('grip_fixed_face','revision',manifest['revision'])
    return body


FX13_HINTS_MM = ((-76.003,12.506,29.59),(-70.075,21.518,28.332))
FX13_POINT_MM = (-80.218,29.327,35.17)


def resolve_fx13(fx9_body):
    vertices=[tuple(getattr(v.geometry,a)*10 for a in 'xyz') for v in fx9_body.vertices]
    corners=[]
    for hint in FX13_HINTS_MM:
        if not vertices:raise RuntimeError('Fx13の接続先Fx9頂点がありません。')
        point=min(vertices,key=lambda p:math.dist(p,hint))
        if math.dist(point,hint)>VERTEX_TOL_MM:
            raise RuntimeError('Fx13の指定点に一致するFx9頂点がありません。')
        corners.append(point)
    corners.append(FX13_POINT_MM)
    u=[corners[1][i]-corners[0][i] for i in range(3)]
    v=[corners[2][i]-corners[0][i] for i in range(3)]
    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    area=math.sqrt(sum(x*x for x in cross))/2
    if not math.isfinite(area) or area<=1e-8:
        raise RuntimeError('Fx13の3点から三角面を作成できません。')
    return corners,area


def create_fx13(root, fx9_body, revision):
    from . import grip_width, grip_surface_names
    import importlib
    importlib.reload(grip_surface_names)
    corners,area=resolve_fx13(fx9_body)
    body=grip_width.create_patch(root,grip_surface_names.display_name('Fx13'),corners,
                                ('Fx13-FxL3端点','Fx13-Fx3端点','Fx13-指定点'),area)
    body.attributes.add('grip_fixed_face','id','Fx13')
    body.attributes.add('grip_fixed_face','revision',revision)
    return body


FX22_HINTS_MM = ((-29.849,-31.039,21.8),(-29.852,-31.039,-3.7),
                 (-29.844,-25.014,-3.7),(-29.844,-27.133,21.8))


def resolve_fx22(manifest,bodies):
    from .grip_semi_variable import resolve_smv1
    corners=resolve_smv1(manifest,bodies,FX22_HINTS_MM,'Fx22','Fx5')
    if any(math.dist(corners[i],corners[j])<1e-8 for i in range(4) for j in range(i)):
        raise ValueError('Fx22の頂点が重複しています。')
    from . import grip_twist as v
    area=sum(v.norm(v.cross(v.sub(corners[i],corners[0]),v.sub(corners[i+1],corners[0])))
             for i in (1,2))/2
    if not math.isfinite(area) or area<1e-8:raise ValueError('Fx22の四角面が退化しています。')
    return corners


def create_fx22(root,corners,revision):
    from . import grip_width, grip_surface_names
    import importlib
    importlib.reload(grip_surface_names)
    body=grip_width.create_patch(root,grip_surface_names.display_name('Fx22'),corners,
                                 ('Fx22-P1','Fx22-P2','Fx22-P3','Fx22-P4'))
    body.attributes.add('grip_fixed_face','id','Fx22')
    body.attributes.add('grip_fixed_face','revision',revision)
    return body
