import math

import adsk.core
import adsk.fusion

try:
    from . import helpers
    from . import naming
except ImportError:
    import helpers
    import naming


GRIP_REFERENCE_POINT_O_MM = (-42.0, 5.0, 0.0)
GRIP_REFERENCE_POINT_G_MM = (-90.0, 0.0, 23.0)
GRIP_REFERENCE_LINE_SKETCH_NAME = 'グリップ参照点：GO'
GRIP_REFERENCE_LINE_DISPLAY_PLANE_NAME = 'グリップ参照点：GO表示平面'
GRIP_REFERENCE_PLANE_I_NAME = 'グリップ参照点：平面I'
GRIP_REFERENCE_PLANE_I_SKETCH_NAME = 'グリップ参照点：平面I 参照'
GRIP_REFERENCE_POINT_O_SKETCH_NAME = 'グリップ参照点：O'
GRIP_REFERENCE_POINT_G_SKETCH_NAME = 'グリップ参照点：G'
GRIP_REFERENCE_POINT_X_SKETCH_NAME = 'グリップ参照点：X'
GRIP_REFERENCE_POINT_Y_SKETCH_NAME = 'グリップ参照点：Y'
GRIP_REFERENCE_POSITIVE_X_AXIS_SKETCH_NAME = 'グリップ参照方向：X軸'
GRIP_REFERENCE_NEGATIVE_X_AXIS_SKETCH_NAME = 'グリップ参照方向：-X軸'
GRIP_REFERENCE_POSITIVE_Y_AXIS_SKETCH_NAME = 'グリップ参照方向：Y軸'
GRIP_REFERENCE_NEGATIVE_Y_AXIS_SKETCH_NAME = 'グリップ参照方向：-Y軸'
GRIP_REFERENCE_POSITIVE_Z_AXIS_SKETCH_NAME = 'グリップ参照方向：Z軸'
GRIP_REFERENCE_NEGATIVE_Z_AXIS_SKETCH_NAME = 'グリップ参照方向：-Z軸'
GRIP_FINGER_A_POINT_P_MM = (-52.5, 32.2, 16.723)
GRIP_FINGER_A_POINT_P_PRIME_MM = (-50.0, 32.2, 19.223)
GRIP_FINGER_A_POINT_P_SKETCH_NAME = 'グリップ参照点：AP'
GRIP_FINGER_A_POINT_P_PRIME_SKETCH_NAME = "グリップ参照点：AP'"
GRIP_FINGER_A_PLANE_J_NAME = 'グリップ参照平面：AJ'
GRIP_FINGER_A_PLANE_J_PRIME_NAME = "グリップ参照平面：AJ'"
GRIP_FINGER_B_POINT_P_MM = (-40.0, 32.2, 2.223)
GRIP_FINGER_B_POINT_P_PRIME_MM = (-40.0, 32.2, 0.77)
GRIP_FINGER_B_POINT_P_SKETCH_NAME = 'グリップ参照点：BP'
GRIP_FINGER_B_POINT_P_PRIME_SKETCH_NAME = "グリップ参照点：BP'"
GRIP_FINGER_B_PLANE_J_NAME = 'グリップ参照平面：BJ'
GRIP_FINGER_B_PLANE_J_PRIME_NAME = "グリップ参照平面：BJ'"
GRIP_FINGER_C_POINT_P_MM = (-60.484, -3.37, -6.0)
GRIP_FINGER_C_POINT_P_PRIME_MM = (-56.40453246066609, 6.394148902055074, 1.675838899691525)
GRIP_FINGER_C_POINT_P_SKETCH_NAME = 'グリップ参照点：CP'
GRIP_FINGER_C_POINT_P_PRIME_SKETCH_NAME = "グリップ参照点：CP'"
GRIP_FINGER_C_PLANE_J_NAME = 'グリップ参照平面：CJ'
GRIP_FINGER_C_PLANE_J_PRIME_NAME = "グリップ参照平面：CJ'"
GRIP_FINGER_D_POINT_P_MM = (-46.48, -27.896, -6.0)
GRIP_FINGER_D_POINT_P_PRIME_MM = (-45.60977291412442, -23.42569022063176, -4.2242341664810645)
GRIP_FINGER_D_POINT_P_SKETCH_NAME = 'グリップ参照点：DP'
GRIP_FINGER_D_POINT_P_PRIME_SKETCH_NAME = "グリップ参照点：DP'"
GRIP_FINGER_D_PLANE_J_NAME = 'グリップ参照平面：DJ'
GRIP_FINGER_D_PLANE_J_PRIME_NAME = "グリップ参照平面：DJ'"
GRIP_REFERENCE_PLANE_DISPLAY_SIZE_MM = 24.0
GRIP_FINGER_A_LINE_SKETCH_NAME = 'グリップ関節線：指A'
GRIP_FINGER_A_LENGTHS_MM = (15.0, 20.0, 17.0, 11.0, 14.0)
GRIP_FINGER_A_TWIST_DEG = 20.0
GRIP_FINGER_A_ANGLES_DEG = (80.0, 126.0, 160.0, 135.0, 150.0)
GRIP_FINGER_B_LINE_SKETCH_NAME = 'グリップ関節線：指B'
GRIP_FINGER_B_LENGTHS_MM = (20.0, 15.0, 21.0, 18.0, 13.0)
GRIP_FINGER_B_ANGLES_DEG = (82.0, 123.0, 162.0, 150.0, 133.0)
GRIP_FINGER_C_LINE_SKETCH_NAME = 'グリップ関節線：指C'
GRIP_FINGER_C_LENGTHS_MM = (15.0, 30.0, 15.0, 18.0, 16.0)
GRIP_FINGER_C_MAX_TOTAL_TURN_DEG = 210.0
GRIP_FINGER_C_TWIST_DEG = 10.0
GRIP_FINGER_C_ANGLES_DEG = (80.0, 130.0, 130.0, 150.0, 140.0)
GRIP_FINGER_D_LINE_SKETCH_NAME = 'グリップ関節線：指D'
GRIP_FINGER_D_LENGTHS_MM = (30.0, 23.0, 15.0, 15.0, 15.0)
GRIP_FINGER_D_TWIST_DEG = 30.0
GRIP_FINGER_D_ANGLES_DEG = (40.0, 150.0, 160.0, 140.0, 150.0)


