import os
import re
from glob import glob
from typing import List, Tuple

SRC_DIR = "src"
APPENDIX_FILE = "course/z-appendices/appendix-a-solutions.md"


def parse_label_part(part: str) -> Tuple[int, str]:
    """
    Parse parts like '12', '12a', '6', '6b' into a sortable tuple.
    Unknown formats are pushed to the end but kept stable.
    """
    match = re.fullmatch(r"(\d+)([A-Za-z]*)", part)
    if not match:
        return (10**9, part.lower())
    return (int(match.group(1)), match.group(2).lower())


def problem_sort_key(problem_id: str) -> List[Tuple[int, str]]:
    return [parse_label_part(part) for part in problem_id.split(".")]


def extract_solutions_from_file(md_content: str, file_path: str):
    """
    Extract solutions from a single markdown file.
    Supports problem IDs like:
    - 10.3.1
    - 12a.6.1
    - 12b.5.2
    """
    solutions = []
    pattern = re.compile(
        r"^####\s+Practice Problem\s+([\dA-Za-z\.]+):\s*(.*?)\s*\n(<details>.*?</details>)",
        re.MULTILINE | re.DOTALL,
    )

    for match in pattern.finditer(md_content):
        problem_id, problem_title, details_block = match.groups()
        problem_title = problem_title.strip()

        inner_content_match = re.search(r"<summary>.*?</summary>(.*)", details_block, re.DOTALL)
        inner_content = inner_content_match.group(1).strip() if inner_content_match else ""

        solutions.append((problem_id, problem_title, inner_content))
        print(f"  - Extracted solution for Problem {problem_id} from {file_path}")

    return solutions


def main():
    os.makedirs(os.path.dirname(APPENDIX_FILE), exist_ok=True)

    all_solutions = []
    print(f"🔍 Scanning for markdown files in '{SRC_DIR}'...")
    files = sorted(glob(os.path.join(SRC_DIR, "**/*.md"), recursive=True))

    for file_path in files:
        if "project_assets" in file_path or "images" in file_path:
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        all_solutions.extend(extract_solutions_from_file(content, file_path))

    if not all_solutions:
        print("⚠️ No solutions found. Appendix will be empty.")
        return

    all_solutions.sort(key=lambda x: problem_sort_key(x[0]))

    appendix_content = [
        "## Appendix A: Solutions\n\n"
        "This appendix provides solutions to the practice problems in the Redstone University curriculum, organized by problem number for easy reference.\n"
    ]

    solution_count = 0
    for problem_id, problem_title, inner_content in all_solutions:
        solution_count += 1
        appendix_content.append(f"### Practice Problem {problem_id}: {problem_title}\n")
        appendix_content.append(inner_content)
        appendix_content.append("\n\n---\n\n")

    appendix_content.append('\n\n<hr class="pagebreak"/>\n\n')
    with open(APPENDIX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(appendix_content))

    print(f"✅ Generated Appendix A with {solution_count} solutions at: {APPENDIX_FILE}")


if __name__ == "__main__":
    main()
