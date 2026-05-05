import adsk.core
import adsk.fusion
import traceback
import math
import os
import sys

def create_base_sketch(root_comp):
    rect_left = 7.5
    rect_front = 3.0
    rect_back = 3.0
    top_start_from_y_axis = 2.5
    top_slope_angle_deg = 4.23

    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = '底面内部'

    lines = sketch.sketchCurves.sketchLines

    x_right = 0.0
    x_left = -rect_left
    y_front = -rect_front
    y_back = rect_back

    slope_start_x = -top_start_from_y_axis
    slope_start_y = y_back
    slope_dx = abs(x_left - slope_start_x)
    slope_drop = math.tan(math.radians(top_slope_angle_deg)) * slope_dx
    slope_end_y = y_back - slope_drop

    point_1 = adsk.core.Point3D.create(x_right, y_front, 0)
    point_2 = adsk.core.Point3D.create(x_left, y_front, 0)
    point_3 = adsk.core.Point3D.create(x_left, slope_end_y, 0)
    point_4 = adsk.core.Point3D.create(slope_start_x, slope_start_y, 0)
    point_5 = adsk.core.Point3D.create(x_right, y_back, 0)

    lines.addByTwoPoints(point_1, point_2)
    lines.addByTwoPoints(point_2, point_3)
    lines.addByTwoPoints(point_3, point_4)
    lines.addByTwoPoints(point_4, point_5)
    lines.addByTwoPoints(point_5, point_1)

    return sketch


def extrude_profile(root_comp, profile, distance_cm, direction, operation):
    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(profile, operation)

    distance_value = adsk.core.ValueInput.createByReal(distance_cm)
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction
    )

    return extrudes.add(extrude_input)


def extrude_profiles(root_comp, profiles, distance_cm, direction, operation):
    profile_collection = adsk.core.ObjectCollection.create()
    for profile in profiles:
        profile_collection.add(profile)

    if profile_collection.count == 0:
        raise RuntimeError('押し出し対象のプロファイルを取得できませんでした。')

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(profile_collection, operation)

    distance_value = adsk.core.ValueInput.createByReal(distance_cm)
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction
    )

    return extrudes.add(extrude_input)


def get_smallest_profile(sketch):
    smallest_profile = None
    smallest_area = None

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        area = profile.areaProperties().area
        if smallest_area is None or area < smallest_area:
            smallest_area = area
            smallest_profile = profile

    if not smallest_profile:
        raise RuntimeError('スケッチから三角形プロファイルを取得できませんでした。')

    return smallest_profile


def add_named_attribute(entity, name):
    existing = entity.attributes.itemByName('fusion_scripts', 'name')
    if existing:
        existing.deleteMe()
    entity.attributes.add('fusion_scripts', 'name', name)


def to_sketch_space(sketch, x, y, z):
    model_point = adsk.core.Point3D.create(x, y, z)
    return sketch.modelToSketchSpace(model_point)


def create_split_triangle_on_face(root_comp, face, helpers):
    split_sketch = helpers.create_sketch_on_face(root_comp, face, '分割断面')
    add_named_attribute(face, '分割断面')
    helpers.project_face_edges(split_sketch, face)

    lines = split_sketch.sketchCurves.sketchLines

    start_point = to_sketch_space(split_sketch, 0.0, 3.0, 0.0)
    axis_bottom_point = to_sketch_space(split_sketch, 0.0, -3.0, 0.0)

    delta_y = 6.0
    delta_z = math.tan(math.radians(2.69)) * delta_y
    top_point = to_sketch_space(split_sketch, 0.0, -3.0, delta_z)

    lines.addByTwoPoints(start_point, top_point)
    lines.addByTwoPoints(axis_bottom_point, top_point)
    lines.addByTwoPoints(axis_bottom_point, start_point)

    return split_sketch


