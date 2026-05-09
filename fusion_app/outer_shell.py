import math

import adsk.core
import adsk.fusion

try:
    from . import helpers
    from . import naming
except ImportError:
    import helpers
    import naming


OUTER_CIRCLE_CENTER_MM = (-42.0, 5.0)
OUTER_CIRCLE_RADIUS_MM = 33.0
INNER_SHELL_TOP_EDGE_START_MM = (-66.67, 26.918)
INNER_SHELL_TOP_EDGE_END_MM = (-25.0, 30.0)
INNER_SHELL_LOWER_STOP_TOP_Y_MM = -20.0
OUTER_SHELL_CONTACT_FACE_NAME = '外殻内殻接面'
OUTER_SHELL_BOTTOM_OUTER_FACE_POINT_MM = (-5.0, -35.0, -3.0)
OUTER_SHELL_BOTTOM_OUTER_EXTRUDE_DISTANCE_MM = -0.2
OUTER_SHELL_BOTTOM_OUTER_SKETCH_NAME = '外殻底面外側'
OUTER_SHELL_BOTTOM_OUTER_SKETCH_Z_MM = -3.2
OUTER_SHELL_BOTTOM_OUTER_REGION_TARGET_MM = (-60.0, 0.0, 0.0)
OUTER_SHELL_BOTTOM_OUTER_REGION_EXTRUDE_DISTANCE_MM = -2.8
OUTER_SHELL_BOTTOM_OUTER_FILLET_RADIUS_MM = 3.0
OUTER_SHELL_BOTTOM_OUTER_FILLET_Z_MM = -6.0
OUTER_SHELL_BOTTOM_OUTER_FILLET_REFERENCE_POINTS_MM = (
    (-5.0, -23.3, -6.0),
    (-25.0, -19.174, -6.0),
)


def mm_to_cm(value_mm):
    return value_mm / 10.0


def create_point_mm(x_mm, y_mm, z_mm=0.0):
    return adsk.core.Point3D.create(
        mm_to_cm(x_mm),
        mm_to_cm(y_mm),
        mm_to_cm(z_mm),
    )


def create_sketch_point(sketch, point_mm):
    return sketch.sketchPoints.add(create_point_mm(*point_mm))


def get_point_distance(point_a, point_b):
    return math.sqrt(
        ((point_a.x - point_b.x) ** 2)
        + ((point_a.y - point_b.y) ** 2)
        + ((point_a.z - point_b.z) ** 2)
    )


def get_body_from_feature(feature):
    body = feature.bodies.item(0)
    if not body:
        raise RuntimeError('外殻ボディを取得できませんでした。')
    return body


def get_face_collection(body):
    return [body.faces.item(index) for index in range(body.faces.count)]


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


def find_face_through_point_on_constant_axis(body, point_mm, axis, tolerance_cm):
    target_point = create_point_mm(*point_mm)

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        box = face.boundingBox
        min_value = getattr(box.minPoint, axis)
        max_value = getattr(box.maxPoint, axis)
        if abs(max_value - min_value) > tolerance_cm:
            continue

        if face.isPointOnFace(target_point, tolerance_cm):
            return face

    raise RuntimeError('指定条件に一致する外殻面を取得できませんでした。')


def find_inner_contact_faces(outer_shell_body, inner_shell_body, tolerance_cm):
    contact_faces = []
    inner_faces = get_face_collection(inner_shell_body)

    for outer_face in get_face_collection(outer_shell_body):
        sample_point = outer_face.pointOnFace
        if not sample_point:
            continue

        for inner_face in inner_faces:
            if inner_face.isPointOnFace(sample_point, tolerance_cm):
                contact_faces.append(outer_face)
                break

    if not contact_faces:
        raise RuntimeError('外殻内殻接面を取得できませんでした。')

    return contact_faces


