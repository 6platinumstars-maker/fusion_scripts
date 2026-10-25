"""独立した立体作成用のFusionスクリプト。"""
import math
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 100.0
MINOR_DIAMETER_MM = 80.0
TWIST_DEGREES = 90.0
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
    """回転後の断面両端。theta(x)=90°×x/50 mm、回転軸はX軸。"""
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
    """幅を保ったねじり面を作り、回転楕円体で所定輪郭に切り出す。"""
    lofts = root.features.loftFeatures
    inp = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid = False
    inp.isClosed = False
    a = MAJOR_DIAMETER_MM / 2.0
    sketches, planes = [], []
    # X=50 mmの先端を面の内部に置き、ロフトの点収束を避ける。
    for i in range(LOFT_INTERVALS + 1):
        x = a * 1.1 * i / LOFT_INTERVALS
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
        theta = math.radians(TWIST_DEGREES) * x / a
        radius = MINOR_DIAMETER_MM / 2.0 * 1.125
        y, z = radius * math.cos(theta), radius * math.sin(theta)
        ends = ((x, -y, -z), (x, y, z))
        line = sketch.sketchCurves.sketchLines.addByTwoPoints(local(ends[0]), local(ends[1]))
        section = adsk.fusion.Path.create(line, adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if section is None or inp.loftSections.add(section) is None:
            raise RuntimeError('ねじりロフト断面を設定できませんでした。X={:.3f} mm'.format(x))
    body = surface_body(lofts.add(inp), '楕円型握手_ねじり基準拡張面')
    for entity in sketches + planes:
        entity.isLightBulbOn = False
    return trim_to_elliptical_outline(root, body)


def ellipsoid_level(point):
    """回転前の楕円半幅を満たす回転楕円体。pointはFusionのcm。"""
    a, b = MAJOR_DIAMETER_MM / 20.0, MINOR_DIAMETER_MM / 20.0
    return (point.x / a) ** 2 + (point.y ** 2 + point.z ** 2) / b ** 2


def trim_to_elliptical_outline(root, surface):
    """正則なねじり面を x²/a²+(y²+z²)/b²=1 の内側へトリム。"""
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '楕円型握手_輪郭切り出し工具'
    arc = sketch.sketchCurves.sketchEllipticalArcs.addByAngle(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Vector3D.create(MAJOR_DIAMETER_MM / 20.0, 0, 0),
        adsk.core.Vector3D.create(0, MINOR_DIAMETER_MM / 20.0, 0),
        0.0, math.pi)
    if arc is None:
        raise RuntimeError('輪郭切り出し工具の楕円弧を作成できませんでした。')
    axis = sketch.sketchCurves.sketchLines.addByTwoPoints(arc.endSketchPoint, arc.startSketchPoint)
    if sketch.profiles.count != 1:
        raise RuntimeError('輪郭切り出し工具の半楕円プロファイルを確認できません。')
    revolves = root.features.revolveFeatures
    inp = revolves.createInput(sketch.profiles.item(0), axis,
                               adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))
    revolve = revolves.add(inp)
    revolve.name = '楕円型握手_輪郭工具回転楕円体'
    tools = [b for b in revolve.bodies if b.isSolid]
    if len(tools) != 1:
        raise RuntimeError('輪郭切り出し用の回転楕円体を作成できませんでした。')
    tool = tools[0]
    splits = root.features.splitBodyFeatures
    split = splits.add(splits.createInput(surface, tool, False))
    split.name = '楕円型握手_拡張面を楕円輪郭で分割'
    keep, outside = [], []
    for piece in split.bodies:
        if piece.isSolid:
            continue
        # 面内部の点で内外を判定する。外側片の重心は内側に入り得る。
        levels = [ellipsoid_level(face.pointOnFace) for face in piece.faces]
        if levels and all(v < 1.0 - 1e-7 for v in levels):
            keep.append(piece)
        elif levels and all(v > 1.0 + 1e-7 for v in levels):
            outside.append(piece)
        else:
            raise RuntimeError('楕円輪郭分割後の面の内外を判定できませんでした。')
    if len(keep) != 1 or not outside:
        raise RuntimeError('楕円輪郭内のねじり面を一意に取得できませんでした。')
    for piece in outside:
        removed = root.features.removeFeatures.add(piece)
        if removed is None:
            raise RuntimeError('楕円輪郭外の余剰面を除去できませんでした。')
        removed.name = '楕円型握手_楕円輪郭外を除去'
    removed = root.features.removeFeatures.add(tool)
    if removed is None:
        raise RuntimeError('輪郭切り出し工具を除去できませんでした。')
    removed.name = '楕円型握手_輪郭工具を除去'
    sketch.isLightBulbOn = False
    body = keep[0]
    body.name = '楕円型握手_＋X側ねじり90度'
    body.isLightBulbOn = True
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
        piece.name = '楕円型握手_＋X側ねじり90度_Z正側' + ('' if i == 0 else '_{}'.format(i + 1))
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
        try:
            feature = thickens.add(inp)
        except RuntimeError as error:
            raise RuntimeError(name + 'の両側7.5 mm厚み付けに失敗しました。\n' + str(error)) from error
        if feature is None or feature.bodies.count == 0:
            raise RuntimeError(name + 'の厚み付けに失敗しました。')
        feature.name = name + '_両側7.5mm厚み付け'
        # bodiesには元のサーフェスも含まれるため、生成ソリッドのみを検証する。
        generated_solids = [body for body in feature.bodies if body.isSolid]
        if not generated_solids:
            raise RuntimeError(name + 'の厚み付け結果にソリッドがありません。')
        for i, body in enumerate(generated_solids):
            if not math.isfinite(body.volume) or body.volume <= 0:
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
        ui.messageBox('楕円型握手：厚み付きの立体を作成しました。\n−X側はXY平面、＋X側は原点0°から先端90°へ徐々にねじります。\nZ=0面で分割し、−Z部分を切り取り後、各面の両側へ7.5 mmずつ厚み付けしました（合計15 mm）。')
    except Exception:
        ui.messageBox(traceback.format_exc())
