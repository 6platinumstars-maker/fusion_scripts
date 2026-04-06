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

        root = design.rootComponent

        # 単位は cm
        base_width = 4.0      # 40 mm
        base_height = 2.5     # 25 mm
        base_thickness = 0.8  # 8 mm
        hole_radius = 0.5     # 5 mm

        # スケッチ作成
        sketch = root.sketches.add(root.xYConstructionPlane)
        lines = sketch.sketchCurves.sketchLines
        circles = sketch.sketchCurves.sketchCircles

        # 中心基準の長方形
        lines.addCenterPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(base_width / 2, base_height / 2, 0)
        )

        # 中央の円
        circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),
            hole_radius
        )

        if sketch.profiles.count < 1:
            ui.messageBox('プロファイルが作成されませんでした。')
            return

        # 面積最大のプロファイルを使う
        target_profile = None
        max_area = -1

        for i in range(sketch.profiles.count):
            prof = sketch.profiles.item(i)
            area = prof.areaProperties().area
            if area > max_area:
                max_area = area
                target_profile = prof

        if not target_profile:
            ui.messageBox('対象プロファイルを取得できませんでした。')
            return

        # 押し出し
        extrudes = root.features.extrudeFeatures
        ext_input = extrudes.createInput(
            target_profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )

        distance = adsk.core.ValueInput.createByReal(base_thickness)
        ext_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(distance),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )

        extrudes.add(ext_input)

        ui.messageBox('穴付きプレートを作成しました。')

    except:
        if ui:
            ui.messageBox('失敗:\n{}'.format(traceback.format_exc()))