"""Finger ribbons with shared midpoint boundaries at the twist joint."""
import math
from . import grip_twist as v


def rectangles(points, a_side_direction, width=10.0, joint_index=2, front_normal=None):
    if not math.isfinite(width) or width <= 0:
        raise ValueError('指幅は正の有限値を指定してください。')
    if joint_index not in (1, 2, 3):
        raise ValueError('幅面の切替関節はG1、G2またはG3を指定してください。')
    if joint_index == 1:
        if front_normal is None:
            raise ValueError('G1幅面には引き継いだ前半平面の法線が必要です。')
        front = v.unit(front_normal)
    else:
        front = v.unit(v.cross(v.sub(points[1],points[0]), v.sub(points[2],points[1])))
    back = v.unit(v.cross(v.sub(points[4],points[3]), v.sub(points[5],points[4])))
    # Define H once on the front plane, then transport that side through twist.
    projection = v.dot(front, v.unit(a_side_direction))
    if abs(projection) < 1e-8:
        raise ValueError('前半の幅方向とDP→APが直交し、H/Fを決定できません。')
    h_sign = 1.0 if projection > 0 else -1.0
    axis = v.unit(v.sub(points[joint_index],points[joint_index-1]))
    turn = math.atan2(v.dot(axis,v.cross(front,back)),v.dot(front,back))
    transported_h = v.rotate(v.mul(front,h_sign),axis,turn)
    back_h_plus = v.dot(transported_h,back) > 0
    result=[]
    for i in range(5):
        normal = front if i < joint_index else back
        a,b=points[i:i+2]
        if abs(v.dot(v.unit(v.sub(b,a)),normal)) > 1e-8:
            raise ValueError('幅方向が関節線に垂直ではありません。')
        offset=v.mul(normal,width/2)
        corners=[v.add(a,offset),v.add(b,offset),v.sub(b,offset),v.sub(a,offset)]
        names=[]
        for idx,plus,minus in ((i,corners[0],corners[3]),(i+1,corners[1],corners[2])):
            # Do not reclassify the back side against DP->AP or O.
            h_plus = h_sign > 0 if i < joint_index else back_h_plus
            suffix = ('_前半' if i<joint_index else '_後半') if idx==joint_index else ''
            names.append((('H' if h_plus else 'F')+str(idx)+suffix,
                          ('F' if h_plus else 'H')+str(idx)+suffix))
        result.append(dict(index=i,normal=normal,corners=corners,
                           names=[names[0][0],names[1][0],names[1][1],names[0][1]],
                           area_mm2=width*v.norm(v.sub(b,a))))
    return result



def connected_faces(points, a_side_direction, width=10.0, joint_index=2, front_normal=None):
    faces = rectangles(points, a_side_direction, width, joint_index, front_normal)
    front, back = faces[joint_index-1], faces[joint_index]
    shared = {}
    for side in ('H', 'F'):
        key = side + str(joint_index)
        before = front['corners'][front['names'].index(key+'_前半')]
        after = back['corners'][back['names'].index(key+'_後半')]
        shared[key] = v.mul(v.add(before, after), 0.5)
    if v.norm(v.sub(*shared.values())) < 1e-8:
        raise ValueError('中点による幅端が重なっています。')
    for face in (front, back):
        for i, label in enumerate(face['names']):
            key = label.split('_')[0]
            if key in shared:
                face['corners'][i] = shared[key]
                face['names'][i] = key
        # Four spatial boundary edges define a patch; its area is not L * width.
        face['area_mm2'] = None
        face['midpoint_boundary'] = True
    return faces



# A L1 is restored on G1-prime; retain original G2 midpoint calculations.
EXCLUDED_SEGMENTS = {
    'A': frozenset((0, 4)),
    'B': frozenset((0, 1, 4)),
    'C': frozenset((0, 1)),
    'D': frozenset((0, 1)),
}


