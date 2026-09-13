from fastapi import APIRouter

from apps.schemas import CalculationResponse, SubtractRequest

router = APIRouter()


@router.post("/calculate/subtract", response_model=CalculationResponse)
def calculate_subtract(request: SubtractRequest) -> CalculationResponse:
    """2つの正の整数を減算する。

    Parameters
    ----------
    request : SubtractRequest
        被減数・減数を保持するリクエストモデル。

    Returns
    -------
    CalculationResponse
        演算結果を含むレスポンスモデル。
    """
    return CalculationResponse(
        operation="subtract", a=request.a, b=request.b, result=request.a - request.b
    )
