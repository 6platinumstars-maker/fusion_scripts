# Fusion API 3D Model Generator

Fusion API と Python を使って 3D モデルを生成し、Fusion 360 上で確認するためのリポジトリです。

## 構成

- `1.py`
  Fusion 360 で直接実行するメインの確認用スクリプトです。現在は `fusion_app/Left_hand_grip.py` と同じ内容を入れて使っています。
- `2.py`
  別案や比較用に使う実行スクリプトです。簡単な穴付きプレートのサンプルが入っています。
- `fusion_app/`
  Fusion API を使うアプリ本体の置き場です。案件ごとの完成コードはここに `名前.py` で置きます。
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
2. 確認したい内容を `1.py` か `2.py` にコピーする
3. `./sync.sh` を実行する
4. Fusion 360 で `1` または `2` を実行する

### `fusion_app/`

Fusion API を前提にした実装を置く場所です。現在は `Left_hand_grip.py` があり、左手グリップ形状のベーススケッチ作成、押し出し、分割断面の三角形処理までを担当しています。

作業の基本方針は次の通りです。

1. 案件ごとに `fusion_app/名前.py` を作る
2. その中で `run(context)` を入口にする
3. スケッチ作成、プロファイル選択、押し出し、探索処理を関数に分ける
4. 動作確認したい版を `1.py` にコピーする

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

実行コマンド:

```bash
cd /home/ps/fusion_scripts
./sync.sh
```

## 現在の主要スクリプト

### `fusion_app/Left_hand_grip.py`

現在の状態では、次の順序で形状を作ります。

1. XY 平面に底面内部スケッチを作る
2. その外形プロファイルを負方向へ押し出してベースボディを作る
3. `x = 0.0` の面を取得する
4. その面に分割断面の三角形スケッチを作る
5. 最小プロファイルを負方向へ `Join` 押し出しして底面斜面を作る
6. YZ 面に `上部止部` スケッチを作り、別ボディとして押し出したあと上面を押し上げる
7. YZ 面に `下部止部` スケッチを作り、ベースへ `Join` 押し出ししたあと `R5.0` フィレットをかける
8. XY 平面に `ジョイステック受け` スケッチを作り、`+Z` 方向へ 10 mm の切り取り押し出しを行う

## 関数の説明

### `fusion_app/Left_hand_grip.py`

- `create_base_sketch(root_comp)`
  底面内部の外形スケッチを XY 平面に作成します。左側の長さ、前後寸法、上辺の傾斜角をここで定義しています。
- `extrude_profile(root_comp, profile, distance_cm, direction, operation)`
  指定したプロファイルを指定距離だけ押し出す共通関数です。`NewBody` と `Join` の両方に使えます。
- `get_smallest_profile(sketch)`
  スケッチ内のプロファイルから最小面積のものを返します。分割断面の三角形選択に使います。
- `add_named_attribute(entity, name)`
  Fusion の属性機能を使って、対象エンティティに `fusion_scripts:name=<name>` を付けます。
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
- `load_fusion_helpers()`
  `core/` を import path に追加し、`fusion_helpers` を読み込みます。
- `run(context)`
  Fusion 360 から呼ばれる入口です。ベース形状、止部、フィレット、ジョイステック受けの切り取りまでを順に実行します。

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
- `fusion_app/` の変更だけでは Fusion 360 側には反映されないので、確認時は `1.py` か `2.py` へコピーしてから `sync.sh` を実行します
- `__pycache__/` は生成物なので通常は管理対象として意識しません
