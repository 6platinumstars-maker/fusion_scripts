"""楕円型握手：長辺の端から1/3を境に、短い側だけ＋Zへ60°反らす楕円面。"""
import math
import traceback
import json
from pathlib import Path

import adsk.core
import adsk.fusion


MODEL_NAME = '楕円型握手'
MAJOR_DIAMETER_MM = 100.0
MINOR_DIAMETER_MM = 30.0
END_BEND_DEGREES = 60.0
SHORT_SIDE_FRACTION = 1.0 / 3.0
FLAT_THICKNESS_MM = 15.0
TIP_THICKNESS_MM = 20.0
FILLET_RADIUS_MM = 3.0
JUNCTION_BLEND_MM = 2.0
OFFSET_SAMPLES = 80
BOUNDARY_SAMPLES_PER_SEGMENT = 64


def bend_start_x_mm():
    return MAJOR_DIAMETER_MM / 2.0 - MAJOR_DIAMETER_MM * SHORT_SIDE_FRACTION


def bend_height_mm(x):
    """開始位置の2 mmだけ曲率を連続にし、以後は確認済みの放物線を保つ。"""
    distance = max(0.0, x - bend_start_x_mm())
    coefficient = math.tan(math.radians(END_BEND_DEGREES)) / (2.0 * MAJOR_DIAMETER_MM * SHORT_SIDE_FRACTION)
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
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(MAJOR_DIAMETER_MM / 20.0, 0, 0),
        adsk.core.Point3D.create(0, MINOR_DIAMETER_MM / 20.0, 0))
    if ellipse is None or sketch.profiles.count != 1:
        raise RuntimeError('楕円の閉じた輪郭を作成できませんでした。')
    return sketch


def create_bent_sheet(root):
    """直線と曲率を連続にした反り断面をY方向へ押し出す。"""
    sketch = root.sketches.add(root.xZConstructionPlane)
    sketch.name = '反り断面_長い側は平面_短い側60度'
    length = MAJOR_DIAMETER_MM / 2.0 * 1.1
    curve = fitted_curve(sketch, [(x, 0, bend_height_mm(x)) for x in bend_sample_positions(length)])
    flat_start = sketch.modelToSketchSpace(adsk.core.Point3D.create(-length / 10.0, 0, 0))
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
    feature.name = '端から1／3_短い側60度反り基準面'
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
    result.name = '楕円型握手_長い側平面_短い側＋Z60度反り面'
    result.isLightBulbOn = False
    ellipse_sketch.isLightBulbOn = False
    return fillet_solid(root, create_variable_thickness(root))


def bend_slope(x):
    distance = max(0.0, x - bend_start_x_mm())
    coefficient = math.tan(math.radians(END_BEND_DEGREES)) / (2.0 * MAJOR_DIAMETER_MM * SHORT_SIDE_FRACTION)
    if distance < JUNCTION_BLEND_MM:
        t = distance / JUNCTION_BLEND_MM
        return coefficient * JUNCTION_BLEND_MM * (9 * t ** 2 - 12 * t ** 3 + 5 * t ** 4)
    return 2.0 * coefficient * distance


