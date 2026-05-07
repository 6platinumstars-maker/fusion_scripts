try:
    from . import helpers
    from . import naming
except ImportError:
    import helpers
    import naming


def build_outer_shell(root_comp, inner_shell_body, params=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if inner_shell_body is None:
        raise RuntimeError('inner_shell_body is required to build the outer shell.')

    if params is None:
        params = dict(naming.DEFAULT_OUTER_SHELL_PARAMS)

    # TODO:
    # 1. inner_shell_body から参照面や参照輪郭を取得する
    # 2. クリアランスを加味した外殻スケッチを作る
    # 3. NewBody で外殻ボディを生成する
    # 4. helpers.set_body_identity(..., naming.BODY_OUTER_SHELL) を設定する
    _ = params
    return None
