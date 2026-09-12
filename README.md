# マルチエージェント開発ワークフロー

このドキュメントは、四則演算APIサーバーの開発を**シングルエージェント(Claude Codeセッション1つ)によるTDD**から、**マルチエージェント(git worktreeで分離した複数のClaude Codeセッション)による並行TDD**に切り替えるための作業手順書です。

git worktree・ブランチ操作はユーザー自身が手動で実行し、マルチエージェント開発の勘所(共有ファイルの衝突・マージ順序・rebase)を体感することを目的としています。エージェントへの自動委譲(Task/Agentツール)は使わず、**worktreeごとに人間が別セッションのClaude Codeを起動する**運用です。さらに各演算の実装自体も単一エージェントが通しで行うのではなく、**テストエージェント・実装エージェント・レビューエージェント**の3ロールに分けて進めます(ロールの責務は[CLAUDE.md](CLAUDE.md)の「エージェントの役割分担」を参照)。

## 事前準備: 初回コミット【ユーザー・ターミナル】(このリポジトリで一度だけ実行)

Phase0を始める**前**に、必ずこのステップを済ませてください。

このリポジトリは現時点でローカル・リモート(GitHub)ともに**1つもコミットがありません**(`git log`は「no commits yet」、`git ls-remote origin`は空)。`CLAUDE.md`・`README.md`・`specs/`もすべて未コミット(untracked)です。この状態のままPhase0を始めると、以下の理由で必ず失敗します。

- Phase0の`git pull origin main`が、リモートに`main`ブランチが存在しないため失敗する。
- `gh pr create`が、GitHub側に`main`が存在しないため失敗する。
- 最も重大な点として、`git worktree add`は**指定したコミットの内容**から新しい作業ディレクトリを作る仕組みのため、未コミット(untracked)のファイルはworktreeにコピーされない。`CLAUDE.md`・`README.md`・`specs/`を未コミットのままPhase1に進むと、`../calc-add`などのworktreeにはこれらのファイルが一切存在せず、各エージェントへの指示テンプレートが前提としている`specs/<op>/tasks.md`等を参照できなくなる。

そのため、`main`に直接コミット・pushして初期状態を作ります(まだ`main`が存在しないためPRを経由できない、この1回限りの例外的な操作です)。

```bash
git add CLAUDE.md README.md specs/
git commit -m "docs: マルチエージェント開発のガイドラインとspecsを追加"
git push -u origin main
```

このコミット・pushを実行してよいタイミングは、必ずユーザー自身の判断・指示で決めてください(Claude Codeセッションに任せる場合も、実行前に明示的に指示すること)。

## Claude Desktop(Codeタブ)での操作手順

以下のPhase0〜Phase2はすべて、Claude DesktopアプリのCodeタブ上で行うことを想定しています。各Phase・各ロールの指示テンプレートは「Claude Desktopでのセッション操作」と組み合わせて使ってください。

### セッションの開き方

1. Claude Desktopアプリを開き、**Code**タブを選択する。
2. 新しいセッションを開始するには、サイドバーの **+ New session** をクリックする(ショートカット: macOSは`Cmd+N`、Windowsは`Ctrl+N`)。
3. 最初のメッセージを送る前に、プロンプト入力欄(prompt area)で **Project folder** を設定する。これがそのセッションのカレントディレクトリ(cwd)になる。
   - Phase0(基盤構築)・Phase2(統合確認): リポジトリのルートディレクトリを指定する。
   - Phase1(4演算並行実装)の各ロール: 該当演算のworktreeディレクトリ(例: `../calc-add`)を指定する。**worktree自体は後述の通り手動で作成しておくこと。**

### git worktreeは手動で作成する(自動worktree機能は使わない)

