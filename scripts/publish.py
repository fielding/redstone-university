#!/usr/bin/env python3
"""
Builds the course materials for web publication on GitHub.

This script processes files from the 'src' directory and generates a clean,
browsable course structure in the 'course' directory. It assumes a PNG-first
strategy for all images to ensure maximum compatibility.

Core responsibilities:
1.  Sets up a clean build environment.
2.  Processes all markdown files from the 'src' directory.
3.  For each local image referenced:
    - Copies the image to the central 'assets/images' directory.
    - Replaces its path with an absolute GitHub URL.
    - If the image is a gate symbol (e.g., NOT.png), it's converted to an
      HTML <img> tag with a fixed width for proper table display.
4.  Applies final HTML polishing for logos and figure captions.
5.  Writes the final markdown files to a clean, flat 'course' directory structure.
"""

import os
import re
import shutil
import subprocess
import sys

SRC_DIR = "src"
COURSE_DIR = "course"
ASSETS_DIR = "assets"
ASSETS_IMG_DIR = os.path.join(ASSETS_DIR, "images")

GITHUB_USER = "fielding"
GITHUB_REPO = "redstone-university"
GITHUB_BRANCH = "main"
RAW_BASE_URL = f"https://media.githubusercontent.com/media/{GITHUB_USER}/{GITHUB_REPO}/" f"{GITHUB_BRANCH}/"

# Files under COURSE_DIR that GitBook owns and this script does NOT generate:
# the table of contents, and the README GitBook auto-creates for the
# appendix section (which has no src/ introduction.md to generate one from).
# The clean rebuild below wipes COURSE_DIR, so these are preserved and
# restored — otherwise GitBook keeps re-committing them, which used to cause
# a rebuild<->sync commit loop on main.
GITBOOK_MANAGED = [
    "SUMMARY.md",
    os.path.join("z-appendices", "README.md"),
]

# A list of gate names used for special image handling in tables.
GATE_SYMBOLS = ["NOT", "AND", "OR", "NAND", "NOR", "XOR", "XNOR"]

# Raw Minecraft screenshots come in at 2-3k px, but nothing downstream
# (course pages, PDF) ever displays them wider than this.
MAX_IMAGE_DIMENSION = 1600

# Every unresolved image reference, reported in a summary at the end of the
# build. With --strict (or STRICT_IMAGES=1) the build fails if any exist.
MISSING_IMAGES = []


def optimize_and_copy_image(src_image_path, dest_image_path):
    """
    Copies an image into assets, downscaling and compressing PNGs along the
    way. Source images in 'src' are never modified. Falls back to a plain
    copy if Pillow is unavailable.
    """
    if not src_image_path.lower().endswith(".png"):
        shutil.copy2(src_image_path, dest_image_path)
        return

    try:
        from PIL import Image
    except ImportError:
        print("    - ⚠️ Pillow not installed; copying image without optimization.")
        shutil.copy2(src_image_path, dest_image_path)
        return

    with Image.open(src_image_path) as img:
        if max(img.size) > MAX_IMAGE_DIMENSION:
            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)
        img.save(dest_image_path, format="PNG", optimize=True)

    if shutil.which("pngquant"):
        subprocess.run(
            [
                "pngquant",
                "--force",
                "--skip-if-larger",
                "--quality",
                "70-95",
                "--strip",
                "--output",
                dest_image_path,
                dest_image_path,
            ],
            check=False,
        )


def setup_directories():
    """Cleans and creates the necessary build directories.

    GitBook-managed files (see GITBOOK_MANAGED) are read before the wipe and
    written back after, so a rebuild never deletes them.
    """
    print("🧹 Cleaning old build directories...")

    preserved = {}
    for rel in GITBOOK_MANAGED:
        path = os.path.join(COURSE_DIR, rel)
        if os.path.exists(path):
            with open(path, "rb") as f:
                preserved[rel] = f.read()

    if os.path.exists(COURSE_DIR):
        shutil.rmtree(COURSE_DIR)
    if os.path.exists(ASSETS_IMG_DIR):
        shutil.rmtree(ASSETS_IMG_DIR)

    os.makedirs(COURSE_DIR)
    os.makedirs(ASSETS_IMG_DIR)

    for rel, data in preserved.items():
        path = os.path.join(COURSE_DIR, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    if preserved:
        print(f"🔒 Preserved GitBook-managed files: {', '.join(sorted(preserved))}")

    print("📁 Created fresh build directories.")


def copy_static_assets():
    """Copies static project assets (e.g., logos) to the build directory."""
    project_assets_src = os.path.join(SRC_DIR, "project_assets")
    if os.path.exists(project_assets_src):
        for asset in os.listdir(project_assets_src):
            optimize_and_copy_image(
                os.path.join(project_assets_src, asset),
                os.path.join(ASSETS_IMG_DIR, asset),
            )
        print("🎨 Copied static project assets.")


def process_markdown_file(src_path, dest_path):
    """
    Processes a single markdown file, handling all images in one pass.
    """
    print(f"  - Processing: {src_path} -> {dest_path}")
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    image_pattern = re.compile(r"!\[([^\]]*)\]\((?!http)([^)]+)\)")

    def image_replacer(match):
        """
        Copies images and returns the appropriate Markdown or HTML.
        """
        alt_text, original_path = match.groups()

        basename = os.path.basename(original_path)
        filename_no_ext, _ = os.path.splitext(basename)
        is_gate_symbol = filename_no_ext in GATE_SYMBOLS

        abs_url = copy_image_and_get_absolute_url(original_path, src_path)

        if is_gate_symbol:
            return f'<img src="{abs_url}" alt="{alt_text}" width="64px">'
        else:
            return f"![{alt_text}]({abs_url})"

    content = image_pattern.sub(image_replacer, content)

    content = apply_final_html_transforms(content)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)


