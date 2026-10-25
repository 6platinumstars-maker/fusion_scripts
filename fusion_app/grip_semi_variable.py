"""Surfaces connecting moving finger points to fixed reference vertices."""
import math

SMV1_HINTS_MM = ((-70.075,21.518,28.332),(-57.976,24.794,28.605))
NAME = '半変動面：SmV1：AF2–AF3とFx3の接続面'


def resolve_smv1(manifest, bodies, hints=None, identifier="SmV1", fixed_id="Fx3"):
    hints = SMV1_HINTS_MM if hints is None else hints
    vertices = [tuple(getattr(v.geometry,a)*10 for a in 'xyz')
                for item,body in zip(manifest['faces'],bodies) if item['fixed_id']==fixed_id
                for v in body.vertices]
    result=[]
    for hint in hints:
        if not vertices: raise RuntimeError(identifier+'の接続先'+fixed_id+'に頂点がありません。')
        point=min(vertices,key=lambda p:math.dist(p,hint))
        if math.dist(point,hint)>0.005:
            raise RuntimeError(identifier+'の指定点に一致する'+fixed_id+'の頂点がありません。')
        result.append(point)
    if len(result)==2 and math.dist(*result)<1e-8:raise RuntimeError(identifier+'の固定側の2点が重複しています。')
    return result


def smv1_corners(finger_a_data, fixed_points, a_side_direction):
    from . import grip_width
    al2 = next(face for face in grip_width.output_faces('A', finger_a_data, a_side_direction)
               if face['index'] == 2)
    points = dict(zip(al2['names'], al2['corners']))
    # Use the actual AL2 boundary, including the averaged F2 at the twist joint.
    return [points['F2'], points['F3'], fixed_points[1], fixed_points[0]]


def create_smv1(root, finger_a_data, fixed_points, a_side_direction):
    from . import grip_width
    body=grip_width.create_patch(root,NAME,smv1_corners(finger_a_data,fixed_points,a_side_direction),
        ('AF2','AF3','SmV1-Fx3-P2','SmV1-Fx3-P1'))
    body.attributes.add('grip_semi_variable_face','id','SmV1')
    return body


SMV2_HINTS_MM = ((-57.976,24.794,28.605),(-57.056,28.129,28.882))
SMV2_NAME = '半変動面：SmV2：AF3–AF4′とFx3曲線の接続面'


def resolve_boundary_edge(manifest, bodies, fixed_id, hints, identifier):
    candidates=[]
    for item,body in zip(manifest['faces'],bodies):
        if item['fixed_id']!=fixed_id:continue
        for edge in body.edges:
            if edge.startVertex is None or edge.endVertex is None:continue
            ends=[tuple(getattr(v.geometry,a)*10 for a in 'xyz')
                  for v in (edge.startVertex,edge.endVertex)]
            if any(all(math.dist(p,h)<=0.005 for p,h in zip(order,hints))
                   for order in (ends,ends[::-1])):
                candidates.append(edge)
    if len(candidates)!=1:
        raise RuntimeError(identifier+'の指定2点間の'+fixed_id+'境界曲線を一意に取得できません。候補数：'+str(len(candidates)))
    return candidates[0]


def resolve_smv2_edge(manifest, bodies):
    return resolve_boundary_edge(manifest,bodies,'Fx3',SMV2_HINTS_MM,'SmV2')

def smv2_endpoints(finger_a_data, a_side_direction):
    from . import grip_width
    al3=next(f for f in grip_width.output_faces('A',finger_a_data,a_side_direction) if f['index']==3)
    points=dict(zip(al3['names'],al3['corners']))
    return points['F3'],points["F4'"]


