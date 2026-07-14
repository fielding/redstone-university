#!/usr/bin/env python3
"""
Renders the combined course markdown (built by prepare_pdf.py) into the
final PDF at course/Redstone-University.pdf.

Pipeline:
1. markdown-it-py parses course/Redstone-University.md (GitHub-flavored:
   tables, raw HTML, fenced code) with dollar-math support.
2. Every $...$ / $$...$$ expression is pre-rendered to HTML server-side
   with KaTeX (via node), so the PDF shows real typeset math.
3. WeasyPrint lays out the HTML with assets/css/pdf-print.css, producing
   page numbers, a table of contents with page references, and a PDF
   bookmark outline derived from the heading levels.

Requirements:
    pip install weasyprint markdown-it-py mdit-py-plugins linkify-it-py pygments
    npm install --no-save katex

Run from the repository root, after prepare_pdf.py.
"""

import html
import json
import os
import re
import subprocess
import sys

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_INPUT_FILE = os.path.join("course", "Redstone-University.md")
PDF_OUTPUT_FILE = os.path.join("course", "Redstone-University.pdf")
PRINT_CSS = os.path.join("assets", "css", "pdf-print.css")
COVER_LOGO = os.path.join("assets", "images", "logo.png")

TITLE = "Redstone University"
SUBTITLE = (
    "An interactive course on computer science and digital architecture, "
    "built from the ground up in Minecraft."
)
AUTHOR = "Fielding Johnston"

# Small node program that batch-renders LaTeX expressions with KaTeX.
# Reads a JSON array of {"tex": ..., "display": bool} from stdin and
# writes a JSON array of HTML strings to stdout.
KATEX_RENDER_JS = """
const katex = require("katex");
let input = "";
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
    const jobs = JSON.parse(input);
    const out = jobs.map((job) =>
        katex.renderToString(job.tex, {
            displayMode: job.display,
            throwOnError: false,
            output: "html",
            strict: false,
        })
    );
    process.stdout.write(JSON.stringify(out));
});
"""