def mm_to_cm(value_mm):
    return value_mm / 10.0


def create_point_mm(x_mm, y_mm, z_mm):
    return adsk.core.Point3D.create(
        mm_to_cm(x_mm),
        mm_to_cm(y_mm),
        mm_to_cm(z_mm),
    )


def normalize_vector(vector):
    length = math.sqrt(
        (vector[0] * vector[0])
        + (vector[1] * vector[1])
        + (vector[2] * vector[2])
    )
    if length <= 1e-9:
        raise RuntimeError('零ベクトルは正規化できません。')
    return (
        vector[0] / length,
        vector[1] / length,
        vector[2] / length,
    )


def dot_vectors(vector_a, vector_b):
    return (
        (vector_a[0] * vector_b[0])
        + (vector_a[1] * vector_b[1])
        + (vector_a[2] * vector_b[2])
    )


def cross_vectors(vector_a, vector_b):
    return (
        (vector_a[1] * vector_b[2]) - (vector_a[2] * vector_b[1]),
        (vector_a[2] * vector_b[0]) - (vector_a[0] * vector_b[2]),
        (vector_a[0] * vector_b[1]) - (vector_a[1] * vector_b[0]),
    )


def add_vector_to_point(point_mm, vector_mm):
    return (
        point_mm[0] + vector_mm[0],
        point_mm[1] + vector_mm[1],
        point_mm[2] + vector_mm[2],
    )


def subtract_points(point_a_mm, point_b_mm):
    return (
        point_a_mm[0] - point_b_mm[0],
        point_a_mm[1] - point_b_mm[1],
        point_a_mm[2] - point_b_mm[2],
    )


def scale_vector(vector, scale):
    return (
        vector[0] * scale,
        vector[1] * scale,
        vector[2] * scale,
    )


def choose_non_parallel_axis(direction_vector):
    candidate_axes = (
        (0.0, 0.0, 1.0),
        (0.0, 1.0, 0.0),
        (1.0, 0.0, 0.0),
    )
    for axis in candidate_axes:
        if abs(dot_vectors(direction_vector, axis)) < 0.95:
            return axis
    return candidate_axes[-1]


def find_sketch_by_name_or_attribute(root_comp, name):
    sketches = root_comp.sketches
    for index in range(sketches.count):
        sketch = sketches.item(index)
        if sketch.name == name:
            return sketch
        attr = sketch.attributes.itemByName(
            naming.ATTRIBUTE_GROUP,
            naming.ATTRIBUTE_NAME_KEY,
        )
        if attr and attr.value == name:
            return sketch
    return None


def delete_sketch_if_present(root_comp, name):
    sketch = find_sketch_by_name_or_attribute(root_comp, name)
    if sketch is not None:
        sketch.deleteMe()


def delete_plane_if_present(root_comp, name):
    plane = helpers.find_construction_plane_by_name_or_attribute(root_comp, name)
    if plane is not None:
        plane.deleteMe()


def create_reference_sketch_point(root_comp, point_mm):
    point_plane = root_comp.xYConstructionPlane
    if abs(point_mm[2]) > 1e-9:
        planes = root_comp.constructionPlanes
        plane_input = planes.createInput()
        plane_input.setByOffset(
            root_comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(mm_to_cm(point_mm[2])),
        )
        point_plane = planes.add(plane_input)

    sketch = root_comp.sketches.add(point_plane)
    sketch.isVisible = False
    return sketch.sketchPoints.add(
        sketch.modelToSketchSpace(create_point_mm(*point_mm))
    )


def create_plane_by_three_points(root_comp, point_a_mm, point_b_mm, point_c_mm, name):
    point_a = create_reference_sketch_point(root_comp, point_a_mm)
    point_b = create_reference_sketch_point(root_comp, point_b_mm)
    point_c = create_reference_sketch_point(root_comp, point_c_mm)

    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByThreePoints(point_a, point_b, point_c)
    plane = planes.add(plane_input)
    plane.name = name
    helpers.add_named_attribute(plane, name)
    return plane


