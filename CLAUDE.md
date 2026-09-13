# CLAUDE.md

このファイルは、このリポジトリで作業するClaude Code (claude.ai/code) に向けたガイダンスを提供します。

## プロジェクトの現状

本リポジトリはマルチエージェント並行実装のPhase0(基盤構築)・Phase1(4演算の並行実装)・Phase2(統合確認)がすべて完了した状態です。`CLAUDE.md`・`README.md`・`specs/`(add/subtract/multiply/divide/deployment/ci/lint)に加えて、`apps/`(FastAPIインスタンス・4演算(add/subtract/multiply/divide)のルーター・`CalculationResponse`/各`XxxRequest`)・`tests/unit/`(4演算分のユニットテスト計47件、すべてGreen)・`pyproject.toml`・`Dockerfile`・`k8s/`・CIワークフロー(`.github/workflows/`)が導入済みです。4演算のブランチはいずれもmainにマージ済みで、Docker Desktop上のKubernetes(Namespace `calculator-api`)への再デプロイ後、`POST /calculate/<operation>`(add/subtract/multiply/divide)の正常系(200)・異常系(422)動作を実機で再確認済みです。

`specs/`は、別リポジトリでSDD(仕様駆動開発)を行っていた際に作成した要件定義・設計ドキュメントをそのまま引き継いだものです。引き継ぎ元では各 `tasks.md` のチェックボックスはすべて `[x]`(完了)でしたが、本リポジトリでは実装状況を正しく表すため**すべて `[ ]`(未チェック)に戻して**あります。本リポジトリでは要件・設計(`requirements.md`・`design.md`)はそのまま仕様源として使いますが、実装の進め方はSDDではなく**TDD(テスト駆動開発)**で行います(詳細は[TDDでの実装の進め方](#tddでの実装の進め方)を参照)。各項目は、対応する演算のPhase1サイクル(テストエージェント→実装エージェント→レビューエージェント)が完了した時点でチェックを入れていくこと。

本リポジトリでは開発体制をシングルエージェントではなくマルチエージェント(git worktreeで分離した複数のClaude Codeセッションによる並行実装)で進める。さらに各演算の実装はテストエージェント・実装エージェント・レビューエージェントの3ロールに分けて進める(詳細は[エージェントの役割分担](#エージェントの役割分担テスト実装レビュー)を参照)。具体的な作業手順(基盤構築→4演算の並行実装→統合確認の3フェーズ、各ロールへの指示、git worktree/rebaseコマンド)は [README.md](README.md) にまとめてあるため、四則演算の実装作業はTDDの方針(本ファイル)とREADME.mdの手順を両方参照すること。

演算を追加した際は、`Dockerfile`・`k8s/`マニフェストは変更不要だが、イメージの再ビルド・再デプロイと全演算での動作再確認が必要(詳細は[README.md](README.md)のPhase2を参照)。

主なコマンド([uv](https://docs.astral.sh/uv/)を使用):

```bash
uv sync                                    # 依存関係のインストール
uv run uvicorn apps.main:app --reload      # 開発サーバー起動
uv run pytest tests/unit/ -v               # ユニットテスト実行
uv run ruff check .                        # lint実行
uv run ruff format --check .               # フォーマット差分チェック(適用しない)
uv run mypy apps/                          # 型チェック(appsディレクトリのみ対象)
```

## プロジェクトの目的

2個の**正の整数**パラメータに対して四則演算(加算・減算・乗算・除算)を行うシンプルなAPIサーバー。技術スタックは Python 3.12+、FastAPI、バリデーション用のPydantic v2、テスト用のpytest + httpx。

## specs/ の構成と使い方

各演算・機能は `specs/` 配下にそれぞれ独立したフィーチャーフォルダを持ち、requirements → design → tasks の3ファイル構成に従う。

```
specs/
├── add/
├── subtract/
├── multiply/
├── divide/
│   ├── requirements.md   # EARS記法(WHEN/THEN/SHALL)による受け入れ基準
│   ├── design.md         # エンドポイント仕様、Pydanticモデル、処理フロー、エラーハンドリング
│   └── tasks.md          # 実装チェックリスト。各項目は対応する要件番号を明記
└── deployment/
    ├── requirements.md   # Kubernetes Deploymentリソースの要件
    ├── design.md         # Deploymentマニフェストの内容と設計判断の理由
    └── tasks.md          # Dockerfile作成〜デプロイ確認までのタスク
```

`requirements.md`・`design.md` は本リポジトリでも仕様源としてそのまま使う(設計をやり直す必要はない)。`tasks.md` のチェックボックスは前述の通り本リポジトリでの実装状況を表すよう `[ ]`(未チェック)に戻してあるため、各演算のPhase1サイクルが完了するたびに該当項目へチェックを入れて実際の進捗を反映すること。新しい演算・機能を追加する場合も、同様に `specs/<feature>/` に同じ3ファイル構成を作成してこの形式を維持すること。

## TDDでの実装の進め方

本リポジトリでは、SDD(仕様が先にあり後からテストを追認生成する進め方)ではなく、**TDD(テスト駆動開発)**で実装する。

- 各演算(add/subtract/multiply/divide)を実装する際は、`specs/<operation>/tasks.md` に列挙されたテストケース一覧を先に `tests/unit/test_<operation>.py` に実装し(Red確認)、その後に `apps/` 側の実装を追加してテストを通す(Green)。
- 演算に依存しない共通部分(`pyproject.toml`・`apps/main.py`雛形・`apps/schemas.py`の共通`CalculationResponse`・CI・Dockerfile・k8sマニフェストなど)は、4演算の実装に先立って**基盤構築(Phase0)**として1サイクルで完了させる([README.md](README.md)のPhase0を参照)。
- 基盤構築の完了後、4演算(add/subtract/multiply/divide)はそれぞれ独立したgit worktree・ブランチで**並行して**実装する(Phase1)。演算ごとの進め方自体は従来通り**1演算1サイクル**(テスト作成→実装→lint/mypy確認→レビュー→PR作成)だが、他の演算のサイクル完了を待つ必要はない([README.md](README.md)のPhase1を参照)。4演算分のテストや実装を1つのブランチにまとめて書く方式は採らない。
- 1演算1サイクルの中身は単一のエージェントが通しで行うのではなく、**テストエージェント→実装エージェント→レビューエージェント**の順に担当を分けて進める(詳細は[エージェントの役割分担](#エージェントの役割分担テスト実装レビュー)を参照)。
- `specs/<operation>/tasks.md` の各項目(スキーマ定義→ハンドラ実装→テスト実装、という記載順)は要件の網羅リストとして参照し、実際の着手順序はテスト実装を先に行う。

## エージェントの役割分担(テスト/実装/レビュー)

各演算(Phase1)の1サイクルは、同じgit worktree・ブランチ上で以下の3ロールが順番に引き継ぐ形で進める。ロールごとに別のClaude Codeセッションを起動すること(同一セッションで役割を兼務しない)。

### テストエージェント

- 読むもの: `specs/<operation>/requirements.md`・`design.md`・`tasks.md`。実装コード(`apps/`)はまだ存在しない前提で進める。
- 触ってよいファイル: `tests/unit/test_<operation>.py`(新規作成)のみ。
- やること: `tasks.md` に列挙された正常系・異常系のテストケースを網羅的に実装し、`uv run pytest tests/unit/test_<operation>.py -v` を実行して**Red(失敗)であることを確認**する(実装が存在しないためのImportError/404等で失敗するのが正しいRedであり、テストコード自体のバグによる失敗ではないことを確認する)。
- やらないこと: `apps/` 配下のコードは一切書かない。
- 完了条件: Redを確認した上でコミット・push。

### 実装エージェント

- 読むもの: `specs/<operation>/design.md`(エンドポイント仕様・Pydanticモデル)と、テストエージェントが実装した `tests/unit/test_<operation>.py`。
- 触ってよいファイル: `apps/schemas.py`(自分の演算の`XxxRequest`追記のみ)、`apps/routers/<operation>.py`(新規作成)、`apps/main.py`(自分の演算のimportと`include_router`追記のみ)。
- やること: テストエージェントが書いたテストを**そのまま**Greenにする実装を行う。テストの期待値やアサーションを実装都合で書き換えない(テスト自体に誤りがあると判断した場合は、書き換えずにレビューエージェント/ユーザーに判断を委ねる)。
- 完了条件: `uv run pytest tests/unit/test_<operation>.py -v`(Green)・`uv run ruff check .`・`uv run ruff format --check .`・`uv run mypy apps/` がすべて通ることを確認し、コミット・push・PR作成まで行う。

### レビューエージェント

- 触ってよいファイル: `specs/<operation>/tasks.md`のみ(レビュー完了時にチェックボックスを更新するため)。それ以外のコード(`apps/`・`tests/`)は書かない。
- やること: 実装エージェントが作成したPRの差分を、`specs/<operation>/requirements.md`(受け入れ基準の網羅性)・本ファイルの「4演算に共通する主要な設計判断」「Docstringの方針」・共有ファイル(`apps/schemas.py`・`apps/main.py`)への追記が自分の演算分に留まっているか、の観点でレビューする。`/code-review` スキルの利用を基本とする。
- 指摘があれば実装エージェント(必要ならテストエージェント)に差し戻し、指摘対応後のpushを受けて再レビューする。
- 完了条件: 指摘がすべて解消されたら、`specs/<operation>/tasks.md`の該当項目すべてに`[x]`のチェックを入れてコミット・push(同じPRブランチに追加コミットする)し、レビュー結果を報告する。**マージは行わない**(マージはユーザーが実施する)。

## 4演算に共通する主要な設計判断

- 全エンドポイントは `POST /calculate/<operation>` で、JSONボディ `{"a": integer, "b": integer}` を受け取り、成功時は `{"operation", "a", "b", "result"}` を返す。
- `a`/`b` は**正の整数(> 0)のみ**を許容する(Pydanticの `PositiveInt` を使用)。`0`・負数・小数・非数値・欠落はすべてFastAPI/Pydantic標準の `422` レスポンスに委ねる。独自のバリデーションを実装しないこと。
- `divide` の `b == 0` も上記の正の整数バリデーションで弾かれるため、ゼロ除算専用の `400` エラーハンドリングは実装しない(`ZeroDivisionError` が発生する経路自体が存在しない)。
- 認証・永続化・CORSはスコープ外。

## 実行環境(Kubernetes)に関する設計判断

詳細は [`specs/deployment/`](specs/deployment/) を参照。**導入済み**(`Dockerfile`・`k8s/namespace.yaml`・`k8s/deployment.yaml`はPhase0で作成済み。Docker Desktop上のKubernetesへのデプロイ・全演算での動作確認は[README.md](README.md)のPhase2で行う)。

- ローカルPCのDocker Desktopで有効化したKubernetes上に、専用Namespace `calculator-api` 配下で `Deployment`リソースとしてデプロイする(本番運用は想定しない)。`default` Namespaceは使用しない。
- リソース節約を最優先するため、レプリカ数は `1`、`livenessProbe`/`readinessProbe`は設定しない、CPU/メモリの`requests`/`limits`は最小限、という最小構成を維持すること。
- `Service`/`Ingress`・オートスケーリングなどはスコープ外。追加する場合は要件から見直すこと。

## CI(GitHub Actions)に関する設計判断

詳細は [`specs/ci/`](specs/ci/) を参照。**導入済み**(Phase0で`.github/workflows/`配下の2ワークフローを作成済み)。

- `.github/workflows/ci-pull-request.yml`: `main`向けPRの作成・更新時(`pull_request`トリガー)に実行。
- `.github/workflows/ci-main.yml`: `main`へのpush(マージ)時(`push`トリガー)に実行。
- 両ファイルとも`test`ジョブ(`uv run ruff check .`・`uv run ruff format --check .`・`uv run mypy apps/`・`uv run pytest tests/unit/ -v`)と`docker-build`ジョブ(`docker build`のみ、push・デプロイなし)を持つ。
- Kubernetesへの自動デプロイ(CD)・イメージのレジストリpushはスコープ外(`specs/deployment/`に従い手動運用)。

## 実装時のディレクトリ構成

アプリケーションコードは `app/` ではなく **`apps/`** ディレクトリ配下に実装すること(各 `specs/<operation>/tasks.md` のファイルパスもこれに合わせて記載済み)。`apps/routers/` は `tests/unit/` と同様に**演算ごとにファイルを分割**し、1ファイルに複数演算のハンドラをまとめないこと。

```
apps/
├── main.py            # FastAPIアプリ、各ルーターの登録
├── routers/
│   ├── add.py         # POST /calculate/add
│   ├── subtract.py    # POST /calculate/subtract
│   ├── multiply.py    # POST /calculate/multiply
│   └── divide.py      # POST /calculate/divide
└── schemas.py         # Pydanticモデル(リクエスト/レスポンス)
tests/
└── unit/
    ├── test_add.py
    ├── test_subtract.py
    ├── test_multiply.py
    └── test_divide.py
Dockerfile
k8s/
├── namespace.yaml      # 専用Namespace "calculator-api" を定義
└── deployment.yaml     # namespace: calculator-api を指定。specs/deployment/design.md の内容に従う
```

## ユニットテストの方針

[TDDでの実装の進め方](#tddでの実装の進め方)の通り、各演算の実装コードより**先に**ユニットテストコードを出力すること(テストが失敗する=Redであることを確認してから実装に進む)。出力先は `tests/unit/` 配下とし、演算ごとに個別のテストファイル(`test_add.py` など)に分ける。テストケースは各 `specs/<operation>/tasks.md` に列挙された正常系・異常系の項目を網羅すること。テスト関数にも[Docstringの方針](#docstringの方針)に従いNumPyスタイルのdocstringを付与すること。

## Docstringの方針

関数・メソッドにはNumPyスタイルのdocstringを付与すること(`Parameters` / `Returns` セクションを`----`の下線で区切る形式)。

```python
def add(a: int, b: int) -> int:
    """2つの整数を加算する。

    Parameters
    ----------
    a : int
        被加数。
    b : int
        加数。

    Returns
    -------
    int
        a + b の結果。
    """
```

## PR作成時の言語

PRのタイトル・本文は日本語で記述すること。

## PR作成の粒度

キリの良い作業単位(1機能・1ドキュメント更新など)が完了するたびに、こまめにコミット・push・PR作成を行うこと。複数の無関係な変更を1つの大きなPRにまとめて溜め込まないこと。このリポジトリはGitHub側の自動削除設定(`delete_branch_on_merge`)を有効にしておらず、マージ済みブランチはユーザーが都度手動で削除する運用のため、新たな作業を始める前には必ず `git fetch origin` して `main` を最新化し、そこから新しいブランチを切ること。

四則演算の実装では、[TDDでの実装の進め方](#tddでの実装の進め方)に記載の「演算ごとに1サイクル」が最小のPR単位となる。ただし本リポジトリでは4演算をマルチエージェントで並行実装するため([README.md](README.md)を参照)、複数の演算のブランチ・PRが同時に存在しうる。以下のルールを厳守すること。

- 基盤構築(`pyproject.toml`・`apps/main.py`雛形・CI・Dockerfile・k8sマニフェストなど、演算に依存しない共通部分)は、4演算の実装に先立って1本のPRで完了させ、mainにマージしてから4演算の並行実装に進むこと。
- `apps/schemas.py`・`apps/main.py`は全演算が共通で追記する共有ファイルである。各演算のPRでは、`apps/schemas.py`への追記(自分の`XxxRequest`のみ)と`apps/main.py`への追記(自分のルーターのimportと`include_router`のみ)に留め、他の演算のコードには触れないこと。
- 複数の演算PRが並行して存在する場合、マージは1本ずつ行う。あるPRがマージされたら、他の未マージブランチ(worktree)は `git fetch origin && git rebase origin/main` で最新化し、共有ファイルのコンフリクトは双方の追記を残す形で解消してから次のPRに進めること。
- 1本のPRには、同一ブランチ上でテストエージェント(Red確認コミット)・実装エージェント(Green確認コミット)・レビュー指摘対応(あれば追加コミット)が積み重なる。PRの作成は実装エージェントが行い、[エージェントの役割分担](#エージェントの役割分担テスト実装レビュー)の通りレビューエージェントの確認が完了するまではマージしないこと(マージ自体は常にユーザーが実施する)。
