# docs/gen/generate_readmes.py

from pathlib import Path
import mkdocs_gen_files
import yaml

SRC_ROOT = Path("src/BFHTW")
DOCS_ROOT = Path("reference")
NAV_FILE = "nav.yml"

readmes = sorted(SRC_ROOT.rglob("README.md"))

nav = [{"Home": "index.md"}]

def add_to_nav(nav_tree, parts, path):
    current = nav_tree
    for part in parts[:-1]:
        found = next((item for item in current if isinstance(item, dict) and part in item), None)
        if not found:
            found = {part: []}
            current.append(found)
        current = found[part]
    current.append({parts[-1]: path})

for readme in readmes:
    rel_path = readme.relative_to(SRC_ROOT).with_suffix(".md")
    index_path = DOCS_ROOT / rel_path.parent / "index.md"
    doc_path_str = str(index_path).replace("\\", "/")

    # Generate the Markdown file
    with mkdocs_gen_files.open(index_path, "w") as f:
        f.write(readme.read_text())

    # Add to nav
    parts = rel_path.parts
    add_to_nav(nav, list(parts[:-1]) + ["index"], f"{doc_path_str}")

# Write nav.yml
with mkdocs_gen_files.open(NAV_FILE, "w") as f:
    yaml.dump({"nav": nav}, f, sort_keys=False)
