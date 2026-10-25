import importlib
import adsk.core
import traceback
from . import helpers, naming, isolated_design
from . import inner_shell, reference_snapshot, inner_shell_joint, inner_shell_joint_bore, inner_shell_joint_bore_c, inner_shell_joint_fillet


def build_for_preview(context=None):
    for module in (helpers, naming, isolated_design, inner_shell, reference_snapshot, inner_shell_joint, inner_shell_joint_bore, inner_shell_joint_bore_c, inner_shell_joint_fillet):
        importlib.reload(module)
    design = helpers.get_active_design()
    isolated_design.require_empty(design)
    root = design.rootComponent
    body = inner_shell.build_inner_shell(context)
    # The old assembly consumed this state before the lid revolve cut.
    pending = reference_snapshot.stage(root)
    inner_shell.add_inner_shell_lid_revolve_cut(root)
    body = inner_shell_joint.add_joint(root, body)
    body = inner_shell_joint_bore.cut(root, body)
    body = inner_shell_joint_bore_c.cut(root, body)
    body = inner_shell_joint_fillet.apply(root, body)
    for candidate in root.bRepBodies:
        candidate.isLightBulbOn = (candidate == body)
    isolated_design.hide_construction(root)
    from . import grip_inner_reference
    importlib.reload(grip_inner_reference)
    grip_inner_reference.publish(body)
    reference_snapshot.publish(pending)
    isolated_design.record(design, 'inner', pending['revision'])
    return {naming.BODY_INNER_SHELL: body}


def run(context):
    try:
        build_for_preview(context)
    except Exception:
        adsk.core.Application.get().userInterface.messageBox(traceback.format_exc())
