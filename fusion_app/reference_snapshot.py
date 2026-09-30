"""Local immutable geometry snapshots; no cloud file or live design link."""
import hashlib
import json
import os
from pathlib import Path
import uuid
import adsk.fusion
from . import helpers, isolated_design


def cache_root():
    # Scripts/1/fusion_app and Scripts/2/fusion_app share Scripts/_grip_reference.
    return Path(__file__).resolve().parents[2] / '_grip_reference'


def stage(root):
    revision = uuid.uuid4().hex
    folder = cache_root() / revision
    folder.mkdir(parents=True, exist_ok=False)
    manager = adsk.fusion.TemporaryBRepManager.get()
    manifest = {'schema': 1, 'revision': revision,
                'code_revision': isolated_design.code_revision(),
                'phase': 'before_inner_lid_revolve_cut', 'bodies': []}
    for index, body in enumerate(root.bRepBodies):
        filename = '{}.smt'.format(index)
        path = folder / filename
        if not manager.exportToFile([manager.copy(body)], str(path)):
            raise RuntimeError('外殻参照形状の保存に失敗しました。')
        manifest['bodies'].append({'file': filename, 'name': body.name,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    if not manifest['bodies']:
        raise RuntimeError('外殻参照形状がありません。')
    (folder/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


def publish(manifest):
    # Publish only after the inner build, including its final cut, has succeeded.
    target = cache_root()/'latest.json'
    temporary = cache_root()/('latest-{}.tmp'.format(manifest['revision']))
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(str(temporary), str(target))


def read_snapshot():
    path = cache_root()/'latest.json'
    if not path.exists():
        raise RuntimeError('外殻の固定参照がありません。先に新しい空のデザインで1を実行し、正常な内殻を確認してください。')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('schema') != 1 or manifest.get('phase') != 'before_inner_lid_revolve_cut':
        raise RuntimeError('外殻参照データの形式が異なります。1から作成し直してください。')
    folder = cache_root()/manifest['revision']
    manager = adsk.fusion.TemporaryBRepManager.get()
    bodies = []
    for item in manifest['bodies']:
        path = folder/item['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError('外殻参照形状の内容が保存時と異なります。')
        loaded = manager.createFromFile(str(path))
        if loaded is None or loaded.count != 1:
            raise RuntimeError('外殻参照形状を読み込めません。')
        bodies.append(loaded.item(0))
    return manifest, bodies


def install(design, manifest, bodies):
    root = design.rootComponent
    base = None
    if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
        base = root.features.baseFeatures.add()
        base.name = '外殻固定参照_' + manifest['revision'][:8]
        if not base.startEdit():
            raise RuntimeError('外殻固定参照の編集を開始できません。')
    try:
        for body in bodies:
            added = root.bRepBodies.add(body, base) if base else root.bRepBodies.add(body)
            if added is None:
                raise RuntimeError('外殻固定参照をデザインに追加できません。')
    finally:
        if base and not base.finishEdit():
            raise RuntimeError('外殻固定参照の編集を終了できません。')
    # Name result bodies after exiting the base feature, not its source bodies.
    installed = base.bodies if base else root.bRepBodies
    if installed.count != len(manifest['bodies']):
        raise RuntimeError('外殻固定参照のボディ数が一致しません。')
    for index, item in enumerate(manifest['bodies']):
        helpers.set_body_identity(installed.item(index), item['name'])
    isolated_design.record(design, 'outer', manifest['revision'])
