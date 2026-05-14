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


BODY9_CANDIDATE_NAMES = ('ボディ9', 'Body9', 'Body 9')


def normalize_body_name(name):
    if name is None:
        return ''
    return name.replace(' ', '').lower()


def remove_body9_if_present(root_comp):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')

    target_names = {
        normalize_body_name(body_name)
        for body_name in BODY9_CANDIDATE_NAMES
    }
    removed_bodies = []

    bodies_to_remove = []
    for index in range(root_comp.bRepBodies.count):
        body = root_comp.bRepBodies.item(index)
        if normalize_body_name(body.name) in target_names:
            bodies_to_remove.append(body)

    for body in bodies_to_remove:
        removed_bodies.append(body.name)
        root_comp.features.removeFeatures.add(body)

    return removed_bodies


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
    end_cut_data = outer_shell.create_outer_shell_end_cut_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_end_region(
        root_comp,
        outer_shell_body,
        end_cut_data['sketch'],
        end_cut_data['face'],
    )
    yz_rect_cut_data = outer_shell.create_outer_shell_yz_rect_cut_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_yz_rect_region(
        root_comp,
        outer_shell_body,
        yz_rect_cut_data['sketch'],
        yz_rect_cut_data['face'],
        inner_shell_body=inner_shell_body,
    )
    side_extension_data = outer_shell.create_outer_shell_side_extension_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.extrude_outer_shell_side_extension_region(
        root_comp,
        outer_shell_body,
        side_extension_data['sketch'],
        side_extension_data['face'],
    )
    fitting_adjustment_data = outer_shell.create_outer_shell_fitting_adjustment_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_fitting_adjustment_region(
        root_comp,
        outer_shell_body,
        fitting_adjustment_data['sketch'],
        fitting_adjustment_data['face'],
    )
    outer_shell.add_outer_shell_l_button_opening_offset_fillet(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.split_outer_shell_by_lid_inner_plane(
        root_comp,
        outer_shell_body,
        inner_shell_body,
    )
    outer_shell_body = outer_shell.extrude_outer_shell_lid_inner_plane_in_positive_z(
        root_comp,
        outer_shell_body,
        inner_shell_body,
    )
    lid_gap_data = outer_shell.create_outer_shell_lid_gap_sketch(
        root_comp,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    outer_shell_body = outer_shell.extrude_outer_shell_lid_gap_region(
        root_comp,
        outer_shell_body,
        lid_gap_data['sketch'],
        lid_gap_data['plane'],
    )
    outer_shell_body = outer_shell.extrude_outer_shell_lid_gap_extension_region(
        root_comp,
        outer_shell_body,
        lid_gap_data['sketch'],
        lid_gap_data['plane'],
        lid_gap_data['extension_profile_target_point'],
    )
    outer_shell.cut_outer_shell_y35_face_region(
        root_comp,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    slope_cut_data = outer_shell.create_outer_shell_l_button_opening_slope_cut_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_l_button_opening_slope_region(
        root_comp,
        outer_shell_body,
        slope_cut_data['sketch'],
        slope_cut_data['face'],
    )
    inner_spec_data = outer_shell.create_outer_shell_l_button_opening_inner_spec_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_l_button_opening_inner_spec_region(
        root_comp,
        outer_shell_body,
        inner_spec_data['sketch'],
        inner_spec_data['axis_line'],
        inner_shell_body=inner_shell_body,
    )
    grip_body = grip.build_grip(
        root_comp,
        outer_shell_body,
        grip_params
    )
    remove_body9_if_present(root_comp)

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