def create_smv2(root, finger_a_data, a_side_direction, edge):
    import adsk.core
    import adsk.fusion
    f,h=smv2_endpoints(finger_a_data,a_side_direction)
    ends=[tuple(getattr(v.geometry,a)*10 for a in 'xyz') for v in (edge.startVertex,edge.endVertex)]
    if math.dist(ends[1],SMV2_HINTS_MM[0])<math.dist(ends[0],SMV2_HINTS_MM[0]):ends.reverse()
    p1,p2=ends
    sketch=root.sketches.add(root.xYConstructionPlane)
    sketch.name='半変動面：SmV2：接続境界'
    points=[]
    for xyz in (p1,f,h,p2):
        world=adsk.core.Point3D.create(*(v/10 for v in xyz))
        point=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
        if math.dist(xyz,tuple(getattr(point.worldGeometry,a)*10 for a in 'xyz'))>1e-5:
            raise RuntimeError('SmV2の接続境界点が指定位置と一致しません。')
        points.append(point)
    boundary=adsk.core.ObjectCollection.create()
    for a,b in zip(points,points[1:]):
        boundary.add(sketch.sketchCurves.sketchLines.addByTwoPoints(a,b))
    boundary.add(edge)
    patches=root.features.patchFeatures
    feature=patches.add(patches.createInput(boundary,adsk.fusion.FeatureOperations.NewBodyFeatureOperation))
    feature.name=SMV2_NAME
    if feature.bodies.count!=1:raise RuntimeError('SmV2が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=0:
        raise RuntimeError('SmV2のサーフェス形状を確認してください。')
    for xyz in (p1,f,h,p2):
        if not any(math.dist(xyz,tuple(getattr(v.geometry,a)*10 for a in 'xyz'))<1e-5 for v in body.vertices):
            raise RuntimeError('SmV2の境界頂点が指定位置と一致しません。')
    body.name=SMV2_NAME
    body.attributes.add('grip_semi_variable_face','id','SmV2')
    body.isLightBulbOn=True
    sketch.isLightBulbOn=False
    return body


SMV3_HINTS_MM = ((-57.056,28.129,28.882),(-58.366,32.20,24.704))
SMV3_NAME = '半変動面：SmV3：AF4′とFx2・Fx3の三角形面'


def resolve_smv3(manifest, bodies):
    result=[]
    for fixed_id,hint in zip(('Fx3','Fx2'),SMV3_HINTS_MM):
        vertices=[tuple(getattr(v.geometry,a)*10 for a in 'xyz')
                  for item,body in zip(manifest['faces'],bodies) if item['fixed_id']==fixed_id
                  for v in body.vertices]
        if not vertices:raise RuntimeError('SmV3の接続先'+fixed_id+'に頂点がありません。')
        point=min(vertices,key=lambda p:math.dist(p,hint))
        if math.dist(point,hint)>0.005:
            raise RuntimeError('SmV3の指定点に一致する'+fixed_id+'の頂点がありません。')
        result.append(point)
    return result


def smv3_corners(finger_a_data, fixed_points, a_side_direction):
    from . import grip_width
    al3=next(f for f in grip_width.output_faces('A',finger_a_data,a_side_direction) if f['index']==3)
    points=dict(zip(al3['names'],al3['corners']))
    return [points["F4'"],fixed_points[1],fixed_points[0]]


def create_smv3(root, finger_a_data, fixed_points, a_side_direction):
    from . import grip_width
    body=grip_width.create_patch(root,SMV3_NAME,smv3_corners(finger_a_data,fixed_points,a_side_direction),
        ("AF4'",'SmV3-Fx2-P2','SmV3-Fx3-P1'))
    body.attributes.add('grip_semi_variable_face','id','SmV3')
    return body


SMV4_HINTS_MM = ((-58.366,32.20,24.704),(-61.254,32.20,19.887))
SMV4_NAME = '半変動面：SmV4：AF4′–AH4′とFx2曲線の接続面'


def resolve_smv4_edge(manifest, bodies):
    return resolve_boundary_edge(manifest,bodies,'Fx2',SMV4_HINTS_MM,'SmV4')


def smv4_endpoints(finger_a_data, a_side_direction):
    from . import grip_width
    al3=next(f for f in grip_width.output_faces('A',finger_a_data,a_side_direction) if f['index']==3)
    points=dict(zip(al3['names'],al3['corners']))
    return points["F4'"],points["H4'"]


def create_smv4(root, finger_a_data, a_side_direction, edge):
    import adsk.core
    import adsk.fusion
    f,h=smv4_endpoints(finger_a_data,a_side_direction)
    ends=[tuple(getattr(v.geometry,a)*10 for a in 'xyz') for v in (edge.startVertex,edge.endVertex)]
    if math.dist(ends[1],SMV4_HINTS_MM[0])<math.dist(ends[0],SMV4_HINTS_MM[0]):ends.reverse()
    p1,p2=ends
    sketch=root.sketches.add(root.xYConstructionPlane)
    sketch.name='半変動面：SmV4：接続境界'
    points=[]
    for xyz in (p1,f,h,p2):
        world=adsk.core.Point3D.create(*(v/10 for v in xyz))
        point=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
        if math.dist(xyz,tuple(getattr(point.worldGeometry,a)*10 for a in 'xyz'))>1e-5:
            raise RuntimeError('SmV4の接続境界点が指定位置と一致しません。')
        points.append(point)
    boundary=adsk.core.ObjectCollection.create()
    for a,b in zip(points,points[1:]):
        boundary.add(sketch.sketchCurves.sketchLines.addByTwoPoints(a,b))
    boundary.add(edge)
    patches=root.features.patchFeatures
    feature=patches.add(patches.createInput(boundary,adsk.fusion.FeatureOperations.NewBodyFeatureOperation))
    feature.name=SMV4_NAME
    if feature.bodies.count!=1:raise RuntimeError('SmV4が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=0:
        raise RuntimeError('SmV4のサーフェス形状を確認してください。')
    for xyz in (p1,f,h,p2):
        if not any(math.dist(xyz,tuple(getattr(v.geometry,a)*10 for a in 'xyz'))<1e-5 for v in body.vertices):
            raise RuntimeError('SmV4の境界頂点が指定位置と一致しません。')
    body.name=SMV4_NAME
    body.attributes.add('grip_semi_variable_face','id','SmV4')
    body.isLightBulbOn=True
    sketch.isLightBulbOn=False
    return body


SMV5_HINTS_MM = ((-61.254,32.20,19.887),(-61.254,32.20,12.80))
SMV5_NAME = '半変動面：SmV5：BH4′–AH4′とFx2の接続面'


def resolve_smv5(manifest, bodies):
    return resolve_smv1(manifest,bodies,SMV5_HINTS_MM,'SmV5','Fx2')


def smv5_corners(finger_data, fixed_points, a_side_direction):
    from . import grip_width
    al3=next(f for f in grip_width.output_faces('A',finger_data['A'],a_side_direction) if f['index']==3)
    bl3=next(f for f in grip_width.output_faces('B',finger_data['B'],a_side_direction) if f['index']==3)
    a=dict(zip(al3['names'],al3['corners']))
    b=dict(zip(bl3['names'],bl3['corners']))
    return [b["H4'"],a["H4'"],fixed_points[0],fixed_points[1]]


def create_smv5(root, finger_data, fixed_points, a_side_direction):
    from . import grip_width
    body=grip_width.create_patch(root,SMV5_NAME,smv5_corners(finger_data,fixed_points,a_side_direction),
        ("BH4'","AH4'",'SmV5-Fx2-P1','SmV5-Fx2-P2'))
    body.attributes.add('grip_semi_variable_face','id','SmV5')
    return body


SMV6_HINTS_MM = ((-61.254,32.20,12.80),(-57.8,32.20,0.0))
SMV6_NAME = '半変動面：SmV6：BH4′–BF4′とFx2曲線の接続面'


def resolve_smv6_edge(manifest, bodies):
    return resolve_boundary_edge(manifest,bodies,'Fx2',SMV6_HINTS_MM,'SmV6')


def bl2_endpoints(finger_b_data, a_side_direction):
    from . import grip_width
    bl2=next(f for f in grip_width.output_faces('B',finger_b_data,a_side_direction) if f['index']==2)
    points=dict(zip(bl2['names'],bl2['corners']))
    return points['H3'],points['F3']


def smv6_endpoints(finger_b_data, a_side_direction):
    from . import grip_width
    bl3=next(f for f in grip_width.output_faces('B',finger_b_data,a_side_direction) if f['index']==3)
    points=dict(zip(bl3['names'],bl3['corners']))
    return points["H4'"],points["F4'"]


def create_smv6(root, finger_b_data, a_side_direction, edge):
    import adsk.core
    import adsk.fusion
    f,h=smv6_endpoints(finger_b_data,a_side_direction)
    ends=[tuple(getattr(v.geometry,a)*10 for a in 'xyz') for v in (edge.startVertex,edge.endVertex)]
    if math.dist(ends[1],SMV6_HINTS_MM[0])<math.dist(ends[0],SMV6_HINTS_MM[0]):ends.reverse()
    p1,p2=ends
    sketch=root.sketches.add(root.xYConstructionPlane)
    sketch.name='半変動面：SmV6：接続境界'
    points=[]
    for xyz in (p1,f,h,p2):
        world=adsk.core.Point3D.create(*(v/10 for v in xyz))
        point=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
        if math.dist(xyz,tuple(getattr(point.worldGeometry,a)*10 for a in 'xyz'))>1e-5:
            raise RuntimeError('SmV6の接続境界点が指定位置と一致しません。')
        points.append(point)
    boundary=adsk.core.ObjectCollection.create()
    for a,b in zip(points,points[1:]):
        boundary.add(sketch.sketchCurves.sketchLines.addByTwoPoints(a,b))
    boundary.add(edge)
    patches=root.features.patchFeatures
    feature=patches.add(patches.createInput(boundary,adsk.fusion.FeatureOperations.NewBodyFeatureOperation))
    feature.name=SMV6_NAME
    if feature.bodies.count!=1:raise RuntimeError('SmV6が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=0:
        raise RuntimeError('SmV6のサーフェス形状を確認してください。')
    for xyz in (p1,f,h,p2):
        if not any(math.dist(xyz,tuple(getattr(v.geometry,a)*10 for a in 'xyz'))<1e-5 for v in body.vertices):
            raise RuntimeError('SmV6の境界頂点が指定位置と一致しません。')
    body.name=SMV6_NAME
    body.attributes.add('grip_semi_variable_face','id','SmV6')
    body.isLightBulbOn=True
    sketch.isLightBulbOn=False
    return body


SMV7_HINTS_MM = ((-57.8,32.20,0.0),(-57.8,32.2,-6.0))
SMV7_NAME = '半変動面：SmV7：BF3–BF4′とFx2直線の接続面'


def resolve_smv7(manifest, bodies):
    return resolve_smv1(manifest,bodies,SMV7_HINTS_MM,'SmV7','Fx2')


def smv7_corners(finger_b_data, fixed_points, a_side_direction):
    return [bl2_endpoints(finger_b_data,a_side_direction)[1],
            smv6_endpoints(finger_b_data,a_side_direction)[1],fixed_points[0],fixed_points[1]]


def create_smv7(root, finger_b_data, fixed_points, a_side_direction):
    from . import grip_width
    corners=smv7_corners(finger_b_data,fixed_points,a_side_direction)
    body=grip_width.create_patch(root,SMV7_NAME,corners,
        ('BF3',"BF4'",'SmV7-Fx2-P1','SmV7-Fx2-P2'))
    body.attributes.add('grip_semi_variable_face','id','SmV7')
    return body


SMV8_HINT_MM = (-57.8,32.2,-6.0)
SMV8_NAME = '半変動面：SmV8：CH4–CH3とFx2頂点の接続面'


def resolve_smv8(manifest, bodies):
    return resolve_smv1(manifest,bodies,(SMV8_HINT_MM,),'SmV8','Fx2')[0]


def smv8_corners(finger_c_data, fixed_point, a_side_direction):
    from . import grip_width
    cl3=next(f for f in grip_width.output_faces('C',finger_c_data,a_side_direction) if f['index']==3)
    points=dict(zip(cl3['names'],cl3['corners']))
    return [points['H4'],points['H3'],fixed_point]


def create_smv8(root, finger_c_data, fixed_point, a_side_direction):
    from . import grip_width
    corners=smv8_corners(finger_c_data,fixed_point,a_side_direction)
    a,b,c=corners
    u=[b[i]-a[i] for i in range(3)]
    v=[c[i]-a[i] for i in range(3)]
    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    area=math.sqrt(sum(x*x for x in cross))/2
    if not math.isfinite(area) or area<=1e-8:
        raise RuntimeError('SmV8の3点から三角形を作成できません。')
    body=grip_width.create_patch(root,SMV8_NAME,corners,('CH4','CH3','SmV8-Fx2-P'),area)
    body.attributes.add('grip_semi_variable_face','id','SmV8')
    return body


SMV9_NAME = '半変動面：SmV9：BF3・CH3とFx2頂点の接続面'


def smv9_corners(finger_data, fixed_point, a_side_direction):
    bf3=bl2_endpoints(finger_data['B'],a_side_direction)[1]
    ch3=smv8_corners(finger_data['C'],fixed_point,a_side_direction)[1]
    return [bf3,ch3,fixed_point]


def create_smv9(root, finger_data, fixed_point, a_side_direction):
    from . import grip_width
    corners=smv9_corners(finger_data,fixed_point,a_side_direction)
    a,b,c=corners
    u=[b[i]-a[i] for i in range(3)]
    v=[c[i]-a[i] for i in range(3)]
    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    area=math.sqrt(sum(x*x for x in cross))/2
    if not math.isfinite(area) or area<=1e-8:
        raise RuntimeError('SmV9の3点から三角形を作成できません。')
    body=grip_width.create_patch(root,SMV9_NAME,corners,('BF3','CH3','SmV9-Fx2-P'),area)
    body.attributes.add('grip_semi_variable_face','id','SmV9')
    return body


SMV10_NAME = '半変動面：SmV10：Fx6指定点–CH5′–CH4接続面'
SMV10_FX6_POINT_MM = (-51.8,28.0,-6.0)


def smv10_corners(finger_c_data, fixed_point, a_side_direction):
    from . import grip_width, grip_reference_fx6
    cl4=next(f for f in grip_width.output_faces('C',finger_c_data,a_side_direction) if f['index']==4)
    points=dict(zip(cl4['names'],cl4['corners']))
    return [fixed_point,SMV10_FX6_POINT_MM,
            grip_reference_fx6.tip_point('C',finger_c_data,a_side_direction),points['H4']]


def create_smv10(root, finger_c_data, fixed_point, a_side_direction):
    from . import grip_width
    corners=smv10_corners(finger_c_data,fixed_point,a_side_direction)
    body=grip_width.create_patch(root,SMV10_NAME,corners,
                                ('SmV10-Fx2-P','SmV10-Fx6-P',"CH5'",'CH4'))
    body.attributes.add('grip_semi_variable_face','id','SmV10')
    return body


HEXAGON_TRIANGLES = (('SmV11','B','C',1,2),('SmV12','C','D',2,3))


def hexagon_triangle_faces(finger_d):
    from . import grip_reference_hexagon
    vertices=grip_reference_hexagon.hexagon_data()['points']
    dg1=finger_d['points_mm'][1]
    result=[]
    for identifier,first,second,i,j in HEXAGON_TRIANGLES:
        corners=[vertices[i],vertices[j],dg1]
        a,b,c=corners
        u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        area=math.sqrt(sum(x*x for x in cross))/2
        if not math.isfinite(area) or area<=1e-8:
            raise ValueError(identifier+'の3点から三角面を作成できません。')
        result.append(dict(identifier=identifier,corners=corners,area_mm2=area,
                           name='半変動面：'+identifier+'：六角形'+first+'–'+second+'–DG1三角面',
                           names=('六角形'+first,'六角形'+second,'DG1')))
    return result


def create_hexagon_triangles(root,finger_d):
    from . import grip_width,grip_reference_hexagon
    import importlib
    importlib.reload(grip_reference_hexagon)
    result=[]
    for face in hexagon_triangle_faces(finger_d):
        body=grip_width.create_patch(root,face['name'],face['corners'],face['names'],face['area_mm2'])
        body.attributes.add('grip_semi_variable_face','id',face['identifier'])
        result.append(body)
    return result