def thickness_mm(x):
    distance = max(0.0, x - bend_start_x_mm())
    gradient = (TIP_THICKNESS_MM - FLAT_THICKNESS_MM) / (MAJOR_DIAMETER_MM * SHORT_SIDE_FRACTION)
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
    limit = MAJOR_DIAMETER_MM / 2.0 * 1.1
    xs = bend_sample_positions(limit)
    upper = fitted_curve(sketch, [normal_offset_mm(x, 0, thickness_mm(x) / 2.0) for x in xs])
    lower = fitted_curve(sketch, [normal_offset_mm(x, 0, -thickness_mm(x) / 2.0) for x in xs])
    lines = sketch.sketchCurves.sketchLines
    left_top = sketch_point_mm(sketch, (-limit, 0, FLAT_THICKNESS_MM / 2.0))
    left_bottom = sketch_point_mm(sketch, (-limit, 0, -FLAT_THICKNESS_MM / 2.0))
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
    angle = math.acos(bend_start_x_mm() / a)
    blend_angle = math.acos((bend_start_x_mm() + JUNCTION_BLEND_MM) / a)
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
                points.append(normal_offset_mm(a * math.cos(t), b * math.sin(t), distance))
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
    origin = adsk.core.Point3D.create(0, 0, 0)
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
    tip = MAJOR_DIAMETER_MM / 2.0
    for x in (-25.0, 0.0, start, start + (tip - start) * .25,
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


def is_sharp_edge(edge):
    """接線が連続する面の継ぎ目を除き、丸める角だけを選ぶ。"""
    if edge.faces.count != 2:
        return False
    ok, lo, hi = edge.evaluator.getParameterExtents()
    if not ok:
        raise RuntimeError('フィレット対象エッジのパラメータ範囲を取得できません。')
    ok, point = edge.evaluator.getPointAtParameter((lo + hi) / 2.0)
    if not ok:
        raise RuntimeError('フィレット対象エッジ上の点を取得できません。')
    normals = []
    for face in edge.faces:
        ok, normal = face.evaluator.getNormalAtPoint(point)
        if not ok or not normal.normalize():
            raise RuntimeError('フィレット対象エッジに隣接する面の法線を取得できません。')
        normals.append(normal)
    # 法線の向きに依存せず、0.5°未満の接線接続を継ぎ目として除外する。
    dot = min(1.0, max(0.0, abs(normals[0].dotProduct(normals[1]))))
    return dot < math.cos(math.radians(0.5))


def fillet_edge_details(edge):
    """辺の中点と両隣の面法線を取得し、外周と側面継ぎ目を識別する。"""
    ok, lo, hi = edge.evaluator.getParameterExtents()
    if not ok:
        raise RuntimeError('フィレットの区分用エッジ範囲を取得できません。')
    ok, point = edge.evaluator.getPointAtParameter((lo + hi) / 2.0)
    if not ok:
        raise RuntimeError('フィレットの区分用エッジ点を取得できません。')
    normals = []
    for face in edge.faces:
        ok, normal = face.evaluator.getNormalAtPoint(point)
        if not ok or not normal.normalize():
            raise RuntimeError('フィレットの区分用法線を取得できません。')
        normals.append(normal)
    return point, normals


def fillet_edge_group(edge):
    """Y方向押し出しの表裏面は法線Y=0、楕円側面は法線Y≠0で区分する。"""
    point, normals = fillet_edge_details(edge)
    if len(normals) != 2:
        raise RuntimeError('フィレット対象エッジの隣接面数が不正です。')
    cap_count = sum(abs(normal.y) < 1e-5 for normal in normals)
    if cap_count == 2:
        return 'つなぎ目'
    if cap_count == 0:
        return '側面つなぎ目'
    # 表裏面と側面が交わる辺だけを外周とし、高さだけで継ぎ目を混ぜない。
    signed_height = point.z * 10.0 - bend_height_mm(point.x * 10.0)
    return '上側外周' if signed_height >= 0 else '下側外周'


def fillet_stage(root, body, group, rolling_ball=True, tangent_chain=False, report=None, selected_edges=None):
    """前工程後の形状からエッジを取り直し、1区分だけR3を適用する。"""
    edges = adsk.core.ObjectCollection.create()
    category, _, part = group.partition('／')
    for edge in (body.edges if selected_edges is None else selected_edges):
        if selected_edges is None and (not is_sharp_edge(edge) or fillet_edge_group(edge) != category):
            continue
        if part and selected_edges is None:
            ok, lo, hi = edge.evaluator.getParameterExtents()
            ok_point, point = edge.evaluator.getPointAtParameter((lo + hi) / 2.0)
            if not ok or not ok_point:
                raise RuntimeError('外周の細分化に使う点を取得できません。')
            is_flat_side = point.x * 10.0 <= bend_start_x_mm()
            if (part == '平面側') != is_flat_side:
                continue
        edges.add(edge)
    if report is not None:
        details = []
        for edge in edges:
            point, normals = fillet_edge_details(edge)
            details.append({'length_mm': edge.length * 10.0,
                            'point_mm': [getattr(point, axis) * 10.0 for axis in 'xyz'],
                            'face_normals': [[getattr(normal, axis) for axis in 'xyz']
                                             for normal in normals]})
        report.append({'group': group, 'edge_count': edges.count, 'edges': details})
    # 接線チェーンに含まれ、先行工程ですでに丸まった区分はスキップする。
    if edges.count == 0:
        return body
    name = body.name
    fillets = root.features.filletFeatures
    inp = fillets.createInput()
    inp.isRollingBallCorner = rolling_ball
    inp.addConstantRadiusEdgeSet(edges,
        adsk.core.ValueInput.createByReal(FILLET_RADIUS_MM / 10.0), tangent_chain)
    try:
        feature = fillets.add(inp)
    except RuntimeError as error:
        raise RuntimeError(group + 'のR3 mmフィレットに失敗しました。\n' + str(error)) from error
    if feature is None:
        raise RuntimeError(group + 'のR3 mmフィレットを作成できませんでした。')
    if feature.faces.count == 0:
        raise RuntimeError(group + 'のフィレット面が生成されていません。')
    feature.name = '楕円型握手_R3mm_' + group
    results = [result for result in feature.bodies if result.isSolid]
    if len(results) != 1 or not math.isfinite(results[0].volume) or results[0].volume <= 0:
        raise RuntimeError(group + 'のR3フィレット後のソリッドを確認できません。')
    result = results[0]
    result.name = name
    result.isLightBulbOn = True
    return result


def restore_fillet_count(root, count):
    fillets = root.features.filletFeatures
    while fillets.count > count:
        if not fillets.item(fillets.count - 1).deleteMe():
            raise RuntimeError('失敗したフィレットを取り消せないため停止しました。')


def find_current_solid(root, name):
    candidates = [body for body in root.bRepBodies if body.isSolid and body.name == name]
    if len(candidates) != 1:
        raise RuntimeError('フィレット再試行用のソリッドを取得できません。')
    return candidates[0]


def capture_original_fillet_targets(body):
    """加工前の角だけを記録し、フィレットで新しく生じる辺は対象に加えない。"""
    targets = []
    for edge in body.edges:
        if not is_sharp_edge(edge):
            continue
        ok, lo, hi = edge.evaluator.getParameterExtents()
        if not ok:
            raise RuntimeError('元の角のパラメータ範囲を取得できません。')
        points = []
        for fraction in (.2, .5, .8):
            ok, point = edge.evaluator.getPointAtParameter(lo + (hi - lo) * fraction)
            if not ok:
                raise RuntimeError('元の角の照合点を取得できません。')
            points.append(point)
        targets.append({'id': len(targets) + 1, 'group': fillet_edge_group(edge),
                        'length_cm': edge.length, 'points': points})
    if not targets:
        raise RuntimeError('R3フィレットを適用する元の角がありません。')
    return targets


def original_edge_matches(edge, target):
    ok, lo, hi = edge.evaluator.getParameterExtents()
    if not ok:
        return False
    for anchor in target['points']:
        ok, parameter = edge.evaluator.getParameterAtPoint(anchor)
        if not ok or parameter < lo - 1e-8 or parameter > hi + 1e-8:
            continue
        ok, point = edge.evaluator.getPointAtParameter(parameter)
        # getParameterAtPointは近傍点にも値を返すため、実距離も必ず確認する。
        if ok and point.distanceTo(anchor) <= 1e-5:
            return True
    return False


def pending_original_edges(body, targets):
    sharp = [edge for edge in body.edges if is_sharp_edge(edge)]
    return [(target, [edge for edge in sharp if original_edge_matches(edge, target)])
            for target in targets]


def fillet_edges_individually(root, body, group, report, targets):
    """元の角の残存片だけをR3で処理し、新しいブレンド面の辺を丸め直さない。"""
    name = body.name
    group_targets = [target for target in targets if target['group'] == group]
    settings = ((True, False), (False, False), (True, True), (False, True))
    for step in range(len(group_targets) * 4 + 8):
        pending = [(target, edges) for target, edges in pending_original_edges(body, group_targets) if edges]
        if not pending:
            return body
        pending.sort(key=lambda item: item[0]['length_cm'], reverse=True)
        succeeded = False
        last_error = None
        for target, _ in pending:
            for rolling, tangent in settings:
                body = find_current_solid(root, name)
                matches = [edge for edge in body.edges
                           if is_sharp_edge(edge) and original_edge_matches(edge, target)]
                if not matches:
                    break
                matches.sort(key=lambda edge: edge.length, reverse=True)
                count = root.features.filletFeatures.count
                trial = {'group': group, 'original_edge_id': target['id'], 'step': step + 1,
                         'rolling_ball': rolling, 'tangent_chain': tangent,
                         'length_mm': matches[0].length * 10.0}
                report.append(trial)
                try:
                    body = fillet_stage(root, body, group, rolling, tangent, selected_edges=[matches[0]])
                    if root.features.filletFeatures.count <= count:
                        raise RuntimeError('フィレット工程が作成されていません。')
                    trial['status'] = 'succeeded'
                    succeeded = True
                    break
                except RuntimeError as error:
                    last_error = error
                    trial['status'] = 'failed'
                    trial['error'] = str(error)
                    restore_fillet_count(root, count)
                    trial['rolled_back'] = True
            if succeeded:
                break
        if not succeeded:
            raise RuntimeError(group + 'の元の角に対するR3処理を進められません。\n' + str(last_error)) from last_error
    raise RuntimeError(group + 'の元の角の処理が上限工程数に達しました。')


def write_fillet_report(report):
    try:
        Path(__file__).with_name('4_fillet_diagnostics.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    except OSError:
        pass


def fillet_solid(root, body):
    """R3を維持し、各失敗を取り消して工程順と角・チェーンの設定を変える。"""
    original_name = '楕円型握手_平面15mm_反り15～20mm'
    if not body.isSolid or body.name != original_name:
        raise RuntimeError('R3フィレット対象の可変厚みソリッドを確認できません。')
    fillets = root.features.filletFeatures
    baseline_count = fillets.count
    strategies = (
        ('上側外周', '下側外周', 'つなぎ目', '側面つなぎ目'),
        ('下側外周', '上側外周', 'つなぎ目', '側面つなぎ目'),
        ('つなぎ目', '側面つなぎ目', '下側外周', '上側外周'),
    )
    targets = capture_original_fillet_targets(body)
    report = {'radius_mm': FILLET_RADIUS_MM, 'original_edge_count': len(targets), 'attempts': []}
    last_error = None
    for order in strategies:
        current = [candidate for candidate in root.bRepBodies
                   if candidate.isSolid and candidate.name == original_name]
        if len(current) != 1:
            raise RuntimeError('再試行前の可変厚みソリッドを取得できません。')
        body = current[0]
        attempt = {'order': order, 'mode': 'one_edge_at_a_time', 'stages': []}
        report['attempts'].append(attempt)
        write_fillet_report(report)
        try:
            for group in order:
                body = fillet_edges_individually(root, body, group, attempt['stages'], targets)
                write_fillet_report(report)
            if fillets.count == baseline_count:
                raise RuntimeError('R3フィレットが1工程も作成されませんでした。')
            remaining = [target['id'] for target, edges in pending_original_edges(body, targets) if edges]
            if remaining:
                raise RuntimeError('R3処理後に元の角が残っています。対象ID={}'.format(remaining))
            attempt['completed_original_edge_count'] = len(targets)
            attempt['created_fillet_feature_count'] = fillets.count - baseline_count
            body.name = original_name + '_全周R3mm'
            body.isLightBulbOn = True
            attempt['status'] = 'succeeded'
            write_fillet_report(report)
            return body
        except RuntimeError as error:
            last_error = error
            attempt['status'] = 'failed'
            attempt['error'] = str(error)
            # 今回の試行で作成したフィレットだけを逆順に取り消す。
            while fillets.count > baseline_count:
                if not fillets.item(fillets.count - 1).deleteMe():
                    write_fillet_report(report)
                    raise RuntimeError('失敗したフィレット工程を取り消せないため停止しました。') from error
            attempt['rolled_back'] = True
            write_fillet_report(report)
    raise RuntimeError('R3 mmを1本ずつ処理して工程順も変えましたが完了できませんでした。'
                       '\n詳細は4_fillet_diagnostics.jsonに保存しました。\n' + str(last_error)) from last_error


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
        ui.messageBox('楕円型握手：＋X端から1／3（X約16.667 mm）を反りの開始位置にしました。\n長い−X側は平面、短い＋X側は先端60°・高さ約28.868 mmです。\n元の面を中央に、法線方向で平面部15 mm・反り開始15 mm→先端20 mmの厚みを付けました。\n可変厚みソリッドの全周の角にR3 mmフィレットを追加しました。')
    except Exception:
        ui.messageBox(traceback.format_exc())
