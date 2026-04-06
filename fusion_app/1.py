import adsk.core
import adsk.fusion
import traceback
import math
import os
import sys

def create_base_sketch(root_comp):
    rect_left = 7.0
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

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