def offset_contact_faces(root_comp, outer_shell_body, inner_shell_body):
    app = adsk.core.Application.get()
    tolerance_cm = max(app.pointTolerance, 1e-5)
    contact_faces = find_inner_contact_faces(
        outer_shell_body,
        inner_shell_body,
        tolerance_cm,
    )

    offset_faces = root_comp.features.offsetFacesFeatures
    distance = adsk.core.ValueInput.createByReal(mm_to_cm(-0.2))
    offset_input = offset_faces.createInput(contact_faces, distance)
    offset_feature = offset_faces.add(offset_input)

    if offset_feature:
        offset_feature.name = OUTER_SHELL_CONTACT_FACE_NAME
        for face in offset_feature.faces:
            helpers.add_named_attribute(face, OUTER_SHELL_CONTACT_FACE_NAME)

    return offset_feature


def extrude_xy_face_in_negative_z(root_comp, face, distance_mm, tolerance=1e-6):
    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('押し出し対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    if abs(normal.x) > tolerance or abs(normal.y) > tolerance or abs(normal.z) <= tolerance:
        raise RuntimeError('押し出し対象面が Z 方向法線を持っていません。')

    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.z > 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        face,
        adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(distance_mm))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def get_curve_geometry(sketch_curve):
    geometry = getattr(sketch_curve, 'worldGeometry', None)
    if geometry:
        return geometry
    return getattr(sketch_curve, 'geometry', None)


def get_curve_midpoint(sketch_curve):
    geometry = get_curve_geometry(sketch_curve)
    evaluator = geometry.evaluator
    success, start_param, end_param = evaluator.getParameterExtents()
    if not success:
        raise RuntimeError('断面カーブのパラメータ範囲を取得できませんでした。')

    success, midpoint = evaluator.getPointAtParameter((start_param + end_param) / 2.0)
    if not success:
        raise RuntimeError('断面カーブの中点を取得できませんでした。')

    return midpoint


def clone_intersection_curve_as_sketch_geometry(sketch, sketch_curve):
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    circles = sketch.sketchCurves.sketchCircles
    splines = sketch.sketchCurves.sketchFittedSplines

    sketch_line = adsk.fusion.SketchLine.cast(sketch_curve)
    if sketch_line:
        lines.addByTwoPoints(
            sketch_line.startSketchPoint.geometry,
            sketch_line.endSketchPoint.geometry,
        )
        return

    sketch_arc = adsk.fusion.SketchArc.cast(sketch_curve)
    if sketch_arc:
        arcs.addByThreePoints(
            sketch_arc.startSketchPoint.geometry,
            get_curve_midpoint(sketch_arc),
            sketch_arc.endSketchPoint.geometry,
        )
        return

    sketch_circle = adsk.fusion.SketchCircle.cast(sketch_curve)
    if sketch_circle:
        geometry = adsk.core.Circle3D.cast(get_curve_geometry(sketch_circle))
        if not geometry:
            raise RuntimeError('断面円のジオメトリを取得できませんでした。')
        circles.addByCenterRadius(geometry.center, geometry.radius)
        return

    sketch_ellipse = adsk.fusion.SketchEllipse.cast(sketch_curve)
    if sketch_ellipse:
        geometry = adsk.core.Ellipse3D.cast(get_curve_geometry(sketch_ellipse))
        if not geometry:
            raise RuntimeError('断面楕円のジオメトリを取得できませんでした。')
        sketch.sketchCurves.sketchEllipses.add(
            geometry.center,
            geometry.majorAxis,
            geometry.pointOnEllipse,
        )
        return

    sketch_spline = adsk.fusion.SketchFittedSpline.cast(sketch_curve)
    if sketch_spline:
        geometry = get_curve_geometry(sketch_spline)
        evaluator = geometry.evaluator
        success, start_param, end_param = evaluator.getParameterExtents()
        if not success:
            raise RuntimeError('断面スプラインのパラメータ範囲を取得できませんでした。')

        fit_points = adsk.core.ObjectCollection.create()
        sample_count = 16
        for index in range(sample_count + 1):
            parameter = start_param + ((end_param - start_param) * index / sample_count)
            success, point = evaluator.getPointAtParameter(parameter)
            if not success:
                raise RuntimeError('断面スプラインのサンプル点を取得できませんでした。')
            fit_points.add(point)
        splines.add(fit_points)
        return

    raise RuntimeError('未対応の断面カーブ種類です。')


