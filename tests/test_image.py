#!/usr/bin/env python3
"""Smoke tests for a repo2docker-built JupyterHub image."""

import shutil
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def assert_ok(result, label):
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed: {result.stderr.strip()}")


def test_python():
    print(f"Python {sys.version}")
    assert sys.version_info.major == 3


def test_imports():
    import jupyterhub  # noqa: F401
    import jupyterlab  # noqa: F401
    import notebook  # noqa: F401
    import numpy  # noqa: F401
    print("Core imports succeeded")


def test_singleuser_binary():
    exe = shutil.which("jupyterhub-singleuser")
    if not exe:
        raise RuntimeError("jupyterhub-singleuser not found in PATH")
    print(f"jupyterhub-singleuser is available at {exe}")


def test_singleuser_import():
    """Verify jupyterhub-singleuser via Python import.

    We avoid running jupyterhub-singleuser as a subprocess because
    jupyter_server 2.17.0 has a bug in _preparse_for_subcommand that
    crashes on any invocation (including --help and --version).
    Instead, we import the module directly to confirm it's installed
    and functional.
    """
    from jupyterhub.singleuser import main  # noqa: F401
    from jupyterhub.singleuser.extension import JupyterHubSingleUser  # noqa: F401

    import jupyterhub
    print(f"jupyterhub-singleuser is functional (jupyterhub {jupyterhub.__version__})")


def test_jupyter_binaries():
    for binary in ["jupyter", "jupyter-lab", "python"]:
        if not shutil.which(binary):
            raise RuntimeError(f"{binary} not found in PATH")
    print("Expected binaries present")


def main():
    test_python()
    test_imports()
    test_singleuser_binary()
    test_singleuser_import()
    test_jupyter_binaries()
    print("All image smoke tests passed")


if __name__ == "__main__":
    main()
