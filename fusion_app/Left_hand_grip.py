import adsk.core
import adsk.fusion
import traceback
import math
import os
import sys

INNER_SHELL_LID_POINT_REFS_MM = {
    'A': (-66.67, -26.918, 25.782),
    'B': (-29.842, -25.976, 21.411),
    'C': (-28.579, -22.944, 21.638),
    'D': (-63.701, -27.138, 25.8),
    'F': (-62.178, -22.954, 25.452),
    'G': (-32.059, -20.122, 21.873),
}


def mm_to_cm(value_mm):
    return value_mm / 10.0


def create_model_point_from_mm(x_mm, y_mm, z_mm):
    return adsk.core.Point3D.create(mm_to_cm(x_mm), mm_to_cm(y_mm), mm_to_cm(z_mm))


INNER_SHELL_LID_POINT_REFS = {
    name: create_model_point_from_mm(*coords_mm)
    for name, coords_mm in INNER_SHELL_LID_POINT_REFS_MM.items()
}


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


def create_inner_shell_lid_slope_cut_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.yZConstructionPlane)
    sketch.name = '内殻蓋部斜面作成'

    lines = sketch.sketchCurves.sketchLines

    top_point = to_sketch_space(sketch, 0.0, 2.7138, 2.58)
    bottom_point = to_sketch_space(sketch, 0.0, -4.0, 2.58)

    delta_y = 2.7138 - (-4.0)
    delta_z = math.tan(math.radians(4.75)) * delta_y
    slope_end_point = to_sketch_space(sketch, 0.0, -4.0, 2.58 - delta_z)

    lines.addByTwoPoints(top_point, bottom_point)
    lines.addByTwoPoints(bottom_point, slope_end_point)
    lines.addByTwoPoints(slope_end_point, top_point)

    return sketch


def get_face_edges(face):
    return [face.edges.item(index) for index in range(face.edges.count)]


def get_edge_endpoints(edge):
    return [edge.startVertex.geometry, edge.endVertex.geometry]


def get_point_distance(point_a, point_b):
    return math.sqrt(
        ((point_a.x - point_b.x) ** 2)
        + ((point_a.y - point_b.y) ** 2)
        + ((point_a.z - point_b.z) ** 2)
    )


def get_nearest_distance_to_edge(edge, target_point, sample_count=80):
    evaluator = edge.evaluator
    success, start_param, end_param = evaluator.getParameterExtents()
    if not success:
        raise RuntimeError('辺のパラメータ範囲を取得できませんでした。')

    parameters = [
        start_param + ((end_param - start_param) * index / sample_count)
        for index in range(sample_count + 1)
    ]
    success, sampled_points = evaluator.getPointsAtParameters(parameters)
    if not success:
        raise RuntimeError('辺上のサンプル点を取得できませんでした。')

    return min(get_point_distance(point, target_point) for point in sampled_points)


def find_non_linear_edge_near_points(face, reference_points, excluded_tokens=None):
    excluded_tokens = excluded_tokens or set()
    candidate_edge = None
    candidate_score = None

    for edge in get_face_edges(face):
        if edge.entityToken in excluded_tokens:
            continue
        if adsk.core.Line3D.cast(edge.geometry):
            continue

        score = sum(get_nearest_distance_to_edge(edge, point) for point in reference_points)
        if candidate_score is None or score < candidate_score:
            candidate_score = score
            candidate_edge = edge

    if not candidate_edge:
        raise RuntimeError('内殻蓋部用の円弧エッジを取得できませんでした。')

    return candidate_edge


def find_linear_edge_near_points(face, reference_points, excluded_tokens=None):
    excluded_tokens = excluded_tokens or set()
    candidate_edge = None
    candidate_score = None

    for edge in get_face_edges(face):
        if edge.entityToken in excluded_tokens:
            continue
        if not adsk.core.Line3D.cast(edge.geometry):
            continue

        score = sum(get_nearest_distance_to_edge(edge, point) for point in reference_points)
        if candidate_score is None or score < candidate_score:
            candidate_score = score
            candidate_edge = edge

    if not candidate_edge:
        raise RuntimeError('内殻蓋部用の直線エッジを取得できませんでした。')

    return candidate_edge


