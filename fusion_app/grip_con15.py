"""Con15 joins the existing Ref12 G-AG2-prime curve to Con13 CH1-prime."""
import math
from . import grip_width, grip_reference_bezier

NAME='グリップ接続面：Con15：Ref12（G–AG2′）–CH1′'


def corners(finger_a,finger_c,direction):
    control=grip_reference_bezier.curve_data(finger_a)['control_points_mm']
    ch1_prime=grip_width.quarter_l1_points('C',finger_c,direction)["CH1'"]
    return [control[0],ch1_prime,control[2]]


def validate_arc_ends(points,ends):
    if len(ends)!=2 or not any(all(math.dist(p,q)<1e-5 for p,q in zip((points[0],points[2]),order))
                              for order in (ends,ends[::-1])):
        raise ValueError('Con15のRef12曲線がG・AG2′に一致しません。')


def create(root,finger_a,finger_c,direction,source):
    import adsk.core
    import adsk.fusion
    points=corners(finger_a,finger_c,direction)
    if source is None or source.sketchCurves.sketchFixedSplines.count!=1:
        raise RuntimeError('Con15のRef12曲線がありません。')
    arc=source.sketchCurves.sketchFixedSplines.item(0)
    def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')
    validate_arc_ends(points,[xyz(p.worldGeometry) for p in (arc.startSketchPoint,arc.endSketchPoint)])
    sketch=root.sketches.add(root.xYConstructionPlane);sketch.name=NAME+'：CH1′接続線'
    anchors=[]
    for p in points:
        world=adsk.core.Point3D.create(*(x/10 for x in p))
        anchor=sketch.sketchPoints.add(sketch.modelToSketchSpace(world))
        if anchor is None or math.dist(xyz(anchor.worldGeometry),p)>1e-5:
            raise RuntimeError('Con15の接続点を指定位置に作成できません。')
        anchors.append(anchor)
    boundary=adsk.core.ObjectCollection.create()
    for i,j in ((0,1),(1,2)):
        line=sketch.sketchCurves.sketchLines.addByTwoPoints(anchors[i],anchors[j])
        if line is None:raise RuntimeError('Con15のCH1′接続線を作成できません。')
        boundary.add(line)
    boundary.add(arc)
    patches=root.features.patchFeatures
    feature=patches.add(patches.createInput(boundary,adsk.fusion.FeatureOperations.NewBodyFeatureOperation))
    feature.name=NAME
    if feature.bodies.count!=1:raise RuntimeError('Con15が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Con15の面積または形状を確認してください。')
    actual=[xyz(vertex.geometry) for vertex in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in actual) for p in points):
        raise RuntimeError('Con15の3頂点が指定位置と一致しません。')
    body.name=NAME;body.isLightBulbOn=True
    body.attributes.add('grip_connection_face','id','Con15')
    sketch.isLightBulbOn=False
    return body
