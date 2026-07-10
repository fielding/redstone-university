#!/usr/bin/env python3
"""Assert the no-false-junction invariant on cv_render output.

Wires of different nets may only meet as perpendicular crossings. Anything
else — collinear overlap, parallel runs close enough to merge at stroke
width, an endpoint landing on (or within a hair of) another net's line —
draws a junction that doesn't exist in the circuit (ru-b24cda).

    CV_DEBUG_SEGS=/tmp/segs.jsonl python3 scripts/cv_render.py <cv> --batch renders/diagrams.json
    python3 scripts/check_cv_junctions.py /tmp/segs.jsonl
"""
import json, sys

EPS = 4.0    # endpoint gap that still reads as touching at wire stroke ≈3
PARA = 6.0   # parallel runs closer than this merge visually (grid pitch 10)


def merge_runs(segs):
    """Collapse same-net collinear segments that touch or overlap into maximal
    runs, so a node splitting a straight wire doesn't count as an endpoint."""
    segs = [list(s) for s in segs]
    changed = True
    while changed:
        changed = False
        out, used = [], [False] * len(segs)
        for i in range(len(segs)):
            if used[i]:
                continue
            r, x1, y1, x2, y2 = segs[i]
            for j in range(i + 1, len(segs)):
                if used[j] or segs[j][0] != r:
                    continue
                _, u1, v1, u2, v2 = segs[j]
                if x1 == x2 == u1 == u2 and not (v1 > y2 or y1 > v2):
                    y1, y2 = min(y1, v1), max(y2, v2)
                    used[j] = True; changed = True
                elif y1 == y2 == v1 == v2 and not (u1 > x2 or x1 > u2):
                    x1, x2 = min(x1, u1), max(x2, u2)
                    used[j] = True; changed = True
            out.append([r, x1, y1, x2, y2])
            used[i] = True
        segs = out
    return segs


def pt_seg_dist(x, y, x1, y1, x2, y2):
    cx = min(max(x, x1), x2); cy = min(max(y, y1), y2)
    return ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5


def violations(runs):
    bad = []
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            (ra, ax1, ay1, ax2, ay2) = runs[i]
            (rb, bx1, by1, bx2, by2) = runs[j]
            if ra == rb:
                continue
            av, bv = ax1 == ax2, bx1 == bx2
            if av == bv:                                   # parallel
                if av:
                    d = abs(ax1 - bx1)
                    ov = min(ay2, by2) - max(ay1, by1)
                else:
                    d = abs(ay1 - by1)
                    ov = min(ax2, bx2) - max(ax1, bx1)
                if d < PARA and ov > 0:
                    bad.append(("PARALLEL-MERGE", runs[i], runs[j]))
                elif d < EPS and -EPS < ov <= 0:
                    bad.append(("END-GAP", runs[i], runs[j]))
            else:                                          # perpendicular
                ends_a = ((ax1, ay1), (ax2, ay2))
                ends_b = ((bx1, by1), (bx2, by2))
                if (any(pt_seg_dist(x, y, bx1, by1, bx2, by2) <= EPS for x, y in ends_a)
                        or any(pt_seg_dist(x, y, ax1, ay1, ax2, ay2) <= EPS for x, y in ends_b)):
                    bad.append(("T-TOUCH", runs[i], runs[j]))
    return bad


def main():
    seen, fail = set(), 0
    for line in open(sys.argv[1]):
        rec = json.loads(line)
        name = rec["scope"]
        if name in seen:
            continue
        seen.add(name)
        runs = merge_runs(rec["segs"])
        bad = violations(runs)
        diag = rec.get("kept_diagonals", 0)
        status = "ok" if not bad else f"{len(bad)} VIOLATIONS"
        extra = f", {diag} kept diagonal(s)" if diag else ""
        print(f"{name}: {status}{extra}")
        for kind, a, b in bad[:10]:
            print(f"    {kind}: {a[1:]} vs {b[1:]}")
        fail += len(bad)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
