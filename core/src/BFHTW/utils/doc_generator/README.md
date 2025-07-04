# Project Documentation Generator

This project provides scripts to automatically generate `README.md` files for all folders in a codebase, while also creating a navigation structure for documentation using MkDocs.

## Overview

The main purpose of this project is to streamline the documentation process for codebases by generating Markdown documentation files based on the contents of source files. It also supports generating a navigation structure for MkDocs, which is a documentation site generator.

## Contents

The project consists of two main scripts:

1. **`generate_docs.py`**: This script is responsible for generating `README.md` files for each folder in the project. It reads the contents of relevant files and uses the OpenAI API to create a structured README file.
2. **`generate_docs_nav.py`**: This script creates a navigation structure for MkDocs based on the generated `README.md` files. It also creates symbolic links to these files in a designated documentation folder.

## Structure

### `generate_docs.py`
- **Imports**: The script imports necessary libraries, including `os`, `Path` from `pathlib`, and `OpenAIAssistant` for API interaction.
- **Settings**: Configuration variables are defined, such as `PROJECT_ROOT`, `EXCLUDE_MARKER`, and `VALID_EXTENSIONS`.
- **Functions**:
  - `collect_folder_contents(folder: str)`: Collects and concatenates text from valid files in a folder.
  - `generate_readmes(assistant: OpenAIAssistant)`: Iterates over project folders, generates `README.md` files using the OpenAI API, and handles folder exclusions based on the `.no-readme` marker.

### `generate_docs_nav.py`
- **Imports**: This script also imports `os` and `yaml`, along with `Path` from `pathlib`.
- **Functions**:
  - `rel_parts(path: Path)`: Breaks down a path into parts relative to the source root.
  - `build_nav_dict(paths: list[Path])`: Constructs a nested dictionary representing the navigation structure from README paths.
  - `dict_to_nav_yaml(nav_dict: dict)`: Converts the navigation dictionary into a format compatible with MkDocs.
  - `generate_symlinks(readme_paths: list[Path])`: Creates symbolic links to the README files in the designated documentation directory.
  - `main()`: The entry point for executing the navigation generation process, including symlink creation and navigation YAML output.

## Usage

1. **Generate README Files**: Run `generate_docs.py` to generate `README.md` files in the project folders.
2. **Generate Navigation Structure**: Execute `generate_docs_nav.py` to create the navigation structure for MkDocs and generate the `mkdocs.yml` configuration file.

## Requirements

- Python 3.x
- Required libraries: `pydantic`, `yaml`, and any dependencies needed for the OpenAI API.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.