def katex_render_all(expressions):
    """Renders [(tex, display), ...] to HTML strings in one node call."""
    if not expressions:
        return {}
    jobs = [{"tex": tex, "display": display} for tex, display in expressions]
    try:
        result = subprocess.run(
            ["node", "-e", KATEX_RENDER_JS],
            input=json.dumps(jobs),
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        )
    except FileNotFoundError:
        sys.exit("❌ node not found. KaTeX rendering requires Node.js.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"❌ KaTeX rendering failed:\n{e.stderr}")
    rendered = json.loads(result.stdout)
    return dict(zip(expressions, rendered))


def find_katex_css():
    """Locates katex.min.css inside the locally installed npm package."""
    try:
        result = subprocess.run(
            ["node", "-p", "require.resolve('katex/dist/katex.min.css')"],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("❌ KaTeX not found. Run: npm install --no-save katex")
    return os.path.relpath(result.stdout.strip(), REPO_ROOT)


def make_highlighter():
    """Returns a markdown-it highlight function backed by Pygments."""
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound

    formatter = HtmlFormatter(nowrap=True)

    def highlighter(code, lang, attrs):
        if not lang:
            return html.escape(code)
        try:
            lexer = get_lexer_by_name(lang)
        except ClassNotFound:
            return html.escape(code)
        return highlight(code, lexer, formatter)

    return highlighter, formatter.get_style_defs(".highlight")


def slugify(title):
    return re.sub(r"[^\w一-鿿\- ]", "", title.strip().lower().replace(" ", "-"))


def collect_math(tokens):
    """Walks the token tree and returns every unique math expression."""
    expressions = set()
    for token in tokens:
        if token.type == "math_inline":
            expressions.add((token.content, False))
        elif token.type in ("math_block", "math_inline_double"):
            expressions.add((token.content, True))
        if token.children:
            expressions.update(collect_math(token.children))
    return expressions


def build_toc(tokens):
    """Returns TOC entries [(level, id, text)] for h2/h3 headings."""
    entries = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag in ("h2", "h3"):
            anchor = token.attrGet("id")
            inline = tokens[i + 1]
            text = "".join(
                child.content for child in (inline.children or []) if child.type in ("text", "code_inline")
            )
            if anchor and text:
                entries.append((int(token.tag[1]), anchor, text))
    return entries


def toc_html(entries):
    parts = ['<nav id="toc"><h2 class="toc-title">Contents</h2><ul class="toc-l1">']
    open_sublist = False
    for level, anchor, text in entries:
        if level == 2:
            if open_sublist:
                parts.append("</ul></li>")
                open_sublist = False
            elif parts[-1].endswith("</a>"):
                parts.append("</li>")
            parts.append(f'<li class="toc-chapter"><a href="#{anchor}">{html.escape(text)}</a>')
        else:
            if not open_sublist:
                parts.append('<ul class="toc-l2">')
                open_sublist = True
            parts.append(f'<li><a href="#{anchor}">{html.escape(text)}</a></li>')
    if open_sublist:
        parts.append("</ul></li>")
    elif parts[-1].endswith("</a>"):
        parts.append("</li>")
    parts.append("</ul></nav>")
    return "".join(parts)


def number_figures(body):
    """Rewrites "Figure:" captions to "Figure <chapter>.<n>:", numbered
    per h2 chapter (Module 5 -> 5.1, 5.2, ...; Interlude II -> II.1).
    Captions in chapters without a module/interlude number keep their
    plain "Figure:" prefix. Long captions get a class so the CSS can
    left-align multi-line text while keeping short ones centered."""
    chapter_key = None
    counter = 0
    numbered = 0
    out = []
    for part in re.split(r"(<h2[^>]*>.*?</h2>)", body, flags=re.DOTALL):
        h2 = re.match(r"<h2[^>]*>(.*?)</h2>$", part, flags=re.DOTALL)
        if h2:
            title = re.sub(r"<[^>]+>", "", h2.group(1))
            key = re.match(r"Module (\d+[ab]?)|Interlude ([IVX]+)", title)
            chapter_key = (key.group(1) or key.group(2)) if key else None
            counter = 0
            out.append(part)
            continue

        def relabel(caption):
            nonlocal counter, numbered
            prefix = ""
            if chapter_key:
                counter += 1
                numbered += 1
                prefix = f"Figure {chapter_key}.{counter}: "
            text = re.sub(r"<[^>]+>", "", caption.group(1))
            # ~100 chars fit on one 10pt caption line; past two lines a
            # centered ragged block reads worse than a left-aligned one.
            cls = ' class="long"' if len(prefix) + len(text) > 200 else ""
            body_text = re.sub(r"^Figure:\s*", prefix or "Figure: ", caption.group(1))
            return f"<figcaption{cls}>{body_text}</figcaption>"

        out.append(re.sub(r"<figcaption>(Figure:.*?)</figcaption>", relabel, part, flags=re.DOTALL))
    print(f"🔢 Numbered {numbered} figure captions.")
    return "".join(out)


# Raw-markdown/TeX artifacts that must never survive into rendered text.
LEAK_PATTERNS = ("|:---", "**", "$$", "\\begin{", "\\text{")
# Exact substrings of lines that are allowed to contain a pattern above.
LEAK_ALLOWLIST: tuple[str, ...] = ()


def check_markdown_leaks(body):
    """Fails the build when raw markdown or TeX survives into rendered
    prose (e.g. a table markdown-it lazily folded into a list item, or a
    code span printing literal **). Code blocks and inline code are
    exempt: their content is verbatim by design."""
    text = rendered_text(body)
    hits = []
    for line in text.splitlines():
        for pattern in LEAK_PATTERNS:
            if pattern in line and not any(ok in line for ok in LEAK_ALLOWLIST):
                hits.append((pattern, line.strip()[:100]))
    if hits:
        print(f"❌ {len(hits)} raw markdown/TeX leak(s) in rendered text:")
        for pattern, context in hits[:20]:
            print(f"   [{pattern}] {context}")
        sys.exit(1)
    print("🔎 Leak scan clean: no raw markdown/TeX in rendered text.")


# Editorial placeholder tokens (docs/pdf-release-checklist.md). TODO and
# TBD are case-sensitive whole words: "PyCryptodome" must not match.
PLACEHOLDER_PATTERNS = (
    ("TODO", re.compile(r"\bTODO\b")),
    ("TBD", re.compile(r"\bTBD\b")),
    ("Figure placeholder", re.compile(r"figure placeholder", re.IGNORECASE)),
    ("Draft note", re.compile(r"draft note", re.IGNORECASE)),
    ("[pending]", re.compile(r"\[pending\]", re.IGNORECASE)),
)
# Chapters whose placeholders are known unreleased draft content and do
# not fail the build (scope decision pending in ru-09bf79).
DRAFT_MODULES = ("Module 9",)


def rendered_text(fragment):
    """HTML fragment -> visible prose. Comments never render; code
    blocks and inline code are verbatim by design."""
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.DOTALL)
    fragment = re.sub(r"<pre\b.*?</pre>|<code\b.*?</code>", " ", fragment, flags=re.DOTALL)
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def check_placeholders(body):
    """Reports editorial placeholders per chapter and fails the build
    for any outside the DRAFT_MODULES allowlist."""
    chapter = "(front matter)"
    counts = {}
    failures = []
    for part in re.split(r"(<h2[^>]*>.*?</h2>)", body, flags=re.DOTALL):
        h2 = re.match(r"<h2[^>]*>(.*?)</h2>$", part, flags=re.DOTALL)
        if h2:
            chapter = re.sub(r"<[^>]+>", "", h2.group(1)).strip()
            continue
        text = rendered_text(part)
        for token, pattern in PLACEHOLDER_PATTERNS:
            n = len(pattern.findall(text))
            if n:
                counts[(chapter, token)] = counts.get((chapter, token), 0) + n
                if not chapter.startswith(DRAFT_MODULES):
                    failures.append((chapter, token, n))
    if counts:
        print("📝 Placeholder report:")
        for (chapter, token), n in sorted(counts.items()):
            mark = "allowed (draft)" if chapter.startswith(DRAFT_MODULES) else "FAIL"
            print(f"   {chapter[:50]}: {n} x {token} [{mark}]")
    else:
        print("📝 Placeholder report: none found.")
    if failures:
        print(f"❌ {len(failures)} placeholder finding(s) outside DRAFT_MODULES.")
        sys.exit(1)


def check_pagination(document):
    """Post-layout checks on the WeasyPrint page boxes: the final page
    must hold real content, and no numbered page may be blank."""
    from weasyprint.formatting_structure import boxes

    def page_content(page):
        words, images = [], 0

        def walk(box):
            nonlocal images
            if type(box).__name__ == "MarginBox":
                return
            if isinstance(box, boxes.TextBox):
                words.extend(box.text.split())
            elif isinstance(box, boxes.ReplacedBox):
                images += 1
            for child in getattr(box, "children", []):
                walk(child)

        walk(page._page_box)
        return words, images

    blank = []
    for index, page in enumerate(document.pages[1:], 2):  # cover exempt
        words, images = page_content(page)
        if not words and not images:
            blank.append(index)
    if blank:
        print(f"⚠️ Blank numbered page(s): {blank}")
    else:
        print("📄 No blank numbered pages.")

    last_words, last_images = page_content(document.pages[-1])
    if len(last_words) < 20 and not last_images:
        print(f"❌ Final page is a fragment ({len(last_words)} words): {' '.join(last_words)[:100]}")
        sys.exit(1)
    print(f"📄 Final page holds {len(last_words)} words / {last_images} image(s).")


def report_missing_images(markdown_src):
    referenced = set(re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", markdown_src))
    missing = sorted(path for path in referenced if not path.startswith("http") and not os.path.exists(path))
    if missing:
        print(f"⚠️ {len(missing)} referenced images do not exist and will be absent from the PDF:")
        for path in missing:
            print(f"   - {path}")


def main():
    os.chdir(REPO_ROOT)
    print("🚀 Building PDF from processed markdown...")

    with open(PDF_INPUT_FILE, "r", encoding="utf-8") as f:
        markdown_src = f.read()

    report_missing_images(markdown_src)

    # None of the embedded fonts carry U+2011 (non-breaking hyphen);
    # map it to the plain hyphen they all have rather than letting
    # fontconfig pull in a random system face.
    markdown_src = markdown_src.replace("\u2011", "\u2010")

    # The leading logo image belongs on the generated cover page, not in
    # the body of the first chapter.
    markdown_src = re.sub(r"\A!\[[^\]]*\]\([^)]*logo[^)]*\)\s*\n", "", markdown_src)

    highlighter, pygments_css = make_highlighter()

    md = MarkdownIt("gfm-like", {"html": True, "linkify": False, "highlight": highlighter})
    # double_inline: a "$$ ... $$" that ends up inside a paragraph (the
    # course sometimes puts it on the line directly after text) must still
    # render as display math instead of leaking literal dollar signs.
    md.use(dollarmath_plugin, allow_space=True, double_inline=True)
    md.use(anchors_plugin, min_level=2, max_level=4, slug_func=slugify)

    tokens = md.parse(markdown_src)

    expressions = sorted(collect_math(tokens))
    print(f"🧮 Rendering {len(expressions)} unique math expressions with KaTeX...")
    math_html = katex_render_all(expressions)

    def render_math_inline(self, tokens, idx, options, env):
        return math_html[(tokens[idx].content, False)]

    def render_math_block(self, tokens, idx, options, env):
        return f'<div class="math-display">{math_html[(tokens[idx].content, True)]}</div>\n'

    md.add_render_rule("math_inline", render_math_inline)
    md.add_render_rule("math_block", render_math_block)
    md.add_render_rule("math_inline_double", render_math_block)

    body = md.renderer.render(tokens, md.options, {})

    # An image (or a stacked group of them) followed by its
    # "*Figure: ...*" caption must never be separated by a page break;
    # give the group a shared <figure> wrapper so the print CSS can
    # apply break-inside: avoid. The caption is either in the images'
    # own paragraph (softbreak) or in the next one. Multi-image figures
    # get a class so the CSS can shrink them to fit a page together.
    def wrap_figure(m):
        multi = ' class="multi"' if m.group(1).count("<img") > 1 else ""
        return f"<figure{multi}>{m.group(1)}<figcaption>{m.group(2)}</figcaption></figure>"

    body = re.sub(
        r"<p>(<img[^>]*>(?:\s*<img[^>]*>)*)(?:\s*</p>\s*<p>|\s*)<em>(Figure:.*?)</em></p>",
        wrap_figure,
        body,
        flags=re.DOTALL,
    )

    # Chapters force their own page start via CSS (main h2
    # break-before). The <hr class="pagebreak"> joiner boxes that used
    # to do this must go: a box mints a blank folio page when the
    # previous chapter ends exactly at a page boundary, whereas
    # adjacent forced breaks deduplicate.
    body = re.sub(r'<hr class="pagebreak"\s*/?>\s*(?=<h2)', "", body)

    # A module conclusion is a short designed closer; keep the heading
    # and its few paragraphs on one page instead of stranding the last
    # lines alone on the next.
    body = re.sub(
        r"(<h3[^>]*>Module [^<]* Conclusion</h3>.*?)(?=<h[23]|\Z)",
        r'<section class="keep-together">\1</section>',
        body,
        flags=re.DOTALL,
    )

    # The glossary ends with a run of "[n]: Module ..." source-key
    # lines; set them as one compact two-column block so the last line
    # cannot strand on its own page.
    body = re.sub(
        r"((?:<p>\[[0-9]+[ab]?\]:[^<]*</p>\s*){2,})",
        r'<div class="source-key">\1</div>',
        body,
    )

    body = number_figures(body)
    check_markdown_leaks(body)
    check_placeholders(body)

    toc_entries = build_toc(tokens)
    print(f"📑 Table of contents: {len(toc_entries)} entries.")

    katex_css = find_katex_css()

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(TITLE)}</title>
<meta name="author" content="{html.escape(AUTHOR)}">
<link rel="stylesheet" href="{katex_css}">
<link rel="stylesheet" href="{PRINT_CSS}">
<style>{pygments_css}</style>
</head>
<body>
<section id="cover">
  <img id="cover-logo" src="{COVER_LOGO}" alt="{html.escape(TITLE)} logo">
  <h1 id="cover-title">{html.escape(TITLE)}</h1>
  <p id="cover-subtitle">{html.escape(SUBTITLE)}</p>
  <p id="cover-author">{html.escape(AUTHOR)}</p>
</section>
{toc_html(toc_entries)}
<main>
{body}
</main>
</body>
</html>"""

    from weasyprint import HTML

    print("📄 Laying out pages with WeasyPrint (this takes a few minutes)...")
    rendered = HTML(string=document, base_url=REPO_ROOT).render()
    check_pagination(rendered)
    rendered.write_pdf(PDF_OUTPUT_FILE)

    size_mb = os.path.getsize(PDF_OUTPUT_FILE) / (1024 * 1024)
    print(f"✅ Wrote {PDF_OUTPUT_FILE} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
