import adsk.core
import adsk.fusion


def is_close(value_a, value_b, tolerance=1e-6):
    return abs(value_a - value_b) <= tolerance


def points_are_equal(point_a, point_b, tolerance=1e-6):
    return (
        is_close(point_a.x, point_b.x, tolerance)
        and is_close(point_a.y, point_b.y, tolerance)
        and is_close(point_a.z, point_b.z, tolerance)
    )


def get_body_from_feature(feature):
    body = feature.bodies.item(0)
    if not body:
        raise RuntimeError('ボディを取得できませんでした。')
    return body


def get_largest_profile(sketch):
    largest_profile = None
    largest_area = -1

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        area = profile.areaProperties().area
        if area > largest_area:
            largest_area = area
            largest_profile = profile

    if not largest_profile:
        raise RuntimeError('スケッチからプロファイルを取得できませんでした。')

    return largest_profile


def get_face_edges(face):
    return [face.edges.item(index) for index in range(face.edges.count)]


def get_edge_vertices(edge):
    return [edge.startVertex, edge.endVertex]


def get_vertex_point(vertex):
    return vertex.geometry


def get_edge_length(edge):
    return edge.length


def get_edge_points(edge):
    start_point = get_vertex_point(edge.startVertex)
    end_point = get_vertex_point(edge.endVertex)
    return start_point, end_point


def is_point_on_line_segment(point, start_point, end_point, tolerance=1e-6):
    segment_vector = adsk.core.Vector3D.create(
        end_point.x - start_point.x,
        end_point.y - start_point.y,
        end_point.z - start_point.z,
    )
    point_vector = adsk.core.Vector3D.create(
        point.x - start_point.x,
        point.y - start_point.y,
        point.z - start_point.z,
    )

    segment_length = segment_vector.length
    if is_close(segment_length, 0.0, tolerance):
        return points_are_equal(point, start_point, tolerance)

    cross_vector = segment_vector.crossProduct(point_vector)
    if cross_vector.length > tolerance:
        return False

    dot_product = (
        point_vector.x * segment_vector.x
        + point_vector.y * segment_vector.y
        + point_vector.z * segment_vector.z
    )
    if dot_product < -tolerance:
        return False

    if dot_product - (segment_length * segment_length) > tolerance:
        return False

    return True


def edge_passes_through_point(edge, point, tolerance=1e-6):
    start_point, end_point = get_edge_points(edge)
    return is_point_on_line_segment(point, start_point, end_point, tolerance)


def find_face_by_axis_value(body, axis, value, tolerance=1e-6):
    for face in body.faces:
        box = face.boundingBox
        min_value = getattr(box.minPoint, axis)
        max_value = getattr(box.maxPoint, axis)
        if is_close(min_value, value, tolerance) and is_close(max_value, value, tolerance):
            return face
    raise RuntimeError('指定条件に一致する面を取得できませんでした。')


def find_longest_edge(face):
    edges = get_face_edges(face)
    if not edges:
        raise RuntimeError('面から辺を取得できませんでした。')
    return max(edges, key=get_edge_length)


def find_shortest_edge(face):
    edges = get_face_edges(face)
    if not edges:
        raise RuntimeError('面から辺を取得できませんでした。')
    return min(edges, key=get_edge_length)


def find_edge_by_constant_axis(face, axis, value, tolerance=1e-6):
    for edge in get_face_edges(face):
        start_point, end_point = get_edge_points(edge)
        start_value = getattr(start_point, axis)
        end_value = getattr(end_point, axis)
        if is_close(start_value, value, tolerance) and is_close(end_value, value, tolerance):
            return edge
    raise RuntimeError('指定条件に一致する辺を取得できませんでした。')


def find_vertex_by_coordinates(vertices, x=None, y=None, z=None, tolerance=1e-6):
    for vertex in vertices:
        point = get_vertex_point(vertex)
        if x is not None and not is_close(point.x, x, tolerance):
            continue
        if y is not None and not is_close(point.y, y, tolerance):
            continue
        if z is not None and not is_close(point.z, z, tolerance):
            continue
        return vertex
    raise RuntimeError('指定条件に一致する頂点を取得できませんでした。')


def find_face_through_origin(body, tolerance=1e-6):
    origin = adsk.core.Point3D.create(0.0, 0.0, 0.0)

    for face in body.faces:
        for edge in get_face_edges(face):
            if edge_passes_through_point(edge, origin, tolerance):
                return face

    raise RuntimeError('原点を通る面を取得できませんでした。')


def create_sketch_on_face(root_comp, face, name):
    sketch = root_comp.sketches.add(face)
    sketch.name = name
    return sketch


def project_face_edges(sketch, face):
    projected_items = []

    for edge in get_face_edges(face):
        projected = sketch.project(edge)
        for index in range(projected.count):
            projected_items.append(projected.item(index))

    return projected_items
