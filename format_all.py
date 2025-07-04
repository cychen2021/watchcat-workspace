# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ruff",
# ]
# ///
import tomllib
import os
import subprocess
import sys

WORKSPACE_ROOT = os.path.realpath(os.path.dirname(__file__))

if __name__ == '__main__':
    with open(os.path.join(WORKSPACE_ROOT, "pyproject.toml"), "rb") as f:
        pyproject_config = tomllib.load(f)

    subprojects = pyproject_config.get("tool", {}).get("uv", {}).get("workspace", [])["members"]

    for subproject in subprojects:
        print(f"Formatting subproject: {subproject}")
        subprocess.run(
            ["uv", "run", os.path.join(WORKSPACE_ROOT, subproject, "format.py")],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr
        )

    print("Formatting Python files in the workspace root...")
    python_files = list(map(lambda f: os.path.join(WORKSPACE_ROOT, f), [
        f for f in os.listdir(WORKSPACE_ROOT) if f.endswith(".py")
    ]))
    subprocess.run(
        ["uvx", "ruff", "format", *python_files],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr
    )