"""楕円型握手：楕円中心を反り開始位置に合わせ、＋X側を60°反らす可変厚み立体。"""
import math
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 100.0
MINOR_DIAMETER_MM = 30.0
END_BEND_DEGREES = 60.0
ELLIPSE_CENTER_X_MM = 16.66666666666667
FLAT_THICKNESS_MM = 15.0
TIP_THICKNESS_MM = 20.0
JUNCTION_BLEND_MM = 2.0
OFFSET_SAMPLES = 80
BOUNDARY_SAMPLES_PER_SEGMENT = 64


def bend_start_x_mm():
    return ELLIPSE_CENTER_X_MM


def bend_length_mm():
    return MAJOR_DIAMETER_MM / 2.0


def bend_height_mm(x):
    """開始位置の2 mmだけ曲率を連続にし、以後は確認済みの放物線を保つ。"""
    distance = max(0.0, x - bend_start_x_mm())
    coefficient = math.tan(math.radians(END_BEND_DEGREES)) / (2.0 * bend_length_mm())
    if distance < JUNCTION_BLEND_MM:
        t = distance / JUNCTION_BLEND_MM
        return coefficient * JUNCTION_BLEND_MM ** 2 * (3 * t ** 3 - 3 * t ** 4 + t ** 5)
    return coefficient * distance * distance


def bend_sample_positions(limit):
    start = bend_start_x_mm()
    join = start + JUNCTION_BLEND_MM
    return ([start + JUNCTION_BLEND_MM * i / 40 for i in range(40)]
            + [join + (limit - join) * i / OFFSET_SAMPLES for i in range(OFFSET_SAMPLES + 1)])


def create_ellipse_sketch(root):
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '元の楕円_長径100mm_短径30mm_XY_Z0'
    ellipse = sketch.sketchCurves.sketchEllipses.add(
        adsk.core.Point3D.create(ELLIPSE_CENTER_X_MM / 10.0, 0, 0),
        adsk.core.Point3D.create(ELLIPSE_CENTER_X_MM / 10.0 + MAJOR_DIAMETER_MM / 20.0, 0, 0),
        adsk.core.Point3D.create(ELLIPSE_CENTER_X_MM / 10.0, MINOR_DIAMETER_MM / 20.0, 0))
    if ellipse is None or sketch.profiles.count != 1:
        raise RuntimeError('楕円の閉じた輪郭を作成できませんでした。')
    return sketch


def create_bent_sheet(root):
    """直線と曲率を連続にした反り断面をY方向へ押し出す。"""
    sketch = root.sketches.add(root.xZConstructionPlane)
    sketch.name = '反り断面_楕円中心で分割_＋X側60度'
    half_extent = MAJOR_DIAMETER_MM / 2.0 * 1.1
    length = ELLIPSE_CENTER_X_MM + half_extent
    curve = fitted_curve(sketch, [(x, 0, bend_height_mm(x)) for x in bend_sample_positions(length)])
    flat_start = sketch.modelToSketchSpace(adsk.core.Point3D.create((ELLIPSE_CENTER_X_MM - half_extent) / 10.0, 0, 0))
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(flat_start, curve.startSketchPoint)
    curves = adsk.core.ObjectCollection.create()
    curves.add(line)
    curves.add(curve)
    profile = root.createOpenProfile(curves, False)
    if profile is None:
        raise RuntimeError('反り断面の開いたプロファイルを作成できませんでした。')
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid = False
    # 短辺より広い36 mmの面を作り、後で楕円輪郭に切り出す。
    inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(MINOR_DIAMETER_MM * 1.2 / 10.0), True)
    feature = extrudes.add(inp)
    if feature is None:
        raise RuntimeError('反り基準面の押し出しに失敗しました。')
    bodies = [body for body in feature.bodies if not body.isSolid]
    if len(bodies) != 1:
        raise RuntimeError('反り基準面が1枚のサーフェスではありません。')
    feature.name = '楕円中心から＋X側60度反り基準面'
    sketch.isLightBulbOn = False
    return bodies[0]


