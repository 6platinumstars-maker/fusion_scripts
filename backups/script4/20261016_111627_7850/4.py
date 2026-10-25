"""独立した立体作成用のFusionスクリプト。"""
import math
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 100.0
MINOR_DIAMETER_MM = 80.0
TWIST_DEGREES = 60.0
LOFT_INTERVALS = 24


def build(design):
    """XY面（Z=0）に原点中心の100×80 mm楕円を描く。"""
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '楕円_長径100mm_短径80mm_XY_Z0'
    # Fusion内部単位はcm。直径mmを半径cmへ変換する。
    center = adsk.core.Point3D.create(0, 0, 0)
    major_end = adsk.core.Point3D.create(MAJOR_DIAMETER_MM / 20.0, 0, 0)
    minor_end = adsk.core.Point3D.create(0, MINOR_DIAMETER_MM / 20.0, 0)
    ellipse = sketch.sketchCurves.sketchEllipses.add(center, major_end, minor_end)
    if ellipse is None:
        raise RuntimeError('楕円を作成できませんでした。')
    sketch.isLightBulbOn = True
    create_flat_half(root)
    create_twisted_half(root)
    return sketch


def section_endpoints_mm(x):
    """回転後の断面両端。theta(x)=60°×x/50 mm、回転軸はX軸。"""
    a = MAJOR_DIAMETER_MM / 2.0
    b = MINOR_DIAMETER_MM / 2.0
    if not 0.0 <= x <= a:
        raise ValueError('ねじり断面は0～50 mmの範囲で指定してください。')
    radius = b * math.sqrt(max(0.0, 1.0 - (x / a) ** 2))
    theta = math.radians(TWIST_DEGREES) * x / a
    y, z = radius * math.cos(theta), radius * math.sin(theta)
    return (x, -y, -z), (x, y, z)


def surface_body(feature, name):
    if feature is None or feature.bodies.count != 1:
        raise RuntimeError(name + 'を1つの面ボディとして作成できませんでした。')
    body = feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area <= 0:
        raise RuntimeError(name + 'の面形状が不正です。')
    body.name = name
    body.isLightBulbOn = True
    feature.name = name
    return body


def create_flat_half(root):
    """−X側は正確な半楕円の平面パッチとする。"""
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '−X側_半楕円輪郭'
    arc = sketch.sketchCurves.sketchEllipticalArcs.addByAngle(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Vector3D.create(MAJOR_DIAMETER_MM / 20.0, 0, 0),
        adsk.core.Vector3D.create(0, MINOR_DIAMETER_MM / 20.0, 0),
        math.pi / 2.0, math.pi)
    if arc is None:
        raise RuntimeError('−X側の半楕円を作成できませんでした。')
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(
        arc.endSketchPoint, arc.startSketchPoint)
    boundary = adsk.core.ObjectCollection.create()
    boundary.add(arc)
    boundary.add(line)
    patches = root.features.patchFeatures
    inp = patches.createInput(boundary, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = surface_body(patches.add(inp), '楕円型握手_−X側平面')
    sketch.isLightBulbOn = False
    return body


def create_twisted_half(root):
    """回転断面を補間する開いたサーフェスロフト。先端は点へ収束。"""
    lofts = root.features.loftFeatures
    inp = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid = False
    inp.isClosed = False
    a = MAJOR_DIAMETER_MM / 2.0
    sketches, planes = [], []
    # 楕円先端付近を密にし、幅がゼロになる先端まで作る。
    for i in range(LOFT_INTERVALS + 1):
        x = a if i == LOFT_INTERVALS else a * math.sin(math.pi * i / (2 * LOFT_INTERVALS))
        plane_input = root.constructionPlanes.createInput()
        plane_input.setByOffset(root.yZConstructionPlane, adsk.core.ValueInput.createByReal(x / 10.0))
        plane = root.constructionPlanes.add(plane_input)
        plane.name = 'ねじり断面平面_X{:.3f}mm'.format(x)
        planes.append(plane)
        sketch = root.sketches.add(plane)
        sketch.name = 'ねじり断面_X{:.3f}mm_{:.3f}deg'.format(x, TWIST_DEGREES * x / a)
        sketches.append(sketch)
        def local(point_mm):
            return sketch.modelToSketchSpace(adsk.core.Point3D.create(*(v / 10.0 for v in point_mm)))
        if i == LOFT_INTERVALS:
            section = sketch.sketchPoints.add(local((a, 0, 0)))
        else:
            ends = section_endpoints_mm(x)
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(local(ends[0]), local(ends[1]))
            section = adsk.fusion.Path.create(line, adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if section is None or inp.loftSections.add(section) is None:
            raise RuntimeError('ねじりロフト断面を設定できませんでした。X={:.3f} mm'.format(x))
    body = surface_body(lofts.add(inp), '楕円型握手_＋X側ねじり60度')
    for entity in sketches + planes:
        entity.isLightBulbOn = False
    return body


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        # 実行前に開いていたデザインを変更せず、毎回専用デザインを作る。
        document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
        if design is None:
            raise RuntimeError('新しいFusionデザインを取得できませんでした。')
        document.name = MODEL_NAME
        build(design)
        app.activeViewport.fit()
        ui.messageBox('楕円型握手：面を作成しました。\n−X側はXY平面、＋X側は原点0°から先端60°へ徐々にねじります。')
    except Exception:
        ui.messageBox(traceback.format_exc())
