# タスク一覧 - 減算 (subtract)

> マルチエージェント並行実装では、`apps/schemas.py`の共通`CalculationResponse`は基盤構築(Phase0)で定義済みのため変更しない。本タスクで追加するのは`SubtractRequest`のみ、かつ`apps/main.py`への追記は自分(subtract)のルーターのimportと`include_router`のみに留めること。役割分担は、下記チェックリストのうちテスト実装(3項目目)をテストエージェントが、スキーマ定義・ハンドラ実装(1・2項目目)を実装エージェントが担当し、レビューエージェントはコードを書かず差分レビューのみを行う。詳細は[README.md](../../README.md)およびCLAUDE.mdの「エージェントの役割分担」を参照。

- [ ] `SubtractRequest`(`a`, `b` を `PositiveInt`)スキーマを `apps/schemas.py` に定義する(`CalculationResponse`はPhase0で定義済みのため変更しない) (Req 1, 2)
- [ ] `apps/routers/subtract.py` に `POST /calculate/subtract` ハンドラを実装する (Req 1)
- [ ] `tests/unit/test_subtract.py` にユニットテストコードを実装する (Req 1, 2, 3)
  - [ ] 正常系テスト: 正の整数同士の減算 (Req 1)
  - [ ] 正常系テスト: `a < b` で結果が負数になるケース (Req 3)
  - [ ] 異常系テスト: `a`/`b` が `0` の場合に422が返る (Req 2)
  - [ ] 異常系テスト: `a`/`b` が負数の場合に422が返る (Req 2)
  - [ ] 異常系テスト: `a`/`b` が小数の場合に422が返る (Req 2)
  - [ ] 異常系テスト: `a`/`b` が数値でない場合に422が返る (Req 2)
  - [ ] 異常系テスト: `a`/`b` が欠落している場合に422が返る (Req 2)
