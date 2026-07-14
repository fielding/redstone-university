#!/usr/bin/env bash
# Build the "preview" PDF: released modules only (Part I + Module 5), with the
# appendix and glossary filtered to just those modules. Writes
# course/Redstone-University-preview.pdf, leaving the full PDF untouched.
#
# Requires the same tooling as the full PDF build (WeasyPrint + KaTeX); see
# .github/workflows/publish_course.yml for the exact dependencies.
set -euo pipefail
cd "$(dirname "$0")/.."

python scripts/extract_solutions.py --released-only
python scripts/extract_key_terms.py --released-only
python scripts/prepare_pdf.py --released-only
python scripts/build_pdf.py --released-only
