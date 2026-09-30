import importlib
import adsk.core
import traceback
from . import helpers, naming, isolated_design
from . import outer_shell, reference_snapshot, outer_shell_lower_notch, outer_shell_lower_cut, outer_shell_rectangle_cut, outer_shell_notches, outer_shell_joint_notch


from . import outer_shell_xy_face_cut, outer_shell_yz_face_extrude, outer_shell_circle_cut, outer_shell_corner_split


def build_for_preview(context=None, outer_shell_params=None):
    for module in (helpers, naming, isolated_design, outer_shell, reference_snapshot, outer_shell_lower_notch, outer_shell_lower_cut, outer_shell_rectangle_cut, outer_shell_notches, outer_shell_joint_notch, outer_shell_xy_face_cut, outer_shell_yz_face_extrude, outer_shell_circle_cut, outer_shell_corner_split):
        importlib.reload(module)
    design = helpers.get_active_design()
    isolated_design.require_empty(design)
    manifest, bodies = reference_snapshot.read_snapshot()
    root_comp = design.rootComponent
    reference_snapshot.install(design, manifest, bodies)
    # The outer shell now follows the reference-first path instead of consuming the inner shell body directly.
    outer_shell_reference = outer_shell.build_outer_shell_runtime_reference(
        root_comp=root_comp,
    )
    outer_shell_body = outer_shell.build_outer_shell_base_structure_from_reference(
        root_comp=root_comp,
        outer_shell_reference=outer_shell_reference,
        params=outer_shell_params,
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
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
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
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    outer_shell_body = outer_shell.extrude_outer_shell_lid_inner_plane_in_positive_z(
        root_comp,
        outer_shell_body,
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    lid_gap_data = outer_shell.create_outer_shell_lid_gap_sketch(
        root_comp,
        outer_shell_body,
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    lid_gap_extension_data = outer_shell.create_outer_shell_lid_gap_extension_sketch(
        root_comp,
        outer_shell_body,
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    outer_shell.cut_outer_shell_y35_face_region(
        root_comp,
        outer_shell_body,
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
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
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    y32_cut_data = outer_shell.create_outer_shell_l_button_opening_y32_cut_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_l_button_opening_y32_region(
        root_comp,
        outer_shell_body,
        y32_cut_data['sketch'],
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
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
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    outer_shell_body = outer_shell.add_outer_shell_lower_stop_structure(
        root_comp,
        outer_shell_body,
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
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
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    outer_shell_body = outer_shell.extrude_outer_shell_bottom_outer_slope(
        root_comp,
        outer_shell_body,
    )
    outer_shell_body = outer_shell.cut_outer_shell_bottom_outer_slope_regions(
        root_comp,
        outer_shell_body,
        inner_shell_body=None,
        outer_shell_reference=outer_shell_reference,
    )
    x90_positive_x_cut_data = outer_shell.create_outer_shell_x90_positive_x_cut_sketch(
        root_comp,
        outer_shell_body,
    )
    outer_shell.cut_outer_shell_x90_positive_x_region(
        root_comp,
        outer_shell_body,
        x90_positive_x_cut_data['sketch'],
        x90_positive_x_cut_data['face'],
    )
    for body in root_comp.bRepBodies:
        body.isLightBulbOn = (body == outer_shell_body)
    isolated_design.hide_construction(root_comp)
    lower_sketch = outer_shell_lower_notch.create_sketch(root_comp, outer_shell_body)
    outer_results = outer_shell_lower_cut.cut(root_comp, outer_shell_body, lower_sketch)
    outer_results = outer_shell_rectangle_cut.cut(root_comp, outer_results)
    outer_results = outer_shell_notches.cut_upper_notch(root_comp, outer_results)
    outer_results = outer_shell_joint_notch.cut(root_comp, outer_results)
    # ３Dプリント用微調整（①XY面切取り → ②YZ面押し出し → ③円切取り → ④3点平面分割・三角錐除去）
    outer_results = outer_shell_xy_face_cut.cut(root_comp, outer_results)
    outer_results = outer_shell_yz_face_extrude.extrude(root_comp, outer_results)
    outer_results = outer_shell_circle_cut.cut(root_comp, outer_results)
    outer_results = outer_shell_corner_split.split_and_remove(root_comp, outer_results)
    isolated_design.record(design, 'outer', manifest['revision'])
    return outer_results


def run(context):
    try:
        build_for_preview(context)
    except Exception:
        adsk.core.Application.get().userInterface.messageBox(traceback.format_exc())
