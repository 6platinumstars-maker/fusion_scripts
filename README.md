# Fusion API 3D Model Generator

Fusion API と Python を使って 3D モデルを生成し、Fusion 360 上で確認するためのリポジトリです。

## 構成

- `1.py`
  Fusion 360 で直接実行する確認用スクリプトです。通常は単体確認用の入口として使います。
- `2.py`
  Fusion 360 で直接実行する追加の確認用スクリプトです。全体確認や別案比較の入口として使います。
- `fusion_app/`
  Fusion API を使うアプリ本体の置き場です。案件ごとの完成コードはここに `名前.py` で置きます。
  左手グリップ案件では、`inner_shell.py` / `outer_shell.py` / `grip.py` / `assembly_left_hand_grip.py` のように役割ごとに分割します。
- `core/`
  複数のスクリプトで使い回す補助関数の置き場です。面・辺・頂点の探索やスケッチ作成など、共通処理をまとめます。
- `model_docs/`
  各モデルごとの説明をまとめるフォルダです。名前を付けた面・辺・頂点の説明や、モデル固有の補足をここで管理します。
- `sync.sh`
  Linux 側の `1.py` / `2.py` を Windows 側の Fusion 360 Scripts フォルダへコピーする同期スクリプトです。
- `__pycache__/`
  Python のキャッシュです。手で編集しません。

## フォルダごとの使い方

### ルート

ルートには、Fusion 360 から直接呼び出す `1.py` と `2.py` を置きます。Fusion 360 の `Scripts and Add-Ins` から実行されるのはこの階層のファイルです。

通常の流れは次の通りです。

1. `fusion_app/` で案件ごとのスクリプトを育てる
2. `1.py` か `2.py` から、確認したい `fusion_app/` の入口モジュールを呼ぶ
3. `./sync.sh` を実行する
4. Fusion 360 で `1` または `2` を実行する

## 左手グリップ案件の運用方法

左手グリップ案件では、ボディごとにファイルを分けて作業します。

- `fusion_app/inner_shell.py`
  `内殻` を作る専用です。固定形状のベースになります。
- `fusion_app/outer_shell.py`
  `外殻` を作る専用です。`内殻` を参照して、はめ込む側の形状を作ります。
- `fusion_app/grip.py`
  `グリップ` を作る専用です。外部入力値に応じて形状が変わります。
- `fusion_app/assembly_left_hand_grip.py`
  `内殻 -> 外殻 -> グリップ` の順に全体を組み立てる実行用です。

確認時の使い分けは次の通りです。

- `1.py`
  単体確認用です。今見たい 1 ボディだけを確認するときに使います。
- `2.py`
  全体確認用です。複数ボディの位置関係や干渉をまとめて確認するときに使います。

おすすめの確認手順:

1. `内殻` だけ見たいときは `1.py` から `fusion_app.inner_shell` を呼ぶ
2. `内殻 + 外殻` を見たいときは `2.py` から `fusion_app.assembly_left_hand_grip` を呼ぶ
3. `内殻 + 外殻 + グリップ` を見たいときも `2.py` から `fusion_app.assembly_left_hand_grip` を呼ぶ

`outer_shell.py` と `grip.py` は単独実行用ではなく、呼び出される部品ファイルとして扱います。

## 各ボディの説明

- `内殻`
  固定形状の基準ボディです。左手グリップ案件の土台であり、他ボディが参照する起点になります。
- `外殻`
  `内殻` をはめ込むための別ボディです。`内殻` の面や外形を参照して形状を決めます。
- `グリップ`
  外部から取得する値に応じて寸法や形状が変わる可変ボディです。`外殻` と重なる部分をカットする参照にも使います。

### `fusion_app/`

Fusion API を前提にした実装を置く場所です。現在は既存の `Left_hand_grip.py` に加えて、左手グリップ案件を段階的に分割するための `inner_shell.py` / `outer_shell.py` / `grip.py` / `assembly_left_hand_grip.py` / `helpers.py` / `naming.py` を置いています。

作業の基本方針は次の通りです。

1. 案件ごとに `fusion_app/名前.py` を作る
2. その中で `run(context)` を入口にする
3. スケッチ作成、プロファイル選択、押し出し、探索処理を関数に分ける
4. `1.py` / `2.py` から呼び出して確認する

### `core/`

Fusion API の共通ヘルパーを置く場所です。個別案件のロジックを書き込みすぎず、複数スクリプトで再利用できる処理をここへ寄せます。

現在の `core/fusion_helpers.py` は次のような用途で使います。