def output_faces(finger, data, a_side_direction, width=10.0):
    faces = connected_faces(data['points_mm'], a_side_direction, width,
                            data.get('twist_joint_index', 2), data.get('front_plane_normal'))
    if finger == 'A':
        # Restore the visible G1-prime segment without changing G2 or H/F identity.
        g,g1,g2=data['points_mm'][:3]
        guideline=data.get('guideline_points_mm')
        g1_prime=guideline[1] if guideline is not None else v.sub(v.add(g,g2),g1)
        displacement=v.sub(g1_prime,g1)
        for i,label in enumerate(faces[1]['names']):
            if label in ('H1','F1'):
                faces[1]['corners'][i]=v.add(faces[1]['corners'][i],displacement)
        faces[1]['area_mm2']=None
        faces[1]['guideline_g1_prime']=True
    if finger in ('A', 'B'):
        fraction = 0.25 if finger == 'A' else 0.2
        face = faces[3]
        a, b, c, d = face['corners']
        # Keep the G3 edge (a,d), shared with L2; trim only the G4 end.
        face['corners'] = [a, v.add(a, v.mul(v.sub(b,a),fraction)),
                           v.add(d, v.mul(v.sub(c,d),fraction)), d]
        face['area_mm2'] *= fraction
        face['length_fraction'] = fraction
        for i in (1,2):
            face['names'][i] += "'"
    return [face for face in faces if face['index'] not in EXCLUDED_SEGMENTS[finger]]


# Suspend surface generation; retain computed points for dependent reference curves.
SUSPENDED_WIDTH_FACES = frozenset({('A', 1)})
SUSPENDED_CONNECTION_FACES = frozenset({'Con2', 'Con4'})


def tip_surface(finger,data,direction):
    from . import grip_reference_fx6
    face=next(f for f in output_faces(finger,data,direction) if f['index']==4)
    points=dict(zip(face['names'],face['corners']))
    points["H5'"]=grip_reference_fx6.tip_point(finger,data,direction)
    names=["H5'",'F5','F4','H4']
    return dict(face,names=names,corners=[points[n] for n in names],area_mm2=None,
                fx6_trimmed=True)


def create(root, finger, data, a_side_direction, width=10.0):
    import adsk.core
    import adsk.fusion
    from . import helpers
    bodies=[]
    for item in output_faces(finger, data, a_side_direction, width):
        if (finger, item['index']) in SUSPENDED_WIDTH_FACES:
            continue
        if finger in ('C','D') and item['index']==4:
            item=tip_surface(finger,data,a_side_direction)
        name='グリップ幅面：{}L{}：幅{:g}mm'.format(finger,item['index'],width)
        if item.get('midpoint_boundary'):
            name += '：G{}中点接続'.format(data.get('twist_joint_index',2))
        if item.get('length_fraction') == 0.25:
            name += '：G3側1／4'
        elif item.get('length_fraction') == 0.2:
            name += '：G3側1／5'
        if item.get('fx6_trimmed'):name += '：H5′–F5–F4–H4'
        bodies.append(create_patch(root, name, item['corners'],
                                   [finger+label for label in item['names']], item['area_mm2']))
    return bodies


def create_patch(root, name, corners, names, expected_area=None):
    import adsk.core
    import adsk.fusion
    from . import helpers
    item = dict(corners=corners, names=names, area_mm2=expected_area)
    sketch=root.sketches.add(root.xYConstructionPlane)
    sketch.name=name+'：境界'
    points=[]
    for xyz,label in zip(item['corners'],item['names']):
        world=adsk.core.Point3D.create(*(c/10 for c in xyz))
        point=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
        actual=point.worldGeometry
        if max(abs(c*10-t) for c,t in zip((actual.x,actual.y,actual.z),xyz))>1e-5:
            raise RuntimeError(name+'の境界点を3D座標に作成できませんでした。')
        helpers.add_named_attribute(point,'グリップ幅点：'+label)
        points.append(point)
    boundary=adsk.core.ObjectCollection.create()
    for i in range(len(points)):
        boundary.add(sketch.sketchCurves.sketchLines.addByTwoPoints(points[i],points[(i+1)%len(points)]))
    patches=root.features.patchFeatures
    feature=patches.add(patches.createInput(boundary,adsk.fusion.FeatureOperations.NewBodyFeatureOperation))
    feature.name=name
    if feature.bodies.count != 1:
        raise RuntimeError(name+'の幅面が1ボディになりませんでした。')
    body=feature.bodies.item(0)
    area = body.area*100
    if body.isSolid or not math.isfinite(area) or area <= 0:
        raise RuntimeError(name+'のサーフェス形状を確認してください。')
    if item['area_mm2'] is not None and abs(area-item['area_mm2'])>max(1e-4,item['area_mm2']*1e-6):
        raise RuntimeError(name+'の表面積を確認してください。')
    for corner in item['corners']:
        if not any(max(abs(c*10-t) for c,t in zip(
                (vertex.geometry.x,vertex.geometry.y,vertex.geometry.z),corner)) < 1e-5
                for vertex in body.vertices):
            raise RuntimeError(name+'の境界頂点が指定位置と一致しません。')
    body.name=name
    helpers.add_named_attribute(body,name)
    body.isLightBulbOn=True
    sketch.isLightBulbOn=False
    return body