def create_named_point_sketch(root_comp, plane, point_mm, sketch_name):
    sketch = root_comp.sketches.add(plane)
    sketch.name = sketch_name
    helpers.add_named_attribute(sketch, sketch_name)
    sketch.sketchPoints.add(
        sketch.modelToSketchSpace(create_point_mm(*point_mm))
    )
    return sketch


def create_named_direction_sketch(root_comp, plane, start_point_mm, end_point_mm, sketch_name):
    sketch = root_comp.sketches.add(plane)
    sketch.name = sketch_name
    helpers.add_named_attribute(sketch, sketch_name)
    start_point = sketch.sketchPoints.add(
        sketch.modelToSketchSpace(create_point_mm(*start_point_mm))
    )
    end_point = sketch.sketchPoints.add(
        sketch.modelToSketchSpace(create_point_mm(*end_point_mm))
    )
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start_point, end_point)
    line.isConstruction = True
    return sketch


def create_finger_reference_planes(root_comp, point_p, point_p_prime,
                                   point_name, point_prime_name, plane_name, plane_prime_name):
    g = GRIP_REFERENCE_POINT_G_MM
    normal = normalize_vector(cross_vectors(subtract_points(point_p, g),
                                             subtract_points(point_p_prime, g)))
    plane_j = create_plane_by_three_points(root_comp, g, point_p, point_p_prime, plane_name)
    create_named_point_sketch(root_comp, plane_j, point_p, point_name)
    create_named_point_sketch(root_comp, plane_j, point_p_prime, point_prime_name)
    normal_point = add_vector_to_point(g, scale_vector(normal, GRIP_REFERENCE_PLANE_DISPLAY_SIZE_MM))
    plane_j_prime = create_plane_by_three_points(root_comp, g, point_p, normal_point, plane_prime_name)
    return plane_j, plane_j_prime