def find_connected_linear_edge(face, anchor_point, target_point, excluded_tokens=None, tolerance=1e-4):
    excluded_tokens = excluded_tokens or set()
    candidate_edge = None
    candidate_score = None

    for edge in get_face_edges(face):
        if edge.entityToken in excluded_tokens:
            continue
        if not adsk.core.Line3D.cast(edge.geometry):
            continue

        edge_points = get_edge_endpoints(edge)
        first_distance = get_point_distance(edge_points[0], anchor_point)
        second_distance = get_point_distance(edge_points[1], anchor_point)

        if first_distance <= tolerance:
            other_point = edge_points[1]
        elif second_distance <= tolerance:
            other_point = edge_points[0]
        else:
            continue

        score = get_point_distance(other_point, target_point)
        if candidate_score is None or score < candidate_score:
            candidate_score = score
            candidate_edge = edge

    if not candidate_edge:
        raise RuntimeError('内殻蓋部用の接続直線エッジを取得できませんでした。')

    return candidate_edge


def assign_named_points_to_edge_endpoints(edge, point_names):
    edge_points = get_edge_endpoints(edge)
    first_pair_score = (
        get_point_distance(edge_points[0], INNER_SHELL_LID_POINT_REFS[point_names[0]])
        + get_point_distance(edge_points[1], INNER_SHELL_LID_POINT_REFS[point_names[1]])
    )
    swapped_pair_score = (
        get_point_distance(edge_points[0], INNER_SHELL_LID_POINT_REFS[point_names[1]])
        + get_point_distance(edge_points[1], INNER_SHELL_LID_POINT_REFS[point_names[0]])
    )

    if first_pair_score <= swapped_pair_score:
        return {
            point_names[0]: edge_points[0],
            point_names[1]: edge_points[1],
        }

    return {
        point_names[0]: edge_points[1],
        point_names[1]: edge_points[0],
    }


def get_other_endpoint_for_named_point(edge, anchor_point, anchor_name, other_name):
    edge_points = get_edge_endpoints(edge)
    first_distance = get_point_distance(edge_points[0], anchor_point)
    second_distance = get_point_distance(edge_points[1], anchor_point)

    if first_distance <= second_distance:
        return {
            anchor_name: edge_points[0],
            other_name: edge_points[1],
        }

    return {
        anchor_name: edge_points[1],
        other_name: edge_points[0],
    }


def project_face_edges_by_token(sketch, face):
    projected_by_token = {}

    for edge in get_face_edges(face):
        projected_items = sketch.project(edge)
        projected_by_token[edge.entityToken] = [
            projected_items.item(index)
            for index in range(projected_items.count)
        ]

    return projected_by_token


def get_first_sketch_curve(entities, error_message):
    for entity in entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(entity)
        if sketch_curve:
            return sketch_curve
    raise RuntimeError(error_message)


def get_profile_nearest_sketch_point(sketch, target_point):
    nearest_profile = None
    nearest_distance = None

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        centroid = profile.areaProperties().centroid
        distance = math.hypot(centroid.x - target_point.x, centroid.y - target_point.y)

        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_profile = profile

    if not nearest_profile:
        raise RuntimeError('内殻蓋部のプロファイルを取得できませんでした。')

    return nearest_profile


def get_profiles_nearest_sketch_points(sketch, target_points):
    selected_profiles = []
    selected_tokens = set()

    for target_point in target_points:
        ranked_profiles = []

        for index in range(sketch.profiles.count):
            profile = sketch.profiles.item(index)
            centroid = profile.areaProperties().centroid
            distance = math.hypot(centroid.x - target_point.x, centroid.y - target_point.y)
            ranked_profiles.append((distance, profile))

        ranked_profiles.sort(key=lambda item: item[0])

        nearest_profile = None
        for _, profile in ranked_profiles:
            if profile.entityToken not in selected_tokens:
                nearest_profile = profile
                break

        if not nearest_profile:
            raise RuntimeError('内殻蓋部のプロファイルを取得できませんでした。')

        profile_token = nearest_profile.entityToken
        selected_tokens.add(profile_token)
        selected_profiles.append(nearest_profile)

    return selected_profiles


def get_sketch_curve_midpoint(sketch_curve):
    box = sketch_curve.boundingBox
    if box:
        return adsk.core.Point3D.create(
            (box.minPoint.x + box.maxPoint.x) / 2.0,
            (box.minPoint.y + box.maxPoint.y) / 2.0,
            0.0,
        )

    return adsk.core.Point3D.create(
        (sketch_curve.startSketchPoint.geometry.x + sketch_curve.endSketchPoint.geometry.x) / 2.0,
        (sketch_curve.startSketchPoint.geometry.y + sketch_curve.endSketchPoint.geometry.y) / 2.0,
        0.0,
    )


