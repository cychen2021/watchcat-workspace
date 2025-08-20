# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ruff",
#     "sh",
# ]
# ///
import tomllib
import os
import sh

WORKSPACE_ROOT = os.path.realpath(os.path.dirname(__file__))

if __name__ == "__main__":
    with open(os.path.join(WORKSPACE_ROOT, "pyproject.toml"), "rb") as f:
        pyproject_config = tomllib.load(f)

    subprojects = (
        pyproject_config.get("tool", {}).get("uv", {}).get("workspace", [])["members"]
    )

    for subproject in subprojects:
        print(f"Formatting subproject: {subproject}")
        sh.uvx(
            "uv",
            "run",
            os.path.join(WORKSPACE_ROOT, subproject, "format.py"),
        )

    print("Formatting Python files in the workspace root...")
    python_files = list(
        map(
            lambda f: os.path.join(WORKSPACE_ROOT, f),
            [f for f in os.listdir(WORKSPACE_ROOT) if f.endswith(".py")],
        )
    )
    sh.uvx("ruff", "format", *python_files)