def build_reference_geometry(root_comp):
    line_direction = normalize_vector(
        subtract_points(GRIP_REFERENCE_POINT_O_MM, GRIP_REFERENCE_POINT_G_MM)
    )
    helper_axis = choose_non_parallel_axis(line_direction)
    plane_u_axis = normalize_vector(cross_vectors(line_direction, helper_axis))
    plane_v_axis = normalize_vector(cross_vectors(line_direction, plane_u_axis))

    display_plane_point_mm = add_vector_to_point(
        GRIP_REFERENCE_POINT_O_MM,
        scale_vector(plane_u_axis, GRIP_REFERENCE_PLANE_DISPLAY_SIZE_MM),
    )
    display_plane = create_plane_by_three_points(
        root_comp,
        GRIP_REFERENCE_POINT_O_MM,
        GRIP_REFERENCE_POINT_G_MM,
        display_plane_point_mm,
        GRIP_REFERENCE_LINE_DISPLAY_PLANE_NAME,
    )

    reference_sketch = root_comp.sketches.add(display_plane)
    reference_sketch.name = GRIP_REFERENCE_LINE_SKETCH_NAME
    helpers.add_named_attribute(reference_sketch, GRIP_REFERENCE_LINE_SKETCH_NAME)

    point_o = reference_sketch.sketchPoints.add(
        reference_sketch.modelToSketchSpace(create_point_mm(*GRIP_REFERENCE_POINT_O_MM))
    )
    point_g = reference_sketch.sketchPoints.add(
        reference_sketch.modelToSketchSpace(create_point_mm(*GRIP_REFERENCE_POINT_G_MM))
    )
    line_go = reference_sketch.sketchCurves.sketchLines.addByTwoPoints(point_g, point_o)
    line_go.isConstruction = True

    plane_i_u_point_mm = add_vector_to_point(
        GRIP_REFERENCE_POINT_G_MM,
        scale_vector(plane_u_axis, GRIP_REFERENCE_PLANE_DISPLAY_SIZE_MM),
    )
    plane_i_v_point_mm = add_vector_to_point(
        GRIP_REFERENCE_POINT_G_MM,
        scale_vector(plane_v_axis, GRIP_REFERENCE_PLANE_DISPLAY_SIZE_MM),
    )
    plane_i = create_plane_by_three_points(
        root_comp,
        GRIP_REFERENCE_POINT_G_MM,
        plane_i_u_point_mm,
        plane_i_v_point_mm,
        GRIP_REFERENCE_PLANE_I_NAME,
    )

    create_named_point_sketch(
        root_comp,
        display_plane,
        GRIP_REFERENCE_POINT_O_MM,
        GRIP_REFERENCE_POINT_O_SKETCH_NAME,
    )
    create_named_point_sketch(
        root_comp,
        display_plane,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_REFERENCE_POINT_G_SKETCH_NAME,
    )
    create_named_point_sketch(
        root_comp,
        plane_i,
        plane_i_v_point_mm,
        GRIP_REFERENCE_POINT_X_SKETCH_NAME,
    )
    create_named_point_sketch(
        root_comp,
        display_plane,
        plane_i_u_point_mm,
        GRIP_REFERENCE_POINT_Y_SKETCH_NAME,
    )
    create_named_direction_sketch(
        root_comp,
        plane_i,
        GRIP_REFERENCE_POINT_G_MM,
        plane_i_v_point_mm,
        GRIP_REFERENCE_POSITIVE_X_AXIS_SKETCH_NAME,
    )
    create_named_direction_sketch(
        root_comp,
        plane_i,
        plane_i_v_point_mm,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_REFERENCE_NEGATIVE_X_AXIS_SKETCH_NAME,
    )
    create_named_direction_sketch(
        root_comp,
        display_plane,
        GRIP_REFERENCE_POINT_G_MM,
        plane_i_u_point_mm,
        GRIP_REFERENCE_POSITIVE_Y_AXIS_SKETCH_NAME,
    )
    create_named_direction_sketch(
        root_comp,
        display_plane,
        plane_i_u_point_mm,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_REFERENCE_NEGATIVE_Y_AXIS_SKETCH_NAME,
    )
    create_named_direction_sketch(
        root_comp,
        display_plane,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_REFERENCE_POINT_O_MM,
        GRIP_REFERENCE_POSITIVE_Z_AXIS_SKETCH_NAME,
    )
    create_named_direction_sketch(
        root_comp,
        display_plane,
        GRIP_REFERENCE_POINT_O_MM,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_REFERENCE_NEGATIVE_Z_AXIS_SKETCH_NAME,
    )

    plane_i_sketch = root_comp.sketches.add(plane_i)
    plane_i_sketch.name = GRIP_REFERENCE_PLANE_I_SKETCH_NAME
    helpers.add_named_attribute(plane_i_sketch, GRIP_REFERENCE_PLANE_I_SKETCH_NAME)
    point_g_on_plane = plane_i_sketch.sketchPoints.add(
        plane_i_sketch.modelToSketchSpace(create_point_mm(*GRIP_REFERENCE_POINT_G_MM))
    )
    u_line = plane_i_sketch.sketchCurves.sketchLines.addByTwoPoints(
        plane_i_sketch.modelToSketchSpace(create_point_mm(*plane_i_u_point_mm)),
        point_g_on_plane,
    )
    v_line = plane_i_sketch.sketchCurves.sketchLines.addByTwoPoints(
        point_g_on_plane,
        plane_i_sketch.modelToSketchSpace(create_point_mm(*plane_i_v_point_mm)),
    )
    u_line.isConstruction = True
    v_line.isConstruction = True

    finger_a_plane_j = create_plane_by_three_points(
        root_comp,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_FINGER_A_POINT_P_MM,
        GRIP_FINGER_A_POINT_P_PRIME_MM,
        GRIP_FINGER_A_PLANE_J_NAME,
    )
    create_named_point_sketch(
        root_comp,
        finger_a_plane_j,
        GRIP_FINGER_A_POINT_P_MM,
        GRIP_FINGER_A_POINT_P_SKETCH_NAME,
    )
    create_named_point_sketch(
        root_comp,
        finger_a_plane_j,
        GRIP_FINGER_A_POINT_P_PRIME_MM,
        GRIP_FINGER_A_POINT_P_PRIME_SKETCH_NAME,
    )
    finger_a_plane_j_normal = normalize_vector(
        cross_vectors(
            subtract_points(GRIP_FINGER_A_POINT_P_MM, GRIP_REFERENCE_POINT_G_MM),
            subtract_points(GRIP_FINGER_A_POINT_P_PRIME_MM, GRIP_REFERENCE_POINT_G_MM),
        )
    )
    finger_a_plane_j_prime_normal_point_mm = add_vector_to_point(
        GRIP_REFERENCE_POINT_G_MM,
        scale_vector(finger_a_plane_j_normal, GRIP_REFERENCE_PLANE_DISPLAY_SIZE_MM),
    )
    finger_a_plane_j_prime = create_plane_by_three_points(
        root_comp,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_FINGER_A_POINT_P_MM,
        finger_a_plane_j_prime_normal_point_mm,
        GRIP_FINGER_A_PLANE_J_PRIME_NAME,
    )

    finger_b_plane_j = create_plane_by_three_points(
        root_comp,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_FINGER_B_POINT_P_MM,
        GRIP_FINGER_B_POINT_P_PRIME_MM,
        GRIP_FINGER_B_PLANE_J_NAME,
    )
    create_named_point_sketch(
        root_comp,
        finger_b_plane_j,
        GRIP_FINGER_B_POINT_P_MM,
        GRIP_FINGER_B_POINT_P_SKETCH_NAME,
    )
    create_named_point_sketch(
        root_comp,
        finger_b_plane_j,
        GRIP_FINGER_B_POINT_P_PRIME_MM,
        GRIP_FINGER_B_POINT_P_PRIME_SKETCH_NAME,
    )
    finger_b_plane_j_normal = normalize_vector(
        cross_vectors(
            subtract_points(GRIP_FINGER_B_POINT_P_MM, GRIP_REFERENCE_POINT_G_MM),
            subtract_points(GRIP_FINGER_B_POINT_P_PRIME_MM, GRIP_REFERENCE_POINT_G_MM),
        )
    )
    finger_b_plane_j_prime_normal_point_mm = add_vector_to_point(
        GRIP_REFERENCE_POINT_G_MM,
        scale_vector(finger_b_plane_j_normal, GRIP_REFERENCE_PLANE_DISPLAY_SIZE_MM),
    )
    finger_b_plane_j_prime = create_plane_by_three_points(
        root_comp,
        GRIP_REFERENCE_POINT_G_MM,
        GRIP_FINGER_B_POINT_P_MM,
        finger_b_plane_j_prime_normal_point_mm,
        GRIP_FINGER_B_PLANE_J_PRIME_NAME,
    )

    finger_c_plane_j, finger_c_plane_j_prime = create_finger_reference_planes(
        root_comp, GRIP_FINGER_C_POINT_P_MM, GRIP_FINGER_C_POINT_P_PRIME_MM,
        GRIP_FINGER_C_POINT_P_SKETCH_NAME, GRIP_FINGER_C_POINT_P_PRIME_SKETCH_NAME,
        GRIP_FINGER_C_PLANE_J_NAME, GRIP_FINGER_C_PLANE_J_PRIME_NAME,
    )

    finger_d_plane_j, finger_d_plane_j_prime = create_finger_reference_planes(
        root_comp, GRIP_FINGER_D_POINT_P_MM, GRIP_FINGER_D_POINT_P_PRIME_MM,
        GRIP_FINGER_D_POINT_P_SKETCH_NAME, GRIP_FINGER_D_POINT_P_PRIME_SKETCH_NAME,
        GRIP_FINGER_D_PLANE_J_NAME, GRIP_FINGER_D_PLANE_J_PRIME_NAME,
    )

    return {
        'point_o_mm': GRIP_REFERENCE_POINT_O_MM,
        'point_g_mm': GRIP_REFERENCE_POINT_G_MM,
        'line_direction': line_direction,
        'plane_i': plane_i,
        'finger_a_plane_j': finger_a_plane_j,
        'finger_a_plane_j_prime': finger_a_plane_j_prime,
        'finger_b_plane_j': finger_b_plane_j,
        'finger_b_plane_j_prime': finger_b_plane_j_prime,
        'finger_c_plane_j': finger_c_plane_j,
        'finger_c_plane_j_prime': finger_c_plane_j_prime,
        'finger_d_plane_j': finger_d_plane_j,
        'finger_d_plane_j_prime': finger_d_plane_j_prime,
    }


