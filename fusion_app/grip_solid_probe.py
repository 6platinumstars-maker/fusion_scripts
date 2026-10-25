"""Non-destructive boundary-fill interaction probes on output copies only."""
import json
from pathlib import Path

TARGETS = ('SmV9', 'Con21')
NEIGHBORS = {'SmV9': ('Con11','SmV8','SmV7'), 'Con21': ('Con15','Con18','Con1','Fx15')}
MAX_TRIALS = 240


class ProbeStopped(Exception):
    pass


def identifier(name):
    parts = name.split('：')
    return parts[1] if len(parts)>1 else name


def investigate(names, test, findings):
    """test(indices) is true only when cell computation actually raises.

    Return small reproducible failures, not a claim about invalid geometry.
    No monotonicity assumption: a failed subset is tested before reducing.
    """
    targets = [i for i,n in enumerate(names) if identifier(n) in TARGETS]
    base = [i for i in range(len(names)) if i not in targets]
    findings['baseline_without_targets_failed'] = test(base)
    findings['targets'] = []
    for target in targets:
        tag = identifier(names[target])
        row = dict(name=names[target],single_failed=test([target]),failing_groups=[])
        findings['targets'].append(row)
        if row['single_failed']:
            row['failing_groups'].append([names[target]])
            continue
        ordered = sorted((i for i in range(len(names)) if i!=target),
                         key=lambda i: (identifier(names[i]) not in NEIGHBORS[tag],i))
        for other in ordered:
            if test([target,other]):
                row['failing_groups'].append([names[target],names[other]])
                if len(row['failing_groups'])>=3: break
        row['pair_search_complete'] = len(row['failing_groups'])<3
        if row['failing_groups']: continue
        # A failure can require three or more faces. Reduce that combination.
        rest = base if target not in base else [i for i in base if i!=target]
        if not test([target]+rest):
            row['base_plus_target_failed'] = False
            continue
        row['base_plus_target_failed'] = True
        width = max(1,len(rest)//2)
        while width:
            changed = False
            for offset in range(0,len(rest),width):
                candidate = rest[:offset]+rest[offset+width:]
                if candidate and test([target]+candidate):
                    rest = candidate; changed = True; break
            if not changed: width //= 2
        row['failing_groups'].append([names[i] for i in [target]+rest])
        row['reduced_group_note'] = '選択順固定の削減結果。原因面の断定ではありません。'


def probe_input(fills, collection, operation):
    inp = None
    row = {'failed': False, 'stage': 'create_input'}
    try:
        inp = fills.createInput(collection,operation)
        if inp is None: raise RuntimeError('境界塗り潰し入力を作成できません。')
        inp.isRemoveTools = False
        row['stage'] = 'compute_cells'
        row['cell_count'] = inp.bRepCells.count
        # Zero cells is a successful calculation, not a kernel failure.
    except Exception as error:
        row.update(failed=True,error=str(error))
        if inp is None: row['unsafe_to_continue'] = True
    finally:
        if inp is not None:
            try:
                if inp.cancel() is False: raise RuntimeError('cancel returned False')
            except Exception as error:
                row.update(cancel_error=str(error),unsafe_to_continue=True)
    return row


def run(design,bodies):
    import adsk.core
    import adsk.fusion
    import adsk
    app = adsk.core.Application.get()
    names = [b.name for b in bodies]
    report = dict(status='running',names=names,trials=[],findings={},
                  note='面形状・保存元は変更しない。閉領域0は正常計算として扱う。')
    path = Path(__file__).resolve().parents[1]/'grip_solid_pair_diagnostics.json'
    cache = {}
    dialog = app.userInterface.createProgressDialog()
    dialog.isCancelButtonShown = True
    dialog.cancelButtonText = '診断を中止'
    dialog.show('グリップ面の組み合わせ診断','診断準備中',0,MAX_TRIALS)
    fills = design.rootComponent.features.boundaryFillFeatures
    def save():
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    def test(indices):
        # Preserve the source selection order and record it for reproduction.
        key = tuple(sorted(indices))
        if not key: return False
        if key in cache: return cache[key]
        adsk.doEvents()
        if dialog.wasCancelled: raise ProbeStopped('ユーザーが中止しました。')
        if len(report['trials'])>=MAX_TRIALS: raise ProbeStopped('診断回数の上限に達しました。')
        dialog.progressValue = len(report['trials'])
        dialog.message = '{}回目：{}面を確認中'.format(len(report['trials'])+1,len(key))
        collection = adsk.core.ObjectCollection.create()
        for i in key:
            if not bodies[i].isValid: raise ProbeStopped('コピー面が無効になったため中止しました。')
            collection.add(bodies[i])
        row = probe_input(fills,collection,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        row['names'] = [names[i] for i in key]
        report['trials'].append(row)
        save()  # Keep partial results even if Fusion stops during a later trial.
        if row.get('unsafe_to_continue'): raise ProbeStopped('診断処理を安全に終了できなかったため中止しました。')
        cache[key] = row['failed']
        return row['failed']
    try:
        save()
        investigate(names,test,report['findings'])
        report['status'] = 'completed'
    except ProbeStopped as error:
        report.update(status='stopped',reason=str(error))
    except Exception as error:
        report.update(status='diagnostic_error',reason=str(error))
    finally:
        dialog.hide()
        save()
    groups = [g for row in report['findings'].get('targets',[]) for g in row['failing_groups']]
    summary = '\n'.join(' + '.join(identifier(n) for n in g) for g in groups)
    text = '組み合わせ診断：{}回\n'.format(len(report['trials']))
    text += ('エラーを再現した組み合わせ：\n'+summary) if summary else '小さい組み合わせでは、まだ原因を絞り込めていません。'
    if report.get('reason'): text += '\n'+report['reason']
    text += '\n\nソリッドは未作成です。元の面は変更していません。\nこの結果画面をお知らせください。\n診断記録：'+str(path)
    app.userInterface.messageBox(text)
    return dict(path=str(path),status=report['status'],failing_groups=groups)
