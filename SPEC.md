# SPEC: falx

> 最終更新: 2026-06-19
> ステータス: current contract

## 目的

fal.ai queue API を YAML 入力から扱う小さな Python library / CLI wrapper。
CLI は request state を保持せず、呼び出し側が stdout YAML を capture して永続化する。
全 submit 経路は asyncio を基盤とし、`asyncio.Semaphore(max_concurrency)` で fal.ai
共有アカウントの concurrent in-flight 数を制御する。

## CLI

| command | 役割 |
|---|---|
| `falx run -c job.yaml` | submit → poll → download を 1 経路に統合実行し、stdout YAML を返す |
| `falx fetch -c job.yaml --request-id <id>` | request_id の status / result を取得し、完了済みならファイルを配置して stdout YAML を返す |
| `falx cancel -c job.yaml --request-id <id>` | request_id を cancel し、stdout YAML を返す |
| `falx validate -c job.yaml` | job.yaml と parameters を検証する |
| `falx schema <app_id>` | job.yaml 例を出力する |
| `falx models` | 登録済み app_id を一覧する |
| `falx upload <files...>` | local file を fal CDN に upload し、TSV で URL を返す |

### deprecated alias

`falx submit` と `falx submit-async` は `run` への deprecated alias である。実体は
`run` 経路 (= submit + poll + download 統合) に転送され、stderr に deprecation 警告を
出す。新規利用は `run` を使う。

## job.yaml

job.yaml は純粋入力 spec である。CLI は job.yaml に request_id / result / status を書き戻さない。

```yaml
app_id: fal-ai/nano-banana-2
parameters:
  prompt: <your prompt here>
output_dir: workspace/demo/exp/G-0001_demo-output/output
slug: demo-output
version: 1
iterations: 1
max_concurrency: 8
```

| field | 仕様 |
|---|---|
| `app_id` | fal app_id |
| `parameters` | fal endpoint に渡す parameters |
| `output_dir` | 出力 root。project root 相対 path を標準とする |
| `slug` | 出力 file 名の slug。必須。`--slug` で上書き可 |
| `version` | 出力 file 名 / folder 名の `vN`。必須。`--version` で上書き可 |
| `iterations` | 同一入力の投入回数。省略時 1。非 matrix run のみ意味を持ち、N 件の独立 task を独立 take folder に展開する。matrix run では常に 1 として扱う。`--iterations/-n` で上書き可 |
| `max_concurrency` | fal.ai 側 concurrent in-flight 数の上限。省略時 8。`--max-concurrency` で上書き可。1 以上の整数 |
| `output_expiration_seconds` | fal object lifecycle header 用の任意 field |

`results` / `request_id` / `submitted_at` / `completed_at` / `result` / `error_type` /
`error` は job.yaml の field として扱わない。これらを含む YAML は validation error になる。

### matrix_axes

`matrix_axes` を指定すると、falx は `axes` の直積から cell を展開する。`mode` は
`cartesian` のみ対応する。各 axis は次のどちらか一方の形を取る。

一つの field を変更する場合:

```yaml
matrix_axes:
  mode: cartesian
  axes:
    - field: prompt
      values: ["A", "B"]
    - field: aspect_ratio
      values: ["16:9", "1:1"]
```

複数の field を同時に変更する場合:

```yaml
matrix_axes:
  mode: cartesian
  axes:
    - fields: [edit_strength, controls, auto_controls]
      value_set:
        - [0.7, null, null]
        - [null, {strength: 0.8}, null]
        - [null, null, true]
```

| field | 仕様 |
|---|---|
| `axis.field` | 単一の `parameters` field 名 |
| `axis.values` | `axis.field` に順番に代入する値の list |
| `axis.fields` | 同期して切り替える複数の `parameters` field 名。1 件でも使用可 |
| `axis.value_set` | `axis.fields` と同じ長さの list を並べた list。各 inner list が同期された 1 cell 単位 |

