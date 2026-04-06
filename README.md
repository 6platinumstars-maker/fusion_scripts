# Fusion API 3D Model Generator

Fusion API と Python を使って 3D モデルを生成し、Fusion 360 上で確認するためのプロジェクトです。

## 概要

このフォルダでは、各プロジェクトで作成した Python ファイルを `1.py` または `2.py` に貼り付け、`sync.sh` を使って Windows 上の Fusion 360 Scripts フォルダへ同期します。

`1.py` / `2.py` は、Fusion ソフトウェア上で 3D モデルを確認できるようにするための実行用ファイルです。

## ファイルの役割

- `1.py`
  Fusion 360 で実行するためのスクリプトです。作成したプロジェクトコードを貼り付けて使います。
- `2.py`
  `1.py` と同じ用途の別ファイルです。別案や比較用のコードを切り替えて確認できます。
- `sync.sh`
  `fusion_scripts` 配下の `.py` ファイルを Windows 上の Fusion 360 Scripts フォルダへ同期するためのスクリプトです。
- `core/`
  純粋な Python のみを置くディレクトリです。Fusion API に依存しないロジックをまとめます。
- `fusion_app/`
  Fusion API のみを扱うディレクトリです。Fusion 360 側の処理をここにまとめます。
- `data/`
  JSON ファイルを置くディレクトリです。

## 基本フロー

1. 各プロジェクトを `名前.py` で作成する
2. 確認したいコードを `1.py` または `2.py` にコピーして貼り付ける
3. `sync.sh` を実行して Windows 側の Fusion 360 に同期する
4. Fusion 360 の `Scripts and Add-Ins` から `1` または `2` を実行する
5. Fusion 360 上で 3D モデルを確認する

## 使い方

### 1. プロジェクトコードを貼り付ける

各プロジェクトは通常 `名前.py` で作成します。

その中で Fusion 360 上で確認したいコードを、`1.py` か `2.py` にコピーして貼り付けます。

例:

- `sample_model.py` の内容を `1.py` に貼り付ける
- 別バージョンのコードを `2.py` に貼り付ける

### 2. Windows 側に同期する

次のコマンドを実行します。

```bash
cd /home/ps/fusion_scripts
./sync.sh
```

これにより、`1.py` / `2.py` などの Python ファイルが Windows 上の Fusion 360 Scripts フォルダへコピーされます。

### 3. Fusion 360 で確認する

1. Fusion 360 を開く
2. `Design` ワークスペースに移動する
3. `Scripts and Add-Ins` を開く
4. `1` または `2` を実行する
5. 生成された 3D モデルを確認する

## 注意事項

- `1.py` / `2.py` は Fusion 360 で実行することを前提にしています
- 通常のローカル Python 環境では `adsk` モジュールをそのまま実行できません
- `sync.sh` のコピー先は Windows 上の Fusion 360 の Scripts パスを前提にしています
- JSON データは `data/` に配置します
- Fusion API に依存しない処理は `core/` に分けます
- Fusion API を使う処理は `fusion_app/` に分けます
- 関数はできるだけ小さく分割して、役割を明確にします
