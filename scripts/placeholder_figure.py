#!/usr/bin/env python3
"""
Generate a placeholder figure card for a slot whose real image doesn't exist
yet. The card uses the design-system palette and says PLACEHOLDER loudly, so
it can never pass for a finished figure; give it the FINAL filename so the
draft reference never changes — the real render simply overwrites the card.

    python3 scripts/placeholder_figure.py <out.png> "<title>" "<pipeline note>"
"""
import os
import sys

INK = "#30231e"
PAPER = "#f5f1ea"
FAINT = "#d2cdc5"
ON = "#f0392a"

W, H = 1400, 520


def svg(title, note):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>
<rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="none"
      stroke="{FAINT}" stroke-width="4" stroke-dasharray="18 12"/>
<text x="{W / 2}" y="150" font-family="Fira Code, ui-monospace, monospace"
      font-size="34" letter-spacing="14" text-anchor="middle"
      fill="{ON}">PLACEHOLDER</text>
<text x="{W / 2}" y="255" font-family="Young Serif, Georgia, serif"
      font-size="44" text-anchor="middle" fill="{INK}">{title}</text>
<text x="{W / 2}" y="330" font-family="Fira Code, ui-monospace, monospace"
      font-size="22" text-anchor="middle" fill="{INK}" opacity="0.65">{note}</text>
</svg>
'''


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    out, title, note = sys.argv[1:4]
    import cairosvg
    cairosvg.svg2png(bytestring=svg(title, note).encode(), write_to=out)
    print(f"wrote {out}")
    if not os.path.basename(out).startswith("placeholder"):
        print("  (final filename: the real render will overwrite this card)")


if __name__ == "__main__":
    main()
