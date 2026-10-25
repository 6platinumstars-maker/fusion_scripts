"""Replace copied Fx5 fragments with one quad after dependent faces exist."""
import math

NAME='固定面：Fx5：指定4頂点統合面'
HINTS_MM=((-29.854,-34.967,23.639),(-29.854,-35.,-6.),
          (-29.844,-24.823,-6.),(-29.844,-27.338,24.273))
TOL_MM=.005


def xyz(p):return tuple(getattr(p,a)*10 for a in 'xyz')


def resolve(manifest,bodies,fx4):
    old=[body for row,body in zip(manifest['faces'],bodies) if row['fixed_id']=='Fx5']
    if not old:raise RuntimeError('統合元のFx5がありません。')
    vertices=[xyz(v.geometry) for b in old for v in b.vertices]
    corners=[]
    for index,hint in enumerate(HINTS_MM):
        # The new upper right corner must share the reconstructed Fx4 vertex.
        candidates=[xyz(v.geometry) for v in fx4.vertices] if index==3 else vertices
        if not candidates:raise RuntimeError('Fx5の指定頂点がありません。')
        point=min(candidates,key=lambda p:math.dist(p,hint))
        if math.dist(point,hint)>TOL_MM:
            raise RuntimeError('Fx5の指定点{}に対応する頂点が0.005 mm以内にありません。'.format(index+1))
        if any(math.dist(point,p)<1e-6 for p in corners):raise RuntimeError('Fx5の頂点が重複しています。')
        corners.append(point)
    return corners,old


def replace(root,manifest,bodies,fx4):
    from . import grip_width
    corners,old=resolve(manifest,bodies,fx4)
    body=grip_width.create_patch(root,NAME,corners,('Fx5-P1','Fx5-P2','Fx5-P3','Fx5-P4'))
    if body.faces.count!=1 or body.edges.count!=4:
        raise RuntimeError('新Fx5が１枚の四角面になりませんでした。')
    body.attributes.add('grip_fixed_face','id','Fx5')
    body.attributes.add('grip_fixed_face','revision',manifest['revision'])
    # Removal features affect only the copies in grip3, never the shell cache.
    for source in old:
        feature=root.features.removeFeatures.add(source)
        if feature is None:raise RuntimeError('旧Fx5の除去に失敗しました。')
        feature.name='旧Fx5分割面の除去'
    return body
