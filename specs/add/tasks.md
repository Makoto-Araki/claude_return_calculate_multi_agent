# タスク一覧 - 加算 (add)

> マルチエージェント並行実装では、`apps/schemas.py`の共通`CalculationResponse`は基盤構築(Phase0)で定義済みのため変更しない。本タスクで追加するのは`AddRequest`のみ、かつ`apps/main.py`への追記は自分(add)のルーターのimportと`include_router`のみに留めること。役割分担は、下記チェックリストのうちテスト実装(3項目目)をテストエージェントが、スキーマ定義・ハンドラ実装(1・2項目目)を実装エージェントが担当し、レビューエージェントはコードを書かず差分レビューのみを行う。詳細は[README.md](../../README.md)およびCLAUDE.mdの「エージェントの役割分担」を参照。

- [x] `AddRequest`(`a`, `b` を `PositiveInt`)スキーマを `apps/schemas.py` に定義する(`CalculationResponse`はPhase0で定義済みのため変更しない) (Req 1, 2)
- [x] `apps/routers/add.py` に `POST /calculate/add` ハンドラを実装する (Req 1)
- [x] `tests/unit/test_add.py` にユニットテストコードを実装する (Req 1, 2)
  - [x] 正常系テスト: 正の整数同士の加算 (Req 1)
  - [x] 異常系テスト: `a`/`b` が `0` の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が負数の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が小数の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が数値でない場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が欠落している場合に422が返る (Req 2)
