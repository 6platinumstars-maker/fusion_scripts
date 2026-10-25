"""SmV17: hexagon B-DF2-DG1 with the existing Ref9 B-DG1 arc."""
import math
from . import grip_width, grip_reference_hexagon

NAME='半変動面：SmV17：六角形B–DF2–DG1楕円境界面'
ARC_SKETCH_NAME='半変動面：SmV11・SmV12：Ref9のDG1–B区間'


def corners(finger_d,direction):
    face=next(f for f in grip_width.output_faces('D',finger_d,direction) if f['index']==2)
    width=dict(zip(face['names'],face['corners']))
    return [grip_reference_hexagon.hexagon_data()['points'][1],width['F2'],finger_d['points_mm'][1]]


def validate_arc_ends(points,ends):
    if len(ends)!=2 or not any(all(math.dist(p,q)<1e-5 for p,q in zip((points[0],points[2]),order))
                              for order in (ends,ends[::-1])):
        raise ValueError('SmV17のRef9部分楕円弧が六角形B・DG1に一致しません。')


def create(root,finger_d,direction):
    import adsk.core
    import adsk.fusion
    points=corners(finger_d,direction)
    source=root.sketches.itemByName(ARC_SKETCH_NAME)
    if source is None or source.sketchCurves.sketchEllipticalArcs.count!=1:
        raise RuntimeError('SmV17のRef9部分楕円弧がありません。')
    arc=source.sketchCurves.sketchEllipticalArcs.item(0)
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    validate_arc_ends(points,[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)])
    sketch=root.sketches.add(root.xYConstructionPlane);sketch.name=NAME+'：DF2接続線'
    anchors=[]
    for p in points:
        world=adsk.core.Point3D.create(*(x/10 for x in p))
        anchor=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
        if anchor is None or math.dist(xyz(anchor.worldGeometry),p)>1e-5:
            raise RuntimeError('SmV17の接続点を指定位置に作成できません。')
        anchors.append(anchor)
    boundary=adsk.core.ObjectCollection.create()
    for i,j in ((0,1),(1,2)):
        line=sketch.sketchCurves.sketchLines.addByTwoPoints(anchors[i],anchors[j])
        if line is None:raise RuntimeError('SmV17のDF2接続線を作成できません。')
        boundary.add(line)
    boundary.add(arc)
    patches=root.features.patchFeatures
    feature=patches.add(patches.createInput(boundary,adsk.fusion.FeatureOperations.NewBodyFeatureOperation))
    feature.name=NAME
    if feature.bodies.count!=1:raise RuntimeError('SmV17が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('SmV17の面積または形状を確認してください。')
    actual=[xyz(vertex.geometry) for vertex in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in actual) for p in points):
        raise RuntimeError('SmV17の3頂点が指定位置と一致しません。')
    body.name=NAME;body.isLightBulbOn=True
    body.attributes.add('grip_semi_variable_face','id','SmV17')
    sketch.isLightBulbOn=False
    return body
