def test_app_is_importable() -> None:
    """apps.main.app がimportできることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
        アサーションのみ行う。
    """
    from apps.main import app

    assert app is not None
