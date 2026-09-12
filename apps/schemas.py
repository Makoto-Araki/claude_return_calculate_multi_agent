from pydantic import BaseModel


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
