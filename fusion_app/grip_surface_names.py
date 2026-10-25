"""Display labels for fixed and reference geometry; IDs stay stable."""
DESCRIPTIONS = {
    'Fx1': '外殻X=-76.795面',
    'Fx2': '外殻Lボタン開口部面',
    'Fx3': '外殻蓋部斜面C字面',
    'Fx4': '上下円弧接続曲面',
    'Fx5': '外殻コの字面',
    'Fx6': '外殻Z=-6.0面',
    'Fx7': '外殻上部三角形面',
    'Fx8': 'Fx2・Fx3間の三角形面',
    'Fx9': 'FxL3・Fx3円弧間ロフト面',
    'Fx10': 'Fx9頂点・Fx3直線間三角形面',
    'Fx11': 'Fx9頂点・Fx5直線間三角形面',
    'Fx12': 'Fx11辺・FxL3接点X間ロフト面',
    'Fx13': 'Fx9端点・指定点間三角形面',
    'Fx14': 'Ref5楕円区間・Fx12辺間ロフト面',
    'Fx15': 'Ref5楕円区間・Fx9接点X間ロフト面',
    'Fx16': 'Ref5・Ref7のG–終点間ロフト面',
    'Fx17': '六角形ABCDEF面',
    'Fx18': '六角形A–B・DF2–DF3接続面',
    'Fx19': '六角形A–F・DF3–DF4接続面',
    'Fx20': '六角形E–F・DF4–DF5接続面',
    'Fx21': 'Ref7楕円区間・六角形D–E間ロフト面',
    'Fx22': 'Fx5指定4頂点接続面',
    'Fx23': 'Fx6上の指定3頂点三角面',
    'Ref1': '内殻円柱側面',
    'Ref2': '接合部円柱側面',
    'Ref3': '接合部円A先端環状面',
}


def display_name(identifier, part=None):
    kind = '参考面' if identifier.startswith('Ref') else '固定面'
    description = DESCRIPTIONS[identifier]
    if part is not None:
        description += '（{}）'.format(part)
    return '{}：{}：{}'.format(kind, identifier, description)
