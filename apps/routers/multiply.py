from fastapi import APIRouter

from apps.schemas import CalculationResponse, MultiplyRequest

router = APIRouter()


@router.post("/calculate/multiply", response_model=CalculationResponse)
def calculate_multiply(request: MultiplyRequest) -> CalculationResponse:
    """2つの正の整数を乗算する。

    Parameters
    ----------
    request : MultiplyRequest
        被乗数・乗数を保持するリクエストモデル。

    Returns
    -------
    CalculationResponse
        演算結果を含むレスポンスモデル。
    """
    return CalculationResponse(
        operation="multiply", a=request.a, b=request.b, result=request.a * request.b
    )