def assign_named_sketch_points_to_curve_endpoints(sketch_curve, point_names, reference_points):
    curve_points = [
        sketch_curve.startSketchPoint.geometry,
        sketch_curve.endSketchPoint.geometry,
    ]
    first_pair_score = (
        math.hypot(curve_points[0].x - reference_points[point_names[0]].x, curve_points[0].y - reference_points[point_names[0]].y)
        + math.hypot(curve_points[1].x - reference_points[point_names[1]].x, curve_points[1].y - reference_points[point_names[1]].y)
    )
    swapped_pair_score = (
        math.hypot(curve_points[0].x - reference_points[point_names[1]].x, curve_points[0].y - reference_points[point_names[1]].y)
        + math.hypot(curve_points[1].x - reference_points[point_names[0]].x, curve_points[1].y - reference_points[point_names[0]].y)
    )

    if first_pair_score <= swapped_pair_score:
        return {
            point_names[0]: curve_points[0],
            point_names[1]: curve_points[1],
        }

    return {
        point_names[0]: curve_points[1],
        point_names[1]: curve_points[0],
    }


def get_other_sketch_endpoint_for_named_point(sketch_curve, anchor_point, anchor_name, other_name):
    curve_points = [
        sketch_curve.startSketchPoint.geometry,
        sketch_curve.endSketchPoint.geometry,
    ]
    first_distance = math.hypot(curve_points[0].x - anchor_point.x, curve_points[0].y - anchor_point.y)
    second_distance = math.hypot(curve_points[1].x - anchor_point.x, curve_points[1].y - anchor_point.y)

    if first_distance <= second_distance:
        return {
            anchor_name: curve_points[0],
            other_name: curve_points[1],
        }

    return {
        anchor_name: curve_points[1],
        other_name: curve_points[0],
    }


