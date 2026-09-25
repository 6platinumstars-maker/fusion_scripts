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
GRIP_FINGER_A_LENGTHS_MM = (12.0, 25.0, 17.0, 11.0, 14.0)
GRIP_FINGER_A_ANGLES_DEG = (80.0, 126.0, 160.0, 135.0, 150.0)
GRIP_FINGER_B_LINE_SKETCH_NAME = 'グリップ関節線：指B'
GRIP_FINGER_B_LENGTHS_MM = (11.0, 24.0, 21.0, 18.0, 13.0)
GRIP_FINGER_B_ANGLES_DEG = (82.0, 123.0, 162.0, 150.0, 133.0)


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


def calculate_finger_line(point_p_mm, point_p_prime_mm, lengths_mm, angles_deg):
    """Keep lengths; scale joint turns uniformly to meet P on J prime."""
    lengths = tuple(lengths_mm)
    angles = tuple(angles_deg)
    if (len(lengths) != 5 or len(angles) != 5
            or any(not math.isfinite(v) or v <= 0 for v in lengths)
            or any(not math.isfinite(v) for v in angles)
            or not 0 <= angles[0] <= 90
            or any(not 0 < v < 180 for v in angles[1:])):
        raise ValueError('指の長さ5個と角度5個を確認してください。')
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
    if not math.hypot(*chain(high)[-1]) <= distance < sum(lengths):
        raise ValueError('指定長さでは半円状の調整範囲内でPへ接続できません。')
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
    points = max(candidates, key=lambda pts: sum(
        (pts[1][j] - GRIP_REFERENCE_POINT_O_MM[j])**2 for j in range(3)))
    points[0], points[-1] = g, p
    actual_angles = (math.degrees(math.asin(abs(math.sin(rotation)))),) + tuple(
        180.0 - math.degrees(turn * factor) for turn in turns)
    return {'points_mm': points, 'lengths_mm': lengths,
            'requested_angles_deg': angles, 'angles_deg': actual_angles,
            'turn_scale': factor}


def calculate_finger_a_line(lengths_mm=None, angles_deg=None):
    return calculate_finger_line(
        GRIP_FINGER_A_POINT_P_MM, GRIP_FINGER_A_POINT_P_PRIME_MM,
        GRIP_FINGER_A_LENGTHS_MM if lengths_mm is None else lengths_mm,
        GRIP_FINGER_A_ANGLES_DEG if angles_deg is None else angles_deg)


def calculate_finger_b_line(lengths_mm=None, angles_deg=None):
    return calculate_finger_line(
        GRIP_FINGER_B_POINT_P_MM, GRIP_FINGER_B_POINT_P_PRIME_MM,
        GRIP_FINGER_B_LENGTHS_MM if lengths_mm is None else lengths_mm,
        GRIP_FINGER_B_ANGLES_DEG if angles_deg is None else angles_deg)


def create_finger_line(root_comp, plane, finger, sketch_name, data):
    sketch = root_comp.sketches.add(plane)
    sketch.name = sketch_name
    helpers.add_named_attribute(sketch, sketch.name)
    point_names = ('G',) + tuple(finger + 'G' + str(i) for i in range(1, 5)) + (finger + 'P',)
    points = []
    for name, coordinates in zip(point_names, data['points_mm']):
        point = sketch.sketchPoints.add(sketch.modelToSketchSpace(create_point_mm(*coordinates)))
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
    return data


def create_finger_a_line(root_comp, plane, params):
    data = calculate_finger_a_line(params.get('finger_a_lengths_mm'),
                                   params.get('finger_a_angles_deg'))
    return create_finger_line(root_comp, plane, 'A', GRIP_FINGER_A_LINE_SKETCH_NAME, data)


def create_finger_b_line(root_comp, plane, params):
    data = calculate_finger_b_line(params.get('finger_b_lengths_mm'),
                                   params.get('finger_b_angles_deg'))
    return create_finger_line(root_comp, plane, 'B', GRIP_FINGER_B_LINE_SKETCH_NAME, data)


def build_grip(root_comp, outer_shell_body, params=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if params is None:
        params = dict(naming.DEFAULT_GRIP_PARAMS)

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
    create_finger_a_line(root_comp, references['finger_a_plane_j_prime'], params)
    create_finger_b_line(root_comp, references['finger_b_plane_j_prime'], params)

    _ = outer_shell_body
    return None
