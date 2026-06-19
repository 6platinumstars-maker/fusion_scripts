try:
    from . import naming
except ImportError:
    import naming


def build_grip(root_comp, outer_shell_body, params=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if params is None:
        params = dict(naming.DEFAULT_GRIP_PARAMS)

    # TODO:
    # 1. 外部入力値 params を使ってグリップ構造の点・線・面を作る
    # 2. 必要な段階で outer_shell_body を参照して接続終端を合わせる
    # 3. 必要なら内殻・外殻側の基準点や基準面もここで扱う
    _ = outer_shell_body
    _ = params
    return None
