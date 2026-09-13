from pydantic import BaseModel, PositiveInt


class AddRequest(BaseModel):
    """加算エンドポイントのリクエストモデル。

    Parameters
    ----------
    a : PositiveInt
        被加数(正の整数)。
    b : PositiveInt
        加数(正の整数)。
    """

    a: PositiveInt
    b: PositiveInt


class SubtractRequest(BaseModel):
    """減算エンドポイントのリクエストモデル。

    Parameters
    ----------
    a : PositiveInt
        被減数(正の整数)。
    b : PositiveInt
        減数(正の整数)。
    """

    a: PositiveInt
    b: PositiveInt


class CalculationResponse(BaseModel):
    """四則演算APIの共通レスポンスモデル。

    Parameters
    ----------
    operation : str
        実行した演算名(例: "add")。
    a : int
        1つ目の被演算数。
    b : int
        2つ目の被演算数。
    result : int
        演算結果。
    """

    operation: str
    a: int
    b: int
    result: int