def project_inner_shell_section_to_sketch(sketch, inner_shell_body):
    projected_entities = sketch.intersectWithSketchPlane([inner_shell_body])
    projected_curves = []

    for entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(entity)
        if sketch_curve:
            projected_curves.append(sketch_curve)

    for sketch_curve in projected_curves:
        clone_intersection_curve_as_sketch_geometry(sketch, sketch_curve)

    for sketch_curve in projected_curves:
        sketch_curve.deleteMe()


def get_profile_nearest_point(sketch, target_point):
    nearest_profile = None
    nearest_distance = None

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        centroid = profile.areaProperties().centroid
        distance = math.hypot(
            centroid.x - target_point.x,
            centroid.y - target_point.y,
        )
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_profile = profile

    if not nearest_profile:
        raise RuntimeError('外殻の押し出しプロファイルを取得できませんでした。')

    return nearest_profile


def line_y_at_x(point_a_mm, point_b_mm, target_x_mm):
    x1_mm, y1_mm = point_a_mm
    x2_mm, y2_mm = point_b_mm

    if abs(x2_mm - x1_mm) <= 1e-9:
        raise RuntimeError('垂直線では y を一意に求められません。')

    ratio = (target_x_mm - x1_mm) / (x2_mm - x1_mm)
    return y1_mm + ((y2_mm - y1_mm) * ratio)


def line_circle_intersections(point_a_mm, point_b_mm, center_mm, radius_mm):
    ax_mm, ay_mm = point_a_mm
    bx_mm, by_mm = point_b_mm
    cx_mm, cy_mm = center_mm

    dx_mm = bx_mm - ax_mm
    dy_mm = by_mm - ay_mm
    fx_mm = ax_mm - cx_mm
    fy_mm = ay_mm - cy_mm

    a = (dx_mm * dx_mm) + (dy_mm * dy_mm)
    b = 2.0 * ((fx_mm * dx_mm) + (fy_mm * dy_mm))
    c = (fx_mm * fx_mm) + (fy_mm * fy_mm) - (radius_mm * radius_mm)

    discriminant = (b * b) - (4.0 * a * c)
    if discriminant < 0.0:
        raise RuntimeError('円と直線の交点を取得できませんでした。')

    sqrt_discriminant = math.sqrt(discriminant)
    intersections = []
    for sign in (-1.0, 1.0):
        t = (-b + (sign * sqrt_discriminant)) / (2.0 * a)
        intersections.append((
            ax_mm + (dx_mm * t),
            ay_mm + (dy_mm * t),
        ))

    return intersections


def offset_point_from_circle(center_mm, point_mm, offset_mm):
    cx_mm, cy_mm = center_mm
    px_mm, py_mm = point_mm

    vector_x_mm = px_mm - cx_mm
    vector_y_mm = py_mm - cy_mm
    vector_length_mm = math.hypot(vector_x_mm, vector_y_mm)
    if vector_length_mm <= 1e-9:
        raise RuntimeError('円の中心と同一点はオフセットできません。')

    scale = (vector_length_mm + offset_mm) / vector_length_mm
    return (
        cx_mm + (vector_x_mm * scale),
        cy_mm + (vector_y_mm * scale),
    )


