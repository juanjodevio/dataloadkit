"""Package import behavior for ``dlk.connectors``."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_import_connectors_does_not_load_sql_submodule() -> None:
    """``import dlk.connectors`` must not pull SQLAlchemy via ``dlk.connectors.sql``."""
    root = Path(__file__).resolve().parents[2]
    code = """
import sys
import dlk.connectors
assert "dlk.connectors.sql" not in sys.modules
from dlk.connectors import build_sql_source
assert "dlk.connectors.sql" in sys.modules
assert callable(build_sql_source)
"""
    subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        cwd=str(root),
    )
