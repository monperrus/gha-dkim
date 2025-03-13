import argparse
from pathlib import Path
from subprocess import check_output
from typing import Literal, Optional, Tuple

from packaging.version import parse, Version
import toml
import requests
import os


def get_main_version(project_file: Path) -> Version:
    """
    Gets the last version on PyPi eg https://pypi.org/pypi/crawler-user-agents/json
    curl https://pypi.org/pypi/crawler-user-agents/json| jq .info.version
    """
    project_name = get_project_name(project_file)
    pypi_version = requests.get("https://pypi.org/pypi/"+project_name+"/json").json()["info"]["version"]
    return parse(pypi_version)


def get_current_version(pyproject: str) -> Version:
    """
    Toml loads the pyproject file and returns the version number.
    """
    with open(pyproject, "r") as fh:
        pyproject_dict = toml.load(fh)
        version_string = pyproject_dict["project"]["version"]
        return parse(version_string)

def get_project_name(pyproject: str) -> Version:
    """
    Toml loads the pyproject file and returns the version number.
    """
    with open(pyproject, "r") as fh:
        pyproject_dict = toml.load(fh)
        return pyproject_dict["project"]["name"]


def get_next_version(
    version_number: Version, bump_type: Literal["major", "minor", "micro"]
) -> str:
    """Bumps the provided version_number by one"""
    if len(version_number.release) == 3:
        major, minor, micro = version_number.release
    elif len(version_number.release) == 2:
        major, minor = version_number.release
    elif len(version_number.release) == 1:
        major = version_number.release
    else:
        raise Exception("not semver")
    if bump_type == "major":
        return f"{major + 1}.0.0"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{micro + 1}"


def bump_pyproject(pyproject: Path, new_version_number: str) -> None:
    """Bumps the version number in the pyproject file"""
    with pyproject.open("r") as fh:
        d = toml.load(pyproject)
        d["project"]["version"] = new_version_number
    with pyproject.open("w") as fh:
        toml.dump(d, fh)


def parse_args() -> Tuple[str, str, str, Path]:
    """get argparse values"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", help="Main branch name", required=False)
    parser.add_argument(
        "--bump_type",
        help="Bump type",
        choices=["major", "minor", "micro"],
        required=True,
    )
    parser.add_argument("--pyproject", help="Path to pyproject.toml", required=True)
    parser.add_argument(
        "--bump_commit_file",
        help="Path to file containing git commit message",
        required=False,
    )
    args = parser.parse_args()
    pyproject = Path(args.pyproject)
    if not Path(pyproject).is_file():
        raise FileNotFoundError(f"{pyproject} does not exist")

    return (
        args.main,
        args.bump_type,
        args.bump_commit_file,
        pyproject,
    )


def main():
    main_branch, bump_type, bump_commit_file, pyproject = parse_args()

    main_version = get_main_version(pyproject)
    local_version = get_current_version(pyproject)

    new_version = get_next_version(main_version, bump_type)
    print(f"Pypi local version: {local_version}")
    print(f"Pypi current version: {main_version}")
    print(f"Next version: {new_version}")
    bump_pyproject(pyproject, new_version)
    if bump_commit_file and os.path.exists(bump_commit_file):
        bump_message = (
            f"Bumped version from {local_version} to {new_version}"
        )
        print(bump_message)
        with open(bump_commit_file, "w") as fh:
            fh.write(bump_message)


if __name__ == "__main__":
    main()
