from fastapi import APIRouter

from apps.schemas import AddRequest, CalculationResponse

router = APIRouter()


@router.post("/calculate/add", response_model=CalculationResponse)
def calculate_add(request: AddRequest) -> CalculationResponse:
    """2つの正の整数を加算する。

    Parameters
    ----------
    request : AddRequest
        被加数・加数を保持するリクエストモデル。

    Returns
    -------
    CalculationResponse
        演算結果を含むレスポンスモデル。
    """
    return CalculationResponse(
        operation="add", a=request.a, b=request.b, result=request.a + request.b
    )
