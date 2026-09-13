# タスク一覧 - Lint・型チェック

> マルチエージェント並行実装では、`pyproject.toml`への設定追加(項目1〜3)は基盤構築(Phase0)で他の演算に先立って完了させる。Phase0時点では`apps/`・`tests/`にまだ演算コードが存在しないため、項目5・6(既存コードへのlint/mypy適用)はPhase0では該当なしとし、代わりにPhase1で各演算エージェントが自分の実装に対して`uv run ruff check .`・`uv run mypy apps/`を実行し、自演算分の指摘事項を解消する形で満たす。詳細は[README.md](../../README.md)のPhase0を参照。

- [x] `pyproject.toml` の `dependency-groups.dev` に `ruff`・`mypy` を追加する (Req 3)
- [x] `pyproject.toml` に `[tool.ruff]` / `[tool.ruff.lint]` 設定を追加する (Req 1, 4)
- [x] `pyproject.toml` に `[tool.mypy]` 設定(`pydantic.mypy`プラグイン含む)を追加する (Req 2, 4)
- [x] `uv sync` で追加した開発依存が導入されることを確認する (Req 3)
- [x] `uv run ruff check .` を実行し、既存の `apps/`・`tests/` の指摘事項を修正する (Req 1, 5)
- [x] `uv run mypy apps/` を実行し、既存の `apps/` の指摘事項を修正する (Req 2, 5)
- [x] `CLAUDE.md` の「主なコマンド」にlint・型チェックの実行コマンドを追記する (Req 1, 2)
