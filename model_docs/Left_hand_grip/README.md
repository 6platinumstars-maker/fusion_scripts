# Left_hand_grip README

`Left_hand_grip` モデル資料の入口です。説明を `内殻` 用と `外殻` 用に分けました。

## 対象ファイル

- 内殻資料: [INNER_SHELL.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/INNER_SHELL.md)
- 外殻資料: [OUTER_SHELL.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/OUTER_SHELL.md)
- グリップ構造開発メモ: [GRIP_STRUCTURE.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/GRIP_STRUCTURE.md)
- 外殻分離チェックリスト: [OUTER_SHELL_SEPARATION_CHECKLIST.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/OUTER_SHELL_SEPARATION_CHECKLIST.md)
- 互換入口として残す旧スクリプト: [fusion_app/Left_hand_grip.py](/home/ps/fusion_scripts/fusion_app/Left_hand_grip.py)
- 現在の内殻生成本体: [fusion_app/inner_shell.py](/home/ps/fusion_scripts/fusion_app/inner_shell.py)
- 分割後の外殻スクリプト: [fusion_app/outer_shell.py](/home/ps/fusion_scripts/fusion_app/outer_shell.py)
- グリップ構造の開発入口: [fusion_app/grip_structure.py](/home/ps/fusion_scripts/fusion_app/grip_structure.py)
- 全体組み立て: [fusion_app/assembly_left_hand_grip.py](/home/ps/fusion_scripts/fusion_app/assembly_left_hand_grip.py)

## 読み分け

- `INNER_SHELL.md`
  `内殻` のベース形状、止部、ジョイスティック受け、回転切り取りを含む現仕様をまとめた資料です。
- `OUTER_SHELL.md`
  `outer_shell.py` で管理している `外殻` の現仕様をまとめた資料です。内殻との接触面逃がし、底面外側の追加形状、蓋部斜面隙間部、フィレットを含みます。
- `OUTER_SHELL_SEPARATION_CHECKLIST.md`
  `外殻` を `内殻` から分離するための依存洗い出し資料です。分離順序、要確認関数、検証観点をまとめています。
- `GRIP_STRUCTURE.md`
  `グリップ構造` の考え方、`外殻基本構造` との接続前提、名前付き点・線・面の管理方針、および現在の参照座標系 `O / G / X / Y / 平面I / ±X / ±Y / ±Z` と、指A・B・C・Dの基準点 `P / P'`、基準平面 `J / J'` をまとめた README です。

## グリップの現在の確定状態（2026-09-25）

- 指A・B：関節線の生成とFusion上での表示・曲がる方向を確認済みです。
- 指C・D：到達点P、参考点P′、基準平面J、関節用平面J′をFusionで確認し、最終確定しました。
- 指Cの関節線はCJ′上、指Dの関節線はDJ′上に配置します。関節長さ・角度の指定と関節線生成は未実施です。
- 確定座標と平面の定義は [GRIP_STRUCTURE.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/GRIP_STRUCTURE.md) を参照してください。

## 補足

- ルートの [README.md](/home/ps/fusion_scripts/README.md) には、プロジェクト全体の運用ルールと確認用スクリプト `1.py` / `2.py` / `3.py` の使い分けがあります。
- `Left_hand_grip.py` は互換入口として残しています。
- `inner_shell.py` が現在の内殻生成本体です。
