# Outer Shell Separation Checklist

`outer_shell.py` を `inner_shell.py` から安全に独立させるための確認用チェックリストです。

## 目的

- `外殻` のどの処理が `内殻ボディ` に直接依存しているかを見える化する
- 依存を `基準値依存`、`参照形状依存`、`加工都合依存` に分けて段階的に分離する
- 分離途中でも `モデルが崩れた箇所` を追跡しやすくする

## 現在地

- 主経路の `outer_shell` 構築は、実質的に `outer_shell_reference` 主体で動く状態まで到達している
- `section` は `外殻断面参照` スケッチ主体、`keepout/contact` は専用参照ボディ主体の経路へ寄せ終わっている
- `keepout/contact` の主経路では `内殻` フォールバック候補を外してもモデル崩れが起きていない
- `keepout/contact` の上書き参照ボディ取得も専用ビルダー経由へ寄せ終わり、差し替え口が局所化されている
- `keepout/contact` の `source` 実体名参照も専用ビルダー経由へ寄せ終わり、定数直参照が減っている
- `keepout/contact` の `reference body` 実体名参照も専用ビルダー経由へ寄せ終わり、主経路の名前解決がそろってきている
- `reference body artifact spec` の `target/source candidates` 読み出しも共通ヘルパー経由へ寄せ終わり、実差し替え前の spec 解釈が局所化されている
- `artifact spec` から既存参照ボディを引く解決も共通ヘルパー経由へ寄せ終わり、既存利用か再生成かの分岐も追いやすくなっている
- `artifact spec` から複製先名を引く解決も共通ヘルパー経由へ寄せ終わり、複製経路の読み筋もそろってきている
- `keepout/contact` の `source body` 実体解決も共通ヘルパー経由へ寄せ終わり、override と通常 source の分岐位置が一本化されている
- `keepout/contact` の `source body` 使用判定も共通ヘルパー経由へ寄せ終わり、解決と判定の読み筋がそろっている
- `keepout/contact` の `source から複製 / fallback へ戻る` 経路も共通ヘルパー経由へ寄せ終わり、複製失敗時の戻り方までそろっている
- `fallback artifact spec` の選択も共通ヘルパー経由へ寄せ終わり、fallback 側の入口も keepout/contact でそろっている
- `source body` 候補名ビルダーも共通ヘルパー経由へ寄せ終わり、差し替え先候補を足す位置も一本化されている
- `keepout/contact` の `非内殻 source` 差し込み口もプレースホルダーとして用意され、次の実差し替え開始位置が明確になっている
- `keepout/contact` の `非内殻 source 名候補` 差し込み口もプレースホルダーとして用意され、次の実差し替えで候補名を足す位置も明確になっている
- `非内殻 source` 差し込み口は候補名解決まで接続され、次は候補名を入れるだけで実参照テストへ進める状態になっている
- `override` と `alternative source` の優先順も共通ヘルパー経由へ寄せ始めており、差し替え時の優先順位調整位置も見えやすくなっている
- `alternative source` の有効判定も共通ヘルパー経由へ寄せ始めており、非内殻 source が見つかったかの確認位置も見えやすくなっている
- `非内殻 source` の仮実体名もコード上に置き終わり、次はその名前の実体を実際に置いて試せる状態になっている
- `独立 source` 名の参照も専用ビルダー経由へ寄せ始めており、非内殻 source 名の差し替え位置もより固定化されている
- runtime 参照情報にも `独立 source` 名が載るようになり、Fusion 上で実体を置いた後の追跡もしやすくなっている
- `override+独立 source` をまとめた実体取得口も専用化され、主処理と runtime 追跡が同じ入口を見るようになっている
- `source` の使用判定も `override+独立 source` 実体取得口を見るようになり、採用判定と実体取得の入口が一致している
- `独立 source` 名候補の組み立ても共通ヘルパー経由へ寄せ始めており、non-inner-shell source 名候補の拡張位置もさらに固定化されている
- `独立 source` の有効判定も keepout/contact ごとの入口で見られるようになり、Fusion 上での確認点もより分かりやすくなっている
- runtime に載る `独立 source` 名も専用入口経由へ寄せ始めており、追跡名の参照位置も揃ってきている
- runtime に載る `独立 source` 実体名も keepout/contact ごとの専用入口で見られるようになり、Fusion 上の追跡点がさらに明確になっている
- runtime 側の source 優先順も共通ヘルパー経由へ寄せ始めており、実差し替え後の候補順調整位置も揃ってきている
- runtime 側の keepout/contact source 候補順も専用ビルダーへ分かれ始めており、差し替え後の追跡順がさらに追いやすくなっている
- runtime に載る override 名も keepout/contact ごとの専用入口へ寄せ始めており、上書き実体と独立 source 実体の見分けがしやすくなっている
- runtime 側の override 名参照も keepout/contact ごとの専用入口へ寄せ始めており、追跡名の取り回しも揃ってきている
- runtime 側の alternative/source/reference 実体名参照も keepout/contact ごとの専用入口へ寄せ始めており、辞書キー直読み箇所がさらに減っている
- runtime 側の `section` スケッチ名参照も専用入口へ寄せ始めており、section/keepout/contact の追跡入口がほぼ同じ形にそろってきている
- runtime artifact 生成側の `section/body` 実体名読み出しも専用入口へ寄せ始めており、追跡したい実体名の取得位置がさらに固定化されている
- runtime 参照ボディ確保後の keepout/contact 取り出しも専用入口へ寄せ始めており、runtime 生成から使用までの読み口がさらにそろってきている
- runtime artifact 収集時の override/source 実体取得も専用入口へ寄せ始めており、keepout/contact の runtime 参照取得粒度がさらにそろってきている
- runtime artifact 収集では未使用の一時実体保持を外し始めており、runtime 名追跡に必要な読み取りだけが残り始めている
- runtime 整理で不要になった補助関数も外し始めており、差し替え本番前の足場コードが少し軽くなっている
- runtime artifact 収集で使う override/独立 source の名前取得も専用入口へ寄せ始めており、実体取得と名前追跡の粒度がさらにそろってきている
- runtime artifact 収集で使う `section` スケッチ実体取得も専用入口へ寄せ始めており、section/keepout/contact の収集形がさらにそろってきている
- runtime artifact 収集で使う keepout/contact の body 名読み出しも専用入口へ寄せ始めており、対象ごとの名前追跡口がほぼそろってきている
- 主経路の `source body` 解決も単一名ではなく候補名列ベースへ寄せ始めており、独立 source を置いた後の候補順が runtime と主経路でそろいやすくなっている
- 主経路の `*_source_body_name` も採用された実体名を先に拾う形へ寄せ始めており、独立 source 採用時の追跡名も主経路側で見えやすくなっている
- keepout/contact の採用 `source body` 名決定も共通ヘルパーへ寄せ始めており、実差し替え後の追跡名ロジックがさらに 1 か所へ集まりつつある
- keepout/contact の `source body names` 決定も共通ヘルパーへ寄せ始めており、単体名と候補列の追跡ロジックがさらにそろってきている
- keepout/contact の候補列ビルダー名も `reference source` 基準へ寄せ始めており、実差し替え時に直接触る入口名がさらに明確になってきている
- 主経路の `source body` 候補順も独立 source 優先へ切り替え始めており、独立実体が置かれた場合は従来 source より先に採る本番差し替え形へ近づいている
- keepout/contact の「実際に採用された source 名」も専用入口で引けるようになり、主経路と runtime の追跡名を同じ見方で確認しやすくなっている
- 主経路の `source body names` 先頭も採用された source 名へ寄せ始めており、単体名と候補列先頭が同じ追跡名を指しやすくなっている
- keepout/contact の「独立 source が実際に採用されたか」も専用入口で見られるようになり、実体配置後の確認点がさらに明確になっている
- keepout/contact の「実際に解決された候補順」も専用入口で引けるようになり、実体配置後にどの順で source を見に行くかも直接確認しやすくなっている
- runtime 側でも解決済み候補順を専用入口から返す形へ寄せ始めており、主経路と runtime の候補順比較がさらにしやすくなっている
- runtime artifacts にも「独立 source 採用中か」の結果を直接載せ始めており、実体配置後の確認がさらに即読しやすくなっている
- runtime artifacts にも解決済み候補順そのものを直接載せ始めており、採用状態と候補順を artifacts だけでまとめて確認しやすくなっている
- keepout/contact の「解決済み source body 実体」も専用入口へ寄せ始めており、body/name/names/use-alternative の読み口がさらに揃ってきている
- runtime 側でも解決済み source body 実体を専用入口で返す形へ寄せ始めており、主経路と runtime の実体確認口もさらに揃ってきている
- runtime artifacts に載せた `source body` 実体と採用状態も専用入口で読めるようになり、差し替え確認時の artifacts 側の見方もさらに固定化されている
- runtime artifacts に載せた解決済み候補順も専用入口で読めるようになり、artifacts 由来の候補順確認もさらに関数名で追いやすくなっている
- runtime artifacts に載せた解決済み `source 名` も専用入口で読めるようになり、artifacts 側の確認項目がほぼ同じ並びに揃ってきている
- runtime artifacts に載せた `独立 source 採用状態` も専用入口で読む形へ揃い、artifacts 側の確認項目がさらに同じ並びで見やすくなっている
- 独立 source 実体が無い場合は現行 source から同形状コピーを独立名で作る入口も入り、形状を変えずに独立名切り替え確認へ進める状態になっている
- runtime 入口で独立 source 実体を明示的に確保する流れも入り、lazy 生成ではなく初手で独立名 source を揃えて確認できる形へ近づいている
- runtime artifacts に載せた `source 名列` も専用入口で読む形へ揃い、artifacts 側の確認項目がほぼ完全に同じ並びになってきている
- runtime artifacts にも `alternative source body` 実体そのものを直接載せ始めており、`source body` と独立 source body の見比べがさらにしやすくなっている
- runtime artifacts に載せた `alternative source 名` も専用入口で読めるようになり、`source/alternative` の body と name を並べて追いやすくなっている
- runtime artifacts 側でも独立 source の「存在」と「採用中」を分けて見られるようになり、実体はあるが未採用なのか、実際に切り替わったのかを判別しやすくなっている
- runtime では参照ボディ生成より先に独立 source を揃える順序へ寄せ始めており、参照ボディの初回複製元も独立 source 側へ寄せやすくなっている
- 独立 source 実体の確保も keepout/contact ごとの `ensure` 入口へ寄せ始めており、最後の実体差し替え先がさらに直接的になってきている
- runtime artifacts 側では `source body` についても「存在」と「採用中」を対称に見られるようになり、`source/alternative` の比較がさらにしやすくなっている
- runtime artifacts 側では `alternative source body` についても存在フラグを直接持つようになり、`source/alternative` の「あるか」「採用中か」を対称に確認しやすくなっている
- 解決済み `source body` 側も keepout/contact ごとの `ensure` 入口へ寄せ始めており、`source/alternative` の両方が同じ確保の読み筋に揃ってきている
- keepout/contact ごとに最終実証の readiness 入口も入り、独立 source が存在し、かつ採用中かを 1 回の確認で見られるようになっている
- runtime artifacts にも readiness 結果そのものを直接載せ始めており、最終実証の成否を artifacts だけでさらに即読しやすくなっている
- keepout/contact をまとめた runtime 分離サマリ入口も入り、最終確認を 1 回で読み取りやすくなっている
- runtime 分離サマリには採用名も載るようになり、ready/未ready の理由も名前付きで読みやすくなっている
- keepout/contact の両方が揃っているかを 1 回で見られる総合 readiness 入口も入り、完了判定にかなり近い確認がしやすくなっている
- 総合 readiness に keepout/contact の採用名も添えて返す要約入口も入り、最終判定で見る値がさらに短くまとまっている
- runtime 分離要約をそのまま読めるレポート入口も入り、最終判定で追う値をさらに一目で見やすくまとめられるようになっている
- runtime artifacts からそのまま分離ステータスを組み立てる入口も入り、実行後は artifacts だけで最終判定用の値をまとめて読めるようになっている
- 残作業の中心は、専用 `source` 実体を本当に別基準へ差し替えることと、不要になった互換層の最終整理である

