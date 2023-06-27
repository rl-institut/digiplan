"""This module helps to load local dotenvs from .envs fodler into .envs file"""

import os
from collections.abc import Sequence

ROOT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOCAL_DOTENVS_DIR_PATH = os.path.join(ROOT_DIR_PATH, ".envs", ".local")
LOCAL_DOTENV_FILE_PATHS = [
    os.path.join(LOCAL_DOTENVS_DIR_PATH, ".django"),
    os.path.join(LOCAL_DOTENVS_DIR_PATH, ".postgres"),
]
DOTENV_FILE_PATH = os.path.join(ROOT_DIR_PATH, ".env")


def merge(output_file_path: str, merged_file_paths: Sequence[str], append_linesep: bool = True) -> None:
    with open(output_file_path, "w", encoding="utf8") as output_file:
        for merged_file_path in merged_file_paths:
            with open(merged_file_path, encoding="utf8") as merged_file:
                merged_file_content = merged_file.read()
                output_file.write(merged_file_content)
                if append_linesep:
                    output_file.write(os.linesep)


def main():
    merge(DOTENV_FILE_PATH, LOCAL_DOTENV_FILE_PATHS)


if __name__ == "__main__":
    main()