def ellipse_level(point):
    a, b = MAJOR_DIAMETER_MM / 20.0, MINOR_DIAMETER_MM / 20.0
    return ((point.x - ELLIPSE_CENTER_X_MM / 10.0) / a) ** 2 + (point.y / b) ** 2


def build(design):
    root = design.rootComponent
    ellipse_sketch = create_ellipse_sketch(root)
    surface = create_bent_sheet(root)
    # 元の楕円からZ方向の工具を作り、平面から見た100×30 mmを維持する。
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(ellipse_sketch.profiles.item(0),
                              adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    half_tool_height_mm = max(50.0, bend_height_mm(ELLIPSE_CENTER_X_MM + MAJOR_DIAMETER_MM / 2.0 * 1.1) + 30.0)
    inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(2.0 * half_tool_height_mm / 10.0), True)
    feature = extrudes.add(inp)
    if feature is None:
        raise RuntimeError('楕円輪郭切り出し工具を作成できませんでした。')
    tools = [body for body in feature.bodies if body.isSolid]
    if len(tools) != 1:
        raise RuntimeError('楕円輪郭切り出し工具を一意に取得できません。')
    tool = tools[0]
    feature.name = '楕円輪郭切り出し工具'
    splits = root.features.splitBodyFeatures
    split = splits.add(splits.createInput(surface, tool, False))
    split.name = '反り面を楕円輪郭で切り出し'
    keep, outside = [], []
    for body in split.bodies:
        if body.isSolid:
            continue
        levels = [ellipse_level(face.pointOnFace) for face in body.faces]
        if levels and all(v < 1.0 - 1e-7 for v in levels):
            keep.append(body)
        elif levels and all(v > 1.0 + 1e-7 for v in levels):
            outside.append(body)
        else:
            raise RuntimeError('楕円輪郭の内側・外側を判定できませんでした。')
    if len(keep) != 1 or not outside:
        raise RuntimeError('反らせた楕円面を一意に取得できません。')
    for body in outside + [tool]:
        removed = root.features.removeFeatures.add(body)
        if removed is None:
            raise RuntimeError('反り面の輪郭外形状を除去できませんでした。')
        removed.name = '反り面の輪郭外と工具を除去'
    result = keep[0]
    if result.isSolid or result.area <= 0:
        raise RuntimeError('反らせた楕円面の形状が不正です。')
    result.name = '楕円型握手_中心移動_−X側平面_＋X側60度反り面'
    result.isLightBulbOn = False
    ellipse_sketch.isLightBulbOn = False
    return create_variable_thickness(root)


def bend_slope(x):
    distance = max(0.0, x - bend_start_x_mm())
    coefficient = math.tan(math.radians(END_BEND_DEGREES)) / (2.0 * bend_length_mm())
    if distance < JUNCTION_BLEND_MM:
        t = distance / JUNCTION_BLEND_MM
        return coefficient * JUNCTION_BLEND_MM * (9 * t ** 2 - 12 * t ** 3 + 5 * t ** 4)
    return 2.0 * coefficient * distance


def thickness_mm(x):
    distance = max(0.0, x - bend_start_x_mm())
    gradient = (TIP_THICKNESS_MM - FLAT_THICKNESS_MM) / bend_length_mm()
    if distance < JUNCTION_BLEND_MM:
        t = distance / JUNCTION_BLEND_MM
        distance = JUNCTION_BLEND_MM * (6 * t ** 3 - 8 * t ** 4 + 3 * t ** 5)
    return FLAT_THICKNESS_MM + gradient * distance


def normal_offset_mm(x, y, distance):
    slope = bend_slope(x)
    norm = math.sqrt(1.0 + slope * slope)
    return (x - distance * slope / norm, y, bend_height_mm(x) + distance / norm)


def sketch_point_mm(sketch, point):
    return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v / 10.0 for v in point)))


