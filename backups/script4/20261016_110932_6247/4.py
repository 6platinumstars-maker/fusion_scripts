"""独立した立体作成用のFusionスクリプト。"""
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 100.0
MINOR_DIAMETER_MM = 80.0


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
    return sketch


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
        design.rootComponent.name = MODEL_NAME
        build(design)
        app.activeViewport.fit()
        ui.messageBox('楕円型握手：楕円スケッチを作成しました。\nXY面・Z=0 mm、原点中心、X方向100 mm × Y方向80 mm。')
    except Exception:
        ui.messageBox(traceback.format_exc())
