#!/usr/bin/env python3
"""Smoke tests for a repo2docker-built JupyterHub image."""

import os
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
    result = run(["jupyterhub-singleuser", "--version"])
    assert_ok(result, "jupyterhub-singleuser --version")
    print(f"jupyterhub-singleuser is available (version {result.stdout.strip()})")


def test_singleuser_starts():
    """Verify jupyterhub-singleuser starts and loads the JupyterHub extension.

    We can't do a full integration test here (that requires a running Hub),
    but we can confirm it starts, loads extensions, and attempts to connect
    to JupyterHub — which proves the image is JupyterHub-ready.
    """
    os.environ["JUPYTERHUB_API_URL"] = "http://localhost:0"
    os.environ["JUPYTERHUB_SERVICE_PREFIX"] = "/"
    os.environ["JUPYTERHUB_SERVICE_URL"] = "http://localhost:0"

    proc = subprocess.Popen(
        ["jupyterhub-singleuser", "--ip=0.0.0.0", "--port=8888"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        stdout, _ = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, _ = proc.communicate()

    if "JupyterHubSingleUser" in stdout or "jupyterhub single-user" in stdout.lower():
        print("jupyterhub-singleuser starts and loads JupyterHub extension")
    else:
        raise RuntimeError(
            f"jupyterhub-singleuser did not start as expected:\n{stdout[-500:]}"
        )


def test_jupyter_binaries():
    for binary in ["jupyter", "jupyter-lab", "python"]:
        if not shutil.which(binary):
            raise RuntimeError(f"{binary} not found in PATH")
    print("Expected binaries present")


def main():
    test_python()
    test_imports()
    test_singleuser_binary()
    test_singleuser_starts()
    test_jupyter_binaries()
    print("All image smoke tests passed")


if __name__ == "__main__":
    main()
