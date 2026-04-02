"""Smoke test: package imports."""

import dlk


def test_version() -> None:
    assert dlk.__version__ == "0.1.0"