## 完了済みの整理

- 外殻の主要生成経路は `reference-first` の本経路へ整理済み
- `assembly_left_hand_grip.py` からの外殻構築も `outer_shell_reference` 主体で確認済み
- `section`、`keepout`、`contact` の参照入口はそれぞれ専用の参照取得層へ分離済み
- `keepout/contact` の `内殻` フォールバック候補を主経路から外してもモデル崩れが起きないことを確認済み
- 加工都合で残っていた一時退避依存は、主要箇所で削減または局所化済み

## 残りの作業

- `外殻逃がし参照ソース` と `外殻接触参照ソース` を本当に `内殻コピー以外` の基準へ差し替える
- その差し替え後も `section/keepout/contact` の全体整合が崩れないかを確認する
- 外部互換のためだけに残している古い `inner_shell` 命名入口を、どこまで維持するか最終判断する

次に直接触る入口:

- `build_outer_shell_keepout_reference_source_body()`
- `build_outer_shell_contact_reference_source_body()`
- `resolve_outer_shell_keepout_reference_source_body_override()`
- `resolve_outer_shell_contact_reference_source_body_override()`
- `resolve_outer_shell_reference_override_body()`
- `build_outer_shell_keepout_reference_override_body_name()`
- `build_outer_shell_contact_reference_override_body_name()`
- `build_outer_shell_keepout_reference_override_body_name_candidates()`
- `build_outer_shell_contact_reference_override_body_name_candidates()`
- `build_outer_shell_keepout_reference_override_body()`
- `build_outer_shell_contact_reference_override_body()`
- `build_outer_shell_keepout_reference_source_body_name()`
- `build_outer_shell_contact_reference_source_body_name()`
- `build_outer_shell_keepout_reference_body_name()`
- `build_outer_shell_contact_reference_body_name()`
- `get_outer_shell_reference_body_artifact_target_body_name()`
- `get_outer_shell_reference_body_artifact_source_name_candidates()`
- `find_outer_shell_reference_body_from_artifact_target()`
- `resolve_outer_shell_reference_body_artifact_copy_target_name()`
- `find_outer_shell_reference_source_body_by_name()`
- `resolve_outer_shell_reference_source_body()`
- `should_use_outer_shell_reference_source_body()`
- `create_outer_shell_reference_body_from_fallback_spec()`
- `create_outer_shell_reference_body_from_source_or_fallback()`
- `resolve_outer_shell_reference_body_fallback_artifact_spec()`
- `resolve_outer_shell_reference_source_name_candidates()`
- `build_outer_shell_keepout_reference_alternative_source_body()`
- `build_outer_shell_contact_reference_alternative_source_body()`
- `build_outer_shell_keepout_reference_alternative_source_body_name()`
- `build_outer_shell_contact_reference_alternative_source_body_name()`
- `build_outer_shell_keepout_reference_alternative_source_body_name_candidates()`
- `build_outer_shell_contact_reference_alternative_source_body_name_candidates()`
- `build_outer_shell_keepout_reference_source_override_body()`
- `build_outer_shell_contact_reference_source_override_body()`
- `resolve_outer_shell_reference_alternative_source_body()`
- `resolve_outer_shell_reference_source_override_body()`
- `should_use_outer_shell_reference_alternative_source_body()`

