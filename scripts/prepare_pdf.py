import os
import re
from glob import glob

SRC_DIR = "src"
COURSE_DIR = "course"
ASSETS_IMG_DIR = "assets/images"
PDF_INPUT_FILE = os.path.join(COURSE_DIR, "Redstone-University.md")

# Appendices to add at the end
APPENDIX_A = "course/z-appendices/appendix-a-solutions.md"
APPENDIX_B = "course/z-appendices/appendix-b-glossary.md"

# --- GitHub URL Configuration ---
GITHUB_USER = "fielding"
GITHUB_REPO = "redstone-university"
GITHUB_BRANCH = "main"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/"


def get_course_files_in_order():
    """
    Finds all 'draft.md' and 'introduction.md' files and returns them in the
    correct structural order for the final combined document.
    """
    print("🔎 Determining correct file order for concatenation...")
    ordered_files = []

    main_intro = os.path.join(SRC_DIR, "introduction.md")
    if os.path.exists(main_intro):
        ordered_files.append(main_intro)
        print(f"  - Found main introduction: {main_intro}")

    part_dirs = sorted(glob(os.path.join(SRC_DIR, "Part-*/")))
    for part_dir in part_dirs:
        part_intro = os.path.join(part_dir, "introduction.md")
        if os.path.exists(part_intro):
            ordered_files.append(part_intro)
            print(f"  - Found Part introduction: {part_intro}")

        lesson_dirs = sorted(glob(os.path.join(part_dir, "[0-9]*_*/")))
        for lesson_dir in lesson_dirs:
            draft_file = os.path.join(lesson_dir, "draft.md")
            if os.path.exists(draft_file):
                ordered_files.append(draft_file)

    print("✅ File order determined.")
    return ordered_files


def process_markdown_content(content, file_path):
    """
    Processes the raw markdown content to make it PDF-ready by:
    1. Removing inline solution <details> blocks.
    2. Rewriting image paths to be root-relative paths that the PDF
       generator's 'image_import' can find and replace.
    """
    solution_placeholder = "> **(Solution for this problem can be found in Appendix A.)**"
    content = re.sub(r"<details>.*?</details>", solution_placeholder, content, flags=re.DOTALL)

    def image_path_replacer(match):
        alt_text, original_path = match.groups()

        if original_path.startswith("http"):
            return match.group(0)

        image_basename = os.path.basename(original_path)

        parent_dir_name = os.path.basename(os.path.dirname(file_path))
        if parent_dir_name[:2].isdigit() and "_" in parent_dir_name:
            module_prefix = parent_dir_name.split("_")[0]
            new_image_name = f"{module_prefix}_{image_basename}"
        else:
            new_image_name = image_basename

        new_path = os.path.join(ASSETS_IMG_DIR, new_image_name)

        new_path = new_path.replace(os.path.sep, "/")

        return f"![{alt_text}]({new_path})"

    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_path_replacer, content)

    content = re.sub(r'<p align="center"><picture>.*?</picture></p>', "", content, flags=re.DOTALL)
    caption_pattern = r'<div align="center">.*?<img src="([^"]+)" alt="([^"]+)"[^>]*>.*?<em>([^<]+)</em>.*?</div><br/>'
    content = re.sub(caption_pattern, r"![\2](\1)\n\n*\3*", content)

    return content


def main():
    print("🚀 Starting PDF preparation process...")

    files_to_combine = get_course_files_in_order()
    print(f"📚 Found {len(files_to_combine)} content files to combine for the PDF.")

    full_course_content = []
    for file_path in files_to_combine:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        processed_content = process_markdown_content(content, file_path)
        full_course_content.append(processed_content)

    combined_md = '\n\n<hr class="pagebreak"/>\n\n'.join(full_course_content)

    for appendix_path in [APPENDIX_A, APPENDIX_B]:
        if os.path.exists(appendix_path):
            print(f"➕ Appending {os.path.basename(appendix_path)}...")
            with open(appendix_path, "r", encoding="utf-8") as f:
                appendix_content = f.read()
            combined_md += '\n\n<hr class="pagebreak"/>\n\n' + appendix_content
        else:
            print(f"⚠️ Warning: Appendix file not found at {appendix_path}. Skipping.")

    with open(PDF_INPUT_FILE, "w", encoding="utf-8") as f:
        f.write(combined_md)

    print(f"✅ Successfully created PDF input file at: {PDF_INPUT_FILE}")


if __name__ == "__main__":
    main()
