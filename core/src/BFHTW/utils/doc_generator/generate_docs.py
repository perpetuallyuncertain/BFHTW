"""
Script to auto-generate README.md files for all folders in a codebase,
excluding folders marked with a `.no-readme` file.

Uses the OpenAIAssistant class to send file contents to the OpenAI API
and generate Markdown documentation.
"""

import os
from pathlib import Path
from BFHTW.ai_assistants.external.open_ai.openai_assistant import OpenAIAssistant

# ────────────────────────────────────────────────────────────────
# Settings
PROJECT_ROOT = Path(__file__).resolve().parent.parent / "src" / "BFHTW"
EXCLUDE_MARKER = ".no-readme"
README_FILENAME = "README.md"
VALID_EXTENSIONS = (".py", ".md", ".txt", ".json", ".yaml", ".toml")

# Hardcoded system prompt
SYSTEM_PROMPT = (
    "You are an expert documentation generator. Your task is to read the contents "
    "of source code files and generate a clear, concise, and informative README.md file "
    "describing the purpose, contents, and structure of the folder."
)

# ────────────────────────────────────────────────────────────────
def collect_folder_contents(folder: str) -> str:
    """Concatenate readable source files in the folder into a single string."""
    content_blocks = []
    for filename in os.listdir(folder):
        if filename == README_FILENAME or filename.startswith('.') or not filename.endswith(VALID_EXTENSIONS):
            continue
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        content_blocks.append(f"# {filename}\n\n{content}")
            except Exception as e:
                print(f"Skipping {filename} due to error: {e}")
    return "\n\n".join(content_blocks)

# ────────────────────────────────────────────────────────────────
def generate_readmes(assistant: OpenAIAssistant):
    """Iterate over project subfolders and generate README.md files."""
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        if EXCLUDE_MARKER in filenames:
            continue
        print(f"Processing: {dirpath}")

        folder_content = collect_folder_contents(dirpath)
        if not folder_content.strip():
            print("Skipped (no valid content)")
            continue

        user_prompt = f"{SYSTEM_PROMPT}\n\n{folder_content}"
        response, cost = assistant.analyse(user_prompt, structured_output=False)

        if response:
            readme_path = os.path.join(dirpath, README_FILENAME)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(response.strip())
            print(f"README.md created — Cost: ${cost:.4f}")
        else:
            print("Failed to generate README")

# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    assistant = OpenAIAssistant(
        name="ReadmeBot",
        sys_content=SYSTEM_PROMPT,
        response_model=str  # No structured output needed, just markdown text
    )
    generate_readmes(assistant)
