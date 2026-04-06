# Left_hand_grip README

`fusion_app/Left_hand_grip.py` 用のモデル説明です。

## 対象ファイル

- スクリプト: [fusion_app/Left_hand_grip.py](/home/ps/fusion_scripts/fusion_app/Left_hand_grip.py)
- 実行用コピー: [1.py](/home/ps/fusion_scripts/1.py)

## 名前を付けた面・辺・頂点の説明

現在のコードで明示的に名前を付けているのは、スケッチと面です。辺と頂点にはまだ名前を付けていません。

### スケッチ

- `底面内部`
  XY 平面上に作るベース外形スケッチです。
- `分割断面`
  `x = 0.0` の面上に作る三角形の断面スケッチです。

### 面

- `分割断面`
  `create_split_triangle_on_face()` 内で属性 `fusion_scripts:name=分割断面` を付けている面です。ベースボディのうち `x = 0.0` にある側面を指します。

### 辺

現在のコードでは、辺に対して固有名は付けていません。

探索に使える関数:

- `find_longest_edge(face)`
- `find_shortest_edge(face)`
- `find_edge_by_constant_axis(face, axis, value, tolerance=1e-6)`

今後、特定の辺に属性名を付けたい場合は `add_named_attribute()` を辺エンティティにも使えます。

### 頂点

現在のコードでは、頂点に対して固有名は付けていません。

探索に使える関数:

- `find_vertex_by_coordinates(vertices, x=None, y=None, z=None, tolerance=1e-6)`

今後必要になれば、頂点にも `add_named_attribute()` で名前を付けられます。
