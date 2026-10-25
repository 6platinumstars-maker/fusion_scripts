"""楕円型握手：短辺を中心に両端を＋Zへ30°反らす楕円面。"""
import math
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 100.0
MINOR_DIAMETER_MM = 30.0
END_BEND_DEGREES = 30.0


def bend_height_mm(x):
    """z=k*x²。中央の傾き0°、長辺の両端の傾きは±30°。"""
    a = MAJOR_DIAMETER_MM / 2.0
    return math.tan(math.radians(END_BEND_DEGREES)) * x * x / (2.0 * a)


def create_ellipse_sketch(root):
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '元の楕円_長径100mm_短径30mm_XY_Z0'
    ellipse = sketch.sketchCurves.sketchEllipses.add(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(MAJOR_DIAMETER_MM / 20.0, 0, 0),
        adsk.core.Point3D.create(0, MINOR_DIAMETER_MM / 20.0, 0))
    if ellipse is None or sketch.profiles.count != 1:
        raise RuntimeError('楕円の閉じた輪郭を作成できませんでした。')
    return sketch


def create_bent_sheet(root):
    """正確な2次ベジェ曲線をY方向へ押し出し、滑らかな放物面を作る。"""
    sketch = root.sketches.add(root.xZConstructionPlane)
    sketch.name = '反り断面_中央0度_両端30度'
    length = MAJOR_DIAMETER_MM / 2.0 * 1.1
    height = bend_height_mm(length)
    # 3つの制御点を持つ2次ベジェで z=k*x² を正確に表す。
    control_mm = ((-length, 0, height), (0, 0, -height), (length, 0, height))
    control = [sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v / 10.0 for v in point)))
               for point in control_mm]
    nurbs = adsk.core.NurbsCurve3D.createNonRational(control, 2, [0, 0, 0, 1, 1, 1], False)
    if nurbs is None:
        raise RuntimeError('反り断面の曲線を作成できませんでした。')
    curve = sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(nurbs)
    if curve is None:
        raise RuntimeError('反り断面をスケッチへ追加できませんでした。')
    profile = root.createOpenProfile(curve, False)
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
    feature.name = '両端30度反り基準面'
    sketch.isLightBulbOn = False
    return bodies[0]


def ellipse_level(point):
    a, b = MAJOR_DIAMETER_MM / 20.0, MINOR_DIAMETER_MM / 20.0
    return (point.x / a) ** 2 + (point.y / b) ** 2


def build(design):
    root = design.rootComponent
    ellipse_sketch = create_ellipse_sketch(root)
    surface = create_bent_sheet(root)
    # 元の楕円からZ方向の工具を作り、平面から見た100×30 mmを維持する。
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(ellipse_sketch.profiles.item(0),
                              adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(10.0), True)
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
    result.name = '楕円型握手_両端＋Z30度反り面'
    result.isLightBulbOn = True
    ellipse_sketch.isLightBulbOn = False
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
        ui.messageBox('楕円型握手：長辺の両端を＋Z側へ30°ずつ反らせました。\n中央はZ=0・傾き0°、両端の高さは約14.434 mmです。\n平面から見た長径100 mm・短径30 mmを維持した、厚みのない面です。')
    except Exception:
        ui.messageBox(traceback.format_exc())
