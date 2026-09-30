"""Protect existing designs; record the code used to build each model."""
import hashlib
from pathlib import Path

GROUP = 'fusion_scripts_build'


def code_revision():
    digest = hashlib.sha256()
    root = Path(__file__).resolve().parent.parent
    for path in sorted(list(root.glob('*.py')) + list((root/'fusion_app').glob('*.py')) + list((root/'core').glob('*.py'))):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def require_empty(design):
    root = design.rootComponent
    if (root.bRepBodies.count or root.occurrences.count or root.sketches.count
            or root.constructionPlanes.count or root.constructionAxes.count
            or root.constructionPoints.count or design.timeline.count):
        raise RuntimeError('既存モデルを保護するため停止しました。新しい空のデザインで実行してください。既存モデルは削除しません。')


def require_grip_design(design):
    role = design.attributes.itemByName(GROUP, 'role')
    if role and role.value == 'grip':
        if design.rootComponent.bRepBodies.count or design.rootComponent.occurrences.count:
            raise RuntimeError('グリップ以外のボディがあるため停止しました。空のデザインで実行してください。')
        return
    require_empty(design)


def record(design, role, reference_revision=''):
    for key, value in [('role', role), ('code_revision', code_revision()),
                       ('reference_revision', reference_revision)]:
        design.attributes.add(GROUP, key, value)


def hide_construction(root):
    for collection in (root.sketches, root.constructionPlanes,
                       root.constructionAxes, root.constructionPoints):
        for entity in collection:
            entity.isLightBulbOn = False
