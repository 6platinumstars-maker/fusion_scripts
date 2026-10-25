"""Read-only sampled boundary checks; never stitch, trim, or stop surface builds."""
import json
import math
from pathlib import Path


def xyz(point):return tuple(getattr(point,a)*10 for a in 'xyz')


def segment_distance(p,a,b):
    d=[b[i]-a[i] for i in range(3)];length=sum(x*x for x in d)
    t=max(0.,min(1.,sum((p[i]-a[i])*d[i] for i in range(3))/length)) if length else 0.
    return math.dist(p,tuple(a[i]+t*d[i] for i in range(3)))


def run(root):
    report={'method':'各辺49点の比較。曲線は最大偏差0.0005mmの折線で照合。位相接続やソリッド成立の保証ではない。',
            'tolerance_mm':.005,'targets':[],'errors':[]}
    try:
        bodies=[b for b in root.bRepBodies if not b.isSolid and
                b.name.startswith(('固定面：','半変動面：','グリップ幅面：','グリップ接続面：'))]
        edges=[];vertices=[]
        for bi,body in enumerate(bodies):
            vertices.extend((bi,xyz(v.geometry)) for v in body.vertices)
            for ei,edge in enumerate(body.edges):
                try:
                    ok,start,end=edge.evaluator.getParameterExtents()
                    if not ok:raise ValueError('パラメータ区間取得失敗')
                    ok,points=edge.evaluator.getStrokes(start,end,.00005)
                    if not ok or len(points)<2:raise ValueError('曲線点取得失敗')
                    line=[xyz(p) for p in points]
                    lo=[min(p[i] for p in line)-.0055 for i in range(3)]
                    hi=[max(p[i] for p in line)+.0055 for i in range(3)]
                    edges.append((bi,ei,edge,start,end,line,lo,hi))
                except Exception as error:report['errors'].append(dict(body=body.name,edge=ei,error=str(error)))
        for bi,body in enumerate(bodies):
            if not body.name.startswith(('グリップ接続面：Con1：','固定面：Fx15：')):continue
            row={'name':body.name,'edges':[],'vertices':[]}
            for vertex in body.vertices:
                p=xyz(vertex.geometry)
                row['vertices'].append(dict(point_mm=p,matching_vertices=sorted({bodies[j].name for j,q in vertices if j!=bi and math.dist(p,q)<1e-5})))
            for owner,ei,edge,start,end,line,lo,hi in edges:
                if owner!=bi:continue
                matches={};missing=[]
                for n in range(49):
                    ok,point=edge.evaluator.getPointAtParameter(start+(end-start)*n/48)
                    if not ok:raise ValueError('検査点取得失敗')
                    p=xyz(point);found=False
                    for j,je,other,_,__,poly,low,high in edges:
                        if j==bi or any(p[i]<low[i] or p[i]>high[i] for i in range(3)):continue
                        distance=min(segment_distance(p,a,b) for a,b in zip(poly,poly[1:]))
                        if distance<=.005:
                            matches.setdefault(bodies[j].name,set()).add(n);found=True
                    if not found:missing.append(p)
                row['edges'].append(dict(edge=ei,endpoints_mm=[line[0],line[-1]],
                    fully_covered_at_samples=not missing,
                    matching_bodies={name:len(samples) for name,samples in matches.items()},
                    unmatched_sample_count=len(missing),unmatched_examples_mm=missing[:3]))
            report['targets'].append(row)
    except Exception as error:report['errors'].append({'error':str(error)})
    path=Path(__file__).resolve().parents[1]/'grip_connection_check.json'
    try:path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    except OSError:pass
    return report
