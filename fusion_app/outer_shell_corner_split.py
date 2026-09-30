"""Split the outer shell through three specified points and remove the corner."""
import json
import math
from pathlib import Path
import adsk.core
import adsk.fusion
from . import helpers, naming, outer_shell, outer_shell_rectangle_cut, isolated_design

POINTS_MM = ((-76.795, 32.229, 29.222), (-57.8, 32.2, -6.0),
             (-76.795, 18.768, -6.0))
REMOVE_SIDE_POINT_MM = (-76.795, 32.2, -6.0)
NAME = '３Dプリント用微調整：4 外殻3点平面分割：三角錐除去'
TOL_MM = 0.0001


def plane_normal():
    a, b, c = POINTS_MM
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    length = math.sqrt(sum(x*x for x in n))
    if length < 1e-9:
        raise RuntimeError('分割平面の3点が一直線上にあります。')
    return tuple(x/length for x in n)


def distance_mm(point_mm):
    return sum(n*(p-a) for n, p, a in zip(plane_normal(), point_mm, POINTS_MM[0]))


def removal_distance(point_cm):
    distance = distance_mm((point_cm.x*10, point_cm.y*10, point_cm.z*10))
    return distance if distance_mm(REMOVE_SIDE_POINT_MM) > 0 else -distance


def bounds_cross_plane(body):
    box = body.boundingBox
    distances = [removal_distance(adsk.core.Point3D.create(x, y, z))
                 for x in (box.minPoint.x, box.maxPoint.x)
                 for y in (box.minPoint.y, box.maxPoint.y)
                 for z in (box.minPoint.z, box.maxPoint.z)]
    return min(distances) < -TOL_MM and max(distances) > TOL_MM


def split_and_remove(root, outer_results):
    report = {'points_mm': POINTS_MM, 'remove_side_point_mm': REMOVE_SIDE_POINT_MM,
              'stage': 'create_plane', 'split_count': 0}
    path = Path(__file__).resolve().parent.parent/'outer_corner_split_diagnostics.json'
    try:
        originals = list(outer_results.values())
        before = sum(body.volume for body in originals)
        plane = outer_shell.create_plane_by_three_points(root, *POINTS_MM, name=NAME+'：平面')
        manager = adsk.fusion.TemporaryBRepManager.get()
        pieces = []
        for body in originals:
            if not bounds_cross_plane(body):
                pieces.append(body)
                continue
            # Bounding boxes can cross the plane even when a curved body does not.
            section = manager.planeIntersection(body, plane.geometry)
            if section is None or section.edges.count == 0:
                pieces.append(body)
                continue
            report['stage'] = 'split_body'
            splits = root.features.splitBodyFeatures
            feature = splits.add(splits.createInput(body, plane, True))
            feature.name = NAME+'：分割'
            results = outer_shell_rectangle_cut.remaining_bodies([body], feature)
            if len(results) < 2:
                raise RuntimeError('平面分割で複数の外殻ボディが得られませんでした。')
            pieces.extend(results)
            report['split_count'] += 1
        keep, remove = [], []
        report['pieces'] = []
        for body in pieces:
            if not body.isSolid:
                raise RuntimeError('分割後のソリッドを確認できません。')
            # A solid entirely on one side has its center of mass on that side.
            distance = removal_distance(body.physicalProperties.centerOfMass)
            if abs(distance) <= TOL_MM:
                raise RuntimeError('分割片の削除側を判定できません。')
            (remove if distance > 0 else keep).append(body)
            report['pieces'].append({'volume_mm3': body.volume*1000,
                                     'remove_side_distance_mm': distance,
                                     'remove': distance > 0})
        if not keep or not remove or report['split_count'] == 0:
            raise RuntimeError('残す外殻と削除する三角錐側の両方を確認できません。')
        report['stage'] = 'remove_corner'
        for body in remove:
            feature = root.features.removeFeatures.add(body)
            feature.name = NAME+'：削除'
        after = sum(body.volume for body in keep)
        if after >= before-1e-9:
            raise RuntimeError('三角錐除去後の体積が減少していません。')
        results = {}
        for index, body in enumerate(sorted(keep, key=lambda b:b.volume, reverse=True)):
            name = naming.BODY_OUTER_SHELL if index == 0 else '{}：平面分割後{}'.format(naming.BODY_OUTER_SHELL,index+1)
            helpers.set_body_identity(body, name)
            body.isLightBulbOn = True
            results[name] = body
        isolated_design.hide_construction(root)
        report.update(stage='succeeded', removed_volume_mm3=(before-after)*1000,
                      result_body_count=len(results))
        return results
    except Exception as error:
        report['error'] = str(error)
        raise RuntimeError('{}\n診断記録: {}'.format(error,path)) from error
    finally:
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
