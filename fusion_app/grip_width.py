"""Finger ribbons with shared midpoint boundaries at the twist joint."""
import math
from . import grip_twist as v


def rectangles(points, a_side_direction, width=10.0, joint_index=2):
    if not math.isfinite(width) or width <= 0:
        raise ValueError('指幅は正の有限値を指定してください。')
    if joint_index not in (2, 3):
        raise ValueError('幅面の切替関節はG2またはG3を指定してください。')
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



def connected_faces(points, a_side_direction, width=10.0, joint_index=2):
    faces = rectangles(points, a_side_direction, width, joint_index)
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



# Removed by the user: all L0/L1 faces, A/B L4, and B L3. Keep full geometry
# calculation above so shared G2 midpoint coordinates do not change.
EXCLUDED_SEGMENTS = {
    'A': frozenset((0, 1, 4)),
    'B': frozenset((0, 1, 3, 4)),
    'C': frozenset((0, 1)),
    'D': frozenset((0, 1)),
}


def output_faces(finger, data, a_side_direction, width=10.0):
    faces = connected_faces(data['points_mm'], a_side_direction, width,
                            data.get('twist_joint_index', 2))
    if finger == 'A':
        face = faces[3]
        a, b, c, d = face['corners']
        # Keep the G3 edge (a,d), shared with L2; trim only the G4 end.
        face['corners'] = [a, v.add(a, v.mul(v.sub(b,a),0.25)),
                           v.add(d, v.mul(v.sub(c,d),0.25)), d]
        face['area_mm2'] *= 0.25
        face['length_fraction'] = 0.25
        for i in (1,2):
            face['names'][i] += "'"
    return [face for face in faces if face['index'] not in EXCLUDED_SEGMENTS[finger]]


def create(root, finger, data, a_side_direction, width=10.0):
    import adsk.core
    import adsk.fusion
    from . import helpers
    bodies=[]
    for item in output_faces(finger, data, a_side_direction, width):
        name='グリップ幅面：{}L{}：幅{:g}mm'.format(finger,item['index'],width)
        if item.get('midpoint_boundary'):
            name += '：G{}中点接続'.format(data.get('twist_joint_index',2))
        if item.get('length_fraction') == 0.25:
            name += '：G3側1／4'
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


def connection_faces(finger_data, a_side_direction):
    points = {}
    for finger in ('A', 'B', 'C', 'D'):
        data = finger_data[finger]
        if finger in ('A', 'B'):
            points[finger+"G1'"] = data['guideline_points_mm'][1]
        for face in output_faces(finger, data, a_side_direction):
            for label, xyz in zip(face['names'], face['corners']):
                key = finger+label
                if key in points and v.norm(v.sub(points[key],xyz)) > 1e-8:
                    raise ValueError('共有する境界点の座標が一致しません：'+key)
                points[key] = xyz
    definitions = [("AG1'", 'AF2', 'AH2'), ("BG1'", 'BF2', 'BH2'),
                   ('AH2','BH2','BH3','AH3'),
                   ("AG1'","BG1'",'BH2','AH2'),
                   ('AH3',"AH4'",'BH3'),
                   ('CF2','DH2','DH3','CF3'),
                   ('CF3','DH3','DH4','CF4'),
                   ('CF4','DH4','DH5','CF5'),
                   ('CH5','CF5','DH5'),
                   ('CF3','CF2','DH2')]
    result = []
    for names in definitions:
        corners = [points[name] for name in names]
        area = None
        if len(corners) == 3:
            area = v.norm(v.cross(v.sub(corners[1],corners[0]),v.sub(corners[2],corners[0])))/2
            if area < 1e-8: raise ValueError('接続三角形の面積がありません。')
        result.append(dict(names=names, corners=corners, area_mm2=area))
    return result


def create_connections(root, finger_data, a_side_direction):
    bodies = []
    for item in connection_faces(finger_data, a_side_direction):
        name = 'グリップ接続面：'+'–'.join(item['names'])
        bodies.append(create_patch(root,name,item['corners'],item['names'],item['area_mm2']))
    return bodies