def vertical_line_circle_intersections(center_mm, radius_mm, x_mm):
    cx_mm, cy_mm = center_mm
    offset_x_mm = x_mm - cx_mm
    remaining = (radius_mm * radius_mm) - (offset_x_mm * offset_x_mm)
    if remaining < 0.0:
        raise RuntimeError('円と鉛直線の交点を取得できませんでした。')

    offset_y_mm = math.sqrt(max(remaining, 0.0))
    return [
        (x_mm, cy_mm - offset_y_mm),
        (x_mm, cy_mm + offset_y_mm),
    ]


def build_outer_shell_reference_points(params):
    clearance_mm = params.get('clearance_mm', naming.DEFAULT_OUTER_SHELL_PARAMS['clearance_mm'])

    point_a_mm = (-5.0, -23.0, 0.0)
    point_b_mm = (-5.0, -35.0, 0.0)
    point_c_mm = (-90.0, -35.0, 0.0)
    point_d_mm = (-90.0, 35.0, 0.0)
    point_e_mm = (-51.8, 35.0, 0.0)
    point_f_mm = (-51.8, 29.0, 0.0)

    point_h_y_mm = line_y_at_x(
        INNER_SHELL_TOP_EDGE_START_MM,
        INNER_SHELL_TOP_EDGE_END_MM,
        point_f_mm[0]
    )
    point_h_mm = (point_f_mm[0], point_h_y_mm, 0.0)

    point_i_mm = (point_a_mm[0], INNER_SHELL_LOWER_STOP_TOP_Y_MM, 0.0)
    point_j_mm = point_h_mm

    top_line_intersections = line_circle_intersections(
        INNER_SHELL_TOP_EDGE_START_MM,
        INNER_SHELL_TOP_EDGE_END_MM,
        OUTER_CIRCLE_CENTER_MM,
        OUTER_CIRCLE_RADIUS_MM,
    )
    point_k_mm = max(top_line_intersections, key=lambda point: point[0])
    point_l_mm = offset_point_from_circle(
        OUTER_CIRCLE_CENTER_MM,
        point_k_mm,
        clearance_mm,
    )
    point_m_mm = (
        point_j_mm[0] - 12.0,
        line_y_at_x(
            INNER_SHELL_TOP_EDGE_START_MM,
            INNER_SHELL_TOP_EDGE_END_MM,
            point_j_mm[0] - 12.0
        ) + clearance_mm,
        0.0,
    )
    point_n_mm = (
        -24.0,
        -26.2,
        0.0,
    )

    return {
        'A': point_a_mm,
        'B': point_b_mm,
        'C': point_c_mm,
        'D': point_d_mm,
        'E': point_e_mm,
        'F': point_f_mm,
        'H': point_h_mm,
        'I': point_i_mm,
        'J': point_j_mm,
        'K': (point_k_mm[0], point_k_mm[1], 0.0),
        'L': (point_l_mm[0], point_l_mm[1], 0.0),
        'M': point_m_mm,
        'N': point_n_mm,
    }


def create_outer_shell_sketch(root_comp, inner_shell_body, params):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = '外殻'

    points = build_outer_shell_reference_points(params)
    lines = sketch.sketchCurves.sketchLines

    project_inner_shell_section_to_sketch(sketch, inner_shell_body)

    line_segments = [
        ('B', 'I'),
        ('B', 'C'),
        ('C', 'D'),
        ('D', 'E'),
        ('E', 'J'),
    ]

    for start_name, end_name in line_segments:
        lines.addByTwoPoints(
            create_point_mm(*points[start_name]),
            create_point_mm(*points[end_name]),
        )

    for point_name in ('A', 'B', 'C', 'D', 'E', 'F', 'H', 'I', 'J'):
        create_sketch_point(sketch, points[point_name])

    return sketch


def cut_body_with_inner_shell(root_comp, target_body, inner_shell_body):
    tool_body_collection = adsk.core.ObjectCollection.create()
    tool_body_collection.add(inner_shell_body)

    combine_features = root_comp.features.combineFeatures
    combine_input = combine_features.createInput(target_body, tool_body_collection)
    combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combine_input.isKeepToolBodies = True
    combine_features.add(combine_input)