def create_upper_stop_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.yZConstructionPlane)
    sketch.name = '上部止部'

    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    # Outer start reference (0.00, 30.00, -3.00) mm -> (0.00, 3.00, -0.30) cm.
    base_y = 3.0
    base_z = -0.3
    outer_radius_cm = 0.9
    inner_radius_cm = 0.615
    # Keep the top wall vertical so the upper tip does not form a triangular spur.
    top_width_cm = outer_radius_cm - inner_radius_cm
    top_height_cm = 0.996
    inner_start_z = 0.0

    top_left = to_sketch_space(sketch, 0.0, base_y + outer_radius_cm - top_width_cm, base_z + top_height_cm)
    top_right = to_sketch_space(sketch, 0.0, base_y + outer_radius_cm, base_z + top_height_cm)
    outer_right = to_sketch_space(sketch, 0.0, base_y + outer_radius_cm, base_z + outer_radius_cm)
    outer_bottom = to_sketch_space(sketch, 0.0, base_y, base_z)
    inner_bottom = to_sketch_space(sketch, 0.0, base_y, inner_start_z)
    inner_right = to_sketch_space(sketch, 0.0, base_y + inner_radius_cm, inner_start_z + inner_radius_cm)

    outer_mid = to_sketch_space(
        sketch,
        0.0,
        base_y + (outer_radius_cm / math.sqrt(2.0)),
        base_z + outer_radius_cm - (outer_radius_cm / math.sqrt(2.0))
    )
    inner_mid = to_sketch_space(
        sketch,
        0.0,
        base_y + (inner_radius_cm / math.sqrt(2.0)),
        inner_start_z + inner_radius_cm - (inner_radius_cm / math.sqrt(2.0))
    )

    lines.addByTwoPoints(top_left, top_right)
    lines.addByTwoPoints(top_right, outer_right)
    arcs.addByThreePoints(outer_right, outer_mid, outer_bottom)
    lines.addByTwoPoints(outer_bottom, inner_bottom)
    arcs.addByThreePoints(inner_bottom, inner_mid, inner_right)
    lines.addByTwoPoints(inner_right, top_left)

    return sketch


def create_lower_stop_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.yZConstructionPlane)
    sketch.name = '下部止部'

    lines = sketch.sketchCurves.sketchLines

    top_left = to_sketch_space(sketch, 0.0, -3.0, 0.7)
    top_right = to_sketch_space(sketch, 0.0, -2.0, 0.7)
    bottom_right = to_sketch_space(sketch, 0.0, -2.0, 0.0)
    bottom_left = to_sketch_space(sketch, 0.0, -3.0, 0.0)

    lines.addByTwoPoints(top_left, top_right)
    lines.addByTwoPoints(top_right, bottom_right)
    lines.addByTwoPoints(bottom_right, bottom_left)
    lines.addByTwoPoints(bottom_left, top_left)

    return sketch


def create_outer_shell_cut_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.yZConstructionPlane)
    sketch.name = '内殻外部_仕様案1'

    lines = sketch.sketchCurves.sketchLines

    top_left = to_sketch_space(sketch, 0.0, -3.0, 0.7)
    top_right = to_sketch_space(sketch, 0.0, -2.3, 0.7)
    bottom_right = to_sketch_space(sketch, 0.0, -2.3, -0.3)
    bottom_left = to_sketch_space(sketch, 0.0, -3.0, -0.3)

    lines.addByTwoPoints(top_left, top_right)
    lines.addByTwoPoints(top_right, bottom_right)
    lines.addByTwoPoints(bottom_right, bottom_left)
    lines.addByTwoPoints(bottom_left, top_left)

    return sketch


def create_joystick_receiver_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = 'ジョイステック受け'

    center_point = adsk.core.Point3D.create(-2.1, -1.0, 0.0)
    sketch_center_point = sketch.sketchPoints.add(center_point)
    add_named_attribute(sketch_center_point, 'ジョイスティック受け基準点')

    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(center_point, 1.5)

    return sketch


def create_inner_shell_outer_perimeter_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = '内殻外周'

    circles = sketch.sketchCurves.sketchCircles
    lines = sketch.sketchCurves.sketchLines

    first_center_point = adsk.core.Point3D.create(-2.1, -1.0, 0.0)
    second_center_point = adsk.core.Point3D.create(-4.2, 0.5, 0.0)
    lower_intersection_point = adsk.core.Point3D.create(-2.8579259696487043, -2.294429690841519, 0.0)
    target_point = adsk.core.Point3D.create(-2.9842, -2.5679, 0.0)

    circles.addByCenterRadius(first_center_point, 1.5)
    circles.addByCenterRadius(second_center_point, 3.1)
    lines.addByTwoPoints(lower_intersection_point, target_point)

    return sketch


def create_outer_shell_option2_preview_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = '内殻外部_仕様案2_確認用'

    circles = sketch.sketchCurves.sketchCircles

    first_center_point = adsk.core.Point3D.create(-2.1, -1.0, 0.0)
    second_center_point = adsk.core.Point3D.create(-4.2, 0.5, 0.0)

    circles.addByCenterRadius(first_center_point, 1.8)
    circles.addByCenterRadius(second_center_point, 3.3)

    return sketch


