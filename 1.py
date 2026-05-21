import adsk.core
import adsk.fusion
import importlib
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
OUTER_SHELL_BASE_STRUCTURE_EXTRA_BODY_CANDIDATE_NAMES = (
    '外殻基準構造（1）',
    '外殻基準構造（１）',
    '外殻基準構造(1)',
    '外殻基準構造 (1)',
)
EXPECTED_OUTER_SHELL_REVISION = '2026-05-21-l-button-opening-y32-cut'


def normalize_body_name(name):
    if name is None:
        return ''
    return name.replace(' ', '').lower()


def remove_bodies_by_candidate_names(root_comp, candidate_names):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')

    target_names = {
        normalize_body_name(body_name)
        for body_name in candidate_names
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


def remove_body9_if_present(root_comp):
    return remove_bodies_by_candidate_names(
        root_comp,
        BODY9_CANDIDATE_NAMES,
    )


def remove_outer_shell_base_structure_extra_body_if_present(root_comp):
    return remove_bodies_by_candidate_names(
        root_comp,
        OUTER_SHELL_BASE_STRUCTURE_EXTRA_BODY_CANDIDATE_NAMES,
    )


def ensure_outer_shell_revision():
    actual_revision = getattr(outer_shell, 'OUTER_SHELL_SCRIPT_REVISION', None)
    if actual_revision == EXPECTED_OUTER_SHELL_REVISION:
        return
    raise RuntimeError(
        'fusion_app/outer_shell.py が古い可能性があります。'
        ' 2.py だけでなく fusion_app/*.py も同期してください。'
        ' expected={}, actual={}'.format(
            EXPECTED_OUTER_SHELL_REVISION,
            actual_revision,
        )
    )


def reload_fusion_app_modules():
    global grip
    global helpers
    global inner_shell
    global naming
    global outer_shell

    naming = importlib.reload(naming)
    helpers = importlib.reload(helpers)
    inner_shell = importlib.reload(inner_shell)
    outer_shell = importlib.reload(outer_shell)
    grip = importlib.reload(grip)


def build_all(context=None, grip_params=None, outer_shell_params=None):
    reload_fusion_app_modules()
    ensure_outer_shell_revision()
    design = helpers.get_active_design()
    root_comp = design.rootComponent

    inner_outer_result = build_inner_and_outer(
        context=context,
        outer_shell_params=outer_shell_params,
    )
    inner_shell_body = inner_outer_result[naming.BODY_INNER_SHELL]
    outer_shell_body = inner_outer_result[naming.BODY_OUTER_SHELL]
    grip_body = grip.build_grip(
        root_comp,
        outer_shell_body,
        grip_params
    )
    remove_body9_if_present(root_comp)
    remove_outer_shell_base_structure_extra_body_if_present(root_comp)

    return {
        naming.BODY_INNER_SHELL: inner_shell_body,
        naming.BODY_OUTER_SHELL: outer_shell_body,
        naming.BODY_GRIP: grip_body,
    }


def build_inner_and_outer(context=None, outer_shell_params=None):
    reload_fusion_app_modules()
    ensure_outer_shell_revision()
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
    lid_gap_extension_data = outer_shell.create_outer_shell_lid_gap_extension_sketch(
        root_comp,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
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
    y32_cut_data = outer_shell.create_outer_shell_l_button_opening_y32_cut_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_l_button_opening_y32_region(
        root_comp,
        outer_shell_body,
        y32_cut_data['sketch'],
        inner_shell_body=inner_shell_body,
    )
    outer_shell_body = outer_shell.extrude_outer_shell_lid_gap_region(
        root_comp,
        outer_shell_body,
        lid_gap_data['sketch'],
        lid_gap_data['plane'],
        lid_gap_data['primary_profile_target_point'],
    )
    outer_shell_body = outer_shell.extrude_outer_shell_lid_gap_extension_region(
        root_comp,
        outer_shell_body,
        lid_gap_extension_data['sketch'],
        lid_gap_extension_data['plane'],
        lid_gap_extension_data['extension_profile_target_point'],
    )
    outer_shell_body = outer_shell.add_outer_shell_lower_stop_structure(
        root_comp,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    lid_decoration_cut_1_data = outer_shell.create_outer_shell_lid_decoration_cut_1_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.cut_outer_shell_lid_decoration_cut_1_region(
        root_comp,
        outer_shell_body,
        lid_decoration_cut_1_data['sketch'],
        lid_decoration_cut_1_data['axis_line'],
    )
    lid_decoration_cut_2_data = outer_shell.create_outer_shell_lid_decoration_cut_2_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.cut_outer_shell_lid_decoration_cut_2_region(
        root_comp,
        outer_shell_body,
        lid_decoration_cut_2_data['sketch'],
    )
    lid_decoration_cut_3_data = outer_shell.create_outer_shell_lid_decoration_cut_3_faces(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.cut_outer_shell_lid_decoration_cut_3_region(
        root_comp,
        outer_shell_body,
        lid_decoration_cut_3_data['face_1'],
        lid_decoration_cut_3_data['face_2'],
    )
    lid_decoration_cut_4_data = outer_shell.create_outer_shell_lid_decoration_cut_4_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.cut_outer_shell_lid_decoration_cut_4_region(
        root_comp,
        outer_shell_body,
        lid_decoration_cut_4_data['sketch'],
        lid_decoration_cut_4_data['axis_line'],
    )
    lid_decoration_cut_5_data = outer_shell.create_outer_shell_lid_decoration_cut_5_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.cut_outer_shell_lid_decoration_cut_5_region(
        root_comp,
        outer_shell_body,
        lid_decoration_cut_5_data['sketch'],
    )
    outer_shell_body = outer_shell.add_outer_shell_fitting_correction(
        root_comp,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    outer_shell_body = outer_shell.extrude_outer_shell_bottom_outer_slope(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.cut_outer_shell_bottom_outer_slope_regions(
        root_comp,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    inner_shell.add_inner_shell_lid_revolve_cut(root_comp, inner_shell_body)

    return {
        naming.BODY_INNER_SHELL: inner_shell_body,
        naming.BODY_OUTER_SHELL: outer_shell_body,
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
