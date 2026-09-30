"""R1 fillet on the outer, diameter-9.2-mm rim of the joining pad."""
import json
import math
from pathlib import Path
import adsk.core
from . import helpers, naming, inner_shell

CENTER_MM = (-76.795, -7.201, 10.492)
OUTER_RADIUS_MM = 4.6
FILLET_RADIUS_MM = 1.0
NAME = '内殻‐外殻‐グリップ部接合部：円A先端外周R1'


def select_outer_rim(body):
    result = []
    tolerance_cm = 1e-5
    for edge in body.edges:
        curve = adsk.core.Circle3D.cast(edge.geometry)
        if curve is None:
            curve = adsk.core.Arc3D.cast(edge.geometry)
        if curve is None:
            continue
        center = curve.center
        if any(abs(value-expected/10) > tolerance_cm
               for value,expected in zip((center.x,center.y,center.z),CENTER_MM)):
            continue
        if abs(curve.radius-OUTER_RADIUS_MM/10) > tolerance_cm:
            continue
        if abs(abs(curve.normal.x)-1) > 1e-6:
            continue
        # The rim must border the planar cap at the specified X coordinate.
        cap_found = False
        for face in edge.faces:
            plane = adsk.core.Plane.cast(face.geometry)
            if (plane is not None and abs(abs(plane.normal.x)-1) < 1e-6
                    and abs(plane.origin.x-CENTER_MM[0]/10) < tolerance_cm):
                cap_found = True
                break
        if cap_found:
            if edge.faces.count != 2:
                raise RuntimeError('円Aの先端外周に面の接続が不正な辺があります。')
            result.append(edge)
    if not result or abs(sum(edge.length for edge in result)-math.tau*OUTER_RADIUS_MM/10) > 1e-4:
        raise RuntimeError('直径9.2 mmの円A先端外周を一周分取得できませんでした。')
    return result


def write_report(report):
    path = Path(__file__).resolve().parent.parent/'inner_joint_fillet_diagnostics.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def apply(root, body):
    report = {'stage':'select_outer_rim', 'center_mm':CENTER_MM,
              'outer_diameter_mm':2*OUTER_RADIUS_MM, 'fillet_radius_mm':FILLET_RADIUS_MM,
              'tangent_chain':False}
    try:
        edges = select_outer_rim(body)
        report.update(stage='apply_fillet', edge_count=len(edges),
                      edge_lengths_mm=[edge.length*10 for edge in edges])
        write_report(report)
        feature = inner_shell.apply_constant_radius_fillet_to_edges(
            root, edges, FILLET_RADIUS_MM/10, tangent_chain=False)
        feature.name = NAME
        if feature.bodies.count != 1:
            raise RuntimeError('円AのR1フィレット後の内殻が1ボディになりませんでした。')
        result = feature.bodies.item(0)
        if not result.isSolid:
            raise RuntimeError('円AのR1フィレット後の内殻がソリッドではありません。')
        helpers.set_body_identity(result, naming.BODY_INNER_SHELL)
        report.update(stage='fillet_succeeded', volume_mm3=result.volume*1000)
        write_report(report)
        return result
    except Exception as error:
        report['error'] = str(error)
        path = write_report(report)
        raise RuntimeError('{}\n診断記録: {}'.format(error,path)) from error
