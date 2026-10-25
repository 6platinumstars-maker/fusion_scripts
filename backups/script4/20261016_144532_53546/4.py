"""楕円型握手：XY面上の100×30 mmの楕円面だけを作成する。"""
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 100.0
MINOR_DIAMETER_MM = 30.0


def build(design):
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '楕円_長径{:g}mm_短径{:g}mm_XY_Z0'.format(MAJOR_DIAMETER_MM, MINOR_DIAMETER_MM)
    # Fusion内部単位はcm。直径mmを半径cmへ変換する。
    ellipse = sketch.sketchCurves.sketchEllipses.add(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(MAJOR_DIAMETER_MM / 20.0, 0, 0),
        adsk.core.Point3D.create(0, MINOR_DIAMETER_MM / 20.0, 0))
    if ellipse is None or sketch.profiles.count != 1:
        raise RuntimeError('楕円の閉じた輪郭を作成できませんでした。')
    patches = root.features.patchFeatures
    inp = patches.createInput(sketch.profiles.item(0),
                              adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    feature = patches.add(inp)
    if feature is None or feature.bodies.count != 1:
        raise RuntimeError('楕円面を1つのサーフェスとして作成できませんでした。')
    body = feature.bodies.item(0)
    if body.isSolid or body.area <= 0:
        raise RuntimeError('楕円面の形状が不正です。')
    feature.name = '楕円面_100×30mm_XY_Z0'
    body.name = '楕円型握手_楕円面'
    body.isLightBulbOn = True
    sketch.isLightBulbOn = False
    return body


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
        ui.messageBox('楕円型握手：長径100 mm・短径30 mmの平らな楕円面を作成しました。\nXY面・Z=0 mm、原点中心です。')
    except Exception:
        ui.messageBox(traceback.format_exc())