def create_outer_shell_option2_cut_sketch(root_comp, face, helpers):
    sketch = helpers.create_sketch_on_face(root_comp, face, '内殻外部_仕様案2')
    helpers.project_face_edges(sketch, face)

    circles = sketch.sketchCurves.sketchCircles

    first_center_point = to_sketch_space(sketch, -2.1, -1.0, 0.0)
    second_center_point = to_sketch_space(sketch, -4.2, 0.5, 0.0)

    circles.addByCenterRadius(first_center_point, 1.8)
    circles.addByCenterRadius(second_center_point, 3.3)

    return sketch


def get_profiles_nearest_points(sketch, target_points):
    selected_profiles = []
    selected_tokens = set()

    for target_x, target_y in target_points:
        nearest_profile = None
        nearest_distance = None

        for index in range(sketch.profiles.count):
            profile = sketch.profiles.item(index)
            centroid = profile.areaProperties().centroid
            distance = math.hypot(centroid.x - target_x, centroid.y - target_y)

            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_profile = profile

        if not nearest_profile:
            raise RuntimeError('内殻外部の仕様案2用プロファイルを取得できませんでした。')

        profile_token = nearest_profile.entityToken
        if profile_token in selected_tokens:
            raise RuntimeError('内殻外部の仕様案2用プロファイルが2領域に分かれていませんでした。')

        selected_tokens.add(profile_token)
        selected_profiles.append(nearest_profile)

    return selected_profiles


def find_highest_xy_face(body, tolerance=1e-6):
    highest_face = None
    highest_z = None

    for face in body.faces:
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > tolerance or abs(normal.y) > tolerance:
            continue

        face_max_z = face.boundingBox.maxPoint.z
        if highest_z is None or face_max_z > highest_z:
            highest_z = face_max_z
            highest_face = face

    if not highest_face:
        raise RuntimeError('上部止部の最上位 XY 面を取得できませんでした。')

    return highest_face


def find_bottom_slope_face(body, tolerance=1e-6):
    matching_faces = []

    for face in body.faces:
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > tolerance:
            continue

        if abs(normal.y) <= tolerance or abs(normal.z) <= tolerance:
            continue

        box = face.boundingBox
        if (
            box.minPoint.x < -1.0 - tolerance
            or box.maxPoint.x > tolerance
            or box.maxPoint.z <= tolerance
        ):
            continue

        matching_faces.append(face)

    if not matching_faces:
        raise RuntimeError('底面斜面を取得できませんでした。')

    return max(matching_faces, key=lambda face: face.area)


def find_face_by_named_attribute(body, name):
    for face in body.faces:
        attribute = face.attributes.itemByName('fusion_scripts', 'name')
        if attribute and attribute.value == name:
            return face
    raise RuntimeError('指定された名前の面を取得できませんでした。')


def find_shared_linear_edge(face_a, face_b):
    for edge_a in face_a.edges:
        for edge_b in face_b.edges:
            if edge_a.entityToken != edge_b.entityToken:
                continue

            geometry = adsk.core.Line3D.cast(edge_a.geometry)
            if geometry:
                return edge_a

    raise RuntimeError('下部止部のフィレット対象エッジを取得できませんでした。')


def apply_constant_radius_fillet(root_comp, edge, radius_cm):
    fillets = root_comp.features.filletFeatures
    fillet_input = fillets.createInput()
    edge_collection = adsk.core.ObjectCollection.create()
    edge_collection.add(edge)

    radius_value = adsk.core.ValueInput.createByReal(radius_cm)
    fillet_input.addConstantRadiusEdgeSet(edge_collection, radius_value, True)

    return fillets.add(fillet_input)


def is_xy_plane_face(face, tolerance=1e-6):
    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        return False

    normal = geometry.normal
    return abs(normal.x) <= tolerance and abs(normal.y) <= tolerance


def find_lower_stop_top_face(body, tolerance=1e-6):
    matching_faces = []

    for face in body.faces:
        if not is_xy_plane_face(face, tolerance):
            continue

        box = face.boundingBox
        if (
            abs(box.minPoint.z - 0.7) <= tolerance
            and abs(box.maxPoint.z - 0.7) <= tolerance
            and box.minPoint.y <= -3.0 + tolerance
            and box.maxPoint.y >= -2.0 - tolerance
        ):
            matching_faces.append(face)

    if not matching_faces:
        raise RuntimeError('下部止部平面を取得できませんでした。')

    return max(matching_faces, key=lambda face: face.boundingBox.maxPoint.x - face.boundingBox.minPoint.x)


