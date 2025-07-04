import os
import yaml
from pathlib import Path

SRC_ROOT = Path(__file__).parents[3]
DOCS_ROOT = Path(SRC_ROOT).parent / "docs"
MKDOCS_YML = Path(SRC_ROOT).parent / "mkdocs.yml"

def rel_parts(path: Path) -> list[str]:
    """Break path into parts relative to SRC_ROOT."""
    return list(path.relative_to(SRC_ROOT).parts)

def build_nav_dict(paths: list[Path]) -> dict:
    """Recursively build nav dict from a list of README paths."""
    nav = {}

    for path in paths:
        parts = rel_parts(path)[:-1]  # exclude README.md
        current = nav
        for part in parts:
            current = current.setdefault(part, {})
        current['index'] = '/'.join(['BFHTW', *parts, 'index.md'])

    return nav

def dict_to_nav_yaml(nav_dict: dict) -> list:
    """Convert nested dict into MkDocs-style nav list."""
    nav = []

    def walk(d):
        if isinstance(d, dict) and "index" in d and len(d) == 1:
            return d["index"]
        result = []
        for k, v in sorted(d.items()):
            result.append({k: walk(v)})
        return result

    for top_level, value in sorted(nav_dict.items()):
        nav.append({top_level: walk(value)})
    return nav

def generate_symlinks(readme_paths: list[Path]):
    for src in readme_paths:
        parts = rel_parts(src)
        dest = DOCS_ROOT.joinpath(*parts).with_name("index.md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.symlink_to(src.resolve())

def main():
    readmes = sorted(SRC_ROOT.rglob("README.md"))
    if not readmes:
        print("No README.md files found.")
        return

    # 1. Symlink them
    generate_symlinks(readmes)

    # 2. Build nav dict
    nav_dict = build_nav_dict(readmes)
    nav = dict_to_nav_yaml(nav_dict)

    # 3. Write mkdocs.generated.yml
    output = {
        "site_name": "Bio AI Docs",
        "theme": { "name": "readthedocs" },
        "plugins": [
            "search",
            {
                "mkdocstrings": {
                    "handlers": {
                        "python": {
                            "options": {
                                "show_source": False,
                                "show_root_heading": True,
                                "separate_signature": True,
                                "docstring_style": "google",
                                "extra": {
                                    "paths": ["src"]
                                }
                            }
                        }
                    }
                }
            }
        ],
        "nav": nav
    }
    import pdb; pdb.set_trace()

    with open(MKDOCS_YML, "w") as f:
        yaml.dump(output, f, sort_keys=False)
    print(f"Generated: {MKDOCS_YML}")

if __name__ == "__main__":
    main()