def calculate_finger_line(point_p_mm, point_p_prime_mm, lengths_mm, angles_deg, prefer_far_from_o=True, max_total_turn_deg=180.0):
    """Keep lengths; scale joint turns uniformly to meet P on J prime."""
    lengths = tuple(lengths_mm)
    angles = tuple(angles_deg)
    if (len(lengths) != 5 or len(angles) != 5
            or any(not math.isfinite(v) or v <= 0 for v in lengths)
            or any(not math.isfinite(v) for v in angles)
            or not 0 <= angles[0] <= 90
            or any(not 0 < v < 180 for v in angles[1:])):
        raise ValueError('指の長さ5個と角度5個を確認してください。')
    if not math.isfinite(max_total_turn_deg) or not 180.0 <= max_total_turn_deg <= 210.0:
        raise ValueError('合計曲げ量の上限は180〜210度で指定してください。')
    g, p = GRIP_REFERENCE_POINT_G_MM, point_p_mm
    axis = normalize_vector(subtract_points(p, g))
    normal = normalize_vector(cross_vectors(
        subtract_points(p, g), subtract_points(point_p_prime_mm, g)))
    distance = math.sqrt(dot_vectors(subtract_points(p, g), subtract_points(p, g)))
    turns = [math.radians(180.0 - value) for value in angles[1:]]

    def chain(factor):
        points = [(0.0, 0.0)]
        heading = 0.0
        for i, length in enumerate(lengths):
            if i:
                heading -= factor * turns[i - 1]
            x, y = points[-1]
            points.append((x + length * math.cos(heading),
                           y + length * math.sin(heading)))
        return points

    # Within a total turn of pi the endpoint distance decreases monotonically.
    low, high = 0.0, math.pi / sum(turns)
    if distance >= sum(lengths):
        raise ValueError('指定長さの合計ではPへ接続できません。')
    if math.hypot(*chain(high)[-1]) > distance:
        # Beyond pi monotonicity is not assumed. Bracket the first crossing
        # in small angular steps, keeping the original <=180-degree solution.
        found = False
        total = 180.0
        while total < max_total_turn_deg:
            low = high
            total = min(total + 0.5, max_total_turn_deg)
            high = math.radians(total) / sum(turns)
            if any(high * turn >= math.pi for turn in turns):
                break
            if math.hypot(*chain(high)[-1]) <= distance:
                found = True
                break
        if not found:
            raise ValueError('指定長さでは合計曲げ量の上限{:g}度以内でPへ接続できません。'.format(max_total_turn_deg))
    for _ in range(80):
        middle = (low + high) / 2.0
        if math.hypot(*chain(middle)[-1]) > distance:
            low = middle
        else:
            high = middle
    factor = (low + high) / 2.0
    flat = chain(factor)
    rotation = -math.atan2(flat[-1][1], flat[-1][0])
    c, sn = math.cos(rotation), math.sin(rotation)
    flat = [(c*x - sn*y, sn*x + c*y) for x, y in flat]
    candidates = []
    for side in (1.0, -1.0):
        points = [tuple(g[j] + x*axis[j] + side*y*normal[j] for j in range(3))
                  for x, y in flat]
        candidates.append(points)
    select_candidate = max if prefer_far_from_o else min
    points = select_candidate(candidates, key=lambda pts: sum(
        (pts[1][j] - GRIP_REFERENCE_POINT_O_MM[j])**2 for j in range(3)))
    points[0], points[-1] = g, p
    actual_angles = (math.degrees(math.asin(abs(math.sin(rotation)))),) + tuple(
        180.0 - math.degrees(turn * factor) for turn in turns)
    return {'points_mm': points, 'lengths_mm': lengths,
            'requested_angles_deg': angles, 'angles_deg': actual_angles,
            'turn_scale': factor}