def quarter_l1_points(finger, data, direction):
    """Keep the G2-side quarter of the current displayed L1 ribbon."""
    face=connected_faces(data['points_mm'],direction,10.0,
                         data.get('twist_joint_index',2),data.get('front_plane_normal'))[1]
    points=dict(zip(face['names'],face['corners']))
    if finger in ('A','B'):
        g,g1,g2=data['points_mm'][:3]
        guideline=data.get('guideline_points_mm')
        displayed_g1=guideline[1] if guideline is not None else v.sub(v.add(g,g2),g1)
        shift=v.sub(displayed_g1,g1)
        for side in 'HF':points[side+'1']=v.add(points[side+'1'],shift)
    return {finger+side+"1'":v.add(points[side+'2'],v.mul(v.sub(points[side+'1'],points[side+'2']),.25))
            for side in 'HF'}


def connection_faces(finger_data, a_side_direction):
    points = {}
    for finger in ('A', 'B', 'C', 'D'):
        data = finger_data[finger]
        if finger in ('A', 'B'):
            points[finger+"G1'"] = data['guideline_points_mm'][1]
        else:
            points[finger+'G1'] = data['points_mm'][1]
        for face in output_faces(finger, data, a_side_direction):
            for label, xyz in zip(face['names'], face['corners']):
                key = finger+label
                if key in points and v.norm(v.sub(points[key],xyz)) > 1e-8:
                    raise ValueError('共有する境界点の座標が一致しません：'+key)
                points[key] = xyz
    for finger in 'ABC':
        points.update(quarter_l1_points(finger,finger_data[finger],a_side_direction))
    from . import grip_reference_fx6
    for finger in 'CD':
        points[finger+"H5'"]=grip_reference_fx6.tip_point(finger,finger_data[finger],a_side_direction)
    from . import grip_reference_bezier
    points["AG2'"] = grip_reference_bezier.curve_data(finger_data['A'])['control_points_mm'][2]
    definitions = [("AG2'",'AF2','AH2'), ('BF2','BH2',"BH1'","BF1'"),
                   ('AH2','BH2','BH3','AH3'),
                   ("BG1'",'AH1','AH2','BH2'),
                   ('AH3',"AH4'","BH4'",'BH3'),
                   ('CF2','DH2','DH3','CF3'),
                   ('CF3','DH3','DH4','CF4'),
                   ('CF4','DH4',"DH5'",'CF5'),
                   ('CF5',"CH5'","DH5'"),
                   ('CF3','CF2','DH2'),
                   ('BF3','BF2','CH2','CH3'),
                   ('DH2','DF2','DG1'),
                   ('CF2','CH2',"CH1'","CF1'")]
    result = []
    for index, names in enumerate(definitions, 1):
        corners = [points[name] for name in names]
        area = None
        if len(corners) == 3:
            area = v.norm(v.cross(v.sub(corners[1],corners[0]),v.sub(corners[2],corners[0])))/2
            if area < 1e-8: raise ValueError('接続三角形の面積がありません。')
        result.append(dict(identifier='Con{}'.format(index), names=names, corners=corners, area_mm2=area))
    return result


def create_connections(root, finger_data, a_side_direction):
    bodies = []
    for item in connection_faces(finger_data, a_side_direction):
        if item['identifier'] in SUSPENDED_CONNECTION_FACES:
            continue
        name = 'グリップ接続面：'+item['identifier']+'：'+'–'.join(item['names'])
        body = create_patch(root,name,item['corners'],item['names'],item['area_mm2'])
        body.attributes.add('grip_connection_face','id',item['identifier'])
        bodies.append(body)
    return bodies