def fitted_curve(sketch, points_mm, first=None, last=None):
    points = adsk.core.ObjectCollection.create()
    for i, point in enumerate(points_mm):
        if i == 0 and first is not None:
            points.add(first)
        elif i == len(points_mm) - 1 and last is not None:
            points.add(last)
        else:
            points.add(sketch_point_mm(sketch, point))
    curve = sketch.sketchCurves.sketchFittedSplines.add(points)
    if curve is None:
        raise RuntimeError('可変厚みの補間曲線を作成できませんでした。')
    return curve


def create_thickness_blank(root):
    """表裏の法線オフセット断面を閉じ、Y方向へ押し出す。"""
    sketch = root.sketches.add(root.xZConstructionPlane)
    sketch.name = '可変厚み断面_平面15mm_反り先端20mm'
    start = bend_start_x_mm()
    half_extent = MAJOR_DIAMETER_MM / 2.0 * 1.1
    limit = ELLIPSE_CENTER_X_MM + half_extent
    xs = bend_sample_positions(limit)
    upper = fitted_curve(sketch, [normal_offset_mm(x, 0, thickness_mm(x) / 2.0) for x in xs])
    lower = fitted_curve(sketch, [normal_offset_mm(x, 0, -thickness_mm(x) / 2.0) for x in xs])
    lines = sketch.sketchCurves.sketchLines
    left_top = sketch_point_mm(sketch, (ELLIPSE_CENTER_X_MM - half_extent, 0, FLAT_THICKNESS_MM / 2.0))
    left_bottom = sketch_point_mm(sketch, (ELLIPSE_CENTER_X_MM - half_extent, 0, -FLAT_THICKNESS_MM / 2.0))
    top_line = lines.addByTwoPoints(left_top, upper.startSketchPoint)
    lines.addByTwoPoints(upper.endSketchPoint, lower.endSketchPoint)
    bottom_line = lines.addByTwoPoints(lower.startSketchPoint, left_bottom)
    lines.addByTwoPoints(bottom_line.endSketchPoint, top_line.startSketchPoint)
    if sketch.profiles.count != 1:
        raise RuntimeError('可変厚みの閉じた断面が1つになりませんでした。')
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(MINOR_DIAMETER_MM * 1.2 / 10.0), True)
    feature = extrudes.add(inp)
    if feature is None:
        raise RuntimeError('可変厚みソリッドの押し出しに失敗しました。')
    bodies = [body for body in feature.bodies if body.isSolid]
    if len(bodies) != 1:
        raise RuntimeError('可変厚みの基準ソリッドを一意に取得できません。')
    feature.name = '法線方向の可変厚み断面を押し出し'
    sketch.isLightBulbOn = False
    return bodies[0]


