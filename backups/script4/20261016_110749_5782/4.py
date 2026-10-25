"""独立した立体作成用のFusionスクリプト。"""
import traceback

import adsk.core
import adsk.fusion


def build(design):
    """今後の立体作成処理をここに追加する。寸法はFusion内部ではcm。"""
    # 内殻・外殻・グリップのモジュールや参照キャッシュは使用しない。
    pass


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        # 実行前に開いていたデザインを変更せず、毎回専用デザインを作る。
        document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
        if design is None:
            raise RuntimeError('新しいFusionデザインを取得できませんでした。')
        design.rootComponent.name = '立体作成4'
        build(design)
        ui.messageBox('4の実行環境を準備しました。\n新しい独立デザインです。立体形状はまだ作成していません。')
    except Exception:
        ui.messageBox(traceback.format_exc())