def create_inner_shell_lid_face_sketch(root_comp, slope_face):
    sketch = root_comp.sketches.addWithoutEdges(slope_face)
    sketch.name = '内殻蓋部'

    ab_edge = find_non_linear_edge_near_points(
        slope_face,
        [INNER_SHELL_LID_POINT_REFS['A'], INNER_SHELL_LID_POINT_REFS['B']]
    )
    cd_edge = find_non_linear_edge_near_points(
        slope_face,
        [INNER_SHELL_LID_POINT_REFS['C'], INNER_SHELL_LID_POINT_REFS['D']],
        excluded_tokens={ab_edge.entityToken}
    )

    named_points = {}
    named_points.update(assign_named_points_to_edge_endpoints(ab_edge, ('A', 'B')))
    ad_edge = find_connected_linear_edge(
        slope_face,
        named_points['A'],
        INNER_SHELL_LID_POINT_REFS['D']
    )
    bc_edge = find_connected_linear_edge(
        slope_face,
        named_points['B'],
        INNER_SHELL_LID_POINT_REFS['C'],
        excluded_tokens={ad_edge.entityToken}
    )
    named_points.update(get_other_endpoint_for_named_point(ad_edge, named_points['A'], 'A', 'D'))
    named_points.update(get_other_endpoint_for_named_point(bc_edge, named_points['B'], 'B', 'C'))

    projected_by_token = project_face_edges_by_token(sketch, slope_face)
    ab_curve = get_first_sketch_curve(
        projected_by_token.get(ab_edge.entityToken, []),
        'AB円弧の投影に失敗しました。'
    )
    ad_curve = get_first_sketch_curve(
        projected_by_token.get(ad_edge.entityToken, []),
        'AD線の投影に失敗しました。'
    )
    bc_curve = get_first_sketch_curve(
        projected_by_token.get(bc_edge.entityToken, []),
        'BC線の投影に失敗しました。'
    )
    cd_curve = get_first_sketch_curve(
        projected_by_token.get(cd_edge.entityToken, []),
        'CD円弧の投影に失敗しました。'
    )

    sketch_reference_points = {
        name: sketch.modelToSketchSpace(point)
        for name, point in INNER_SHELL_LID_POINT_REFS.items()
    }

    named_sketch_points = {}
    named_sketch_points.update(assign_named_sketch_points_to_curve_endpoints(ab_curve, ('A', 'B'), sketch_reference_points))
    named_sketch_points.update(get_other_sketch_endpoint_for_named_point(ad_curve, named_sketch_points['A'], 'A', 'D'))
    named_sketch_points.update(get_other_sketch_endpoint_for_named_point(bc_curve, named_sketch_points['B'], 'B', 'C'))
    named_sketch_points.update(assign_named_sketch_points_to_curve_endpoints(cd_curve, ('D', 'C'), named_sketch_points))

    outer_curve_collection = adsk.core.ObjectCollection.create()
    outer_curve_collection.add(ab_curve)
    inner_direction_point = adsk.core.Point3D.create(
        (named_sketch_points['C'].x + named_sketch_points['D'].x) / 2.0,
        (named_sketch_points['C'].y + named_sketch_points['D'].y) / 2.0,
        0.0,
    )
    offset_curves = sketch.offset(outer_curve_collection, inner_direction_point, 0.6)
    e_curve = get_first_sketch_curve(
        [offset_curves.item(index) for index in range(offset_curves.count)],
        'E円弧の作成に失敗しました。'
    )

    e_endpoints = [e_curve.startSketchPoint.geometry, e_curve.endSketchPoint.geometry]
    direct_score = (
        math.hypot(e_endpoints[0].x - named_sketch_points['D'].x, e_endpoints[0].y - named_sketch_points['D'].y)
        + math.hypot(e_endpoints[1].x - named_sketch_points['C'].x, e_endpoints[1].y - named_sketch_points['C'].y)
    )
    swapped_score = (
        math.hypot(e_endpoints[0].x - named_sketch_points['C'].x, e_endpoints[0].y - named_sketch_points['C'].y)
        + math.hypot(e_endpoints[1].x - named_sketch_points['D'].x, e_endpoints[1].y - named_sketch_points['D'].y)
    )

    if direct_score <= swapped_score:
        f_point = e_curve.startSketchPoint.geometry
        g_point = e_curve.endSketchPoint.geometry
    else:
        f_point = e_curve.endSketchPoint.geometry
        g_point = e_curve.startSketchPoint.geometry

    named_sketch_points['F'] = f_point
    named_sketch_points['G'] = g_point

    lines = sketch.sketchCurves.sketchLines
    df_curve = lines.addByTwoPoints(named_sketch_points['D'], named_sketch_points['F'])
    cg_curve = lines.addByTwoPoints(named_sketch_points['C'], named_sketch_points['G'])

    sketch.sketchCurves.sketchArcs.addFillet(
        e_curve,
        e_curve.startSketchPoint.geometry,
        df_curve,
        df_curve.endSketchPoint.geometry,
        0.2
    )
    sketch.sketchCurves.sketchArcs.addFillet(
        e_curve,
        e_curve.endSketchPoint.geometry,
        cg_curve,
        cg_curve.endSketchPoint.geometry,
        0.2
    )

    ab_midpoint = get_sketch_curve_midpoint(ab_curve)
    e_midpoint = get_sketch_curve_midpoint(e_curve)
    cd_midpoint = get_sketch_curve_midpoint(cd_curve)

    lid_profile_target_point = adsk.core.Point3D.create(
        (ab_midpoint.x + e_midpoint.x) / 2.0,
        (ab_midpoint.y + e_midpoint.y) / 2.0,
        0.0,
    )
    cut_face_profile_target_point = adsk.core.Point3D.create(
        ((e_midpoint.x * 0.35) + (cd_midpoint.x * 0.65)),
        ((e_midpoint.y * 0.35) + (cd_midpoint.y * 0.65)),
        0.0,
    )
    c_shape_profiles = get_profiles_nearest_sketch_points(
        sketch,
        [lid_profile_target_point, cut_face_profile_target_point]
    )

    return {
        'sketch': sketch,
        'profiles': c_shape_profiles,
        'ab_curve': ab_curve,
        'cd_curve': cd_curve,
        'e_curve': e_curve,
        'ad_curve': ad_curve,
        'bc_curve': bc_curve,
        'A': sketch.sketchToModelSpace(named_sketch_points['A']),
        'B': sketch.sketchToModelSpace(named_sketch_points['B']),
        'C': sketch.sketchToModelSpace(named_sketch_points['C']),
        'D': sketch.sketchToModelSpace(named_sketch_points['D']),
        'F': sketch.sketchToModelSpace(named_sketch_points['F']),
        'G': sketch.sketchToModelSpace(named_sketch_points['G']),
    }


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