def create_normal_outline_tool(root):
    """元の楕円輪郭を法線方向へ延ばした壁面で、端の厚みも維持する。"""
    a, b = MAJOR_DIAMETER_MM / 2.0, MINOR_DIAMETER_MM / 2.0
    angle = math.acos((bend_start_x_mm() - ELLIPSE_CENTER_X_MM) / a)
    blend_angle = math.acos((bend_start_x_mm() + JUNCTION_BLEND_MM - ELLIPSE_CENTER_X_MM) / a)
    breaks = (0.0, blend_angle, angle, math.pi, math.tau - angle, math.tau - blend_angle, math.tau)
    paths, sketches = [], []
    # 曲率半径より小さく、総厚20 mmの表裏を覆う範囲で輪郭壁を作る。
    for distance in (-12.0, 12.0):
        sketch = root.sketches.add(root.xYConstructionPlane)
        sketch.name = '法線方向輪郭工具_{:+g}mm'.format(distance)
        curves = adsk.core.ObjectCollection.create()
        first_point = previous_end = None
        for segment in range(len(breaks) - 1):
            lo, hi = breaks[segment:segment + 2]
            points = []
            for i in range(BOUNDARY_SAMPLES_PER_SEGMENT + 1):
                t = lo + (hi - lo) * i / BOUNDARY_SAMPLES_PER_SEGMENT
                points.append(normal_offset_mm(ELLIPSE_CENTER_X_MM + a * math.cos(t), b * math.sin(t), distance))
            curve = fitted_curve(sketch, points, previous_end,
                                 first_point if segment == len(breaks) - 2 else None)
            if first_point is None:
                first_point = curve.startSketchPoint
            previous_end = curve.endSketchPoint
            curves.add(curve)
        path = adsk.fusion.Path.create(curves, adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None:
            raise RuntimeError('法線方向の楕円輪郭工具を閉じられませんでした。')
        paths.append(path)
        sketches.append(sketch)
    lofts = root.features.loftFeatures
    inp = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid = False
    inp.isClosed = False
    for path in paths:
        inp.loftSections.add(path)
    feature = lofts.add(inp)
    if feature is None:
        raise RuntimeError('法線方向の輪郭壁面を作成できませんでした。')
    bodies = [body for body in feature.bodies if not body.isSolid]
    if len(bodies) != 1:
        raise RuntimeError('法線方向の輪郭壁面を一意に取得できません。')
    feature.name = '元の楕円輪郭を法線方向へ延ばした工具壁面'
    for sketch in sketches:
        sketch.isLightBulbOn = False
    return bodies[0]


def create_variable_thickness(root):
    blank = create_thickness_blank(root)
    tool = create_normal_outline_tool(root)
    splits = root.features.splitBodyFeatures
    feature = splits.add(splits.createInput(blank, tool, False))
    feature.name = '可変厚みソリッドを法線方向の楕円輪郭で切り出し'
    keep, outside = [], []
    origin = adsk.core.Point3D.create(ELLIPSE_CENTER_X_MM / 10.0, 0, 0)
    for body in feature.bodies:
        if not body.isSolid:
            continue
        if body.pointContainment(origin) == adsk.fusion.PointContainment.PointInsidePointContainment:
            keep.append(body)
        else:
            outside.append(body)
    if len(keep) != 1 or not outside:
        raise RuntimeError('楕円輪郭内の可変厚みソリッドを一意に取得できません。')
    for body in outside + [tool]:
        removed = root.features.removeFeatures.add(body)
        if removed is None:
            raise RuntimeError('可変厚みの輪郭外形状と工具を除去できませんでした。')
        removed.name = '可変厚みの輪郭外形状と工具を除去'
    result = keep[0]
    if not result.isSolid or not math.isfinite(result.volume) or result.volume <= 0:
        raise RuntimeError('可変厚みの最終ソリッドが不正です。')
    # 補間面を実際に検査し、各測定点で指定厚みの内外が一致することを確認する。
    start = bend_start_x_mm()
    tip = ELLIPSE_CENTER_X_MM + MAJOR_DIAMETER_MM / 2.0
    for x in (ELLIPSE_CENTER_X_MM - MAJOR_DIAMETER_MM / 4.0, ELLIPSE_CENTER_X_MM - MAJOR_DIAMETER_MM / 8.0, start, start + (tip - start) * .25,
              start + (tip - start) * .5, start + (tip - start) * .75, tip - .5):
        for sign in (-1, 1):
            for delta, expected in ((-.05, adsk.fusion.PointContainment.PointInsidePointContainment),
                                    (.05, adsk.fusion.PointContainment.PointOutsidePointContainment)):
                point = normal_offset_mm(x, 0, sign * (thickness_mm(x) / 2.0 + delta))
                actual = result.pointContainment(adsk.core.Point3D.create(*(v / 10.0 for v in point)))
                if actual != expected:
                    raise RuntimeError('法線方向の厚み検証に失敗しました。X={:.4f} mm'.format(x))
    result.name = '楕円型握手_平面15mm_反り15～20mm'
    result.isLightBulbOn = True
    return result


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
        if design is None:
            raise RuntimeError('新しいFusionデザインを取得できませんでした。')
        document.name = MODEL_NAME
        build(design)
        app.activeViewport.fit()
        ui.messageBox('楕円型握手：楕円中心を反り開始位置（X約16.667 mm）に移しました。\n中心から−X側50 mmは平面、＋X側50 mmは先端60°・高さ約43.301 mmです。\n元の面を中央に、法線方向で平面部15 mm・反り開始15 mm→先端20 mmの厚みを付けました。')
    except Exception:
        ui.messageBox(traceback.format_exc())
