"""Build a solid in a separate unsaved document, preserving the grip source."""
import json
import math
from datetime import datetime
from pathlib import Path

PREFIXES = ('固定面：', '半変動面：', 'グリップ幅面：', 'グリップ接続面：')
GROUP = 'fusion_scripts_build'
EXCLUDED_CONNECTIONS = frozenset({'Con2', 'Con10'})
EXPECTED_SURFACE_COUNT = 69
STITCH_TOLERANCE_MM = 0.10


def excluded_from_solid(body):
    parts = body.name.split('：')
    if len(parts) < 3:
        return False
    if parts[0] == 'グリップ接続面':
        return parts[1] in EXCLUDED_CONNECTIONS
    from .grip_surface_names import display_name
    return any(body.name == display_name(identifier,3) or
               body.name.startswith(display_name(identifier,3)+' (')
               for identifier in ('Fx2','Fx3'))



def validate_source_version(sources):
    """Saved Fusion documents do not update when the Python files change."""
    names = [body.name for body in sources]
    missing = []
    for prefix in ('固定面：Fx4：上下円弧接続曲面','固定面：Fx5：指定4頂点統合面',
                   '固定面：Fx6：統合・指定5頂点切り取り面'):
        if not any(name.startswith(prefix) for name in names):missing.append(prefix)
    if any(name.startswith(('固定面：Fx22：','固定面：Fx23：')) for name in names):
        missing.append('Fx22削除・Fx23統合後の構成')
    if missing:
        raise RuntimeError('実行対象は最新のグリップ面構成ではありません。\n不足：'+
            '、'.join(missing)+'\n保存済みのモデルはPython更新だけでは変わりません。'+
            '\n元ファイルはそのまま残し、新しい空のデザインで３を実行してください。'+
            '\n面を最新コードで再生成した後、別デザインでソリッド化します。')


def configure_new_target(design, direct_type):
    """Only switch an empty new output document, never an existing design."""
    root = design.rootComponent
    if (root.bRepBodies.count or root.occurrences.count or root.sketches.count
            or design.timeline.count):
        raise RuntimeError('履歴なし設定は空の新規出力デザインだけに適用できます。')
    design.designType = direct_type


def prepare_fill(fills, tools, operation, report):
    """Cancel a failed lazy cell computation before returning to the caller."""
    inp = None
    try:
        report['stage'] = 'boundary_fill_create_input'
        inp = fills.createInput(tools,operation)
        if inp is None: raise RuntimeError('境界塗り潰しを開始できません。')
        # Do not request deletion of tools while cells are being calculated.
        inp.isRemoveTools = False
        report['stage'] = 'boundary_fill_compute_cells'
        cells = inp.bRepCells
        volumes = cell_volumes(cells)
        return inp,cells,volumes
    except Exception:
        if inp is not None:
            try:
                if inp.cancel() is False:
                    raise RuntimeError('cancel returned False')
            except Exception as error:
                report['cancel_error'] = str(error)
        raise