def load_fusion_helpers():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.join(script_dir, 'core')

    if core_dir not in sys.path:
        sys.path.append(core_dir)

    import fusion_helpers

    return fusion_helpers


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Fusion Design workspace is not active.')

        helpers = load_fusion_helpers()

        root_comp = design.rootComponent

        base_sketch = create_base_sketch(root_comp)
        create_inner_shell_outer_perimeter_sketch(root_comp)
        base_profile = helpers.get_largest_profile(base_sketch)
        base_feature = extrude_profile(
            root_comp,
            base_profile,
            0.3,
            adsk.fusion.ExtentDirections.NegativeExtentDirection,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )

        body = helpers.get_body_from_feature(base_feature)
        split_face = helpers.find_face_by_axis_value(body, 'x', 0.0)
        split_sketch = create_split_triangle_on_face(root_comp, split_face, helpers)
        split_profile = get_smallest_profile(split_sketch)

        extrude_profile(
            root_comp,
            split_profile,
            1.0,
            adsk.fusion.ExtentDirections.NegativeExtentDirection,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        bottom_slope_face = find_bottom_slope_face(body)
        add_named_attribute(bottom_slope_face, '底面斜面')

        top_face = helpers.find_face_by_axis_value(body, 'z', 0.0)
        outer_shell_option2_sketch = create_outer_shell_option2_cut_sketch(root_comp, top_face, helpers)
        outer_shell_option2_profiles = get_profiles_nearest_points(
            outer_shell_option2_sketch,
            [(-7.5, 2.6), (-7.5, -3.0)]
        )
        extrude_profiles(
            root_comp,
            outer_shell_option2_profiles,
            1.0,
            adsk.fusion.ExtentDirections.NegativeExtentDirection,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )

        upper_stop_sketch = create_upper_stop_sketch(root_comp)
        upper_stop_profile = helpers.get_largest_profile(upper_stop_sketch)
        upper_stop_feature = extrude_profile(
            root_comp,
            upper_stop_profile,
            2.5,
            adsk.fusion.ExtentDirections.NegativeExtentDirection,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        upper_stop_body = helpers.get_body_from_feature(upper_stop_feature)
        add_named_attribute(upper_stop_body, '上部止部')

        highest_xy_face = find_highest_xy_face(upper_stop_body)
        extrude_profile(
            root_comp,
            highest_xy_face,
            0.3,
            adsk.fusion.ExtentDirections.PositiveExtentDirection,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )

        lower_stop_sketch = create_lower_stop_sketch(root_comp)
        lower_stop_profile = helpers.get_largest_profile(lower_stop_sketch)
        extrude_profile(
            root_comp,
            lower_stop_profile,
            1.0,
            adsk.fusion.ExtentDirections.NegativeExtentDirection,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )

        body = root_comp.bRepBodies.item(0)
        bottom_slope_face = find_face_by_named_attribute(body, '底面斜面')
        lower_stop_face = helpers.find_face_by_axis_value(body, 'y', -2.0)
        lower_stop_fillet_edge = find_shared_linear_edge(bottom_slope_face, lower_stop_face)
        apply_constant_radius_fillet(root_comp, lower_stop_fillet_edge, 0.5)

        body = root_comp.bRepBodies.item(0)
        lower_stop_top_face = find_lower_stop_top_face(body)
        add_named_attribute(lower_stop_top_face, '下部止部平面')

        joystick_receiver_sketch = create_joystick_receiver_sketch(root_comp)
        joystick_receiver_profile = helpers.get_largest_profile(joystick_receiver_sketch)
        extrude_profile(
            root_comp,
            joystick_receiver_profile,
            1.0,
            adsk.fusion.ExtentDirections.PositiveExtentDirection,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )

        outer_shell_cut_sketch = create_outer_shell_cut_sketch(root_comp)
        outer_shell_cut_profile = helpers.get_largest_profile(outer_shell_cut_sketch)
        extrude_profile(
            root_comp,
            outer_shell_cut_profile,
            1.0,
            adsk.fusion.ExtentDirections.NegativeExtentDirection,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
