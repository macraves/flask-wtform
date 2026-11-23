"""OC006 bug 4: `using session/backend/user_app.py` must import and run."""
import os
import shutil
import subprocess
import sys

import pytest

SESSION_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "using session",
)


@pytest.fixture
def session_copy(tmp_path):
    """Copy the legacy `using session` variant so its data folders stay temporary.

    Args:
        tmp_path (Path): pytest temporary directory.

    Returns:
        Path: Location of the copied project.
    """
    target = tmp_path / "using_session"
    shutil.copytree(
        SESSION_DIR, target, ignore=shutil.ignore_patterns("__pycache__", "data", "registry")
    )
    return target


def _run(code, cwd):
    """Run a Python snippet in the copied project and return the result.

    Args:
        code (str): Source passed to `python -c`.
        cwd (Path): Working directory (the copied project).

    Returns:
        subprocess.CompletedProcess: Captured result.
    """
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_user_app_imports(session_copy):
    """Importing backend.user_app exits cleanly."""
    result = _run("import backend.user_app", session_copy)
    assert result.returncode == 0, result.stderr


def test_user_app_users_route_runs(session_copy):
    """The imported app answers GET /users without a 500."""
    code = (
        "import backend.user_app as m;"
        "r = m.app.test_client().get('/users');"
        "print(r.status_code)"
    )
    result = _run(code, session_copy)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "200", result.stdout + result.stderr