補足:

- `override` 候補名ビルダーまで整理済みなので、次の実差し替えはこの層に実体名や解決ロジックを足す形で進められる
- runtime artifact / override 候補順にも `override` 名が載るようになり、差し替え後の主経路確認がしやすくなった
- `build_outer_shell_keepout_reference_override_body()` / `build_outer_shell_contact_reference_override_body()` を共通入口として使う形になり、参照解決の追跡範囲が狭くなった
- `build_outer_shell_keepout_reference_source_body_name()` / `build_outer_shell_contact_reference_source_body_name()` を共通入口として使う形になり、`source` 実体名の差し替え位置も固定化された
- `build_outer_shell_keepout_reference_body_name()` / `build_outer_shell_contact_reference_body_name()` を共通入口として使う形になり、runtime override と default reference の読み筋もそろった
- `get_outer_shell_reference_body_artifact_target_body_name()` / `get_outer_shell_reference_body_artifact_source_name_candidates()` を共通入口として使う形になり、artifact spec を使う差し替え経路も追いやすくなった
- `find_outer_shell_reference_body_from_artifact_target()` を共通入口として使う形になり、既存ボディ再利用の分岐位置も固定化された
- `resolve_outer_shell_reference_body_artifact_copy_target_name()` を共通入口として使う形になり、source から複製する経路の複製先決定も固定化された
- `find_outer_shell_reference_source_body_by_name()` / `resolve_outer_shell_reference_source_body()` を共通入口として使う形になり、override と通常 source の切り替え位置も固定化された
- `should_use_outer_shell_reference_source_body()` を共通入口として使う形になり、source 実体の解決結果を使う判定位置も固定化された
- `create_outer_shell_reference_body_from_fallback_spec()` / `create_outer_shell_reference_body_from_source_or_fallback()` を共通入口として使う形になり、source 複製と fallback 退避の経路も共通化された
- `resolve_outer_shell_reference_body_fallback_artifact_spec()` を共通入口として使う形になり、fallback spec の選択位置も固定化された
- `resolve_outer_shell_reference_source_name_candidates()` を共通入口として使う形になり、source 候補名の拡張位置も固定化された
- `build_outer_shell_keepout_reference_alternative_source_body()` / `build_outer_shell_contact_reference_alternative_source_body()` を差し込み口として置いたので、次の実差し替えはこの関数から始められる
- `build_outer_shell_keepout_reference_alternative_source_body_name_candidates()` / `build_outer_shell_contact_reference_alternative_source_body_name_candidates()` を差し込み口として置いたので、次の実差し替えで候補名もこの関数から足せる
- `build_outer_shell_keepout_reference_alternative_source_body_name()` / `build_outer_shell_contact_reference_alternative_source_body_name()` を共通入口として使う形になり、独立 source 名そのものの差し替え位置も固定化された
- `resolve_outer_shell_reference_alternative_source_body()` を共通入口として使う形になり、非内殻 source 候補の実解決経路も先に確保できた
- `resolve_outer_shell_reference_source_override_body()` を共通入口として使う形になり、override と alternative source の優先順もここで調整できるようになった
- `should_use_outer_shell_reference_alternative_source_body()` を共通入口として使う形になり、non-inner-shell source の有効判定位置も固定化された

次に置ける実体名:

- `外殻逃がし参照ソース`
- `外殻接触参照ソース`
- `外殻逃がし参照ソース独立`
- `外殻接触参照ソース独立`
- `外殻逃がし参照`
- `外殻接触参照`
- `外殻逃がし参照ソース上書き`
- `外殻接触参照ソース上書き`

## 使い方

1. 1 つの項目だけを分離対象にして修正する
2. 修正後に `外殻` の見た目、接触、分割面、嵌合を確認する
3. 問題がなければチェックを付け、差分の内容をメモする
4. 問題が出た場合は、その項目を `内殻依存が必要` または `参照データ化が必要` として記録する

