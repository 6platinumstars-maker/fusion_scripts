import adsk.core
import adsk.fusion
import traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        if not design:
            ui.messageBox('Fusion の DESIGN ワークスペースで実行してください。')
            return

        ui.messageBox('Left_hand_grip project is ready.')

    except:
        if ui:
            ui.messageBox('失敗:\n{}'.format(traceback.format_exc()))
