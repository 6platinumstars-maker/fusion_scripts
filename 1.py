import adsk.core
import traceback

try:
    from .fusion_app import inner_shell
    from .fusion_app import helpers
except ImportError:
    from fusion_app import inner_shell
    from fusion_app import helpers


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        inner_shell_body = inner_shell.build_inner_shell(context)
        root_comp = helpers.get_root_component()
        inner_shell.add_inner_shell_lid_revolve_cut(root_comp, inner_shell_body)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
