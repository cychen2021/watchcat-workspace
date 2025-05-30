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
            ["python", os.path.join(WORKSPACE_ROOT, subproject, "format.py")],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