def calculate_finger_a_line(lengths_mm=None, angles_deg=None, twist_deg=GRIP_FINGER_A_TWIST_DEG):
    data = calculate_finger_line(
        GRIP_FINGER_A_POINT_P_MM, GRIP_FINGER_A_POINT_P_PRIME_MM,
        GRIP_FINGER_A_LENGTHS_MM if lengths_mm is None else lengths_mm,
        GRIP_FINGER_A_ANGLES_DEG if angles_deg is None else angles_deg)

    return apply_finger_twist(data, twist_deg, GRIP_FINGER_A_POINT_P_MM,
                              GRIP_FINGER_A_POINT_P_PRIME_MM)


def apply_finger_twist(data, twist_deg, point_p, point_p_prime, joint_index=2):
    from . import grip_twist
    import importlib
    importlib.reload(grip_twist)
    g = GRIP_REFERENCE_POINT_G_MM
    b_axis = subtract_points(GRIP_FINGER_B_POINT_P_MM, g)
    b_j_normal = cross_vectors(b_axis, subtract_points(GRIP_FINGER_B_POINT_P_PRIME_MM, g))
    b_joint_normal = cross_vectors(b_axis, b_j_normal)
    reference_normal = cross_vectors(subtract_points(point_p, g), subtract_points(point_p_prime, g))
    return grip_twist.solve(data, twist_deg, b_joint_normal, reference_normal, joint_index=joint_index)


def calculate_finger_b_line(lengths_mm=None, angles_deg=None):
    return calculate_finger_line(
        GRIP_FINGER_B_POINT_P_MM, GRIP_FINGER_B_POINT_P_PRIME_MM,
        GRIP_FINGER_B_LENGTHS_MM if lengths_mm is None else lengths_mm,
        GRIP_FINGER_B_ANGLES_DEG if angles_deg is None else angles_deg)


def calculate_finger_c_line(lengths_mm=None, angles_deg=None, twist_deg=GRIP_FINGER_C_TWIST_DEG):
    data = calculate_finger_line(
        GRIP_FINGER_C_POINT_P_MM, GRIP_FINGER_C_POINT_P_PRIME_MM,
        GRIP_FINGER_C_LENGTHS_MM if lengths_mm is None else lengths_mm,
        GRIP_FINGER_C_ANGLES_DEG if angles_deg is None else angles_deg,
        max_total_turn_deg=GRIP_FINGER_C_MAX_TOTAL_TURN_DEG)

    return apply_finger_twist(data, twist_deg, GRIP_FINGER_C_POINT_P_MM,
                              GRIP_FINGER_C_POINT_P_PRIME_MM, joint_index=2)


def calculate_finger_d_line(lengths_mm=None, angles_deg=None, twist_deg=GRIP_FINGER_D_TWIST_DEG):
    data = calculate_finger_line(
        GRIP_FINGER_D_POINT_P_MM, GRIP_FINGER_D_POINT_P_PRIME_MM,
        GRIP_FINGER_D_LENGTHS_MM if lengths_mm is None else lengths_mm,
        GRIP_FINGER_D_ANGLES_DEG if angles_deg is None else angles_deg,
        prefer_far_from_o=False)

    return apply_finger_twist(data, twist_deg, GRIP_FINGER_D_POINT_P_MM,
                              GRIP_FINGER_D_POINT_P_PRIME_MM, joint_index=2)



def calculate_guideline_points(finger, data):
    """Replace A/B G1 with the opposite parallelogram vertex.

    Keep source points unchanged for the established width surfaces and twist.
    """
    coordinates = list(data['points_mm'])
    names = ['G'] + [finger + 'G' + str(i) for i in range(1, 5)] + [finger + 'P']
    if finger in ('A', 'B'):
        g, g1, g2 = coordinates[:3]
        coordinates[1] = tuple(g[j] + g2[j] - g1[j] for j in range(3))
        names[1] = finger + "G1'"
    return coordinates, names