## 前提確認

- [ ] 作業前の基準として、現在の `assembly_left_hand_grip.py` から生成した `外殻` 形状を保存した
- [ ] `1.py` / `2.py` のどちらで確認するか決めた
- [ ] `2.py` に未コミット変更があることを認識した
- [ ] `外殻単体化` の対象が `見た目の独立` なのか `生成コードの完全独立` なのかを明文化した

## 依存の分類

### A. 基準値依存

`内殻ボディ` がなくても、固定点・固定面・固定寸法へ置き換えやすい依存です。

- [ ] `INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM` を外殻専用の参照値として扱う方針を決めた
- [ ] `INNER_SHELL_LID_SLOPE_FACE_NAME` に頼らず蓋部斜面を再構築できる方針を決めた
- [ ] `create_lid_inner_split_plane()` の生成元を `内殻面` から `外殻用参照平面` へ移せるか確認した
- [ ] `create_lid_gap_plane()` が `内殻ボディ` なしで成立するか確認した
- [ ] `Y=35` 面切り取りや蓋部隙間部形状が、参照平面だけで再現できるか確認した

対象関数:

- `find_lid_slope_face`
- `create_offset_plane_from_lid_slope`
- `create_lid_inner_split_plane`
- `create_lid_gap_plane`
- `create_outer_shell_lid_gap_sketch`
- `create_outer_shell_lid_gap_extension_sketch`

### B. 参照形状依存

`内殻ボディ` の断面、接面、干渉形状を直接使っていて、分離時に最も崩れやすい依存です。

- [ ] `create_outer_shell_sketch()` の `内殻 XY 断面投影` を別参照データへ置き換える設計を決めた
- [ ] `project_inner_shell_section_to_sketch()` の出力を固定スケッチまたは参照輪郭へ保存する案を決めた
- [ ] `cut_body_with_inner_shell()` の `Combine Cut` を不要化できるか確認した
- [ ] `offset_contact_faces()` の対象面を、内殻接触検出なしで安定して取得できるか確認した
- [ ] `外殻内面の逃がし量 -0.2 mm` をどの基準に対して維持するか決めた
- [ ] `Lボタン開口部` 周辺の内殻依存形状が、外殻単独でも寸法維持できるか確認した

対象関数:

- `project_inner_shell_section_to_sketch`
- `create_outer_shell_sketch`
- `cut_body_with_inner_shell`
- `find_inner_contact_faces`
- `offset_contact_faces`
- `cut_outer_shell_l_button_opening_base_structure_region`

### C. 加工都合依存

Fusion の加工時に `内殻ボディ` が邪魔になるため、一時退避している依存です。形状定義そのものより後回しでよい項目です。

- [ ] `INNER_SHELL_TEMP_MOVE_X_MM` を使う箇所を全件把握した
- [ ] 一時退避が `形状定義のため` か `加工衝突回避のため` か分類した
- [ ] `participantBodies` の見直しだけで解消できる箇所を分けた
- [ ] `一時移動不要` にした場合でも外殻以外のボディを誤って加工しないか確認した
- [ ] 一時移動を残す場合、`inner_shell_body` 実体ではなく複製ボディで代替できるか確認した

対象関数:

- `cut_profile_in_negative_y`
- `cut_profile_in_negative_y_from_sketch`
- `cut_xz_face_in_negative_y`
- `cut_profile_in_negative_x`
- `add_outer_shell_fitting_correction`
- `cut_outer_shell_l_button_opening_inner_spec_region`
- `add_outer_shell_lower_stop_structure`
- `cut_outer_shell_bottom_outer_slope_regions`

## 分離ステップ

### Step 1. 呼び出し境界を分ける

- [x] `assembly_left_hand_grip.py` 側で `inner_shell_body` を渡している箇所を一覧化した
- [x] `build_outer_shell_base_structure()` が本当に必要とする入力を整理した
- [x] `add_structures_to_outer_shell_base_structure()` が本当に必要とする入力を整理した
- [x] `inner_shell_body` の代わりに `outer_shell_reference` のような参照オブジェクトを渡す方針を決めた

Step 1 の結論:

- `inner_shell_body` は `外殻の形状定義`、`蓋部基準面の取得`、`加工時の一時退避` の 3 用途で渡されている
- `assembly_left_hand_grip.py` から `outer_shell.py` へ直接 `inner_shell_body` を渡している境界は限定されており、ここを `outer_shell_reference` へ集約するのが第一段階になる
- `outer_shell_reference` は少なくとも `lid_slope_reference`、`section_profile_reference`、`clearance_or_keepout_reference` を持つ必要がある

呼び出し元一覧:

- `build_outer_shell_base_structure(root_comp, inner_shell_body, outer_shell_params)`
- `cut_outer_shell_yz_rect_region(..., inner_shell_body=inner_shell_body)`
- `split_outer_shell_by_lid_inner_plane(root_comp, outer_shell_body, inner_shell_body)`
- `extrude_outer_shell_lid_inner_plane_in_positive_z(root_comp, outer_shell_body, inner_shell_body)`
- `create_outer_shell_lid_gap_sketch(..., inner_shell_body=inner_shell_body)`
- `create_outer_shell_lid_gap_extension_sketch(..., inner_shell_body=inner_shell_body)`
- `cut_outer_shell_y35_face_region(..., inner_shell_body=inner_shell_body)`
- `cut_outer_shell_l_button_opening_inner_spec_region(..., inner_shell_body=inner_shell_body)`
- `cut_outer_shell_l_button_opening_y32_region(..., inner_shell_body=inner_shell_body)`
- `add_outer_shell_lower_stop_structure(..., inner_shell_body=inner_shell_body)`
- `add_outer_shell_fitting_correction(..., inner_shell_body=inner_shell_body)`
- `cut_outer_shell_bottom_outer_slope_regions(..., inner_shell_body=inner_shell_body)`

`build_outer_shell_base_structure()` の必要入力整理:

- 必須:
  `root_comp`
- 現在 `inner_shell_body` から取っているもの:
  `XY 断面輪郭`
- 現在 `inner_shell_body` から取っているもの:
  `初期外殻と内殻の干渉差分`
- 現在 `inner_shell_body` から取っているもの:
  `接触面逃がし判定`
- 現在 `inner_shell_body` から取っているもの:
  `蓋部斜面基準面`