def copy_image_and_get_absolute_url(original_path, markdown_src_path):
    """
    Copies a local image to assets and returns its absolute GitHub URL.
    """
    src_image_path = os.path.normpath(os.path.join(os.path.dirname(markdown_src_path), original_path))

    if not os.path.exists(src_image_path):
        print(f"    - ⚠️ WARNING: Image not found: {src_image_path}")
        MISSING_IMAGES.append((markdown_src_path, original_path))
        return original_path

    module_dir = os.path.basename(os.path.dirname(markdown_src_path))
    module_prefix = module_dir.split("_")[0]
    new_image_name = f"{module_prefix}_{os.path.basename(src_image_path)}"
    dest_image_path = os.path.join(ASSETS_IMG_DIR, new_image_name)

    optimize_and_copy_image(src_image_path, dest_image_path)

    absolute_url = RAW_BASE_URL + dest_image_path.replace(os.path.sep, "/")
    return absolute_url


def apply_final_html_transforms(content):
    """
    Applies non-image-copy transformations for web presentation.
    """
    logo_light = RAW_BASE_URL + ASSETS_IMG_DIR + "/logo.png"
    logo_dark = RAW_BASE_URL + ASSETS_IMG_DIR + "/logo-dark.png"
    logo_html = (
        f'<p align="center"><picture>'
        f'<source media="(prefers-color-scheme: light)" srcset="{logo_light}">'
        f'<img alt="Redstone University Logo" src="{logo_dark}">'
        f"</picture></p>"
    )
    content = re.sub(r"!\[Redstone University Logo\]\([^)]+\)", logo_html, content)

    caption_pattern = r"!\[([^\]]*)\]\(([^)]+)\)\s*\n\s*\*(Figure:[^\n]*)\*"

    def caption_replacer(match):
        alt, src, caption = match.groups()
        return (
            f'<div align="center">'
            f'<img src="{src}" alt="{alt}" width="512px"/><br/>'
            f"<em>{caption}</em>"
            f"</div><br/>"
        )

    content = re.sub(caption_pattern, caption_replacer, content)
    return content


def main():
    """Main function to orchestrate the entire build process."""
    setup_directories()
    copy_static_assets()

    print("\n📝 Processing all markdown source files...")
    for root, _, files in os.walk(SRC_DIR):
        if "project_assets" in root or "images" in root:
            continue

        dest_path = None
        src_path = None

        if "draft.md" in files:
            src_path = os.path.join(root, "draft.md")
            module_name = os.path.basename(root)
            parent_dir_rel_path = os.path.relpath(os.path.dirname(root), SRC_DIR)
            dest_dir = os.path.join(COURSE_DIR, parent_dir_rel_path)
            dest_path = os.path.join(dest_dir, f"{module_name}.md")
        elif "introduction.md" in files:
            src_path = os.path.join(root, "introduction.md")
            relative_dir = os.path.relpath(root, SRC_DIR)
            dest_dir = os.path.join(COURSE_DIR, relative_dir) if relative_dir != "." else COURSE_DIR
            dest_path = os.path.join(dest_dir, "README.md")

        if src_path and dest_path:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            process_markdown_file(src_path, dest_path)

    if MISSING_IMAGES:
        print(f"\n⚠️  {len(MISSING_IMAGES)} missing image reference(s):")
        for markdown_file, image_path in MISSING_IMAGES:
            print(f"   - {markdown_file}: {image_path}")
        strict = "--strict" in sys.argv or os.environ.get("STRICT_IMAGES") == "1"
        if strict:
            print("\n❌ Failing build (strict mode): resolve the missing images above.")
            sys.exit(1)

    print("\n✅ Build complete! The 'course' directory has the correct flat structure.")


if __name__ == "__main__":
    main()
