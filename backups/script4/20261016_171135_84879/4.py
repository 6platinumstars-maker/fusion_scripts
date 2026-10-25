"""楕円型握手：基準点を長径の1/3位置にした100×30 mmの卵形スケッチ。"""
import math
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
TOTAL_LENGTH_MM = 100.0
MINOR_DIAMETER_MM = 30.0
SHORT_SIDE_FRACTION = 1.0 / 3.0


def build(design):
    """XY面・Z=0。基準点を原点とし、左1/3・右2/3の半楕円弧を接続する。"""
    root = design.rootComponent
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
        ui.messageBox('楕円型握手：卵形のスケッチを作成しました。\n全長100 mm・短径30 mm、XY面・Z=0 mm。\n短径中央を原点とし、左33.333 mm・右66.667 mmです。')
    except Exception:
        ui.messageBox(traceback.format_exc())
