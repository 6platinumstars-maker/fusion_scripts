import adsk.core

try:
    from . import Left_hand_grip as legacy_inner_shell
    from . import helpers
    from . import naming
except ImportError:
    import Left_hand_grip as legacy_inner_shell
    import helpers
    import naming


def build_inner_shell(context=None):
    legacy_inner_shell.run(context)

    root_comp = helpers.get_root_component()
    body = helpers.find_body_by_name_or_attribute(root_comp, naming.BODY_INNER_SHELL)
    if body is None and root_comp.bRepBodies.count > 0:
        body = root_comp.bRepBodies.item(0)
        helpers.set_body_identity(body, naming.BODY_INNER_SHELL)

    return body


def run(context):
    build_inner_shell(context)
