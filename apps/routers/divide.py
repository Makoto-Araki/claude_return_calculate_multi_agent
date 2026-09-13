from fastapi import APIRouter

from apps.schemas import DivideRequest, DivideResponse

router = APIRouter()


@router.post("/calculate/divide", response_model=DivideResponse)
def calculate_divide(request: DivideRequest) -> DivideResponse:
    """2つの正の整数を除算する。

    Parameters
    ----------
    request : DivideRequest
        被除数・除数を保持するリクエストモデル。

    Returns
    -------
    DivideResponse
        演算結果を含むレスポンスモデル。
    """
    return DivideResponse(
        operation="divide", a=request.a, b=request.b, result=request.a / request.b
    )