def create_outer_bottom_semicircle_sketch(root_comp, face, helpers):
    sketch = helpers.create_sketch_on_face(root_comp, face, '止金半円部')
    helpers.project_face_edges(sketch, face)

    center_point = to_sketch_space(
        sketch,
        mm_to_cm(0.0),
        mm_to_cm(5.0),
        mm_to_cm(-3.0),
    )
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, mm_to_cm(14.96))

    return sketch


def create_retainer_outer_fan_sketch(root_comp, face, helpers):
    sketch = helpers.create_sketch_on_face(root_comp, face, '留金部外部 ')

    center_x = mm_to_cm(0.0)
    center_y = mm_to_cm(5.0)
    center_z = mm_to_cm(-8.48)
    radius_cm = mm_to_cm(17.0)

    center_point = to_sketch_space(sketch, center_x, center_y, center_z)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, radius_cm)

    lines = sketch.sketchCurves.sketchLines
    auxiliary_angles_deg = [135.0, 225.0]
    radial_angles_deg = [127.5, 142.5, 217.5, 232.5]

    for angle_deg in auxiliary_angles_deg:
        angle_rad = math.radians(angle_deg)
        target_point = to_sketch_space(
            sketch,
            center_x + (radius_cm * math.cos(angle_rad)),
            center_y + (radius_cm * math.sin(angle_rad)),
            center_z,
        )
        line = lines.addByTwoPoints(center_point, target_point)
        line.isConstruction = True

    for angle_deg in radial_angles_deg:
        angle_rad = math.radians(angle_deg)
        target_point = to_sketch_space(
            sketch,
            center_x + (radius_cm * math.cos(angle_rad)),
            center_y + (radius_cm * math.sin(angle_rad)),
            center_z,
        )
        lines.addByTwoPoints(center_point, target_point)

    return sketch


def get_retainer_outer_fan_profiles(sketch):
    center_x = mm_to_cm(0.0)
    center_y = mm_to_cm(5.0)
    center_z = mm_to_cm(-8.48)
    target_radius_cm = mm_to_cm(8.5)
    target_angles_deg = [135.0, 225.0]

    profiles = []
    selected_tokens = set()

    for angle_deg in target_angles_deg:
        angle_rad = math.radians(angle_deg)
        target_point = to_sketch_space(
            sketch,
            center_x + (target_radius_cm * math.cos(angle_rad)),
            center_y + (target_radius_cm * math.sin(angle_rad)),
            center_z,
        )
        profile = get_profile_nearest_sketch_point(sketch, target_point)
        if profile.entityToken in selected_tokens:
            raise RuntimeError('留金部の扇状プロファイルを2つ取得できませんでした。')

        selected_tokens.add(profile.entityToken)
        profiles.append(profile)

    return profiles


def create_joystick_receiver_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = 'ジョイステック受け'

    center_point = adsk.core.Point3D.create(-2.1, -1.0, 0.0)
    sketch_center_point = sketch.sketchPoints.add(center_point)
    add_named_attribute(sketch_center_point, 'ジョイスティック受け基準点')

    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(center_point, 1.5)

    return sketch


def create_joystick_receiver_outer_perimeter_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = 'ジョイスティック受け外周'

    circles = sketch.sketchCurves.sketchCircles
    lines = sketch.sketchCurves.sketchLines

    center_point = adsk.core.Point3D.create(-2.1, -1.0, 0.0)
    upper_circle_point = adsk.core.Point3D.create(-2.8579, -2.2944, 0.0)
    target_point = adsk.core.Point3D.create(-2.9842, -2.5679, 0.0)
    line_start_point = adsk.core.Point3D.create(-1.0, -2.0, 0.0)
    line_end_point = adsk.core.Point3D.create(-1.0, -3.0, 0.0)

    circles.addByCenterRadius(center_point, 1.5)
    circles.addByCenterRadius(center_point, 1.8)
    lines.addByTwoPoints(upper_circle_point, target_point)
    lines.addByTwoPoints(line_start_point, line_end_point)

    return sketch


def create_inner_shell_outer_perimeter_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = '内殻外周'

    circles = sketch.sketchCurves.sketchCircles
    lines = sketch.sketchCurves.sketchLines

    second_center_point = adsk.core.Point3D.create(-4.2, 0.5, 0.0)
    upper_circle_point = adsk.core.Point3D.create(-2.8579, -2.2944, 0.0)
    target_point = adsk.core.Point3D.create(-2.9842, -2.5679, 0.0)
    line_start_point = adsk.core.Point3D.create(-6.667, 2.6918, 0.0)
    line_end_point = adsk.core.Point3D.create(-2.5, 3.0, 0.0)

    circles.addByCenterRadius(second_center_point, 3.1)
    circles.addByCenterRadius(second_center_point, 3.3)
    lines.addByTwoPoints(upper_circle_point, target_point)
    lines.addByTwoPoints(line_start_point, line_end_point)

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


def find_xy_face_through_point(body, target_point, tolerance=1e-6):
    nearest_face = None
    nearest_score = None

    for face in body.faces:
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > tolerance or abs(normal.y) > tolerance or abs(abs(normal.z) - 1.0) > tolerance:
            continue

        box = face.boundingBox
        if (
            abs(box.minPoint.z - target_point.z) <= tolerance
            and abs(box.maxPoint.z - target_point.z) <= tolerance
            and box.minPoint.x - tolerance <= target_point.x <= box.maxPoint.x + tolerance
            and box.minPoint.y - tolerance <= target_point.y <= box.maxPoint.y + tolerance
        ):
            return face

        x_distance = 0.0
        if target_point.x < box.minPoint.x:
            x_distance = box.minPoint.x - target_point.x
        elif target_point.x > box.maxPoint.x:
            x_distance = target_point.x - box.maxPoint.x

        y_distance = 0.0
        if target_point.y < box.minPoint.y:
            y_distance = box.minPoint.y - target_point.y
        elif target_point.y > box.maxPoint.y:
            y_distance = target_point.y - box.maxPoint.y

        score = x_distance + y_distance + abs(box.maxPoint.z - target_point.z)
        if nearest_score is None or score < nearest_score:
            nearest_score = score
            nearest_face = face

    if nearest_face:
        return nearest_face

    raise RuntimeError('止金半円部用の XY 面を取得できませんでした。')


def find_inner_shell_lid_slope_face(body, tolerance=1e-6):
    matching_faces = []
    target_slope = math.tan(math.radians(4.75))
    slope_tolerance = 0.02

    for face in body.faces:
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > tolerance:
            continue

        if abs(normal.y) <= tolerance or abs(normal.z) <= tolerance:
            continue

        slope = abs(normal.y / normal.z)
        if abs(slope - target_slope) > slope_tolerance:
            continue

        box = face.boundingBox
        if (
            box.maxPoint.x > tolerance
            or box.minPoint.x < -8.0 - tolerance
            or box.maxPoint.z < 2.0 - tolerance
            or box.minPoint.z > 2.58 + tolerance
        ):
            continue

        matching_faces.append(face)

    if not matching_faces:
        raise RuntimeError('内殻蓋部斜面を取得できませんでした。')

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


def find_vertical_linear_edges(edges, tolerance=1e-3):
    matching_edges = []

    for edge in edges:
        geometry = adsk.core.Line3D.cast(edge.geometry)
        if not geometry:
            continue

        start_point = edge.startVertex.geometry
        end_point = edge.endVertex.geometry
        if abs(start_point.x - end_point.x) > tolerance or abs(start_point.y - end_point.y) > tolerance:
            continue

        if abs(start_point.z - end_point.z) <= tolerance:
            continue

        matching_edges.append(edge)

    if not matching_edges:
        raise RuntimeError('留金部の Z 方向エッジを取得できませんでした。')

    return matching_edges


def get_unique_edges_from_faces(faces):
    unique_edges = []
    seen_tokens = set()

    for face in faces:
        for edge in face.edges:
            if edge.entityToken in seen_tokens:
                continue
            seen_tokens.add(edge.entityToken)
            unique_edges.append(edge)

    return unique_edges


def apply_constant_radius_fillet(root_comp, edge, radius_cm, tangent_chain=True):
    fillets = root_comp.features.filletFeatures
    fillet_input = fillets.createInput()
    edge_collection = adsk.core.ObjectCollection.create()
    edge_collection.add(edge)

    radius_value = adsk.core.ValueInput.createByReal(radius_cm)
    fillet_input.addConstantRadiusEdgeSet(edge_collection, radius_value, tangent_chain)

    return fillets.add(fillet_input)


def apply_constant_radius_fillet_to_edges(root_comp, edges, radius_cm, tangent_chain=True):
    fillets = root_comp.features.filletFeatures
    fillet_input = fillets.createInput()
    edge_collection = adsk.core.ObjectCollection.create()

    for edge in edges:
        edge_collection.add(edge)

    radius_value = adsk.core.ValueInput.createByReal(radius_cm)
    fillet_input.addConstantRadiusEdgeSet(edge_collection, radius_value, tangent_chain)

    return fillets.add(fillet_input)


def find_circular_edge_by_center_radius_z(body, center_x, center_y, radius_cm, z_value, tolerance=1e-6):
    for edge in body.edges:
        geometry = edge.geometry
        circle = adsk.core.Circle3D.cast(geometry)
        arc = adsk.core.Arc3D.cast(geometry)

        if circle:
            center = circle.center
            radius = circle.radius
        elif arc:
            center = arc.center
            radius = arc.radius
        else:
            continue

        if (
            abs(center.x - center_x) <= tolerance
            and abs(center.y - center_y) <= tolerance
            and abs(center.z - z_value) <= tolerance
            and abs(radius - radius_cm) <= tolerance
        ):
            return edge

    raise RuntimeError('指定条件に一致する円弧エッジを取得できませんでした。')


def find_arc_edges_by_xy_radius(body, center_x, center_y, radius_cm, tolerance=1e-6):
    matching_edges = []

    for edge in body.edges:
        geometry = edge.geometry
        circle = adsk.core.Circle3D.cast(geometry)
        arc = adsk.core.Arc3D.cast(geometry)

        if circle:
            center = circle.center
            radius = circle.radius
        elif arc:
            center = arc.center
            radius = arc.radius
        else:
            continue

        if (
            abs(center.x - center_x) <= tolerance
            and abs(center.y - center_y) <= tolerance
            and abs(radius - radius_cm) <= tolerance
        ):
            matching_edges.append(edge)

    if not matching_edges:
        raise RuntimeError('止金半円部の円弧エッジを取得できませんでした。')

    return matching_edges


def find_arc_edges_by_xy_radius_and_z(body, center_x, center_y, radius_cm, z_value, tolerance=1e-6):
    matching_edges = []

    for edge in body.edges:
        geometry = edge.geometry
        circle = adsk.core.Circle3D.cast(geometry)
        arc = adsk.core.Arc3D.cast(geometry)

        if circle:
            center = circle.center
            radius = circle.radius
        elif arc:
            center = arc.center
            radius = arc.radius
        else:
            continue

        if (
            abs(center.x - center_x) <= tolerance
            and abs(center.y - center_y) <= tolerance
            and abs(center.z - z_value) <= tolerance
            and abs(radius - radius_cm) <= tolerance
        ):
            matching_edges.append(edge)

    return matching_edges


def find_arc_edges_on_faces_by_xy_radius(faces, center_x, center_y, radius_cm, tolerance=1e-6):
    matching_edges = []
    seen_tokens = set()

    for face in faces:
        for index in range(face.edges.count):
            edge = face.edges.item(index)
            if edge.entityToken in seen_tokens:
                continue

            geometry = edge.geometry
            circle = adsk.core.Circle3D.cast(geometry)
            arc = adsk.core.Arc3D.cast(geometry)

            if circle:
                center = circle.center
                radius = circle.radius
            elif arc:
                center = arc.center
                radius = arc.radius
            else:
                continue

            if (
                abs(center.x - center_x) <= tolerance
                and abs(center.y - center_y) <= tolerance
                and abs(radius - radius_cm) <= tolerance
            ):
                seen_tokens.add(edge.entityToken)
                matching_edges.append(edge)

    return matching_edges


def find_outer_bottom_semicircle_top_edges(feature, center_x, center_y, radius_cm, base_z, tolerance=1e-6):
    matching_edges = []
    seen_tokens = set()

    for face in feature.sideFaces:
        for index in range(face.edges.count):
            edge = face.edges.item(index)
            if edge.entityToken in seen_tokens:
                continue

            geometry = edge.geometry
            circle = adsk.core.Circle3D.cast(geometry)
            arc = adsk.core.Arc3D.cast(geometry)

            if circle:
                center = circle.center
                radius = circle.radius
            elif arc:
                center = arc.center
                radius = arc.radius
            else:
                continue

            if (
                abs(center.x - center_x) > tolerance
                or abs(center.y - center_y) > tolerance
                or abs(radius - radius_cm) > tolerance
            ):
                continue

            has_upper_xy_face = False
            for adjacent_face in edge.faces:
                if not is_xy_plane_face(adjacent_face, tolerance):
                    continue
                if adjacent_face.boundingBox.maxPoint.z > base_z + tolerance:
                    has_upper_xy_face = True
                    break

            if not has_upper_xy_face:
                continue

            seen_tokens.add(edge.entityToken)
            matching_edges.append(edge)

    if not matching_edges:
        raise RuntimeError('止金半円部の上側円弧エッジを取得できませんでした。')

    return matching_edges


def find_arc_edges_by_xy_radius_adjacent_upper_xy_face(body, center_x, center_y, radius_cm, base_z, tolerance=1e-6):
    matching_edges = []
    seen_tokens = set()

    for edge in body.edges:
        if edge.entityToken in seen_tokens:
            continue

        geometry = edge.geometry
        circle = adsk.core.Circle3D.cast(geometry)
        arc = adsk.core.Arc3D.cast(geometry)

        if circle:
            center = circle.center
            radius = circle.radius
        elif arc:
            center = arc.center
            radius = arc.radius
        else:
            continue

        if (
            abs(center.x - center_x) > tolerance
            or abs(center.y - center_y) > tolerance
            or abs(radius - radius_cm) > tolerance
        ):
            continue

        has_upper_xy_face = False
        for adjacent_face in edge.faces:
            if not is_xy_plane_face(adjacent_face, tolerance):
                continue
            if adjacent_face.boundingBox.maxPoint.z > base_z + tolerance:
                has_upper_xy_face = True
                break

        if not has_upper_xy_face:
            continue

        seen_tokens.add(edge.entityToken)
        matching_edges.append(edge)

    if not matching_edges:
        raise RuntimeError('止金半円部の上側 XY 面に接する円弧エッジを取得できませんでした。')

    return matching_edges


def exclude_edges_on_face(edges, face):
    excluded_tokens = {face.edges.item(index).entityToken for index in range(face.edges.count)}
    filtered_edges = [edge for edge in edges if edge.entityToken not in excluded_tokens]

    if not filtered_edges:
        raise RuntimeError('底面外部に接していない止金半円部の円弧エッジを取得できませんでした。')

    return filtered_edges


def keep_edges_adjacent_to_xy_face(edges, excluded_face, tolerance=1e-6):
    filtered_edges = []

    for edge in edges:
        for face in edge.faces:
            if face.entityToken == excluded_face.entityToken:
                continue
            if is_xy_plane_face(face, tolerance):
                filtered_edges.append(edge)
                break

    if not filtered_edges:
        raise RuntimeError('止金半円部の上側 XY 面に接する円弧エッジを取得できませんでした。')

    return filtered_edges


def get_edges_on_faces(edges, faces):
    face_edge_tokens = set()

    for face in faces:
        for index in range(face.edges.count):
            face_edge_tokens.add(face.edges.item(index).entityToken)

    filtered_edges = [edge for edge in edges if edge.entityToken in face_edge_tokens]

    return filtered_edges


def join_all_bodies_into_first(root_comp):
    bodies = root_comp.bRepBodies
    if bodies.count <= 1:
        return None

    target_body = bodies.item(0)
    tool_body_collection = adsk.core.ObjectCollection.create()
    for index in range(1, bodies.count):
        tool_body_collection.add(bodies.item(index))

    combine_features = root_comp.features.combineFeatures
    combine_input = combine_features.createInput(target_body, tool_body_collection)
    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combine_input.isKeepToolBodies = False

    return combine_features.add(combine_input)


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
    candidate_core_dirs = [
        os.path.join(script_dir, 'core'),
        os.path.join(os.path.dirname(script_dir), 'core'),
    ]

    for core_dir in candidate_core_dirs:
        if os.path.isdir(core_dir) and core_dir not in sys.path:
            sys.path.append(core_dir)

    import fusion_helpers

    return fusion_helpers


def run(context):
    try:
        from . import inner_shell
    except ImportError:
        import inner_shell

    inner_shell.run(context)
