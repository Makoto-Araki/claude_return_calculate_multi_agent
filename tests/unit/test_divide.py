from fastapi.testclient import TestClient

from apps.main import app

client = TestClient(app)


def test_divide_success_evenly_divisible() -> None:
    """割り切れる正の整数同士の除算が200 OKで正しい結果を返すことを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": 5})

    assert response.status_code == 200
    assert response.json() == {
        "operation": "divide",
        "a": 10,
        "b": 5,
        "result": 2.0,
    }


def test_divide_success_not_evenly_divisible() -> None:
    """割り切れず結果が小数になる場合に200 OKで小数の結果を返すことを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": 3})

    assert response.status_code == 200
    assert response.json() == {
        "operation": "divide",
        "a": 10,
        "b": 3,
        "result": 10 / 3,
    }


def test_divide_returns_422_when_b_is_zero() -> None:
    """bが0の場合に422が返る(独自の400エラーは実装しない)ことを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": 0})

    assert response.status_code == 422


def test_divide_returns_422_when_a_is_zero() -> None:
    """aが0の場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 0, "b": 3})

    assert response.status_code == 422


def test_divide_returns_422_when_a_is_negative() -> None:
    """aが負数の場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": -1, "b": 3})

    assert response.status_code == 422


def test_divide_returns_422_when_b_is_negative() -> None:
    """bが負数の場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": -3})

    assert response.status_code == 422


def test_divide_returns_422_when_a_is_float() -> None:
    """aが小数の場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 1.5, "b": 3})

    assert response.status_code == 422


def test_divide_returns_422_when_b_is_float() -> None:
    """bが小数の場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": 3.5})

    assert response.status_code == 422


def test_divide_returns_422_when_a_is_not_a_number() -> None:
    """aが数値でない場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": "abc", "b": 3})

    assert response.status_code == 422


def test_divide_returns_422_when_b_is_not_a_number() -> None:
    """bが数値でない場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": "abc"})

    assert response.status_code == 422


def test_divide_returns_422_when_a_is_missing() -> None:
    """aが欠落している場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"b": 3})

    assert response.status_code == 422


def test_divide_returns_422_when_b_is_missing() -> None:
    """bが欠落している場合に422が返ることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    response = client.post("/calculate/divide", json={"a": 10})

    assert response.status_code == 422