Claude DesktopにはGitリポジトリ向けに、セッション開始時にブランチ名の隣の **worktree** オプションを選ぶと自動でgit worktreeを作成してくれる機能があります。ただし本ワークフローでは、git worktreeコマンドを自分の手で実行してマルチエージェント開発の勘所を学ぶことが目的のため、**この自動worktree機能は使わず**、各Phaseの「git手順」に記載のコマンド(`git worktree add ...`など)を自分で実行してworktreeディレクトリを作成し、そのディレクトリを上記の**Project folder**として指定してください。

### コマンドの実行方法(統合ターミナル / エージェントのBashツール)

各Phaseの手順には【ユーザー・ターミナル】【Claude Desktop・○○エージェント】のラベルを付けています。

- 【ユーザー・ターミナル】と書かれた手順(worktree作成、PR作成、マージ、rebase、後片付けなど)は、ユーザー自身がターミナルで実行します。WSLの通常のターミナルでも、各セッションの統合ターミナル(`Views`メニューまたは`` Ctrl+` ``で開く。macOS/Windows共通)でもどちらでも構いません。統合ターミナルはそのセッションのProject folderをカレントディレクトリとして開くため、Claudeが編集しているファイルと同じ場所でコマンドを実行できます。
- 【Claude Desktop・○○エージェント】と書かれた手順は、そのロールのセッションに指示テンプレートを送ると、エージェント自身がBashツールでgit/gh/uv/docker/kubectlなどのコマンドを実行します。Claude Desktopから実行許可を求められたら承認してください。

### ロールの引き継ぎ(同じworktreeで別セッションに切り替える)

テストエージェント→実装エージェント→レビューエージェントの引き継ぎは、**同じProject folder(同じworktreeディレクトリ)を指定した新しいセッションを開き直す**ことで行います。

1. 現在のセッションでの作業(コミット・pushまで)が終わったら、セッションを閉じる(`Cmd+W` / `Ctrl+W`)。
2. 再度 **+ New session** で同じworktreeディレクトリ(例: `../calc-add`)をProject folderに指定し、次のロールの指示テンプレートを入力する。

各セッションは互いに独立したコンテキストを持つため、新しいセッションを開くだけで「前の担当者の記憶を持たない別のエージェント」として振る舞います。

### 4 worktreeを並行して進める(複数セッションの管理)

- 4つのworktree(add/subtract/multiply/divide)それぞれに対してセッションを開くと、サイドバーに4セッションが並びます。
- セッション間の切り替え: `Ctrl+Tab` / `Ctrl+Shift+Tab`、またはサイドバーのセッション名をクリック。
- 2セッションを左右に並べて表示: `Cmd`(macOS) / `Ctrl`(Windows)を押しながらサイドバーのセッションをクリック。
- 不要になったセッションは、サイドバーでホバーして表示されるアーカイブアイコンから削除できる。

## 前提: なぜPhaseを分けるのか

4演算(add/subtract/multiply/divide)は独立していますが、以下のファイルは**全演算が共通で触る**ため、4エージェントが同時に手を付けると確実に衝突します。

| 共有ファイル | 誰が触るか | 衝突の種類 |
|---|---|---|
| `pyproject.toml` | Phase0の基盤構築(依存関係・lint/mypy設定) | 同一ブロックの重複追記 |
| `apps/main.py` | 各演算の実装エージェント(`include_router`追加) | 同一行付近への追記競合 |
| `apps/schemas.py` | 各演算の実装エージェント(`CalculationResponse`は共通/`XxxRequest`は演算ごと) | `CalculationResponse`の重複定義 |
| `Dockerfile` / `k8s/*.yaml` | 誰も演算ごとには触らない(演算数に依存しない) | 該当なし |

そのため、**Phase0で共有ファイルを先に確定**させてから、**Phase1で4演算を並行実装**し、**Phase2で統合確認**する3段構成にします。

```
Phase0: 基盤構築(1エージェント・mainから直接ブランチ)
   │  pyproject.toml / apps/main.py雛形 / apps/schemas.py共通部分 / CI / Dockerfile / k8s
   ▼  ← このPRがmainにマージされてから Phase1 に進む
Phase1: 4演算を並行実装(4 worktree × テスト/実装/レビューの3ロール)
   │  feature/add, feature/subtract, feature/multiply, feature/divide
   │  各worktree内: テストエージェント(Red)→実装エージェント(Green)→レビューエージェント(承認)
   ▼  ← レビュー承認済みのPRから1本ずつマージし、都度他のworktreeをrebase
Phase2: 統合・デプロイ確認(1エージェント)
   │  Docker再ビルド・k8s再デプロイ・4演算の動作確認
```

---

## Phase0: 基盤構築

Phase0は以下の4ステップで構成されます。ステップごとに**誰が・どこで**行うかが異なるので、その点を明示します。

| ステップ | 実施者 | 場所 |
|---|---|---|
| 1. ブランチ作成 | ユーザー | ターミナル(WSLのターミナル、またはClaude Desktopの統合ターミナルのどちらでもよい) |
| 2. ファイル作成・確認・コミット・push | 基盤構築エージェント | Claude Desktop(Codeタブ)のセッション内(Bashツール経由でgitコマンドを実行) |
| 3. PR作成 | ユーザー | ターミナル |
| 4. レビュー | レビューエージェント | Claude Desktop(Codeタブ)の別セッション |
| 5. マージ | ユーザー | ターミナル |

### 作成物(ステップ2でエージェントが作成するファイル)

- `.gitignore`(`.venv/`・`__pycache__/`・`*.pyc`など。以降のステップで`git add`する際に仮想環境などを誤って含めないため)
- `pyproject.toml`・`uv.lock`(uv管理。fastapi/pydantic/uvicorn/pytest/httpx本体依存 + `dependency-groups.dev`にruff/mypy、`[tool.ruff]`/`[tool.ruff.lint]`/`[tool.mypy]`設定を最初から含める。`uv sync`実行時に`uv.lock`が生成されるので、これもコミット対象に含める)
- `apps/__init__.py`, `apps/main.py`(FastAPIインスタンスのみ。`include_router`はまだ書かない)
- `apps/schemas.py`(共通の`CalculationResponse`のみ定義。各演算の`XxxRequest`はPhase1で各エージェントが追記)
- `tests/unit/test_main.py`(スモークテスト1件。`apps.main.app`がimportできることを確認するだけでよい)
  - **注意**: `tests/unit/`が空のままPhase0でCIを導入すると、`pytest`がテスト収集0件で終了コード5を返しCIが失敗します。最低1件のテストを用意してから`ci-pull-request.yml`を有効化してください。
- `.github/workflows/ci-pull-request.yml` / `ci-main.yml`(`specs/ci/design.md`通り)
- `Dockerfile`(`specs/deployment/design.md`通り。演算数に依存しないため今のうちに作成してよい)
- `k8s/namespace.yaml` / `k8s/deployment.yaml`

### ステップ1: ブランチ作成【ユーザー・ターミナル】

Claude Desktopでセッションを開く**前**に、リポジトリのローカルクローン(WSL上のディレクトリ)で以下を実行し、`foundation/init`ブランチに切り替えておきます。Phase0はまだ並行作業がないためworktreeは使わず、リポジトリのメインの作業ディレクトリをそのまま使います。

```bash
git fetch origin
git checkout main
git pull origin main
git checkout -b foundation/init
```

### ステップ2: 基盤構築エージェントへの指示【Claude Desktop・基盤構築エージェント】

1. Claude Desktopで **+ New session** を開き、**Project folder**にステップ1でブランチを切り替えたリポジトリのディレクトリ(worktreeではなく通常のリポジトリのパス)を指定する。
2. 以下の指示テンプレートを送る。

```
このリポジトリのCLAUDE.mdとspecs/lint, specs/ci, specs/deploymentを読んだ上で、
マルチエージェント並行実装(README.md参照)のPhase0(基盤構築)のみを行ってください。
現在のブランチはfoundation/initです。

やること:
- .gitignoreの新規作成(.venv/・__pycache__/・*.pycなど)
- pyproject.tomlの新規作成(fastapi/pydantic/uvicorn/pytest/httpx本体依存 +
  dependency-groups.devにruff/mypy、[tool.ruff]/[tool.mypy]設定を最初から含める)。
  uv syncを実行してuv.lockも生成する
- apps/__init__.py, apps/main.py(FastAPIインスタンスのみ。ルーター登録はまだ書かない)
- apps/schemas.py(CalculationResponseのみ定義。各演算のXxxRequestは書かない)
- tests/unit/test_main.pyにスモークテストを1件実装(apps.main.appがimportできることの確認)
- .github/workflows/ci-pull-request.yml, ci-main.yml をspecs/ci/design.mdに従って作成
- Dockerfile, k8s/namespace.yaml, k8s/deployment.yaml をspecs/deployment/design.mdに従って作成

やらないこと:
- 各演算(add/subtract/multiply/divide)のルーター・テストの実装
- apps/main.pyへのinclude_router追加
- PR作成(コミット・pushまでで止めること)

完了条件: uv run ruff check . / uv run mypy apps/ / uv run pytest tests/unit/ -v が
すべて通ること。確認できたら以下の内容でコミットし、foundation/initブランチにpushして
ください(gitコマンドは自身のBashツールで実行してよい)。

git commit -m "基盤構築: pyproject.toml・FastAPI雛形・CI・Docker・k8sを整備"
git push -u origin foundation/init
```

エージェントはBashツールでgitコマンド(`git add`・`git commit`・`git push`)を実行します。Claude Desktopから実行許可を求められたら承認してください。

### ステップ3: PR作成【ユーザー・ターミナル】

エージェントのpushが完了したら、ターミナル(WSLまたはClaude Desktopの統合ターミナル)で以下を実行してPRを作成します。

```bash
gh pr create --title "基盤構築: マルチエージェント並行実装のための土台整備" --body "$(cat <<'EOF'
## 概要
- 4演算を並行実装できるよう、共有ファイル(pyproject.toml / apps/main.py / apps/schemas.py)とCI/Docker/k8sを先に整備する。

## 内容
- pyproject.toml: 本体依存 + ruff/mypy設定
- apps/main.py, apps/schemas.py: 雛形(CalculationResponseのみ)
- tests/unit/test_main.py: スモークテスト
- .github/workflows/*: CI
- Dockerfile, k8s/*: デプロイ設定

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### ステップ4: レビュー【Claude Desktop・レビューエージェント】

Phase0はTDDのRed/Greenサイクルを持たない準備作業のため、テスト/実装エージェントには分けず単一の「基盤構築エージェント」で行いますが、マージ前の**レビューエージェント**によるレビュー(`/code-review`)は他フェーズと同様に必須とします。

Claude Desktopで同じディレクトリをProject folderとした**別セッション**を開き、次のように指示します。

```
foundation/initブランチのPRを /code-review でレビューしてください。
指摘があれば一覧化して報告し、なければ「レビュー完了・マージ可能」と報告してください。
マージは行わないでください。
```

### ステップ5: マージ【ユーザー・ターミナル】

レビューエージェントが「レビュー完了・マージ可能」と報告したら、ターミナルでマージします。

```bash
gh pr merge --merge
```

**このマージが完了するまでPhase1には進まないこと。**

---

## Phase1: 4演算の並行実装

Phase0のPRがmainにマージされたことを確認してから開始します。以下のステップを`<op>`(`add`/`subtract`/`multiply`/`divide`)ごとに繰り返します。ステップ1〜3は4つのworktreeで並行して進められますが、マージ(ステップ4)は1本ずつ行います。

| ステップ | 実施者 | 場所 |
|---|---|---|
| 0. worktree作成 | ユーザー | ターミナル(WSLのターミナル、またはClaude Desktopの統合ターミナル) |
| 1. テストエージェント(Red) | テストエージェント | Claude Desktop(Codeタブ)のセッション(Project folder = `../calc-<op>`) |
| 2. 実装エージェント(Green)・PR作成 | 実装エージェント | Claude Desktop(Codeタブ)の別セッション(同じ`../calc-<op>`) |
| 3. レビュー | レビューエージェント | Claude Desktop(Codeタブ)の別セッション(同じ`../calc-<op>`) |
| 4. マージ・他worktreeのrebase | ユーザー | ターミナル |
| 5. worktreeの後片付け | ユーザー | ターミナル |

### ステップ0: worktreeの作成【ユーザー・ターミナル】

Claude Desktopでセッションを開く**前**に、ターミナルで4つのworktreeを作成しておきます。

```bash
git checkout main
git fetch origin
git pull origin main
git worktree add -b feature/add      ../calc-add      origin/main
git worktree add -b feature/subtract ../calc-subtract origin/main
git worktree add -b feature/multiply ../calc-multiply origin/main
git worktree add -b feature/divide   ../calc-divide   origin/main
git worktree list   # 4つ作成されたことを確認
```

Claude Desktopの自動worktree機能は使わず、上記のように自分で作成したディレクトリをProject folderとして指定します(詳細は[Claude Desktop(Codeタブ)での操作手順](#claude-desktopcodeタブでの操作手順)を参照)。以下のステップ1〜3は、演算ごとに個別のClaude Codeセッションを起動して進めます(同時に複数ロールを開かない。ロールが変わるたびに新しいセッションを起動し、前のセッションは終了してよい)。

### ステップ1: テストエージェント(Red)【Claude Desktop・テストエージェント】

Claude Desktopで **+ New session** を開き、Project folderに`../calc-<op>`を指定して以下を送ります。

```
このworktree(calc-<op>)では calculator-api の "<op>" 演算のテストのみをTDDのRedフェーズとして
実装してください。CLAUDE.mdの「エージェントの役割分担」テストエージェントの節と
specs/<op>/requirements.md, design.md, tasks.md に従ってください。

厳守事項:
1. 触ってよいファイルは tests/unit/test_<op>.py(新規作成)のみ。apps/配下は一切書かないこと。
2. tasks.mdに列挙された正常系・異常系のテストケースをすべて実装すること。
3. 実装後 uv run pytest tests/unit/test_<op>.py -v を実行し、実装が存在しないことによる
   失敗(Red)であることを確認すること(テストコード自体のバグによる失敗ではないこと)。
4. Red確認後、以下のコミット・pushを自身のBashツールで実行してください(PR作成はまだ行わない)。

git add tests/unit/test_<op>.py
git commit -m "test: <op>のユニットテストを実装(Red確認)"
git push -u origin feature/<op>
```

Project folderが既に`../calc-<op>`のため、エージェントは`cd`せずそのままBashツールでgitコマンドを実行できます。Claude Desktopから実行許可を求められたら承認してください。

### ステップ2: 実装エージェント(Green)・PR作成【Claude Desktop・実装エージェント】

同じ`../calc-<op>`をProject folderとした**新しいセッション**を開き、以下を送ります。

```
このworktree(calc-<op>)では calculator-api の "<op>" 演算の実装をTDDのGreenフェーズとして
行ってください。CLAUDE.mdの「エージェントの役割分担」実装エージェントの節と
specs/<op>/design.md に従ってください。

厳守事項:
1. 触ってよいファイルは以下のみ:
   - apps/routers/<op>.py(新規作成)
   - apps/schemas.py への追記(<Op>Requestクラスの追加のみ。既存のCalculationResponseは変更しない)
   - apps/main.py への追記(<op>ルーターのimportとinclude_router呼び出しの追加のみ)
2. 他の演算(add/subtract/multiply/divide)のファイルには一切触れないこと。
3. tests/unit/test_<op>.py に書かれたテストの期待値・アサーションは書き換えないこと。
   テスト自体に誤りがあると思われる場合は書き換えずに報告すること。
4. 完了条件: uv run pytest tests/unit/test_<op>.py -v(Green)・uv run ruff check . /
   uv run ruff format --check . / uv run mypy apps/ がすべて通ること。
5. 完了条件を満たしたら、以下を自身のBashツールで実行してコミット・push・PR作成まで行ってください。

git add apps/routers/<op>.py apps/schemas.py apps/main.py
git commit -m "feat: <op>エンドポイントを実装(Green)"
git push -u origin feature/<op>
gh pr create --title "<op>演算エンドポイントの実装" --body "POST /calculate/<op> をTDDで実装(テストエージェント→実装エージェントの2段階)。"
```

エージェントはBashツールでgit・ghコマンドを実行します。Claude Desktopから実行許可を求められたら承認してください。

### ステップ3: レビュー【Claude Desktop・レビューエージェント】

コードは書かず差分のレビューのみを行うロールなので、専用のworktreeは不要です。実装エージェントと同じ`../calc-<op>`をProject folderとした**別セッション**を開き、以下を送ります。

```
このworktree(calc-<op>)で作成されたPR(<op>演算)をレビューしてください。
CLAUDE.mdの「エージェントの役割分担」レビューエージェントの節に従ってください。

やること:
1. /code-review を使って、このブランチの差分(テストエージェント・実装エージェントの
   コミット)をレビューする。
2. 以下の観点を特に確認する:
   - specs/<op>/requirements.md の受け入れ基準を満たしているか
   - CLAUDE.mdの「4演算に共通する主要な設計判断」(PositiveInt使用、独自バリデーション
     禁止など)に沿っているか
   - apps/schemas.py・apps/main.pyへの変更が自分の演算(<op>)分のみに留まっているか
   - Docstringの方針(NumPyスタイル)に沿っているか
3. 指摘があれば一覧化して報告する(自分では修正しない)。指摘がなければ
   「レビュー完了・マージ可能」と報告する。

マージは行わないでください(マージはユーザーが行います)。
```

指摘があった場合は、実装エージェント(またはテストエージェント)のセッションを再度起動して修正・push → レビューエージェントで再レビュー、を指摘がなくなるまで繰り返します。

### ステップ4: マージ・他worktreeのrebase【ユーザー・ターミナル】

4本のPRのうち**レビューエージェントが「レビュー完了・マージ可能」と報告したものから1本ずつ**マージします(例: add → subtract → multiply → divide)。レビュー未完了のPRはマージしないこと。

```bash
gh pr merge <add のPR番号> --merge
```

**1本マージするたびに、残り3つのworktreeを必ずrebaseしてから作業を続ける・PRを出す:**

```bash
cd ../calc-subtract
git fetch origin
git rebase origin/main
```

`apps/schemas.py`・`apps/main.py`でコンフリクトが起きた場合、**基本方針は「両方の追記を残す」**(片方を消さない)ことです。

```bash
# コンフリクト箇所を確認
git status
git diff

# apps/schemas.py: マージ済み演算のXxxRequestクラスと自分のXxxRequestクラスを両方残す
# apps/main.py: マージ済み演算のimport/include_routerと自分の分を両方残す

git add apps/schemas.py apps/main.py
git rebase --continue
git push --force-with-lease
```

4本目のPRがマージされ、`main`に4演算すべてのルーター登録が揃った状態になったらPhase1完了です。

### ステップ5: worktreeの後片付け【ユーザー・ターミナル】

各PRのマージ後、リモートブランチは自動削除されますが、ローカルworktreeは手動で消します。

```bash
git worktree remove ../calc-add
git worktree remove ../calc-subtract
git worktree remove ../calc-multiply
git worktree remove ../calc-divide
git worktree prune
git branch -d feature/add feature/subtract feature/multiply feature/divide
```

---

## Phase2: 統合・デプロイ確認

4演算すべてがマージされた`main`から最終確認を行います。Phase2もPhase0と同様、TDDのRed/Greenサイクルを持たないため単一の「統合確認エージェント」で行いますが、マージ前のレビューエージェントによるレビューは他フェーズと同様に必須です。worktreeは使わず、リポジトリのメインの作業ディレクトリをそのまま使います。

| ステップ | 実施者 | 場所 |
|---|---|---|
| 1. ブランチ作成 | ユーザー | ターミナル |
| 2. 統合確認・CLAUDE.md更新・コミット・push・PR作成 | 統合確認エージェント | Claude Desktop(Codeタブ)のセッション |
| 3. レビュー | レビューエージェント | Claude Desktop(Codeタブ)の別セッション |
| 4. マージ | ユーザー | ターミナル |

### ステップ1: ブランチ作成【ユーザー・ターミナル】

```bash
git checkout main
git fetch origin
git pull origin main
git checkout -b integration/verify-all
```

### ステップ2: 統合確認エージェントへの指示【Claude Desktop・統合確認エージェント】

Claude Desktopで **+ New session** を開き、Project folderにステップ1でブランチを切り替えたリポジトリのディレクトリを指定して以下を送ります。

```
現在のブランチはintegration/verify-allです。4演算(add/subtract/multiply/divide)が
すべてmainにマージされた状態での統合確認を行ってください。

やること:
1. uv run pytest tests/unit/ -v で4演算全テストがGreenであることを確認する。
2. docker build -t calculator-api:local . でイメージを再ビルドする。
3. kubectl apply -f k8s/namespace.yaml / kubectl apply -f k8s/deployment.yaml を実行する
   (既にデプロイ済みの場合は kubectl rollout restart deployment -n calculator-api)。
4. kubectl port-forward -n calculator-api <pod名> 8000:8000 で4演算それぞれ
   POST /calculate/<operation> の正常系(200)・異常系(422)を確認する。
5. 問題なければCLAUDE.mdの「プロジェクトの現状」を、4演算の実装・デプロイが完了した
   内容に更新する。

完了したら、以下を自身のBashツールで実行してコミット・push・PR作成まで行ってください。

git add CLAUDE.md
git commit -m "docs: マルチエージェント並行実装での4演算完了・デプロイ確認を反映"
git push -u origin integration/verify-all
gh pr create --title "統合確認: 4演算のデプロイ・動作確認" --body "マルチエージェント並行実装で完成した4演算をDocker/k8s上で再確認。"
```

`docker build`・`kubectl apply`・`git`・`gh`などのコマンドはすべてエージェントがBashツールで実行します。Claude Desktopから実行許可を求められたら承認してください。

### ステップ3: レビュー【Claude Desktop・レビューエージェント】

同じディレクトリをProject folderとした**別セッション**を開き、次のように指示します。

```
integration/verify-allブランチのPRを /code-review でレビューしてください。
指摘があれば一覧化して報告し、なければ「レビュー完了・マージ可能」と報告してください。
マージは行わないでください。
```

### ステップ4: マージ【ユーザー・ターミナル】

レビューエージェントが「レビュー完了・マージ可能」と報告したら、ターミナルでマージします。

```bash
gh pr merge --merge
```

---

## 参考: フェーズと既存specsの対応

| フェーズ | 対応するspecs |
|---|---|
| Phase0 | `specs/lint/`(設定部分)、`specs/ci/`、`specs/deployment/`(Dockerfile/k8sマニフェスト作成部分) |
| Phase1 | `specs/add/`, `specs/subtract/`, `specs/multiply/`, `specs/divide/` |
| Phase2 | `specs/deployment/`(デプロイ・動作確認部分)、`specs/lint/`(既存コードへのlint適用確認部分) |

各`tasks.md`のチェックボックスは、旧リポジトリでの完了状態(`[x]`)を引き継がず本リポジトリの実装状況を表すよう`[ ]`に戻してあります(CLAUDE.md記載の通り)。各演算のPhase1サイクル(テストエージェント→実装エージェント→レビューエージェント)が完了するたびに該当項目へチェックを入れること。
