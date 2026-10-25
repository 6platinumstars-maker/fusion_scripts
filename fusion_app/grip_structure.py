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
    from . import grip_fixed_reference
    importlib.reload(grip_fixed_reference)
    fixed_manifest, fixed_bodies = grip_fixed_reference.read_snapshot()
    from . import grip_fixed_surfaces
    importlib.reload(grip_fixed_surfaces)
    fx7_corners, fx7_area = grip_fixed_surfaces.resolve_fx7(fixed_bodies)
    fx8_corners, fx8_area = grip_fixed_surfaces.resolve_fx8(fixed_bodies)
    from . import grip_inner_reference
    importlib.reload(grip_inner_reference)
    inner_manifest, inner_bodies = grip_inner_reference.read_snapshot()
    from . import grip_semi_variable
    importlib.reload(grip_semi_variable)
    smv1_fixed_points = grip_semi_variable.resolve_smv1(fixed_manifest, fixed_bodies)
    smv3_fixed_points = grip_semi_variable.resolve_smv3(fixed_manifest, fixed_bodies)
    grip_semi_variable.resolve_smv2_edge(fixed_manifest, fixed_bodies)
    grip_semi_variable.resolve_smv4_edge(fixed_manifest, fixed_bodies)
    smv5_fixed_points = grip_semi_variable.resolve_smv5(fixed_manifest, fixed_bodies)
    grip_semi_variable.resolve_smv6_edge(fixed_manifest, fixed_bodies)
    smv7_fixed_points = grip_semi_variable.resolve_smv7(fixed_manifest, fixed_bodies)
    smv8_fixed_point = grip_semi_variable.resolve_smv8(fixed_manifest, fixed_bodies)
    from . import grip_d_tip_surfaces
    importlib.reload(grip_d_tip_surfaces)
    d_tip_fixed_points = grip_d_tip_surfaces.resolve_fixed_points(fixed_manifest, fixed_bodies)
    installed_fixed = grip_fixed_reference.install(design, fixed_manifest, fixed_bodies)
    smv2_edge = grip_semi_variable.resolve_smv2_edge(fixed_manifest, installed_fixed)
    smv4_edge = grip_semi_variable.resolve_smv4_edge(fixed_manifest, installed_fixed)
    smv6_edge = grip_semi_variable.resolve_smv6_edge(fixed_manifest, installed_fixed)
    grip_body = grip.build_grip(root_comp, None, grip_params,
                               smv1_fixed_points=smv1_fixed_points, smv2_edge=smv2_edge,
                               smv3_fixed_points=smv3_fixed_points, smv4_edge=smv4_edge,
                               smv5_fixed_points=smv5_fixed_points, smv6_edge=smv6_edge,
                               smv7_fixed_points=smv7_fixed_points, smv8_fixed_point=smv8_fixed_point,
                               d_tip_fixed_points=d_tip_fixed_points)
    grip_fixed_surfaces.create_fx7(root_comp, fx7_corners, fx7_area, fixed_manifest['revision'])
    grip_fixed_surfaces.create_fx8(root_comp, fx8_corners, fx8_area, fixed_manifest['revision'])
    grip_fixed_surfaces.create_fx23(root_comp, fixed_manifest['revision'])
    grip_inner_reference.install(design, inner_manifest, inner_bodies)
    from . import grip_fixed_arc
    importlib.reload(grip_fixed_arc)
    fxl3_sketch = grip_fixed_arc.create(root_comp, fixed_manifest, installed_fixed)
    from . import grip_fixed_loft
    importlib.reload(grip_fixed_loft)
    fx9_body = grip_fixed_loft.create_fx9(root_comp, fixed_manifest, installed_fixed, fxl3_sketch)
    from . import grip_con16_18
    importlib.reload(grip_con16_18)
    con18_params = grip_params or {}
    con18_a = grip.calculate_finger_a_line(con18_params.get('finger_a_lengths_mm'),
        con18_params.get('finger_a_angles_deg'),
        con18_params.get('finger_a_twist_deg', grip.GRIP_FINGER_A_TWIST_DEG))
    con18_direction = grip.subtract_points(grip.GRIP_FINGER_A_POINT_P_MM, grip.GRIP_FINGER_D_POINT_P_MM)
    con18_body = grip_con16_18.create_fixed(root_comp, con18_a, con18_direction, fx9_body)
    from . import grip_con21
    importlib.reload(grip_con21)
    grip_con21.create(root_comp, con18_a, con18_direction, con18_body)
    grip_fixed_surfaces.create_fx10(root_comp, fixed_manifest, installed_fixed, fx9_body)
    fx11_body = grip_fixed_surfaces.create_fx11(root_comp, fixed_manifest, installed_fixed, fx9_body)
    from . import grip_reference_x
    importlib.reload(grip_reference_x)
    reference_x = grip_reference_x.create(root_comp, fixed_manifest, installed_fixed, fxl3_sketch)
    fx12_body = grip_fixed_loft.create_fx12(root_comp, fx11_body, fxl3_sketch, reference_x, fixed_manifest['revision'])
    # Fx13 is suspended; keep the vacant ID for later renumbering.
    from . import grip_ref5_lofts, grip_reference_ellipse
    importlib.reload(grip_ref5_lofts)
    ref5_sketch = root_comp.sketches.itemByName(grip_reference_ellipse.NAME)
    grip_ref5_lofts.create(root_comp, ref5_sketch, fx12_body, fx9_body, fxl3_sketch, reference_x, fixed_manifest['revision'])
    from . import grip_fixed_loft_fx16
    importlib.reload(grip_fixed_loft_fx16)
    ref7_sketch = root_comp.sketches.itemByName(grip_reference_ellipse.REF7_NAME)
    grip_fixed_loft_fx16.create(root_comp, ref5_sketch, ref7_sketch, fixed_manifest['revision'])
    from . import grip_reference_hexagon
    importlib.reload(grip_reference_hexagon)
    hexagon_sketch = grip_reference_hexagon.create(root_comp)
    from . import grip_fixed_loft_fx21
    importlib.reload(grip_fixed_loft_fx21)
    fx21_body = grip_fixed_loft_fx21.create(root_comp, ref7_sketch, hexagon_sketch, fixed_manifest['revision'])
    from . import grip_smv16
    importlib.reload(grip_smv16)
    from . import grip_smv12
    importlib.reload(grip_smv12)
    grip_smv12.create(root_comp, fx21_body, grip.GRIP_REFERENCE_POINT_G_MM)
    grip_smv16.create(root_comp, ref7_sketch, fx21_body, grip.GRIP_REFERENCE_POINT_G_MM)
    from . import grip_fx4
    importlib.reload(grip_fx4)
    fx4_body = grip_fx4.replace(root_comp, fixed_manifest, installed_fixed)
    from . import grip_fx5
    importlib.reload(grip_fx5)
    grip_fx5.replace(root_comp, fixed_manifest, installed_fixed, fx4_body)
    from . import grip_fx6_cut
    importlib.reload(grip_fx6_cut)
    grip_fx6_cut.create(root_comp, fixed_manifest['revision'])
    from . import grip_connection_check
    importlib.reload(grip_connection_check)
    grip_connection_check.run(root_comp)
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
        design = helpers.get_active_design()
        from . import grip_solid
        importlib.reload(grip_solid)
        # Reuse named, unstitched source surfaces; never rebuild a saved model.
        if design.rootComponent.bRepBodies.count == 0:
            build_for_preview(context)
            design = helpers.get_active_design()
        grip_solid.create(design)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
