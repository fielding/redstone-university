"""Which modules count as "released" (published on the public site).

Used by the PDF pipeline's ``--released-only`` builds to produce a preview PDF
containing only the shipped content. This mirrors the web app's gating in
``web/src/utils/gating.ts`` (all of Part I plus Module 5); keep the two in sync
when a new part ships.
"""

import os
import re

# Modules 0 through RELEASED_MAX_MODULE (inclusive) are released. Interlude
# directories like "03b_Interlude-..." parse to 3, so they're covered. Bump
# this as later parts are published.
RELEASED_MAX_MODULE = 5


def module_number(label):
    """Leading module number from a directory name ("03b_Interlude-..."), a
    problem id ("5.3.1"), or a glossary module footnote ("5"). Returns an int,
    or None when there is no leading number."""
    match = re.match(r"\s*(\d+)", str(label))
    return int(match.group(1)) if match else None


def is_released(label):
    """True when label's leading module number is within the released range."""
    num = module_number(label)
    return num is not None and num <= RELEASED_MAX_MODULE


def preview_path(path):
    """Insert a '-preview' suffix before the extension, e.g.
    course/Redstone-University.pdf -> course/Redstone-University-preview.pdf"""
    root, ext = os.path.splitext(path)
    return f"{root}-preview{ext}"
