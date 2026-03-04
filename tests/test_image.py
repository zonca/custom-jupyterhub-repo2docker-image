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
    result = run(["jupyterhub-singleuser", "--help"])
    assert_ok(result, "jupyterhub-singleuser --help")
    print("jupyterhub-singleuser is available")


def test_jupyter_binaries():
    for binary in ["jupyter", "jupyter-lab", "python"]:
        if not shutil.which(binary):
            raise RuntimeError(f"{binary} not found in PATH")
    print("Expected binaries present")


def main():
    test_python()
    test_imports()
    test_singleuser_binary()
    test_jupyter_binaries()
    print("All image smoke tests passed")


if __name__ == "__main__":
    main()