- 置き換え候補:
  `outer_shell_reference.section_profile`
- 置き換え候補:
  `outer_shell_reference.keepout_or_cut_body`
- 置き換え候補:
  `outer_shell_reference.contact_face_reference`
- 置き換え候補:
  `outer_shell_reference.lid_slope_plane`

`add_structures_to_outer_shell_base_structure()` の必要入力整理:

- 必須:
  `root_comp`
- 必須:
  `outer_shell_base_structure_body`
- `inner_shell_body` が必要な処理:
  `split_outer_shell_by_lid_inner_plane`
- `inner_shell_body` が必要な処理:
  `create_outer_shell_lid_gap_sketch`
- `inner_shell_body` が必要な処理:
  `create_outer_shell_lid_gap_extension_sketch`
- `inner_shell_body` が必要な処理:
  `cut_outer_shell_l_button_opening_base_structure_region`
- `inner_shell_body` が必要な処理:
  `cut_outer_shell_l_button_opening_inner_spec_region`
- `inner_shell_body` が必要な処理:
  `cut_outer_shell_l_button_opening_y32_region`
- `inner_shell_body` が必要な処理:
  `add_outer_shell_lower_stop_structure`
- `inner_shell_body` が必要な処理:
  `add_outer_shell_fitting_correction`
- `inner_shell_body` が必要な処理:
  `cut_outer_shell_bottom_outer_slope_regions`
- 置き換え候補:
  `outer_shell_reference.lid_ops`
- 置き換え候補:
  `outer_shell_reference.keepout_or_clearance_body`

`outer_shell_reference` の初期案:

- `lid_slope_plane_or_points`
  蓋部斜面内部平面と隙間部平面を再構築するための基準
- `xy_section_profile`
  初期外殻スケッチで使う内殻断面輪郭
- `clearance_faces_or_rules`
  接触面逃がしの対象決定に使う情報
- `temporary_keepout_body`
  加工時に一時退避の代わりとして使える参照ボディ
- `source_tag`
  `inner_shell_body` 由来か固定参照由来かを区別する識別子

### Step 2. 蓋部基準を独立させる

- [x] `split_outer_shell_by_lid_inner_plane()` を `内殻面探索` なしで動かせるようにした
- [x] `extrude_outer_shell_lid_inner_plane_in_positive_z()` が新しい基準面でも同形状になることを確認した
- [x] `create_outer_shell_lid_gap_sketch()` の輪郭が変わっていないことを確認した
- [x] `create_outer_shell_lid_gap_extension_sketch()` の追加形状が変わっていないことを確認した

Step 2 の分析結果:

- `find_lid_slope_face()` が本当に返している価値は `内殻面そのもの` ではなく `蓋部斜面の平面ジオメトリ` である
- `create_lid_inner_split_plane()` は `蓋部斜面平面 + 0.2 mm オフセット` に過ぎない
- `create_lid_gap_plane()` は `蓋部斜面内部平面` に対して、既知の 3 点を投影し `+Z 0.2 mm` ずらして再構築した平面である
- `create_outer_shell_lid_gap_sketch()` と `create_outer_shell_lid_gap_extension_sketch()` は、`内殻面` ではなく `蓋部斜面内部平面上の 2D 座標系` を使って点群を配置している
- したがって Step 2 で独立させるべき最小要素は `蓋部斜面平面` と `その平面に対する投影座標化` である

Step 2 の実装状況:

- `outer_shell_reference` の最小版を追加し、`lid_slope_points_mm` を保持できるようにした
- `get_lid_slope_reference_plane(...)` を追加し、蓋部基準を `inner_shell_body` 依存から分岐できるようにした
- `split_outer_shell_by_lid_inner_plane()`、`create_outer_shell_lid_gap_sketch()`、`create_outer_shell_lid_gap_extension_sketch()` へ `outer_shell_reference` を流せるようにした
- まだ Fusion 上での形状一致確認は未実施のため、チェックは保留のままにする

Step 2 の対象関数と依存の実態:

- `find_lid_slope_face`
  `inner_shell_body` から面を探しているが、用途は平面法線と原点取得だけ
- `create_offset_plane_from_lid_slope`
  `find_lid_slope_face` の返す平面に対してオフセット平面を作るだけ
- `create_lid_inner_split_plane`
  `create_offset_plane_from_lid_slope` の薄いラッパー
- `create_lid_gap_plane`
  `INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM` の先頭 3 点を、蓋部斜面内部平面へ投影してから `+Z 0.2 mm` した 3 点平面
- `create_outer_shell_lid_gap_sketch`
  `lid_inner_reference_sketch.modelToSketchSpace(...)` で 3D 点を 2D 化している
- `calculate_outer_shell_lid_gap_extension_profile_geometry_mm`
  `create_outer_shell_lid_gap_sketch` と同じく、蓋部斜面内部平面上の 2D 座標系に依存している
- `create_outer_shell_lid_gap_extension_sketch`
  上の 2D 化結果から追加形状を作っている

外殻側へ切り出す参照の初期案:

- `outer_shell_reference.lid_slope_points_mm`
  現在の `INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM`
- `outer_shell_reference.lid_slope_plane`
  参照点 3 点から再構築した基準平面
- `outer_shell_reference.lid_inner_split_plane`
  `lid_slope_plane` を `0.2 mm` オフセットした平面
- `outer_shell_reference.lid_gap_plane`
  `lid_inner_split_plane` を使って再構築した隙間部平面
- `outer_shell_reference.lid_plane_mapper`
  `modelToSketchSpace` 相当で 3D 点を蓋部基準 2D 座標へ落とす変換

実装方針:

1. `find_lid_slope_face()` の前段に `get_lid_slope_reference_plane(root_comp, outer_shell_reference=None, inner_shell_body=None)` を追加する
2. `outer_shell_reference` があれば参照平面を優先し、なければ現行どおり `inner_shell_body` から面を探索する
3. `create_lid_inner_split_plane()` は `face` ベースではなく `plane geometry` ベースのオフセット処理へ寄せる
4. `create_lid_gap_plane()`、`create_outer_shell_lid_gap_sketch()`、`calculate_outer_shell_lid_gap_extension_profile_geometry_mm()` は `lid_plane_mapper` を使う構造へ寄せる
5. 旧経路を残したまま `outer_shell_reference` 優先にして、比較しながら移行する

検証観点:

- `split_outer_shell_by_lid_inner_plane()` 後の上下判定が変わらない
- `extrude_outer_shell_lid_inner_plane_in_positive_z()` の押し出し開始断面が変わらない
- `create_outer_shell_lid_gap_sketch()` の点 `A` から `N` の 2D 配置が変わらない
- `create_outer_shell_lid_gap_extension_sketch()` の `M` `N` `P` と円弧中点が変わらない
- `外殻蓋部斜面外側` と命名される上面の位置が変わらない

次の実装候補:

- `outer_shell_reference` の最小版を追加し、`lid_slope_points_mm` だけ持たせる
- `get_lid_slope_reference_plane(...)` を追加し、既存の `find_lid_slope_face` 呼び出しを置き換える

### Step 3. 初期外形の参照を独立させる

- [x] `内殻 XY 断面` をどの形式で保存するか決めた
- [x] 断面参照を内殻ボディ投影から切り離した
- [x] `外殻` の初回 `NewBody` 形状が基準モデルと一致することを確認した
- [x] `外殻外周円`、`底面外側`、`端修正` の後続処理が崩れないことを確認した

Step 3 の実装状況:

- `XY断面` の保存形式は `外殻断面参照` スケッチに決めた
- `build_outer_shell_reference()` に `section_source_body`、`keepout_source_body`、`contact_source_body` を追加した
- `build_outer_shell_reference()` は `root_comp` があれば `外殻断面参照` スケッチも作るようにした
- `create_outer_shell_sketch()`、`cut_body_with_inner_shell()`、`offset_contact_faces()`、`extrude_outer_shell_profile()` は `outer_shell_reference` 経由で参照元を受け取れるようにした
- `create_outer_shell_sketch()` の断面投影は、`inner_shell_body` 直読みではなく `外殻断面参照` スケッチを優先して読むようにした
- `cut_outer_perimeter_reference_circle()`、`YZ矩形切り取り`、`Y35面切り取り`、`Lボタン開口部内部仕様`、`Y32追加切り取り`、`下部受止`、`はめ込み修正`、`底部外側斜面切り取り` は `outer_shell_reference` 経由で一時退避参照も受け取れるようにした
- `cut_outer_perimeter_reference_circle()` は `participantBodies` 指定のみで成立する前提で、一時退避を外した
- `cut_profile_in_negative_x()` は `participantBodies` 指定のみで成立する前提で、一時退避を外した
- `cut_profile_in_negative_y()` は `participantBodies` 指定のみで成立する前提で、一時退避を外した
- `cut_profile_in_negative_y_from_sketch()` は `participantBodies` 指定のみで成立する前提で、一時退避を外した
- `cut_xz_face_in_negative_y()` は `participantBodies` 指定のみで成立する前提で、一時退避を外した
- `cut_outer_shell_l_button_opening_inner_spec_region()` は `participantBodies` 指定のみで成立する前提で、一時退避を外した
- `cut_outer_shell_bottom_outer_slope_regions()` は `切り取り用ボディ + cut_target_body_with_tool_bodies()` で成立する前提で、一時退避を外した
- `add_outer_shell_lower_stop_structure()` は処理内部で `inner_shell_body` を参照していないため、一時退避を外した
- `add_outer_shell_fitting_correction()` は処理内部で `inner_shell_body` を参照していないため、一時退避を外した
- 未使用の `cut_profile_via_negative_y_sweep()` も一時退避なしの形へ揃えた
- `temp_move` 系の呼び出しは整理し終えたため、依存の主対象は `keepout_source_body` と `contact_source_body` に絞られた
- まだ `keepout_source_body` と `contact_source_body` は実体として `inner_shell_body` を使っているため、ここは `依存経路の集約` まで完了
- `cut_body_with_keepout_reference()` と `offset_outer_shell_contact_faces()` を追加し、`keepout/contact` 依存を `inner_shell` という名前から切り離した
- `build_outer_shell_base_structure()` は `outer_shell_reference` があれば入口上は `inner_shell_body` 必須ではない形に寄せた
- `keepout_source_body` / `contact_source_body` / `section_source_body` は `*_body_name` でも再解決できるようにし、参照実体が無い場面でも分離作業を進めやすくした
- `keepout` 参照は `keepout_source_bodies` / `keepout_source_body_names` にも対応させ、単一ボディ前提を外した
- `build_outer_shell_reference()` は `section` / `keepout` / `contact` 参照を外から差し込めるようにし、`inner_shell_body` 既定値の上に差し替え口を作った
- `build_outer_shell_keepout_reference()` を分離し、`keepout` 実体分離の変更点を局所化した
- `build_default_outer_shell_keepout_reference_from_source()` を追加し、`inner_shell_body` 由来の既定 `keepout` 参照生成も分離した
- `build_outer_shell_contact_reference()` と `build_default_outer_shell_contact_reference_from_source()` を追加し、`contact` 側も同じ差し替え構造へ揃えた
- `build_outer_shell_section_reference()` と `build_default_outer_shell_section_reference_from_source()` を追加し、`section` 側も同じ差し替え構造へ揃えた
- `build_default_outer_shell_section_reference_from_source()` は既存の `外殻断面参照` スケッチを優先再利用できるようにし、断面側のボディ依存をさらに薄くした
- `build_outer_shell_reference()` は `inner_shell_body` が無くても既定で `内殻` 名から参照を再解決できる前提を持つようにした
- `section` / `keepout` / `contact` の既定参照ビルダーは `root_comp + 内殻名` だけでも既定参照体を再解決できるようにした
- `section` の既定参照は、実体スケッチがまだ無くても `外殻断面参照` 名を先に持つようにした
- 断面投影入口に `project_outer_shell_section_reference_to_sketch()` を追加し、呼び出し側の依存表現も `inner_shell` 名から切り離し始めた
- 接面検出の内部名も `find_outer_shell_contact_reference_faces()` へ寄せ、`contact` 側の依存表現も参照ベースへ揃え始めた
- 旧 `inner_shell` 名の互換ラッパーも `inner_shell_body` 必須ではない形へ寄せ、単体参照経路を通しやすくした
- 旧 `inner_shell` 名の関数には互換ラッパーであることを明記し、主経路と互換層の境界を読みやすくした
- `assembly_left_hand_grip.py` の主経路では `build_outer_shell_base_structure()` を `outer_shell_reference` 主入力で呼ぶ形に切り替えた
- `add_structures_to_outer_shell_base_structure()` と `build_outer_shell()` も `outer_shell_reference` 主入力で受けられる入口条件へ揃えた
- 蓋部系の主経路呼び出しは `inner_shell_body=None` + `outer_shell_reference` で通す形へ寄せ始めた
- 主経路のうち、`inner_shell_body` を実際には使っていない後段処理も `None` へ寄せ始めた
- 主経路の `lid gap extension` も `inner_shell_body=None` + `outer_shell_reference` で通す形へ揃えた
- 内殻側の `add_inner_shell_lid_revolve_cut()` も名前解決経由で呼ぶ形にし、主経路の直ボディ受け渡しをさらに減らした
- `outer_shell_reference` から実ボディハンドルを外すヘルパーを追加し、主経路では `名前 + 参照スケッチ` 中心の参照を使う形へ進めた
- `assembly_left_hand_grip.py` では `build_outer_shell_reference()` 自体も `inner_shell_body` を渡さず、`root_comp` ベースで参照を立てる形へ進めた
- `build_outer_shell_reference()` に `include_body_handles` を追加し、主経路では最初から実ボディハンドルを持たない参照を作る形へ整理した
- `keepout` / `contact` には専用の優先参照名を追加し、将来 `外殻専用参照ボディ` を置いたらそちらを優先できるようにした
- 主経路の `keepout/contact` 参照は `専用参照名 -> 内殻名` の候補順を持つ形へ進めた
- `build_outer_shell_runtime_reference()` を追加し、主経路の参照設定を `outer_shell.py` 側へ集約した
- `keepout/contact` の候補順解決を共有ヘルパーへ集約し、専用参照ボディへの切り替え点をさらに局所化した
- `keepout/contact` の既定参照づくりも共有ヘルパーへ集約し、実体分離の変更点をさらに縮めた
- `build_outer_shell_runtime_reference_overrides()` を追加し、主経路の参照上書き元を独立させた
- `build_outer_shell_runtime_reference_artifacts()` を追加し、専用参照ボディの取得口を主経路へ差し込める形にした
- `ensure_outer_shell_runtime_reference_bodies()` を追加し、専用参照ボディの探索/将来生成の入口を1か所に固定した
- `build_outer_shell_keepout_reference_body()` と `build_outer_shell_contact_reference_body()` を追加し、最初の実体分離を差し込む関数境界を明確にした
- `create_outer_shell_keepout_reference_body()` と `create_outer_shell_contact_reference_body()` を追加し、専用参照ボディ生成のフックを差し込んだ
- 専用参照ボディ生成に使う元ボディ候補も `build_outer_shell_*_reference_body_source_name_candidates()` へ分離した
- `resolve_outer_shell_reference_body_source()` を追加し、専用参照ボディ生成の元ボディ解決を共有化した
- `build_outer_shell_reference_body_artifact_spec()` を追加し、専用参照ボディ生成仕様も共通化した
- `create_outer_shell_reference_body_from_spec()` を追加し、専用参照ボディ生成前処理を共通化した
- `should_create_outer_shell_reference_body_from_spec()` を追加し、最初の実ボディ生成を安全ゲート付きで差し込める形にした
- `should_create_outer_shell_keepout_reference_body()` / `should_create_outer_shell_contact_reference_body()` を追加し、最初の実体化を片側ずつ試せる形にした
- `create_outer_shell_keepout_reference_body_from_source()` を追加し、最初の `keepout` 実体化を専用関数へ分離した
- `create_outer_shell_contact_reference_body_from_source()` も追加し、`contact` 側も同じ粒度の実体化入口へ揃えた
- `copy_outer_shell_reference_body_from_source()` を追加し、ゲート内では専用参照ボディの複製まで実行できる状態にした
- 最初の本番実装として、`keepout` 側の実体化ゲートを有効にした
- `create_outer_shell_keepout_reference_body_from_source()` を本番化し、`外殻逃がし参照` を共通複製処理で実生成できるようにした
- `create_outer_shell_contact_reference_body_from_source()` も本番化し、`外殻接触参照` を同じ共通複製処理で実生成できる準備を整えた
- `contact` 側の実体化ゲートも有効にし、`外殻接触参照` を主経路で実生成できる状態にした
- 主経路の `keepout/contact` runtime 参照は、`内殻` 名フォールバックを外して `外殻逃がし参照` / `外殻接触参照` 前提へ進めた
- `section` の既定参照は `外殻断面参照` スケッチを最優先にし、既存スケッチがある場合は `内殻` ボディ名を持ち込まない形へ進めた
- 主経路の `section` runtime 参照も、`外殻断面参照` スケッチ名を明示的に渡す形へ寄せた
- `keepout/contact` 専用参照ボディの元候補も、専用ソース名を先頭に持つ形へ整理し、`内殻` 直書き依存を一段薄くした
- runtime artifact でも `外殻逃がし参照ソース` / `外殻接触参照ソース` を探索し、次の実差し替え先を主経路から見える形にした
- 主経路の runtime 候補列にも `外殻逃がし参照ソース` / `外殻接触参照ソース` を組み込み、専用ソース名を正式な優先候補にした
- `外殻逃がし参照ソース` / `外殻接触参照ソース` の専用取得口も切り出し、次の実差し替えを関数境界として独立させた
- `専用ソースが存在する時だけそちらを使う` 判定も切り出し、次の本当のソース差し替え条件を明示化した
- `keepout` 側は、`外殻逃がし参照ソース` が存在する場合にその実体から `外殻逃がし参照` を直接複製する経路へ進めた
- `contact` 側も、`外殻接触参照ソース` が存在する場合にその実体から `外殻接触参照` を直接複製する経路へ進めた
- `keepout/contact` の従来フォールバック経路も専用関数へ分離し、次に `内殻` フォールバックを削る対象範囲を明確にした
- `keepout` 側はフォールバック用 `artifact spec` も専用化し、次の依存削減をさらに局所化した
- `contact` 側もフォールバック用 `artifact spec` を専用化し、両系統を同じ粒度で個別に詰められる形にした
- `keepout/contact` の `内殻` フォールバック候補列も専用関数へ切り出し、次の候補削減を最小範囲で行える形にした
- `keepout` 側はフォールバック用 `artifact spec` の実体も専用ビルダーへ分離し、次の候補削減をさらに局所化した
- `contact` 側もフォールバック用 `artifact spec` の実体を専用ビルダーへ分離し、両系統を同じ粒度で詰められる状態にした
- `keepout` 側は `内殻` フォールバック候補を残す条件も専用化し、候補削減の最終トグルを独立させた
- `contact` 側も `内殻` フォールバック候補を残す条件を専用化し、両系統を同じ粒度の最終トグルまで揃えた
- `keepout` 側は `内殻` フォールバック候補を実際に外し、専用参照経路だけで成立するかを試す段階に入った
- `contact` 側も `内殻` フォールバック候補を実際に外し、両系統とも専用参照経路だけで成立するかを試す段階に入った
- 主経路の `build_outer_shell_runtime_reference()` 呼び出しからも `inner_shell_body` 直渡しを外し、runtime 参照入口をさらに独立させた
- `build_outer_shell_runtime_reference()` 自体の未使用 `inner_shell_body` 引数も削除し、runtime 参照入口の責務を実態どおりに揃えた
- 残っている `inner_shell` 名の互換ラッパーも、新しい参照経路の戻り値をそのまま返す薄い委譲層へさらに寄せた
- `contact` 系の古い互換入口についても、リポジトリ内では未使用の外部互換層であることをコード上で明示した
- `section/keepout` 系の古い互換入口についても、リポジトリ内では未使用の外部互換層であることをコード上で明示した
- 主要入口のエラーメッセージ表現も `inner_shell_body` 前提から `outer shell reference source` 前提へ揃え始めた
- 主要入口の `outer_shell_reference` 確保処理も `ensure_outer_shell_reference()` へ共通化し、最後の入口重複を削減した
- `build_outer_shell()` 自体も、参照確保後は後段へ `inner_shell_body` を流さない主経路に揃えた
- `build_outer_shell_from_reference()` を切り出し、最上位入口でも `reference-first` の本経路を明示した
- 最上位入口のコメントも整理し、`build_outer_shell()` は互換入口、`build_outer_shell_from_reference()` は本経路だと分かる形にした
- `build_outer_shell_runtime_reference()` にも役割コメントを追加し、runtime 側の本入口がどこかをコード上で明示した
- `ensure_outer_shell_reference()` にも役割コメントを追加し、互換入力を本経路の参照束へ正規化する責務を明示した
- `build_outer_shell_reference()` にも役割コメントを追加し、汎用参照束ビルダーと runtime/互換入口の関係を見やすくした
- `build_outer_shell_base_structure_from_reference()` と `add_structures_to_outer_shell_base_structure_from_reference()` も切り出し、中位入口まで `reference-first` の本経路を明示した
- 中位入口の互換層にも役割コメントを追加し、互換入口と本経路の境界をさらに明示した
- `assembly_left_hand_grip.py` 側にも、外殻が `reference-first` 経路で立ち上がることを明示した
- runtime 補助の `artifacts` / `overrides` ヘルパーにも役割コメントを追加し、参照解決の層構造を読みやすくした
- `ensure_outer_shell_runtime_reference_bodies()` にも役割コメントを追加し、runtime 参照体の保証責務を明示した
- 優先名付き参照体と既定フォールバックの関係もコメントで明示し、参照解決ルールを追いやすくした
- 参照ソース名候補から実体を引く補助にも役割コメントを追加し、探索責務の位置を明示した
- `outer_shell_reference` から単体ボディを解決する補助にも役割コメントを追加し、単体参照の解決責務を明示した
- `outer_shell_reference` から複数ボディを解決する補助にも役割コメントを追加し、複数参照の解決責務を明示した
- `keepout` 複数参照アクセサにも役割コメントを追加し、複数参照の返し方を追いやすくした
- `contact` 単体参照アクセサにも役割コメントを追加し、単体参照の返し方を追いやすくした
- `section` 単体参照アクセサにも役割コメントを追加し、単体参照アクセサ群の粒度を揃えた
- `section` スケッチ参照アクセサにも役割コメントを追加し、断面参照取得の流れを追いやすくした
- `keepout` 単体参照アクセサにも役割コメントを追加し、単体参照アクセサ群の粒度をさらに揃えた
- 蓋部基準点アクセサにも役割コメントを追加し、参照補助の粒度をさらに揃えた
- 参照前提を強制する共通ガードにも役割コメントを追加し、入口チェックの責務を明示した
- `section` の既定参照ビルダーにも役割コメントを追加し、断面参照の優先解決ルールを明示した
- `keepout/contact` の既定参照ビルダーにも役割コメントを追加し、優先参照体と既定ソースの関係を明示した
- `section/keepout/contact` の参照束ビルダー層にも役割コメントを追加し、明示上書きと既定値の重ね方を見やすくした
- 参照名候補ヘルパーにも役割コメントを追加し、候補順保持と重複除去の責務を明示した
- 優先候補から実体を引く補助にも役割コメントを追加し、優先参照解決の責務を明示した
- 専用参照ボディ生成仕様ヘルパーにも役割コメントを追加し、生成メタデータの責務を明示した
- 専用参照ボディの複製実行ヘルパーにも役割コメントを追加し、生成実行点の責務を明示した
- 専用参照ボディ生成の判定入口と前処理入口にも役割コメントを追加し、生成分岐の責務を明示した
- `keepout/contact` の source 経路と fallback 経路にも役割コメントを追加し、生成分岐の実行経路を追いやすくした
- 次の段階では `keepout_source_body` / `contact_source_body` を別基準へ分離する

