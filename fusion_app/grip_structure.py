import adsk.core
import importlib
import traceback

try:
    from . import assembly_left_hand_grip
    from . import grip
    from . import helpers
    from . import naming
except ImportError:
    try:
        from .fusion_app import assembly_left_hand_grip
        from .fusion_app import grip
        from .fusion_app import helpers
        from .fusion_app import naming
    except ImportError:
        from fusion_app import assembly_left_hand_grip
        from fusion_app import grip
        from fusion_app import helpers
        from fusion_app import naming


def reload_fusion_app_modules():
    global assembly_left_hand_grip
    global grip
    global helpers
    global naming

    naming = importlib.reload(naming)
    helpers = importlib.reload(helpers)
    grip = importlib.reload(grip)
    assembly_left_hand_grip = importlib.reload(assembly_left_hand_grip)


def prepare_reference_bodies(context=None, outer_shell_params=None):
    return assembly_left_hand_grip.build_inner_and_outer(
        context=context,
        outer_shell_params=outer_shell_params,
    )


def remove_body_if_present(root_comp, name):
    body = helpers.find_body_by_name_or_attribute(root_comp, name)
    if body is None:
        return False
    root_comp.features.removeFeatures.add(body)
    return True


def build_for_preview(context=None, grip_params=None, outer_shell_params=None):
    reload_fusion_app_modules()
    design = helpers.get_active_design()
    root_comp = design.rootComponent

    use_reference_bodies = False
    prerequisite_bodies = {}
    if use_reference_bodies:
        prerequisite_bodies = prepare_reference_bodies(
            context=context,
            outer_shell_params=outer_shell_params,
        )
    grip_body = grip.build_grip(
        root_comp,
        prerequisite_bodies.get(naming.BODY_OUTER_SHELL),
        grip_params,
    )

    if use_reference_bodies:
        # 3.py はグリップ構造単体確認用なので、参照生成した内殻と外殻は残さない。
        remove_body_if_present(root_comp, naming.BODY_OUTER_SHELL)
        remove_body_if_present(root_comp, naming.BODY_INNER_SHELL)

    if grip_body is None:
        return {}

    return {
        naming.BODY_GRIP: grip_body,
    }


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        build_for_preview(context)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