def extrude_outer_shell_profile(root_comp, sketch, inner_shell_body):
    target_point = create_point_mm(-80.0, 0.0, 0.0)
    profile = get_profile_nearest_point(sketch, target_point)

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(3.0))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )

    feature = extrudes.add(extrude_input)
    body = get_body_from_feature(feature)
    cut_body_with_inner_shell(root_comp, body, inner_shell_body)
    helpers.set_body_identity(body, naming.BODY_OUTER_SHELL)
    offset_contact_faces(root_comp, body, inner_shell_body)
    return body


def add_bottom_outer_face(root_comp, outer_shell_body):
    app = adsk.core.Application.get()
    tolerance_cm = max(app.pointTolerance, 1e-5)
    face = find_face_through_point_on_constant_axis(
        outer_shell_body,
        OUTER_SHELL_BOTTOM_OUTER_FACE_POINT_MM,
        'z',
        tolerance_cm,
    )
    extrude_xy_face_in_negative_z(
        root_comp,
        face,
        OUTER_SHELL_BOTTOM_OUTER_EXTRUDE_DISTANCE_MM,
        tolerance_cm,
    )


def create_bottom_outer_face_sketch(root_comp, outer_shell_body):
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        root_comp.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(mm_to_cm(OUTER_SHELL_BOTTOM_OUTER_SKETCH_Z_MM)),
    )
    sketch_plane = planes.add(plane_input)

    sketch = root_comp.sketches.add(sketch_plane)
    sketch.name = OUTER_SHELL_BOTTOM_OUTER_SKETCH_NAME

    circles = sketch.sketchCurves.sketchCircles
    lines = sketch.sketchCurves.sketchLines

    circle_center_mm = (0.0, 5.0, 0.0)
    circle_point_mm = (-5.0, -23.3, 0.0)
    b_start_mm = (-25.0, 30.0, 0.0)
    b_pass_mm = (-25.0, 14.0, 0.0)
    c_pass_mm = (-51.8, 28.0, 0.0)
    d_start_mm = (-51.8, 35.0, 0.0)
    d_pass_mm = (-51.8, 28.0, 0.0)
    f_point_mm = (-5.0, -35.0, 0.0)
    g_point_mm = (-90.0, -35.0, 0.0)
    h_point_mm = (-90.0, 35.0, 0.0)
    i_point_mm = (-5.0, -34.0, 0.0)
    circle_radius_mm = math.hypot(
        circle_point_mm[0] - circle_center_mm[0],
        circle_point_mm[1] - circle_center_mm[1],
    )
    point_e_xy_mm = min(
        vertical_line_circle_intersections(
            (circle_center_mm[0], circle_center_mm[1]),
            circle_radius_mm,
            b_start_mm[0],
        ),
        key=lambda point: math.hypot(point[0] - b_start_mm[0], point[1] - b_start_mm[1]),
    )
    point_e_mm = (point_e_xy_mm[0], point_e_xy_mm[1], 0.0)
    point_j_xy_mm = min(
        vertical_line_circle_intersections(
            (circle_center_mm[0], circle_center_mm[1]),
            circle_radius_mm,
            i_point_mm[0],
        ),
        key=lambda point: math.hypot(point[0] - i_point_mm[0], point[1] - i_point_mm[1]),
    )
    point_j_mm = (point_j_xy_mm[0], point_j_xy_mm[1], 0.0)

    circles.addByCenterRadius(
        create_point_mm(*circle_center_mm),
        circle_radius_mm / 10.0,
    )
    lines.addByTwoPoints(
        create_point_mm(*b_start_mm),
        create_point_mm(*b_pass_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*b_start_mm),
        create_point_mm(*c_pass_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*d_start_mm),
        create_point_mm(*d_pass_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*f_point_mm),
        create_point_mm(*g_point_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*g_point_mm),
        create_point_mm(*h_point_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*h_point_mm),
        create_point_mm(*d_start_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*f_point_mm),
        create_point_mm(*point_j_mm),
    )

    for point_mm in (
        circle_center_mm,
        circle_point_mm,
        b_start_mm,
        b_pass_mm,
        c_pass_mm,
        d_start_mm,
        d_pass_mm,
        f_point_mm,
        g_point_mm,
        h_point_mm,
        i_point_mm,
        point_e_mm,
        point_j_mm,
    ):
        create_sketch_point(sketch, point_mm)

    return sketch