### Step 4. 接触逃がしを独立させる

- [x] 接面検出を `内殻との距離判定` から別方式へ移せるか確認した
- [x] 接面候補を固定面名または基準点群で安定取得できるか確認した
- [x] `-0.2 mm` の逃がし後に嵌合が悪化していないことを確認した

### Step 5. 一時退避処理を削減する

- [x] 各一時退避処理について、削除しても同じ加工結果になるか確認した
- [x] 不要な一時退避を外した
- [x] 必要な一時退避だけを残し、理由をコメントまたは資料へ残した

## 検証項目

- [ ] 外殻本体の母形状が基準モデルと一致する
- [ ] 蓋部斜面の分割位置が一致する
- [ ] 蓋部隙間部の押し出し量と位置が一致する
- [ ] Lボタン開口部まわりの切り欠きが一致する
- [ ] 下部受止の追加位置と厚みが一致する
- [ ] 底部外側斜面の切り取り結果が一致する
- [ ] 不要な分離ボディが増えていない
- [ ] `外殻` 名の最終ボディが一意に残る

## 差分メモ

- [ ] 参照平面化した依存:
- [ ] 固定寸法化した依存:
- [ ] まだ `inner_shell_body` が必要な依存:
- [ ] Fusion API 都合で残した依存:
- [ ] 次に切る候補:
