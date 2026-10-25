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
THICKNESS_PER_SIDE_MM = 7.5


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
    twisted_body = create_twisted_half(root)
    cut_negative_z(root, twisted_body)
    thicken_surfaces(root)
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


def cut_negative_z(root, body):
    """ねじり面をXY面で分割し、Z<0側の面ボディを除去する。"""
    tolerance_cm = 1e-5
    splits = root.features.splitBodyFeatures
    split_input = splits.createInput(body, root.xYConstructionPlane, True)
    if split_input is None:
        raise RuntimeError('Z=0面による分割を設定できませんでした。')
    split = splits.add(split_input)
    split.name = '楕円型握手_Z0面で分割'
    pieces = list(split.bodies)
    if len(pieces) < 2:
        raise RuntimeError('ねじり面をZ=0で複数の面に分割できませんでした。')
    keep, remove = [], []
    for piece in pieces:
        box = piece.boundingBox
        if box.maxPoint.z <= tolerance_cm and box.minPoint.z < -tolerance_cm:
            remove.append(piece)
        elif box.minPoint.z >= -tolerance_cm and box.maxPoint.z > tolerance_cm:
            keep.append(piece)
        else:
            raise RuntimeError('分割面のZ方向を判定できませんでした。')
    if not keep or not remove:
        raise RuntimeError('Zの正側・負側の両方を確認できませんでした。')
    for piece in remove:
        feature = root.features.removeFeatures.add(piece)
        if feature is None:
            raise RuntimeError('−Z側の面を除去できませんでした。')
        feature.name = '楕円型握手_−Z部分を切り取り'
    for i, piece in enumerate(keep):
        piece.name = '楕円型握手_＋X側ねじり60度_Z正側' + ('' if i == 0 else '_{}'.format(i + 1))
        piece.isLightBulbOn = True
    for remaining in root.bRepBodies:
        if remaining.boundingBox.minPoint.z < -tolerance_cm:
            raise RuntimeError('切り取り後もZ<0の面が残っています。')
    return keep


def thicken_surfaces(root):
    """切り取り後の各面を法線の両側へ7.5 mmずつ厚み付けする。"""
    sources = [body for body in root.bRepBodies if not body.isSolid]
    if len(sources) < 2:
        raise RuntimeError('厚み付け対象の平面とねじり面がそろっていません。')
    thickens = root.features.thickenFeatures
    solids = []
    for source in sources:
        name = source.name
        surfaces = adsk.core.ObjectCollection.create()
        surfaces.add(source)
        # 対称厚み付けのthicknessは片側の距離。0.75 cm × 両側 = 15 mm。
        thickness = adsk.core.ValueInput.createByReal(THICKNESS_PER_SIDE_MM / 10.0)
        inp = thickens.createInput(surfaces, thickness, True,
                                  adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        if inp is None:
            raise RuntimeError(name + 'の対称厚み付けを設定できませんでした。')
        feature = thickens.add(inp)
        if feature is None or feature.bodies.count == 0:
            raise RuntimeError(name + 'の厚み付けに失敗しました。')
        feature.name = name + '_両側7.5mm厚み付け'
        for i, body in enumerate(feature.bodies):
            if not body.isSolid or not math.isfinite(body.volume) or body.volume <= 0:
                raise RuntimeError(name + 'を有効なソリッドにできませんでした。')
            body.name = name + '_厚さ15mm' + ('' if i == 0 else '_{}'.format(i + 1))
            body.isLightBulbOn = True
            solids.append(body)
        if source.isValid:
            source.isLightBulbOn = False
    return solids


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
        ui.messageBox('楕円型握手：厚み付きの立体を作成しました。\n−X側はXY平面、＋X側は原点0°から先端60°へ徐々にねじります。\nZ=0面で分割し、−Z部分を切り取り後、各面の両側へ7.5 mmずつ厚み付けしました（合計15 mm）。')
    except Exception:
        ui.messageBox(traceback.format_exc())