- プロファイル取得
- ボディ取得
- 面・辺・頂点の探索
- 面上スケッチ作成
- 面の輪郭投影
- 幾何判定の共通化

### `model_docs/`

各モデルの説明を `モデル名/README.md` の形で整理するフォルダです。

現在は次のファイルがあります。

- `model_docs/Left_hand_grip/README.md`

モデル固有の面・辺・頂点の説明は、今後このフォルダ側へ集約します。

### `sync.sh`

`/home/ps/fusion_scripts` 直下の `.py` を読み取り、Windows 側の Fusion 360 Scripts フォルダへ次の形でコピーします。

- `1.py` -> `.../Scripts/1/1.py`
- `2.py` -> `.../Scripts/2/2.py`
- `core/*.py` -> 各 Scripts フォルダ配下の `core/`
- `fusion_app/*.py` -> 各 Scripts フォルダ配下の `fusion_app/`

実行コマンド:

```bash
cd /home/ps/fusion_scripts
./sync.sh
```

## 現在の主要スクリプト

### `fusion_app/Left_hand_grip.py`

現在の状態では、次の順序で形状を作ります。

1. XY 平面に底面内部スケッチを作る
2. XY 平面に `ジョイスティック受け外周` スケッチを作る
3. XY 平面に `内殻外周` スケッチを作る
4. その外形プロファイルを負方向へ押し出してベースボディを作る
5. `x = 0.0` の面を取得する
6. その面に分割断面の三角形スケッチを作る
7. YZ 面に `内殻蓋部斜面作成` スケッチを作る
8. 最小プロファイルを負方向へ `Join` 押し出しして底面斜面を作る
9. `ジョイスティック受け外周` の指定領域を `+Z` 方向へ 5 mm 押し出す
10. `内殻外周` の指定領域を `+Z` 方向へ 25.8 mm 押し出す
11. `内殻蓋部斜面作成` の三角形を `-X` 方向へ 80 mm 切り取り押し出しし、`内殻蓋部斜面` を作る
12. `内殻蓋部斜面` 上に `内殻蓋部` スケッチを作り、A-B-C-D-F-G で囲まれる C字状 2 領域を `-2.3 mm` 相当で `Join` 押し出しする
13. 押し出し後の `内殻蓋部斜面` 上で、E 円弧と `DF` / `CG` に対応する 3 本のエッジへ `R2.0` フィレットを入れる
14. ベース上面に `内殻外部_仕様` スケッチを作り、2つの円の外側で指定2領域だけを `-Z` 方向へ 10 mm 切り取る
15. YZ 面に `上部止部` スケッチを作り、押し出したあと上面を押し上げる
16. `ジョイスティック受け外周`、`内殻外周`、`上部止部` をベースへ結合し、以後は同一ボディとして扱う
17. YZ 面に `下部止部` スケッチを作り、ベースへ `Join` 押し出ししたあと `R5.0` フィレットをかける
18. `z = -3.0 mm` の XY 面に `止金半円部` スケッチを作り、`底面外部` に接する半円領域を `+Z` 方向へ 5.48 mm `Join` 押し出ししたあと、先端側円弧だけに `R1.0` フィレットをかける
19. `z = -8.48 mm` の XY 面に `留金部外部 ` スケッチを作り、中心 `(0.00, 5.0, -8.48) mm`・`R17` の円と `-X` 側の扇状 2 領域を作成する
20. `留金部外部 ` の 2 つの扇状領域を `-Z` 方向へ 2 mm `Join` 押し出しし、`留金部` を作る
21. `留金部` の Z 方向直線エッジへ `R1.0` フィレットを入れる
22. XY 平面に `ジョイステック受け` スケッチを作り、`+Z` 方向へ 10 mm の切り取り押し出しを行う
23. ベースボディ作成直後に Fusion 上の表示名 `内殻` を設定し、最終加工後の 1 ボディに対しても同名を再設定する

### `ジョイスティック受け外周` の仕様

- スケッチ面は XY 平面です。
- `底面内部` 上に、中心 `(-21.00, -10.00, 0.00) mm` の同心円 `R15` と `R18` を作成します。
- 円上の点 `(-28.579, -22.944, 0.00) mm` から指定点 `(-29.842, -25.679, 0.00) mm` へ直線を引きます。
- `(-10.0, -20.0, 0.00) mm` と `(-10.0, -30.0, 0.00) mm` を結ぶ直線を追加します。
- スケッチで囲まれたうち、`(-10.00, -24.00, 0.00) mm` を通る領域を `+Z` 方向へ `5 mm` 押し出します。
- 押し出し後はいったん `ジョイスティック受外周` の名前を付け、後続でベースボディへ結合します。