def write_failure_geometry(manager, copies, names, report):
    """Capture unchanged temporary source bodies for subsequent diagnosis."""
    folder = Path(__file__).resolve().parents[1]/'grip_solid_failure_geometry'
    rows = []
    try:
        folder.mkdir(exist_ok=True)
        for index,(body,name) in enumerate(zip(copies,names),1):
            row = dict(index=index,name=name)
            try:
                row['area_mm2'] = body.area*100
                row['face_count'] = body.faces.count
                row['edge_count'] = body.edges.count
                path = folder/('surface_{:03d}.smt'.format(index))
                row['exported'] = bool(manager.exportToFile([body],str(path)))
                row['file'] = path.name
            except Exception as error:
                row['error'] = str(error)
            rows.append(row)
        (folder/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
        report['failure_geometry_folder'] = str(folder)
    except Exception as error:
        report['geometry_diagnostic_error'] = str(error)


def source_surfaces(root):
    # Ref1-3 are reference surfaces, not part of the enclosing boundary.
    bodies = [b for b in root.bRepBodies if not b.isSolid and b.name.startswith(PREFIXES)
              and not excluded_from_solid(b)]
    if not bodies:
        raise RuntimeError('グリップの固定面・半変動面・幅面・接続面がありません。３の元デザインを開いてください。')
    return bodies


def cell_volumes(cells):
    volumes = []
    for i in range(cells.count):
        body = cells.item(i).cellBody
        if body is None or not body.isSolid:
            raise RuntimeError('閉じていない領域が検出されました。')
        volume = body.volume * 1000  # cm^3 -> mm^3
        if not math.isfinite(volume) or volume <= 1e-8:
            raise RuntimeError('体積が不正な領域が検出されました。')
        volumes.append(volume)
    return volumes


def add_copies(design, copies, names, label):
    import adsk.fusion
    root = design.rootComponent
    base = None
    if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
        base = root.features.baseFeatures.add()
        base.name = label
        if not base.startEdit(): raise RuntimeError('ソリッド用コピーの編集を開始できません。')
    added = []
    try:
        for body in copies:
            new = root.bRepBodies.add(body, base) if base else root.bRepBodies.add(body)
            if new is None: raise RuntimeError('別デザインに形状をコピーできません。')
            added.append(new)
    finally:
        if base and not base.finishEdit(): raise RuntimeError('コピーの編集を終了できません。')
    result = list(base.bodies) if base else added
    if len(result) != len(names): raise RuntimeError('コピーしたボディ数が一致しません。')
    for body, name in zip(result,names): body.name = name
    return result


def validate_stitched_result(bodies):
    if len(bodies) != 1 or not bodies[0].isSolid:
        raise RuntimeError('ステッチ結果が１つのソリッドではありません。元の面モデルは保持しています。')
    if not math.isfinite(bodies[0].volume) or bodies[0].volume <= 0:
        raise RuntimeError('ステッチ結果の体積が不正です。')
    return bodies[0]


def inspect_stitch_result(feature,root,report):
    report['stage'] = 'stitch_validate_bodies'
    report['stitch_feature_returned'] = feature is not None
    bodies = list(root.bRepBodies)
    report['result_bodies'] = [dict(name=b.name,is_solid=b.isSolid,
        face_count=b.faces.count,volume_mm3=b.volume*1000 if b.isSolid else 0)
        for b in bodies]
    try:
        return validate_stitched_result(bodies)
    except RuntimeError as error:
        raise RuntimeError('ステッチ後のボディ数：{}、ソリッド数：{}。{}'.format(
            len(bodies),sum(b.isSolid for b in bodies),error)) from error


def create(source_design):
    import adsk.core
    import adsk.fusion
    from . import isolated_design
    app = adsk.core.Application.get()
    source_doc = app.activeDocument
    sources = source_surfaces(source_design.rootComponent)
    validate_source_version(sources)
    if len(sources)!=EXPECTED_SURFACE_COUNT:
        raise RuntimeError('選択対象は{}面です。確認済みの69面と異なるため停止しました。最新の面モデルを開いてください。'.format(len(sources)))
    manager = adsk.fusion.TemporaryBRepManager.get()
    copies = [manager.copy(body) for body in sources]
    if any(body is None for body in copies): raise RuntimeError('元サーフェスのコピーに失敗しました。')
    report = dict(source_document=source_doc.name, surfaces=[b.name for b in sources],
                  created_at=datetime.now().isoformat(), status='started',
                  generation_code_revision=isolated_design.code_revision())
    report['excluded_surfaces'] = [b.name for b in source_design.rootComponent.bRepBodies
                                  if not b.isSolid and excluded_from_solid(b)]
    report['selection_policy'] = '手動ステッチで成功した69面。Con2・Con10・Fx2（3）・Fx3（3）と参考面・参考線を除外。'
    for key in ('code_revision','fixed_reference_revision','inner_reference_revision'):
        attribute = source_design.attributes.itemByName(GROUP,key)
        if attribute: report['source_'+key] = attribute.value
    try:
        if source_doc.dataFile: report['source_file_id'] = source_doc.dataFile.id
    except RuntimeError:
        pass  # The source can be an unsaved design.
    target_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    target_doc.name = 'グリップ_ソリッド_未保存'
    design = adsk.fusion.Design.cast(app.activeProduct)
    inp = None
    try:
        report['stage'] = 'configure_new_parametric_design'
        configure_new_target(design,adsk.fusion.DesignTypes.ParametricDesignType)
        report['target_design_mode'] = 'parametric'
        report['stage'] = 'copy_surfaces'
        tools_bodies = add_copies(design,copies,report['surfaces'],'元グリップ面のコピー')
        collection = adsk.core.ObjectCollection.create()
        for body in tools_bodies: collection.add(body)
        report['stage'] = 'stitch_add'
        report['stitch_tolerance_mm'] = STITCH_TOLERANCE_MM
        stitches = design.rootComponent.features.stitchFeatures
        stitch_input = stitches.createInput(collection,
            adsk.core.ValueInput.createByString('0.10 mm'),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        if stitch_input is None:
            raise RuntimeError('ステッチ入力を作成できません。')
        feature = stitches.add(stitch_input)
        body = inspect_stitch_result(feature,design.rootComponent,report)
        if feature is not None:
            feature.name = 'グリップ：69面ステッチ'
        import importlib
        from . import grip_solid_circle_cut
        importlib.reload(grip_solid_circle_cut)
        body = grip_solid_circle_cut.cut(design.rootComponent,body,report)
        from . import grip_solid_z6_cut
        importlib.reload(grip_solid_z6_cut)
        body = grip_solid_z6_cut.cut(design.rootComponent,body,report)
        from . import grip_solid_yz_cut
        importlib.reload(grip_solid_yz_cut)
        body = grip_solid_yz_cut.cut(design.rootComponent,body,report)
        from . import grip_solid_xy_lug
        importlib.reload(grip_solid_xy_lug)
        body = grip_solid_xy_lug.create(design.rootComponent,body,report)
        from . import grip_solid_clearance
        importlib.reload(grip_solid_clearance)
        body = grip_solid_clearance.cut(design,body,copies,report['surfaces'],report,add_copies)
        from . import grip_solid_pin
        importlib.reload(grip_solid_pin)
        body = grip_solid_pin.create(design.rootComponent,body,report)
        from . import grip_solid_pin_fillet
        importlib.reload(grip_solid_pin_fillet)
        body = grip_solid_pin_fillet.apply(design.rootComponent,body,report)
        from . import grip_solid_rectangle_cleanup
        importlib.reload(grip_solid_rectangle_cleanup)
        body = grip_solid_rectangle_cleanup.cut(design.rootComponent,body,report)
        from . import grip_solid_sector_cut
        importlib.reload(grip_solid_sector_cut)
        body = grip_solid_sector_cut.cut(design.rootComponent,body,report)
        report['solid_body_count'] = 1
        report['total_volume_mm3'] = body.volume*1000
        body.name = 'グリップ：完成ソリッド'
        body.isLightBulbOn = True
        report['status'] = 'solid_created_unsaved'
        report['volume_mm3'] = body.volume*1000
        design.attributes.add(GROUP,'role','grip_solid')
        body.attributes.add('grip_solid','source_document',source_doc.name)
        app.activeViewport.fit()
        app.userInterface.messageBox('別デザインに追加加工済みのグリップソリッドを作成しました。\n元の３にはサーフェス・ガイドライン・参考線が残っています。\n形状を確認し、Ctrl+Sでソリッド専用の名前・保存先を指定してください。まだ保存はしていません。')
        return body
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = str(error)
        target_doc.name = 'グリップ_ソリッド未生成_確認用'
        write_failure_geometry(manager,copies,report['surfaces'],report)
        raise
    finally:
        if inp is not None:
            try:
                inp.cancel()
            except Exception as error:
                report['cancel_error'] = str(error)
        design.attributes.add('grip_solid','build_report',json.dumps(report,ensure_ascii=False))
        try:
            path = Path(__file__).resolve().parents[1]/'grip_solid_diagnostics.json'
            path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        except OSError:
            pass