`axis.field` / `axis.values` と `axis.fields` / `axis.value_set` は排他である。
`axis.value_set` の inner list 長は `axis.fields` 長と一致する必要がある。`null` は
その field を上書きしない値として扱う。`axes` 間は直積で展開し、`fields` 内だけを同期
unit として扱う。

## stdout YAML

`run`, `fetch` は次の形の block style YAML を stdout に出す。

```yaml
request_id: req-0001
takes:
  - take: 1
    request_id: req-0001
    batches:
      - batch: 1
        file_path: workspace/demo/exp/G-0001_demo-output/output/v1-1/G-0001_demo-output_v1-1-1.png
status: completed
```

`fetch` は未完了 request の場合 `status: "in_progress"` を返す。
`takes[].take` は対象 task が払い出した絶対 take 値を表し、CLI が同 run で投入した
N 件の独立 task をそれぞれ 1 entry として並べる。各 task は独立した take を消費して
独立 folder (`v{V}-{T}/`, `v{V}-{T+1}/`, ...) に配置されるため、並列 fetch による
ファイル衝突が構造的に発生しない。

`cancel` は次の形を返す。

```yaml
request_id: req-0001
status: cancelled
```

matrix run (`matrix_axes` あり) では次の形を返す。

```yaml
matrix: true
status: completed
cells:
  - cell: 1
    coords: {prompt: A}
    request_id: req-0001
    status: completed
    takes:
      - take: 1
        batches:
          - batch: 1
            file_path: workspace/demo/exp/G-0002_matrix-demo/output/c1-v1-1/G-0002_matrix-demo_c1_v1-1-1.mp4
skipped_cells:
  - cell: 2
    take: 1
```

matrix run では cell 内の `takes` は常に 1 件で固定する (= 各 cell が単一 task)。
複数 iteration 投入は非 matrix run の専用機能であり、matrix と組み合わせない。
`skipped_cells[]` の各 entry は完走済 cell の番号 + その完走を検出した take 値を
表し、resume 判定で skip された (cell, take) ペアを示す。

## file naming

download 済みファイルは `output_dir` 直下の submit folder に置く。

```text
非 matrix: <output_dir>/v{V}-{T}/{identity}_v{V}-{T}-{B}.{ext}
matrix:    <output_dir>/c{C}-v{V}-{T}/{identity}_c{C}_v{V}-{T}-{B}.{ext}
```

| part | 仕様 |
|---|---|
| `identity` | `output_dir` の親が `G-NNNN_<slug>` 形式ならその folder 名。そうでない汎用利用では job.yaml `slug` または `--slug` |
| `C` | matrix cell の 1 始まり index。ゼロ埋めなし |
| `V` | job.yaml `version` または `--version` |
| `T` | take。`output_dir` 配下の既存 take folder を scan して決める G entry scope の submit 通し番号。非 matrix は version を跨いで通算する。matrix は対象 version の `c{C}-v{V}-{T}` folder を scan し、同一 version 内で 1 から開始する。ゼロ埋めなし |
| `B` | submit folder 内の file index。単一出力でも `-1` を付ける。同一 take folder 内では 1 から開始する。ゼロ埋めなし |

submit folder 名は `v{V}-{T}/` または `c{C}-v{V}-{T}/` とし、file 名と同じ
version / take / cell の値を含める。`request_id` は stdout YAML と
single-result yaml に保持し、folder 名と file 名には含めない。

`run` は command 開始時に次 take を確定する。非 matrix run で `iterations: N` を投入
した場合は、各 task に独立した take を割り当てる (= base take から N 連番で take++)。
1 request_id = 1 take folder の対応が崩れず、並列 task は disk 上で構造的に分離される。
非 matrix take は version を跨いで通算する。

matrix run は同一 version の全 cell で同じ take を共有する。既存 matrix take group が
一部完走の場合は同 take 内で未完了 cell だけを再投入し、全 cell 完走済みの場合は
同一 version 内の次 take に進める。別 version の matrix take group は当該 version の
take 判定に影響しない。