### `内殻外周` の仕様

- スケッチ面は XY 平面です。
- `底面内部` 上に、中心 `(-42.00, 5.00, 0.00) mm` の同心円 `R31` と `R33` を作成します。
- 円上の点 `(-28.579, -22.944, 0.00) mm` から指定点 `(-29.842, -25.679, 0.00) mm` へ直線を引きます。
- `(-66.67, 26.918, 0.00) mm` と `(-25.0, 30.0, 0.00) mm` を結ぶ直線を追加します。
- 小さい円の外側かつ大きい円の内側で、2 本の直線に区切られた円弧領域を押し出し対象にします。
- 押し出し方向は `+Z`、押し出し量は `25.8 mm` です。
- 押し出し後はいったん `内殻外周` の名前を付け、後続でベースボディへ結合します。

## 関数の説明

### `fusion_app/Left_hand_grip.py`

- `create_base_sketch(root_comp)`
  底面内部の外形スケッチを XY 平面に作成します。左側の長さ `7.5 mm`、前後寸法、上辺の傾斜角をここで定義しています。
- `extrude_profile(root_comp, profile, distance_cm, direction, operation)`
  指定したプロファイルを指定距離だけ押し出す共通関数です。`NewBody` と `Join` の両方に使えます。
- `extrude_profiles(root_comp, profiles, distance_cm, direction, operation)`
  複数のプロファイルをまとめて同じ条件で押し出す共通関数です。内殻外部の2領域切り取りに使います。
- `get_smallest_profile(sketch)`
  スケッチ内のプロファイルから最小面積のものを返します。分割断面の三角形選択に使います。
- `add_named_attribute(entity, name)`
  Fusion の属性機能を使って、対象エンティティに `fusion_scripts:name=<name>` を付けます。
  一時ボディや面の識別に使います。ベースボディと最終ボディには、属性 `内殻` もあわせて付けています。
- `to_sketch_space(sketch, x, y, z)`
  モデル空間の座標を、対象スケッチ上の座標に変換します。
- `create_split_triangle_on_face(root_comp, face, helpers)`
  指定した面上に `分割断面` スケッチを作成し、三角形の分割ラインを追加します。
- `create_upper_stop_sketch(root_comp)`
  YZ 面に `上部止部` の断面スケッチを作成します。
- `create_lower_stop_sketch(root_comp)`
  YZ 面に `下部止部` の長方形スケッチを作成します。
- `create_joystick_receiver_sketch(root_comp)`
  XY 平面に `ジョイステック受け` の円スケッチを作成し、中心点へ `ジョイスティック受け基準点` の名前を付けます。
- `create_joystick_receiver_outer_perimeter_sketch(root_comp)`
  XY 平面に `ジョイスティック受け外周` スケッチを作成します。同心円 `R15` / `R18` と 2 本の直線を追加し、外周押し出し用の閉領域を作ります。
- `create_inner_shell_outer_perimeter_sketch(root_comp)`
  XY 平面に `内殻外周` スケッチを作成します。同心円 `R31` / `R33` と 2 本の直線を追加し、小円外側かつ大円内側の円弧領域を押し出し対象として使います。
- `create_inner_shell_lid_slope_cut_sketch(root_comp)`
  YZ 面に `内殻蓋部斜面作成` スケッチを作成します。後続で `内殻蓋部斜面` を作るための三角形断面です。
- `create_inner_shell_lid_face_sketch(root_comp, slope_face)`
  `内殻蓋部斜面` 上に `内殻蓋部` スケッチを作成します。`内殻外周` との交線上の A-B-C-D 点を近傍参照で取り直し、AB 円弧の 6 mm 内側に E 円弧を作って F-G を決め、A-B-C-D-F-G で囲まれる C字状 2 領域のプロファイルを返します。
- `apply_constant_radius_fillet_to_edges(root_comp, edges, radius_cm)`
  複数のエッジへ同じ半径の 3D フィレットをまとめて適用します。`内殻蓋部斜面` 上の E / `DF` / `CG` に対応する `R2.0` フィレットで使います。
- `join_all_bodies_into_first(root_comp)`
  その時点で存在する複数ボディを 1 つ目のボディへ `Join` 結合し、以後の処理を同一ボディ前提に揃えます。
- `create_outer_shell_option2_cut_sketch(root_comp, face, helpers)`
  ベース上面に `内殻外部_仕様` スケッチを作成し、面の輪郭を投影した上で2つの円を追加します。