def extrude_bottom_outer_region(root_comp, sketch):
    profile = get_profile_nearest_point(
        sketch,
        create_point_mm(*OUTER_SHELL_BOTTOM_OUTER_REGION_TARGET_MM),
    )

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(abs(OUTER_SHELL_BOTTOM_OUTER_REGION_EXTRUDE_DISTANCE_MM))
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )
    extrudes.add(extrude_input)


def find_arc_edge_near_points_on_xy_plane(body, reference_points_mm, z_value_mm, tolerance_cm=1e-5):
    target_points = [create_point_mm(*point_mm) for point_mm in reference_points_mm]
    target_z = mm_to_cm(z_value_mm)
    candidate_edge = None
    candidate_score = None

    for edge in body.edges:
        geometry = edge.geometry
        circle = adsk.core.Circle3D.cast(geometry)
        arc = adsk.core.Arc3D.cast(geometry)

        if circle:
            center = circle.center
            normal = circle.normal
        elif arc:
            center = arc.center
            normal = arc.normal
        else:
            continue

        if abs(center.z - target_z) > tolerance_cm:
            continue
        if abs(normal.x) > tolerance_cm or abs(normal.y) > tolerance_cm:
            continue

        score = sum(get_nearest_distance_to_edge(edge, point) for point in target_points)
        if candidate_score is None or score < candidate_score:
            candidate_score = score
            candidate_edge = edge

    if not candidate_edge:
        raise RuntimeError('指定条件に一致する円弧エッジを取得できませんでした。')

    return candidate_edge


def apply_constant_radius_fillet(root_comp, edge, radius_mm, tangent_chain=True):
    fillets = root_comp.features.filletFeatures
    fillet_input = fillets.createInput()
    edge_collection = adsk.core.ObjectCollection.create()
    edge_collection.add(edge)

    radius_value = adsk.core.ValueInput.createByReal(mm_to_cm(radius_mm))
    fillet_input.addConstantRadiusEdgeSet(edge_collection, radius_value, tangent_chain)

    return fillets.add(fillet_input)


def add_bottom_outer_arc_fillet(root_comp, outer_shell_body):
    edge = find_arc_edge_near_points_on_xy_plane(
        outer_shell_body,
        OUTER_SHELL_BOTTOM_OUTER_FILLET_REFERENCE_POINTS_MM,
        OUTER_SHELL_BOTTOM_OUTER_FILLET_Z_MM,
    )
    apply_constant_radius_fillet(
        root_comp,
        edge,
        OUTER_SHELL_BOTTOM_OUTER_FILLET_RADIUS_MM,
    )


def build_outer_shell(root_comp, inner_shell_body, params=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if inner_shell_body is None:
        raise RuntimeError('inner_shell_body is required to build the outer shell.')

    if params is None:
        params = dict(naming.DEFAULT_OUTER_SHELL_PARAMS)

    sketch = create_outer_shell_sketch(root_comp, inner_shell_body, params)
    outer_shell_body = extrude_outer_shell_profile(root_comp, sketch, inner_shell_body)
    add_bottom_outer_face(root_comp, outer_shell_body)
    bottom_outer_sketch = create_bottom_outer_face_sketch(root_comp, outer_shell_body)
    extrude_bottom_outer_region(root_comp, bottom_outer_sketch)
    add_bottom_outer_arc_fillet(root_comp, outer_shell_body)
    return outer_shell_body
