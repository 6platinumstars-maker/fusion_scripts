"""Remove 0.8 mm outward layers based on the original trimmed Fx1/Fx4."""
import math
THICKNESS_MM=0.8
# Used only to determine outward sign, not to reconstruct the trimmed surface.
AXIS_ORIGIN_MM=(-41.895,5.3030031238150865,26.984962406065254)
AXIS=(0.,-0.08280820751220438,0.9965655024977614)


def outward(identifier,point):
    if identifier=='Fx1':return (-1.,0.,0.)
    delta=tuple(p-c for p,c in zip(point,AXIS_ORIGIN_MM))
    along=sum(d*n for d,n in zip(delta,AXIS))
    radial=tuple(d-along*n for d,n in zip(delta,AXIS))
    length=math.sqrt(sum(x*x for x in radial))
    if length<1e-8:raise RuntimeError('Fx4の半径方向を決定できません。')
    return tuple(x/length for x in radial)


def cut(design,body,copies,names,report,add_copies):
    import adsk.core
    import adsk.fusion
    root=design.rootComponent
    report['fx_clearance']=[]
    for identifier in ('Fx1','Fx4'):
        report['stage']=identifier+'_clearance'
        sources=[copy for copy,name in zip(copies,names) if name.startswith('固定面：'+identifier+'：')]
        if len(sources)!=1:raise RuntimeError(identifier+'の元サーフェスを一意に取得できません。')
        source=add_copies(design,sources,[identifier+'：0.8mm切り取り基準面'],identifier+'切り取り基準')[0]
        if source.faces.count!=1:raise RuntimeError(identifier+'の基準面が１面ではありません。')
        face=source.faces.item(0)
        point=face.pointOnFace
        ok,normal=face.evaluator.getNormalAtPoint(point)
        if not ok:raise RuntimeError(identifier+'の法線を取得できません。')
        direction=outward(identifier,tuple(getattr(point,a)*10 for a in 'xyz'))
        dot=sum(getattr(normal,a)*d for a,d in zip('xyz',direction))
        if abs(dot)<0.9:raise RuntimeError(identifier+'の面法線が指定の外向き方向と一致しません。')
        signed=THICKNESS_MM if dot>0 else -THICKNESS_MM
        before=body.volume
        info=dict(id=identifier,thickness_mm=THICKNESS_MM,signed_thickness_mm=signed,
                  direction_dot_normal=dot,before_volume_mm3=before*1000)
        report['fx_clearance'].append(info)
        faces=adsk.core.ObjectCollection.create();faces.add(face)
        thickens=root.features.thickenFeatures
        data=thickens.createInput(faces,adsk.core.ValueInput.createByReal(signed/10),False,
                                  adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        data.isChainSelection=False
        feature=thickens.add(data)
        if feature is None:raise RuntimeError(identifier+'の切り取り層を作成できません。')
        feature.name=identifier+'：外側0.8mm切り取り層'
        tools=[b for b in feature.bodies if b.isSolid]
        if len(tools)!=1:raise RuntimeError(identifier+'の切り取り層が１ソリッドではありません。')
        tool=tools[0]
        # Verify the generated layer is on the requested side before cutting.
        if identifier=='Fx1':
            bounds=tool.boundingBox
            if abs(bounds.minPoint.x*10+77.595)>0.005 or abs(bounds.maxPoint.x*10+76.795)>0.005:
                raise RuntimeError('Fx1の切り取り層がX=-77.595～-76.795 mmに一致しません。')
        collection=adsk.core.ObjectCollection.create();collection.add(tool)
        combines=root.features.combineFeatures
        inp=combines.createInput(body,collection)
        inp.operation=adsk.fusion.FeatureOperations.CutFeatureOperation
        inp.isKeepToolBodies=False
        result=combines.add(inp)
        if result is not None:result.name='グリップ加工：'+identifier+'外側へ0.8mm切り取り'
        if source.isValid and not source.isSolid:
            if root.features.removeFeatures.add(source) is None:raise RuntimeError(identifier+'の基準面を出力から除去できません。')
        bodies=list(root.bRepBodies)
        info['result_bodies']=[]
        for current in bodies:
            bounds=current.boundingBox
            info['result_bodies'].append(dict(name=current.name,is_solid=current.isSolid,
                lumps=current.lumps.count,face_count=current.faces.count,
                volume_mm3=current.volume*1000 if current.isSolid else 0,
                bounds_mm=[[getattr(point,a)*10 for a in 'xyz']
                           for point in (bounds.minPoint,bounds.maxPoint)]))
        if len(bodies)!=1 or not bodies[0].isSolid or bodies[0].lumps.count!=1:
            raise RuntimeError(identifier+'切り取り後が連続した１ソリッドではありません。ボディ数：{}。診断に各ボディの体積と位置を記録しました。'.format(len(bodies)))
        body=bodies[0]
        if not math.isfinite(body.volume) or not 0<body.volume<before-1e-9:
            raise RuntimeError(identifier+'切り取り後の体積減少を確認できません。')
        info['after_volume_mm3']=body.volume*1000
    return body
