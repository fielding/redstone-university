import argparse
import os
import re
from glob import glob
from typing import Dict, List, Tuple

from released_filter import is_released, preview_path

SRC_DIR = "src"
APPENDIX_FILE = "course/z-appendices/appendix-b-glossary.md"

GITHUB_USER = "fielding"
GITHUB_REPO = "redstone-university"
GITHUB_BRANCH = "main"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/"
ASSETS_IMG_DIR = "assets/images"


def parse_module_label(label: str) -> Tuple[int, str]:
    """
    Parse labels like '12', '12a', '12b' into sortable tuples.
    """
    match = re.fullmatch(r"(\d+)([A-Za-z]*)", label)
    if not match:
        return (10**9, label.lower())
    return (int(match.group(1)), match.group(2).lower())


def rewrite_image_paths(md_content):
    def replacer(match):
        alt_text, rel_path = match.groups()
        if rel_path.startswith("./images/") or rel_path.startswith("images/"):
            image_name = rel_path.split("/")[-1]
            abs_url = RAW_BASE_URL + ASSETS_IMG_DIR + "/" + image_name
            return f"![{alt_text}]({abs_url})"
        return match.group(0)

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replacer, md_content)


def extract_module_titles(md_content: str, file_path: str) -> Dict[str, str]:
    """
    Extract module labels and titles from headings like:
    - ## Module 12: Title
    - ## Module 12a: Title
    - ## Module 12b: Title
    """
    module_pattern = re.compile(r"^##\s+Module\s+(\d+[A-Za-z]?):\s*(.+)$", re.MULTILINE)
    module_titles: Dict[str, str] = {}
    for match in module_pattern.finditer(md_content):
        module_num = match.group(1)
        title = match.group(2).strip()
        module_titles[module_num] = title
        print(f"📋 Found module in {file_path}: Module {module_num}: {title}")
    return module_titles


def extract_key_terms_from_md(md_content, file_path, module_num=None):
    """
    Extract key terms and definitions from '#### Key Terms' sections.
    Returns a list of (term, definition, module_num) tuples.
    """
    # continuation lines stop at list items AND at headings — without the
    # heading guard, the last term's definition swallows whatever section
    # follows the Key Terms block (e.g. a module conclusion with no ---
    # separator, which is how Module 1's conclusion ended up inside the
    # glossary's R entries)
    pattern = re.compile(
        r"^####\s*Key Terms\s*\n((?:-\s*\*\*[^*]+\*\*:[^\n]*(?:\n+(?!\s*[-#])[^\n]*)*\n*)+)",
        re.MULTILINE | re.DOTALL,
    )
    term_pattern = re.compile(r"-\s*\*\*([^*]+?)\*\*:\s*((?:[^\n]*(?:\n+(?!\s*[-#])[^\n]*)*))(?=\s*(?:-|\n|$))", re.DOTALL)
    all_terms = []

    matches = pattern.finditer(md_content)
    section_count = 0
    for section_match in matches:
        section_count += 1
        term_list_str = section_match.group(1).strip()
        print(f"📄 Found 'Key Terms' section in {file_path}")

        if module_num is None:
            print(f"⚠️ Warning: No module number provided for {file_path}. Skipping terms.")
            continue

        term_matches = term_pattern.finditer(term_list_str)
        term_count = 0
        for match in term_matches:
            term_count += 1
            term = match.group(1).strip().rstrip(":")
            definition = match.group(2).strip()
            if term and definition:
                all_terms.append((term, definition, module_num))
                print(f"  - Extracted term: '{term}' (Module {module_num})")
            else:
                print(f"  ⚠️ Warning: Skipped invalid term entry in {file_path}: {match.group(0).strip()}")

        print(f"  📝 Extracted {term_count} terms from Module {module_num}")

    if section_count == 0:
        print(f"⚠️ Warning: No 'Key Terms' sections found in {file_path}")

    return all_terms


def collect_markdown_files(directory):
    return sorted(glob(os.path.join(directory, "**/*.md"), recursive=True))


def main(released_only=False):
    os.makedirs(os.path.dirname(APPENDIX_FILE), exist_ok=True)

    all_terms: List[Tuple[str, str, str]] = []
    module_titles: Dict[str, str] = {}

    print(f"🔍 Scanning markdown files in '{SRC_DIR}'...")
    files = collect_markdown_files(SRC_DIR)
    if not files:
        print(f"❌ Error: No markdown files found in '{SRC_DIR}'.")
        return
    print(f"📜 Found {len(files)} markdown files: {files}")

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            md = f.read()
        current_modules = extract_module_titles(md, file_path)
        module_titles.update(current_modules)

        if current_modules:
            module_num = list(current_modules.keys())[0]
            terms = extract_key_terms_from_md(md, file_path, module_num)
        else:
            terms = []
            print(f"⚠️ No module found in {file_path}, skipping key terms extraction.")

        all_terms.extend(terms)

    if not all_terms:
        print(f"❌ Error: No terms extracted from any files in '{SRC_DIR}'.")
        return

    sorted_terms = sorted(all_terms, key=lambda x: x[0].lower())

    if released_only:
        # x[2] is the module the term was introduced in.
        sorted_terms = [t for t in sorted_terms if is_released(t[2])]

    appendix_content = [
        "## Appendix B: Glossary\n\n"
        "This glossary compiles key terms from the Redstone University curriculum, "
        "organized alphabetically. Each term’s definition is followed by a footnote "
        "indicating the module where it is introduced.\n"
    ]
    # dedupe by token-set signature, not exact string: "BCD (Binary-Coded
    # Decimal)" and "Binary-Coded Decimal (BCD)" are the same glossary entry
    def term_signature(t: str) -> str:
        return " ".join(sorted(re.findall(r"[a-z0-9]+", t.lower())))

    seen_terms = set()
    unique_terms = []
    for term, definition, module in sorted_terms:
        sig = term_signature(term)
        if sig in seen_terms:
            print(f"⚠️ Warning: Duplicate term '{term}' in Module {module}. Keeping first definition.")
            continue
        seen_terms.add(sig)
        unique_terms.append((term, definition, module))
        appendix_content.append(f"**{term}**\n: {definition} [{module}]\n")

    appendix_content.append("\n---\n")
    for module in sorted(module_titles.keys(), key=parse_module_label):
        if released_only and not is_released(module):
            continue
        title = module_titles.get(module, f"Module {module}")
        appendix_content.append(f"[{module}]: Module {module}: {title}\n")

    appendix_markdown = "\n".join(appendix_content)
    appendix_markdown = rewrite_image_paths(appendix_markdown)

    out_file = preview_path(APPENDIX_FILE) if released_only else APPENDIX_FILE
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(appendix_markdown)

    print(f"✅ Extracted and alphabetized {len(unique_terms)} unique key terms into {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--released-only",
        action="store_true",
        help="Only include released modules (Part I + Module 5); writes the -preview variant.",
    )
    main(parser.parse_args().released_only)
