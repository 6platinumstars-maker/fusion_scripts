"""独立した立体作成用のFusionスクリプト。"""
import math
import traceback

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 50.0
MINOR_DIAMETER_MM = 30.0
TWIST_DEGREES = 90.0
LOFT_INTERVALS = 24
TOTAL_THICKNESS_MM = 15.0
THICKNESS_PER_SIDE_MM = TOTAL_THICKNESS_MM / 2.0
FLAT_FILLET_RADIUS_MM = 3.0


def build(design):
    """XY面（Z=0）に原点中心の50×30 mm楕円を描く。"""
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = '楕円_長径{:g}mm_短径{:g}mm_XY_Z0'.format(MAJOR_DIAMETER_MM, MINOR_DIAMETER_MM)
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
    solids = thicken_surfaces(root)
    fillet_flat_half(root, solids)
    return sketch


def section_endpoints_mm(x):
    """回転後の断面両端。theta(x)=90°×x/25 mm、回転軸はX軸。"""
    a = MAJOR_DIAMETER_MM / 2.0
    b = MINOR_DIAMETER_MM / 2.0
    if not 0.0 <= x <= a:
        raise ValueError('ねじり断面は0～25 mmの範囲で指定してください。')
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
    # X=25 mmの先端を面の内部に置き、ロフトの点収束を避ける。
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
    """片側+7.5 mmと反対側−7.5 mmを別々に生成して結合し、総厚15 mmにする。"""
    sources = [body for body in root.bRepBodies if not body.isSolid]
    if len(sources) != 2:
        raise RuntimeError('厚み付け対象の平面とねじり面を確認できません。')
    thickens = root.features.thickenFeatures
    solids = []
    for source in sources:
        name = source.name
        sides = []
        for sign in (1, -1):
            surfaces = adsk.core.ObjectCollection.create()
            surfaces.add(source)
            thickness = adsk.core.ValueInput.createByReal(sign * THICKNESS_PER_SIDE_MM / 10.0)
            # 対称モードではなく、符号を指定した片側7.5 mmを2回作る。
            inp = thickens.createInput(surfaces, thickness, False,
                                      adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            if inp is None:
                raise RuntimeError(name + 'の片側厚み付けを設定できませんでした。')
            try:
                feature = thickens.add(inp)
            except RuntimeError as error:
                raise RuntimeError(name + 'の{:+g} mm厚み付けに失敗しました。\n'.format(
                    sign * THICKNESS_PER_SIDE_MM) + str(error)) from error
            if feature is None:
                raise RuntimeError(name + 'の厚み付け結果がありません。')
            feature.name = name + '_片側{:+g}mm'.format(sign * THICKNESS_PER_SIDE_MM)
            generated = [body for body in feature.bodies if body.isSolid]
            if len(generated) != 1 or not math.isfinite(generated[0].volume) or generated[0].volume <= 0:
                raise RuntimeError(name + 'の片側厚み付けが有効なソリッドではありません。')
            sides.append(generated[0])
        tools = adsk.core.ObjectCollection.create()
        tools.add(sides[1])
        combines = root.features.combineFeatures
        inp = combines.createInput(sides[0], tools)
        inp.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        inp.isKeepToolBodies = False
        feature = combines.add(inp)
        if feature is None:
            raise RuntimeError(name + 'の表裏の厚みを結合できませんでした。')
        feature.name = name + '_表裏結合_総厚15mm'
        results = [body for body in feature.bodies if body.isValid and body.isSolid]
        if len(results) != 1:
            raise RuntimeError(name + 'の総厚15 mmのソリッドを一意に取得できません。')
        result = results[0]
        if not math.isfinite(result.volume) or result.volume <= 0:
            raise RuntimeError(name + 'の結合後のソリッド体積が不正です。')
        result.name = name + '_厚さ15mm'
        result.isLightBulbOn = True
        if name == '楕円型握手_−X側平面':
            # 境界ボックスではなく、実際の上下の平面から総厚を検証する。
            cap_heights = []
            for face in result.faces:
                plane = adsk.core.Plane.cast(face.geometry)
                if plane is not None and abs(abs(plane.normal.z) - 1.0) < 1e-6:
                    cap_heights.append(plane.origin.z * 10.0)
            if (len(cap_heights) < 2
                    or abs(min(cap_heights) + THICKNESS_PER_SIDE_MM) > 1e-4
                    or abs(max(cap_heights) - THICKNESS_PER_SIDE_MM) > 1e-4):
                raise RuntimeError('半楕円の実際の上下の面がZ=±7.5 mmではありません。')
        solids.append(result)
        if source.isValid:
            source.isLightBulbOn = False
    return solids


def fillet_flat_half(root, solids):
    """ねじりのない−X側ソリッドの全周の角へR3 mmを適用する。"""
    candidates = [body for body in solids
                  if body.isSolid and body.name.startswith('楕円型握手_−X側平面_厚さ15mm')]
    if len(candidates) != 1:
        raise RuntimeError('R3フィレット対象の半楕円ソリッドを一意に取得できません。')
    body = candidates[0]
    # 厚み付け結果の候補リストと専用名で対象を限定する。
    # 境界ボックスは加工対象を識別するための厳密な寸法判定に使わない。
    before_volume = body.volume
    name = body.name
    edges = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        edges.add(edge)
    if edges.count == 0:
        raise RuntimeError('半楕円のフィレット対象エッジがありません。')
    fillets = root.features.filletFeatures
    inp = fillets.createInput()
    inp.addConstantRadiusEdgeSet(
        edges, adsk.core.ValueInput.createByReal(FLAT_FILLET_RADIUS_MM / 10.0), False)
    try:
        feature = fillets.add(inp)
    except RuntimeError as error:
        raise RuntimeError('半楕円ソリッドの全周R3 mmフィレットに失敗しました。\n' + str(error)) from error
    if feature is None:
        raise RuntimeError('半楕円のR3フィレットを作成できませんでした。')
    feature.name = '楕円型握手_−X側半楕円_全周R3mm'
    results = [b for b in feature.bodies if b.isSolid]
    if len(results) != 1:
        raise RuntimeError('半楕円のR3フィレット結果を一意に取得できません。')
    result = results[0]
    if not math.isfinite(result.volume) or not 0 < result.volume < before_volume:
        raise RuntimeError('半楕円のR3フィレット後の体積を確認できません。')
    result.name = name + '_R3mm'
    result.isLightBulbOn = True
    return result


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
        ui.messageBox('楕円型握手：長径50 mm・短径30 mm・厚み15 mmの立体を作成しました。\n−X側はXY平面、＋X側は原点0°から先端90°へ徐々にねじります。\nZ=0面で分割し、−Z部分を切り取り後、各面の両側へ7.5 mmずつ厚み付けしました（合計15 mm）。\nねじりのない半楕円ソリッドの全周にR3 mmフィレットを追加しました。')
    except Exception:
        ui.messageBox(traceback.format_exc())
