# Left_hand_grip README

`fusion_app/Left_hand_grip.py` 用のモデル説明です。

## 対象ファイル

- スクリプト: [fusion_app/Left_hand_grip.py](/home/ps/fusion_scripts/fusion_app/Left_hand_grip.py)
- 実行用コピー: [1.py](/home/ps/fusion_scripts/1.py)

## 現在の構成

`Left_hand_grip.py` は現在、次の順序で形状を作ります。

1. `底面内部` スケッチからベースボディを作成する
2. `分割断面` スケッチから三角形断面を作成する
3. YZ 面に `上部止部` スケッチを作成する
4. `上部止部` を `-X` 方向へ 25 mm 押し出して別ボディとして作成する
5. `上部止部` のうち、最も Z が高い XY 面を `+Z` 方向へ 3 mm 押し上げる

## 上部止部の確定仕様

- 名称: `上部止部`
- スケッチ面: YZ 面
- 押し出し方向: `-X`
- 押し出し量: 25 mm
- 外側円弧半径: `R9.0`
- 内側円弧半径: `R6.15`
- 内側円弧開始点: `(0.00, 30.00, 0.00)` mm
- 外側基準点: `(0.00, 30.00, -3.00)` mm
- 上面の追加押し上げ: 最上位 XY 面を `+Z` へ 3 mm

上端の寸法は、先端に三角突起が出ないよう、外側半径と内側半径の差に合わせて調整しています。

## 名前を付けた面・辺・頂点の説明

現在のコードで明示的に名前を付けているのは、スケッチ、面、ボディです。辺と頂点にはまだ名前を付けていません。

### スケッチ

- `底面内部`
  XY 平面上に作るベース外形スケッチです。
- `分割断面`
  `x = 0.0` の面上に作る三角形の断面スケッチです。
- `上部止部`
  YZ 面上に作る J 字断面のスケッチです。

### 面

- `分割断面`
  `create_split_triangle_on_face()` 内で属性 `fusion_scripts:name=分割断面` を付けている面です。ベースボディのうち `x = 0.0` にある側面を指します。

### ボディ

- `上部止部`
  YZ 面スケッチから生成する J 字形状のボディです。別ボディとして作成したあと、最上位 XY 面をさらに `+Z` へ 3 mm 押し上げています。

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