- `create_outer_bottom_semicircle_sketch(root_comp, face, helpers)`
  `底面外部` 上に `止金半円部` スケッチを作成し、中心 `(0.00, 5.0, -3.0) mm`、半径 `R14.96` の円を追加します。
- `create_retainer_outer_fan_sketch(root_comp, face, helpers)`
  `留金部外部 ` 上に、中心 `(0.00, 5.0, -8.48) mm`、半径 `R17` の円と、`-X` 側へ向く扇状の補助直線 2 本と本線 4 本を追加します。
- `get_retainer_outer_fan_profiles(sketch)`
  `留金部外部 ` スケッチから、押し出し対象となる 2 つの扇状プロファイルを取得します。
- `find_vertical_linear_edges(edges, tolerance=1e-3)`
  `留金部` の side face から集めたエッジのうち、XY がほぼ一定で Z に長さを持つ直線エッジを抽出します。
- `get_profiles_nearest_points(sketch, target_points)`
  指定した座標に最も近いプロファイルを選びます。内殻外部の上側領域と下側領域の選択に使います。
- `load_fusion_helpers()`
  `core/` を import path に追加し、`fusion_helpers` を読み込みます。
- `run(context)`
  Fusion 360 から呼ばれる入口です。ベース形状、ジョイスティック受け外周の押し出し、内殻外周の押し出し、複数ボディの結合、内殻外部の2領域切り取り、止部、フィレット、止金半円部、留金部、ジョイステック受けの切り取りまでを順に実行します。

### `core/fusion_helpers.py`

- `is_close(value_a, value_b, tolerance=1e-6)`
  浮動小数点値を許容誤差付きで比較します。
- `points_are_equal(point_a, point_b, tolerance=1e-6)`
  2 点の座標が一致しているか判定します。
- `get_body_from_feature(feature)`
  押し出しなどで作られた feature から最初のボディを取得します。
- `get_largest_profile(sketch)`
  スケッチ内の最大面積プロファイルを返します。
- `get_face_edges(face)`
  面に属する辺をリストで返します。
- `get_edge_vertices(edge)`
  辺の始点頂点と終点頂点を返します。
- `get_vertex_point(vertex)`
  頂点の 3D 座標を返します。
- `get_edge_length(edge)`
  辺の長さを返します。
- `get_edge_points(edge)`
  辺の両端点座標を返します。
- `is_point_on_line_segment(point, start_point, end_point, tolerance=1e-6)`
  点が線分上にあるかを判定します。
- `edge_passes_through_point(edge, point, tolerance=1e-6)`
  辺が指定点を通るかを判定します。
- `find_face_by_axis_value(body, axis, value, tolerance=1e-6)`
  指定軸で一定値にある面を探します。現在は `x = 0.0` の分割面取得に使っています。
- `find_longest_edge(face)`
  面上の最長辺を返します。
- `find_shortest_edge(face)`
  面上の最短辺を返します。
- `find_edge_by_constant_axis(face, axis, value, tolerance=1e-6)`
  指定軸の値が一定な辺を返します。
- `find_vertex_by_coordinates(vertices, x=None, y=None, z=None, tolerance=1e-6)`
  指定座標に一致する頂点を返します。
- `find_face_through_origin(body, tolerance=1e-6)`
  原点を通る辺を持つ面を返します。
- `create_sketch_on_face(root_comp, face, name)`
  指定面上にスケッチを作り、名前を付けて返します。
- `project_face_edges(sketch, face)`
  面の輪郭辺をスケッチへ投影し、投影結果を返します。

## モデル別ドキュメント

モデル固有の説明は `model_docs/` に分けて管理します。

- `Left_hand_grip` の説明: [model_docs/Left_hand_grip/README.md](/home/ps/fusion_scripts/model_docs/Left_hand_grip/README.md)

## 注意事項

- `adsk` モジュールは通常の Python 環境ではそのまま実行できません
- 実行確認は Fusion 360 の `Design` ワークスペースで行います
- ルートの `1.py` と `2.py` が Fusion 360 から直接実行される前提です
- `fusion_app/` の変更を Fusion 360 側へ反映するには、`sync.sh` を実行して `fusion_app/` ごと同期します
- `__pycache__/` は生成物なので通常は管理対象として意識しません

## 現在の補足

- `留金部` は `留金部外部 ` スケッチの 2 領域を `-Z` 方向へ `2 mm` 押し出して作成しています。
- `留金部` の Z 方向直線エッジには `R1.0` フィレットを適用しています。
- `止金半円部` の先端円弧フィレットは有効です。
- 既知の状態として、`留金部` と `止金半円部` の接線側にもフィレットが残っています。現時点ではこの状態を許容して作業を継続しています。
