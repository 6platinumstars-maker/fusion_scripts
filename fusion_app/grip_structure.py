import adsk.core
import importlib
import traceback

try:
    from . import grip
    from . import helpers
    from . import naming
except ImportError:
    try:
        from .fusion_app import grip
        from .fusion_app import helpers
        from .fusion_app import naming
    except ImportError:
        from fusion_app import grip
        from fusion_app import helpers
        from fusion_app import naming


def reload_fusion_app_modules():
    global grip
    global helpers
    global naming

    naming = importlib.reload(naming)
    helpers = importlib.reload(helpers)
    grip = importlib.reload(grip)


def build_for_preview(context=None, grip_params=None, outer_shell_params=None):
    reload_fusion_app_modules()
    design = helpers.get_active_design()
    root_comp = design.rootComponent

    from . import isolated_design
    importlib.reload(isolated_design)
    isolated_design.require_grip_design(design)
    grip_body = grip.build_grip(root_comp, None, grip_params)
    isolated_design.record(design, 'grip')

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
