import adsk.core
import traceback

try:
    from .fusion_app import grip_structure
except ImportError:
    from fusion_app import grip_structure


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        grip_structure.run(context)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
