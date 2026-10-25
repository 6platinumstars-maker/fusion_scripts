"""Con21 lofts the existing Ref12 spline to the actual Con18 AF2-FxL3 edge."""
import math
from . import grip_width, grip_reference_bezier

NAME='グリップ接続面：Con21：Con15曲線・Con18辺間ロフト面'
FIXED_HINT_MM=(-76.003,12.506,29.59)


def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')


def resolve_edge(body,finger_a,direction):
    from .grip_semi_variable import resolve_boundary_edge
    face=next(f for f in grip_width.output_faces('A',finger_a,direction) if f['index']==2)
    af2=dict(zip(face['names'],face['corners']))['F2']
    edge=resolve_boundary_edge({'faces':[{'fixed_id':'Con18'}]},[body],'Con18',(af2,FIXED_HINT_MM),'Con21')
    ends=[xyz(p.geometry) for p in (edge.startVertex,edge.endVertex)]
    if math.dist(ends[0],af2)>math.dist(ends[1],af2):ends.reverse()
    return edge,ends


def create(root,finger_a,direction,con18_body):
    import adsk.fusion
    edge,ends=resolve_edge(con18_body,finger_a,direction)
    source=root.sketches.itemByName(grip_reference_bezier.NAME)
    if source is None or source.sketchCurves.sketchFixedSplines.count!=1:
        raise RuntimeError('Con21のRef12曲線がありません。')
    curve=source.sketchCurves.sketchFixedSplines.item(0)
    controls=grip_reference_bezier.curve_data(finger_a)['control_points_mm']
    curve_ends=[xyz(p.worldGeometry) for p in (curve.startSketchPoint,curve.endSketchPoint)]
    expected=(controls[0],controls[2])
    if any(math.dist(p,q)>1e-5 for p,q in zip(curve_ends,expected)):
        raise RuntimeError('Con21の曲線端点がG・AG2′と一致しません。')
    lofts=root.features.loftFeatures
    inp=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.isSolid=False;inp.isClosed=False
    for section in (curve,edge):
        path=adsk.fusion.Path.create(section,adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None or inp.loftSections.add(path) is None:raise RuntimeError('Con21のロフト断面を設定できません。')
    feature=lofts.add(inp);feature.name=NAME
    if feature.bodies.count!=1:raise RuntimeError('Con21が1つのサーフェスになりませんでした。')
    body=feature.bodies.item(0)
    if body.isSolid or not math.isfinite(body.area) or body.area<=1e-8:
        raise RuntimeError('Con21の面積または形状を確認してください。')
    actual=[xyz(p.geometry) for p in body.vertices]
    if any(not any(math.dist(p,q)<1e-5 for q in actual) for p in curve_ends+ends):
        raise RuntimeError('Con21の4頂点が指定位置と一致しません。')
    for start,end in ((curve_ends[0],ends[1]),(curve_ends[1],ends[0])):
        if not any(e.startVertex is not None and e.endVertex is not None and
                   any(math.dist(xyz(a.geometry),start)<1e-5 and math.dist(xyz(b.geometry),end)<1e-5
                       for a,b in ((e.startVertex,e.endVertex),(e.endVertex,e.startVertex))) for e in body.edges):
            raise RuntimeError('Con21の端点対応（G–指定頂点、AG2′–AF2）を確認してください。')
    body.name=NAME;body.isLightBulbOn=True
    body.attributes.add('grip_connection_face','id','Con21')
    return body
