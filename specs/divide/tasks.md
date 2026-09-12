# タスク一覧 - 除算 (divide)

> マルチエージェント並行実装では、`apps/main.py`への追記は自分(divide)のルーターのimportと`include_router`のみに留めること。`DivideResponse`は`add`/`subtract`/`multiply`と共有しない専用モデルのため、基盤構築(Phase0)で定義済みの共通`CalculationResponse`には触れない。役割分担は、下記チェックリストのうちテスト実装(3項目目)をテストエージェントが、スキーマ定義・ハンドラ実装(1・2項目目)を実装エージェントが担当し、レビューエージェントはコードを書かず差分レビューのみを行う。詳細は[README.md](../../README.md)およびCLAUDE.mdの「エージェントの役割分担」を参照。

- [ ] `DivideRequest`(`a`, `b` を `PositiveInt`)/ `DivideResponse`(`result` は `float`)スキーマを `apps/schemas.py` に定義する (Req 1, 2)
  - 既存の共有 `CalculationResponse`(`result: int`)を `add`/`subtract`/`multiply` と共用しているため、`result: float` は専用の `DivideResponse` として新設した(共有モデルを `float` に変更すると既存演算のレスポンス形式が変わってしまうため)。
- [ ] `apps/routers/divide.py` に `POST /calculate/divide` ハンドラを実装する (Req 1)
- [ ] `tests/unit/test_divide.py` にユニットテストコードを実装する (Req 1, 2, 3)
  - [ ] 正常系テスト: 割り切れる正の整数同士の除算 (Req 1)
  - [ ] 正常系テスト: 割り切れず結果が小数になるケース (Req 3)
  - [ ] 異常系テスト: `b` が `0` の場合に422が返る(独自の400エラーは実装しない) (Req 2)
  - [ ] 異常系テスト: `a`/`b` が負数の場合に422が返る (Req 2)
  - [ ] 異常系テスト: `a`/`b` が小数の場合に422が返る (Req 2)
  - [ ] 異常系テスト: `a`/`b` が数値でない場合に422が返る (Req 2)
  - [ ] 異常系テスト: `a`/`b` が欠落している場合に422が返る (Req 2)
