import adsk.core
import adsk.fusion
import traceback

try:
    from . import grip
    from . import helpers
    from . import inner_shell
    from . import naming
    from . import outer_shell
except ImportError:
    try:
        from .fusion_app import grip
        from .fusion_app import helpers
        from .fusion_app import inner_shell
        from .fusion_app import naming
        from .fusion_app import outer_shell
    except ImportError:
        from fusion_app import grip
        from fusion_app import helpers
        from fusion_app import inner_shell
        from fusion_app import naming
        from fusion_app import outer_shell


def build_all(context=None, grip_params=None, outer_shell_params=None):
    design = helpers.get_active_design()
    root_comp = design.rootComponent

    inner_shell_body = inner_shell.build_inner_shell(context)
    outer_shell_body = outer_shell.build_outer_shell_base_structure(
        root_comp,
        inner_shell_body,
        outer_shell_params
    )
    opening_data = outer_shell.create_outer_shell_l_button_opening_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.extrude_outer_shell_l_button_opening_region(
        root_comp,
        outer_shell_body,
        opening_data['sketch'],
    )
    outer_shell_body = outer_shell.split_outer_shell_by_lid_inner_plane(
        root_comp,
        outer_shell_body,
        inner_shell_body,
    )
    grip_body = grip.build_grip(
        root_comp,
        outer_shell_body,
        grip_params
    )

    return {
        naming.BODY_INNER_SHELL: inner_shell_body,
        naming.BODY_OUTER_SHELL: outer_shell_body,
        naming.BODY_GRIP: grip_body,
    }


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        build_all(context)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
