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
    # 1. 外部入力値 params を使ってグリップ形状を作る
    # 2. outer_shell_body を参照して重複部分を Cut する
    # 3. 必要なら外殻側の基準面・基準点もここで更新する
    _ = outer_shell_body
    _ = params
    return None
