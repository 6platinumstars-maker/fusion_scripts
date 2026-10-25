"""楕円型握手：基準点を長径の1/3位置にした100×30 mmの卵形の短い側を60°反らせた面。"""
import math
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
TOTAL_LENGTH_MM = 100.0
MINOR_DIAMETER_MM = 30.0
SHORT_SIDE_FRACTION = 1.0 / 3.0
END_BEND_DEGREES = 60.0


def create_egg_sketch(root):
    """XY面・Z=0。基準点を原点とし、左1/3・右2/3の半楕円弧を接続する。"""
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '卵形_全長100mm_短径30mm_基準点1／3'
    short_radius_mm = TOTAL_LENGTH_MM * SHORT_SIDE_FRACTION
    long_radius_mm = TOTAL_LENGTH_MM - short_radius_mm
    minor_radius_mm = MINOR_DIAMETER_MM / 2.0
    center = adsk.core.Point3D.create(0, 0, 0)
    minor = adsk.core.Vector3D.create(0, minor_radius_mm / 10.0, 0)
    arcs = sketch.sketchCurves.sketchEllipticalArcs
    left = arcs.addByAngle(center,
        adsk.core.Vector3D.create(short_radius_mm / 10.0, 0, 0),
        minor, math.pi / 2.0, math.pi)
    right = arcs.addByAngle(center,
        adsk.core.Vector3D.create(long_radius_mm / 10.0, 0, 0),
        minor, 3.0 * math.pi / 2.0, math.pi)
    if left is None or right is None:
        raise RuntimeError('左右の半楕円弧を作成できませんでした。')
    # 共通の短径端（0,±15 mm）で接続し、接線はどちらもX方向となる。
    if (left.startSketchPoint.worldGeometry.distanceTo(right.endSketchPoint.worldGeometry) > 1e-6
            or left.endSketchPoint.worldGeometry.distanceTo(right.startSketchPoint.worldGeometry) > 1e-6):
        raise RuntimeError('左右の半楕円弧の接続点が一致しません。')
    lines = sketch.sketchCurves.sketchLines
    length_axis = lines.addByTwoPoints(
        adsk.core.Point3D.create(-short_radius_mm / 10.0, 0, 0),
        adsk.core.Point3D.create(long_radius_mm / 10.0, 0, 0))
    length_axis.isConstruction = True
    width_axis = lines.addByTwoPoints(
        adsk.core.Point3D.create(0, -minor_radius_mm / 10.0, 0),
        adsk.core.Point3D.create(0, minor_radius_mm / 10.0, 0))
    width_axis.isConstruction = True
    if sketch.profiles.count != 1:
        raise RuntimeError('卵形の閉じた輪郭が1つになりませんでした。')
    sketch.isLightBulbOn = True
    return sketch


def bend_height_mm(x):
    """短い−X側だけを＋Zへ反らす。原点の傾き0°、−X端の傾き60°。"""
    short_length = TOTAL_LENGTH_MM * SHORT_SIDE_FRACTION
    distance = max(0.0, -x)
    return math.tan(math.radians(END_BEND_DEGREES)) * distance ** 2 / (2.0 * short_length)


def egg_level(point):
    """卵形の投影輪郭の内外を判定する。pointはFusionのcm。"""
    short_length = TOTAL_LENGTH_MM * SHORT_SIDE_FRACTION
    long_length = TOTAL_LENGTH_MM - short_length
    radius_cm = (short_length if point.x < 0 else long_length) / 10.0
    minor_cm = MINOR_DIAMETER_MM / 20.0
    return (point.x / radius_cm) ** 2 + (point.y / minor_cm) ** 2