single-result yaml は download 済みファイルと同じ submit folder に置く。`output_dir` の親が
`G-NNNN_<slug>` 形式なら file 名は `G-NNNN_<slug>.yaml`、それ以外の汎用利用では
`<slug>.yaml` とする。

matrix run では cell ごとの compiled child yaml を同じ submit folder に置く。

```text
<output_dir>/c{C}-v{V}-{T}/G-NNNN_c{C}-v{V}-{T}-job.yaml
```

`G-NNNN` は `output_dir` の親 folder `G-NNNN_<slug>` から導出する。`output_dir` の親が
`G-NNNN_<slug>` 形式ではない汎用利用では `<output_dir>/c{C}-v{V}-{T}/c{C}-v{V}-{T}-job.yaml`
を fallback とする。

## concurrency control

`run` は `asyncio.Semaphore(max_concurrency)` で fal.ai 側の concurrent in-flight 数を
制御する。matrix の全 cell 並列、および非 matrix `iterations > 1` の並列はいずれも同じ
semaphore を共有する。N 件超過の submit は内部 task queue で待機し、in-flight 数が
N 未満になり次第順次発火する。

1 cell の例外 / cancel / timeout が発生しても semaphore は確実に release され、他 cell
を deadlock させない。1 cell が completed すれば即座に download + write を実施し、
他 cell の completion を待たない。

## contact-sheet thumbnail

同一 take 内の batch 出力が複数の still image である場合、サマリー用に 1 枚の
contact-sheet thumbnail を生成し、その submit folder 直下に同居させる。

```text
<output_dir>/v{V}-{T}/{identity}_v{V}-{T}_contact.jpg
```

| part | 仕様 |
|---|---|
| stem | batch file の末尾 `-{B}` を剥がした `{identity}_v{V}-{T}` |
| 拡張子 | `.jpg` 固定 (90% quality) |

生成条件は次の三つを満たす場合に限る。

- take folder 内 batch path が 2 件以上
- model parameter (`num_images` 等) が複数枚出力に設定
- take folder 内全 batch が still image (動画 / 音声では生成しない)

## URL fields

job.yaml `parameters` 内の key 末尾が `url` / `urls` の field を URL field として扱う。許容値:

- public URL (`http` / `https` scheme + netloc)
- local file path (絶対 path、または job.yaml dir 起点の relative path)
- `null` / 未設定

local file path の解決規則:

- 絶対 path はそのまま採用
- relative path は job.yaml が置かれた dir を起点に解決
- 解決後の path が存在しない場合は validation error

`null` / 未設定は「指定なし」として通過させ、reject しない。optional URL field を空のまま submit したいケースを受ける。

## module boundaries

| module | 責務 |
|---|---|
| `falx.core` | fal queue primitive (`submit`, `fetch_status`, `fetch_result`, `cancel`)。asyncio ベース |
| `falx.models` | job.yaml / model parameter validation |
| `falx.io` | YAML load, URL validation support, upload/download file placement, thumbnail utilities |
| `falx.matrix` | matrix sweep 展開、cell-level resume、compiled child yaml 出力 |
| `falx.cli` | Typer command orchestration、asyncio entry、stdout YAML emission |

`falx.core` の primitive はすべて async function として公開する。CLI は各 command の
entry で `asyncio.run()` を呼び、内部で async 経路を駆動する。

## state ownership

falx CLI は中断耐性 state を内部に保持しない。呼び出し側は stdout YAML の
`request_id` / `takes[]` / `batches[]` を自身の metadata store に保存し、必要に応じて
`falx fetch --request-id` または `falx cancel --request-id` を呼ぶ。

`run` の中断 (timeout / Ctrl-C / 例外) 後の挙動は経路ごとに異なる。

- 非 matrix run は各 task の出力を独立した take folder に置く。再 `run` は前回完走分を
  上書きせず、submit の通し番号である take を増やして新しい folder を作る。
- matrix run は同一 take 内で cell 単位の resume が成立する。再 `run` は完走済み
  cell を skip し、未完了 cell だけを同 take 内で再 submit する。全 cell 完走済みの
  場合は次 take に進む。