def create_finger_line(root_comp, plane, finger, sketch_name, data):
    sketch = root_comp.sketches.add(plane)
    sketch.name = sketch_name
    helpers.add_named_attribute(sketch, sketch.name)
    guideline_points, point_names = calculate_guideline_points(finger, data)
    points = []
    for name, coordinates in zip(point_names, guideline_points):
        point = sketch.sketchPoints.add(sketch.modelToSketchSpace(create_point_mm(*coordinates)))
        if data.get('twist_deg', 0) or finger in ('A', 'B'):
            actual = point.worldGeometry
            if max(abs(v * 10.0 - target) for v, target in zip(
                    (actual.x, actual.y, actual.z), coordinates)) > 1e-5:
                raise RuntimeError('指{}の3D関節点を指定座標に作成できませんでした。'.format(finger))
        helpers.add_named_attribute(point, 'グリップ関節点：' + name)
        points.append(point)
    for index in range(5):
        line = sketch.sketchCurves.sketchLines.addByTwoPoints(points[index], points[index + 1])
        line.isConstruction = True
        helpers.add_named_attribute(line, 'グリップ関節線：{}L{}'.format(finger, index))
    reference = sketch.sketchCurves.sketchLines.addByTwoPoints(points[0], points[-1])
    reference.isConstruction = True
    helpers.add_named_attribute(reference, 'グリップ参考線：' + finger + 'GP')
    sketch.isVisible = True
    return dict(data, guideline_points_mm=guideline_points, guideline_point_names=point_names)


def create_finger_a_line(root_comp, plane, params):
    data = calculate_finger_a_line(params.get('finger_a_lengths_mm'),
                                   params.get('finger_a_angles_deg'),
                                   params.get('finger_a_twist_deg', GRIP_FINGER_A_TWIST_DEG))
    return create_finger_line(root_comp, plane, 'A', GRIP_FINGER_A_LINE_SKETCH_NAME, data)


def create_finger_b_line(root_comp, plane, params):
    data = calculate_finger_b_line(params.get('finger_b_lengths_mm'),
                                   params.get('finger_b_angles_deg'))
    return create_finger_line(root_comp, plane, 'B', GRIP_FINGER_B_LINE_SKETCH_NAME, data)


def create_finger_c_line(root_comp, plane, params):
    data = calculate_finger_c_line(params.get('finger_c_lengths_mm'),
                                   params.get('finger_c_angles_deg'),
                                   params.get('finger_c_twist_deg', GRIP_FINGER_C_TWIST_DEG))
    return create_finger_line(root_comp, plane, 'C', GRIP_FINGER_C_LINE_SKETCH_NAME, data)


def create_finger_d_line(root_comp, plane, params):
    data = calculate_finger_d_line(params.get('finger_d_lengths_mm'),
                                   params.get('finger_d_angles_deg'),
                                   params.get('finger_d_twist_deg', GRIP_FINGER_D_TWIST_DEG))
    return create_finger_line(root_comp, plane, 'D', GRIP_FINGER_D_LINE_SKETCH_NAME, data)


def build_grip(root_comp, outer_shell_body, params=None, smv1_fixed_points=None, smv2_edge=None, smv3_fixed_points=None, smv4_edge=None, smv5_fixed_points=None, smv6_edge=None, smv7_fixed_points=None, smv8_fixed_point=None, d_tip_fixed_points=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if params is None:
        params = dict(naming.DEFAULT_GRIP_PARAMS)

    delete_sketch_if_present(root_comp, GRIP_FINGER_D_LINE_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_C_LINE_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_B_LINE_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_A_LINE_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_LINE_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_PLANE_I_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_POINT_O_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_POINT_G_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_POINT_X_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_POINT_Y_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_POSITIVE_X_AXIS_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_NEGATIVE_X_AXIS_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_POSITIVE_Y_AXIS_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_NEGATIVE_Y_AXIS_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_POSITIVE_Z_AXIS_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_REFERENCE_NEGATIVE_Z_AXIS_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_A_POINT_P_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_A_POINT_P_PRIME_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_B_POINT_P_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_B_POINT_P_PRIME_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_C_POINT_P_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_C_POINT_P_PRIME_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_D_POINT_P_SKETCH_NAME)
    delete_sketch_if_present(root_comp, GRIP_FINGER_D_POINT_P_PRIME_SKETCH_NAME)
    delete_plane_if_present(root_comp, GRIP_REFERENCE_LINE_DISPLAY_PLANE_NAME)
    delete_plane_if_present(root_comp, GRIP_REFERENCE_PLANE_I_NAME)
    delete_plane_if_present(root_comp, GRIP_FINGER_A_PLANE_J_NAME)
    delete_plane_if_present(root_comp, GRIP_FINGER_A_PLANE_J_PRIME_NAME)
    delete_plane_if_present(root_comp, GRIP_FINGER_B_PLANE_J_NAME)
    delete_plane_if_present(root_comp, GRIP_FINGER_B_PLANE_J_PRIME_NAME)

    delete_plane_if_present(root_comp, GRIP_FINGER_C_PLANE_J_NAME)
    delete_plane_if_present(root_comp, GRIP_FINGER_C_PLANE_J_PRIME_NAME)
    delete_plane_if_present(root_comp, GRIP_FINGER_D_PLANE_J_NAME)
    delete_plane_if_present(root_comp, GRIP_FINGER_D_PLANE_J_PRIME_NAME)

    references = build_reference_geometry(root_comp)
    finger_data = {
        'A': create_finger_a_line(root_comp, references['finger_a_plane_j_prime'], params),
        'B': create_finger_b_line(root_comp, references['finger_b_plane_j_prime'], params),
        'C': create_finger_c_line(root_comp, references['finger_c_plane_j_prime'], params),
        'D': create_finger_d_line(root_comp, references['finger_d_plane_j_prime'], params),
    }
    from . import grip_width
    import importlib
    importlib.reload(grip_width)
    a_side_direction = subtract_points(GRIP_FINGER_A_POINT_P_MM, GRIP_FINGER_D_POINT_P_MM)
    from . import grip_reference_fx6
    importlib.reload(grip_reference_fx6)
    grip_reference_fx6.create(root_comp, finger_data, a_side_direction)
    for finger, data in finger_data.items():
        grip_width.create(root_comp, finger, data, a_side_direction, 10.0)
    grip_width.create_connections(root_comp, finger_data, a_side_direction)

    if smv1_fixed_points is not None:
        from . import grip_semi_variable
        importlib.reload(grip_semi_variable)
        grip_semi_variable.create_smv1(root_comp, finger_data['A'], smv1_fixed_points, a_side_direction)

    if smv2_edge is not None:
        from . import grip_semi_variable
        grip_semi_variable.create_smv2(root_comp, finger_data['A'], a_side_direction, smv2_edge)

    if smv3_fixed_points is not None:
        from . import grip_semi_variable
        grip_semi_variable.create_smv3(root_comp, finger_data['A'], smv3_fixed_points, a_side_direction)

    if smv4_edge is not None:
        from . import grip_semi_variable
        grip_semi_variable.create_smv4(root_comp, finger_data['A'], a_side_direction, smv4_edge)

    if smv5_fixed_points is not None:
        from . import grip_semi_variable
        grip_semi_variable.create_smv5(root_comp, finger_data, smv5_fixed_points, a_side_direction)

    if smv6_edge is not None:
        from . import grip_semi_variable
        grip_semi_variable.create_smv6(root_comp, finger_data['B'], a_side_direction, smv6_edge)

    if smv7_fixed_points is not None:
        from . import grip_semi_variable
        grip_semi_variable.create_smv7(root_comp, finger_data['B'], smv7_fixed_points, a_side_direction)

    if smv8_fixed_point is not None:
        from . import grip_semi_variable
        grip_semi_variable.create_smv8(root_comp, finger_data['C'], smv8_fixed_point, a_side_direction)
        grip_semi_variable.create_smv9(root_comp, finger_data, smv8_fixed_point, a_side_direction)
        grip_semi_variable.create_smv10(root_comp, finger_data['C'], smv8_fixed_point, a_side_direction)

    from . import grip_reference_ellipse
    importlib.reload(grip_reference_ellipse)
    grip_reference_ellipse.create(root_comp, finger_data['A'], a_side_direction)
    grip_reference_ellipse.create_ref6(root_comp, finger_data['C'], finger_data['D'])
    grip_reference_ellipse.create_ref7(root_comp, finger_data['A'], a_side_direction)
    from . import grip_reference_bezier
    importlib.reload(grip_reference_bezier)
    ref12_sketch = grip_reference_bezier.create(root_comp, finger_data['A'])
    from . import grip_con15
    importlib.reload(grip_con15)
    grip_con15.create(root_comp, finger_data['A'], finger_data['C'], a_side_direction, ref12_sketch)
    from . import grip_reference_closest
    importlib.reload(grip_reference_closest)
    ref13_point = grip_reference_closest.create(root_comp, finger_data['A'], finger_data['C'], a_side_direction)
    from . import grip_con19_20
    importlib.reload(grip_con19_20)
    grip_con19_20.create(root_comp, finger_data, a_side_direction, ref13_point)
    hexagon_curve_sketches = grip_reference_ellipse.create_hexagon_curves(root_comp, finger_data['C'], finger_data['D'])
    from . import grip_con14
    importlib.reload(grip_con14)
    grip_con14.create(root_comp, finger_data['C'], finger_data['D'], a_side_direction)
    from . import grip_con22_23
    importlib.reload(grip_con22_23)
    grip_con22_23.create(root_comp, finger_data['C'], finger_data['D'], a_side_direction)
    from . import grip_con16_18
    importlib.reload(grip_con16_18)
    grip_con16_18.create_moving(root_comp, finger_data, a_side_direction, ref13_point)

    from . import grip_semi_variable
    importlib.reload(grip_semi_variable)
    from . import grip_hexagon_curved_surfaces
    importlib.reload(grip_hexagon_curved_surfaces)
    grip_hexagon_curved_surfaces.create(root_comp, finger_data['D'], hexagon_curve_sketches)
    from . import grip_smv17
    importlib.reload(grip_smv17)
    grip_smv17.create(root_comp, finger_data['D'], a_side_direction)

    from . import grip_hexagon_fixed_surfaces
    importlib.reload(grip_hexagon_fixed_surfaces)
    grip_hexagon_fixed_surfaces.create(root_comp, finger_data['D'], a_side_direction)
    if d_tip_fixed_points is not None:
        from . import grip_d_tip_surfaces
        importlib.reload(grip_d_tip_surfaces)
        grip_d_tip_surfaces.create(root_comp, finger_data['D'], a_side_direction, d_tip_fixed_points)

    _ = outer_shell_body
    return None
