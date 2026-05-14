# Left_hand_grip README

`Left_hand_grip` モデル資料の入口です。説明を `内殻` 用と `外殻` 用に分けました。

## 対象ファイル

- 内殻資料: [INNER_SHELL.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/INNER_SHELL.md)
- 外殻資料: [OUTER_SHELL.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/OUTER_SHELL.md)
- 旧一体型スクリプト: [fusion_app/Left_hand_grip.py](/home/ps/fusion_scripts/fusion_app/Left_hand_grip.py)
- 分割後の内殻スクリプト: [fusion_app/inner_shell.py](/home/ps/fusion_scripts/fusion_app/inner_shell.py)
- 分割後の外殻スクリプト: [fusion_app/outer_shell.py](/home/ps/fusion_scripts/fusion_app/outer_shell.py)
- 全体組み立て: [fusion_app/assembly_left_hand_grip.py](/home/ps/fusion_scripts/fusion_app/assembly_left_hand_grip.py)

## 読み分け

- `INNER_SHELL.md`
  `内殻` のベース形状、止部、ジョイスティック受け、旧 `Left_hand_grip.py` に残っている内殻仕様をまとめた資料です。
- `OUTER_SHELL.md`
  `outer_shell.py` で管理している `外殻` の現仕様をまとめた資料です。内殻との接触面逃がし、底面外側の追加形状、蓋部斜面隙間部、フィレットを含みます。

## 補足

- ルートの [README.md](/home/ps/fusion_scripts/README.md) には、プロジェクト全体の運用ルールと確認用スクリプト `1.py` / `2.py` の使い分けがあります。
- `Left_hand_grip.py` は内殻中心の旧実装資料として残し、外殻の最新仕様は `outer_shell.py` 側を正とします。