def create_bent_sheet(root):
    sketch = root.sketches.add(root.xZConstructionPlane)
    sketch.name = '卵形反り断面_−X短辺側60度_＋X長辺側平面'
    short_length = TOTAL_LENGTH_MM * SHORT_SIDE_FRACTION
    long_length = TOTAL_LENGTH_MM - short_length
    left_extent, right_extent = short_length * 1.1, long_length * 1.1
    height = bend_height_mm(-left_extent)
    # 2次ベジェで正確な放物線を作る。原点側の接線は水平。
    controls_mm = ((-left_extent, 0, height), (-left_extent / 2.0, 0, 0), (0, 0, 0))
    controls = [sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v / 10.0 for v in point)))
                for point in controls_mm]
    nurbs = adsk.core.NurbsCurve3D.createNonRational(controls, 2, [0, 0, 0, 1, 1, 1], False)
    if nurbs is None:
        raise RuntimeError('卵形の反り断面を定義できませんでした。')
    curve = sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(nurbs)
    if curve is None:
        raise RuntimeError('卵形の反り断面をスケッチに追加できませんでした。')
    flat_end = sketch.modelToSketchSpace(adsk.core.Point3D.create(right_extent / 10.0, 0, 0))
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(curve.endSketchPoint, flat_end)
    curves = adsk.core.ObjectCollection.create()
    curves.add(curve)
    curves.add(line)
    profile = root.createOpenProfile(curves, False)
    if profile is None:
        raise RuntimeError('卵形の反り断面プロファイルを作成できませんでした。')
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid = False
    inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(MINOR_DIAMETER_MM * 1.2 / 10.0), True)
    feature = extrudes.add(inp)
    if feature is None:
        raise RuntimeError('卵形の反り基準面を作成できませんでした。')
    bodies = [body for body in feature.bodies if not body.isSolid]
    if len(bodies) != 1:
        raise RuntimeError('卵形の反り基準面が1つのサーフェスではありません。')
    feature.name = '卵形_短い側60度の反り基準面'
    sketch.isLightBulbOn = False
    return bodies[0]


def build(design):
    root = design.rootComponent
    sketch = create_egg_sketch(root)
    surface = create_bent_sheet(root)
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    half_height_mm = max(50.0, bend_height_mm(-TOTAL_LENGTH_MM * SHORT_SIDE_FRACTION * 1.1) + 10.0)
    inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(2.0 * half_height_mm / 10.0), True)
    feature = extrudes.add(inp)
    if feature is None:
        raise RuntimeError('卵形の輪郭工具を作成できませんでした。')
    tools = [body for body in feature.bodies if body.isSolid]
    if len(tools) != 1:
        raise RuntimeError('卵形の輪郭工具を一意に取得できません。')
    tool = tools[0]
    feature.name = '卵形_輪郭切り出し工具'
    splits = root.features.splitBodyFeatures
    split = splits.add(splits.createInput(surface, tool, False))
    split.name = '反り面を卵形輪郭で切り出し'
    keep, outside = [], []
    for body in split.bodies:
        if body.isSolid:
            continue
        levels = [egg_level(face.pointOnFace) for face in body.faces]
        if levels and all(level < 1.0 - 1e-7 for level in levels):
            keep.append(body)
        elif levels and all(level > 1.0 + 1e-7 for level in levels):
            outside.append(body)
        else:
            raise RuntimeError('卵形輪郭の内外を判定できませんでした。')
    if len(keep) != 1 or not outside:
        raise RuntimeError('卵形の反り面を一意に取得できません。')
    for body in outside + [tool]:
        removed = root.features.removeFeatures.add(body)
        if removed is None:
            raise RuntimeError('卵形の輪郭外形状と工具を除去できませんでした。')
        removed.name = '卵形の余剰面と工具を除去'
    result = keep[0]
    if result.isSolid or not math.isfinite(result.area) or result.area <= 0:
        raise RuntimeError('卵形の反り面の形状が不正です。')
    result.name = '楕円型握手_卵形_短い−X側60度反り面'
    result.isLightBulbOn = True
    sketch.isLightBulbOn = False
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
        ui.messageBox('楕円型握手：卵形の面を作成し、短い−X側だけを＋Zへ60°反らせました。\n基準点で傾き0°、短い側の先端高さは約28.868 mmです。\n長い＋X側は平面です。厚みはありません。')
    except Exception:
        ui.messageBox(traceback.format_exc())
