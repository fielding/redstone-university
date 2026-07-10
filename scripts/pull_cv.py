#!/usr/bin/env python3
"""
Pull the CircuitVerse project straight from circuitverse.org, replacing the
local .cv export — no manual "Export as file" round-trip.

    python3 scripts/pull_cv.py <project id or URL>          # public project
    python3 scripts/pull_cv.py <id> --token $CV_API_TOKEN   # private project
    python3 scripts/pull_cv.py --login you@example.com      # print a token

The project id can also live in renders/diagrams.json under
`_defaults.cv_project`, so a bare `python3 scripts/pull_cv.py` works.

Uses GET /api/v1/projects/:id/circuit_data — the same JSON the simulator
saves, which is what the .cv export contains. The previous file is kept as
<target>.bak and the write is atomic, so a failed pull can't eat the export.
"""
import argparse
import getpass
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request

BASE = "https://circuitverse.org"
DEFAULT_TARGET = os.path.expanduser("~/Downloads/Redstone University.cv")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_id(arg):
    if arg is None:
        try:
            with open(os.path.join(REPO, "renders/diagrams.json")) as f:
                pid = json.load(f).get("_defaults", {}).get("cv_project")
            if pid:
                return str(pid)
        except OSError:
            pass
        sys.exit("no project given — pass an id/URL or set _defaults.cv_project "
                 "in renders/diagrams.json")
    # accept a bare id, a slug, or any project/simulator URL — the API's
    # finder resolves both numeric ids and friendly slugs
    seg = str(arg).rstrip("/").rsplit("/", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", seg):
        sys.exit(f"can't find a project id in {arg!r}")
    return seg


def login(email):
    password = getpass.getpass(f"CircuitVerse password for {email}: ")
    req = urllib.request.Request(
        f"{BASE}/api/v1/auth/login",
        data=json.dumps({"email": email, "password": password}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        token = json.load(r).get("token")
    if not token:
        sys.exit("login succeeded but no token in the response")
    print(f"export CV_API_TOKEN={token}")


def pull(pid, token, target):
    req = urllib.request.Request(
        f"{BASE}/api/v1/projects/{pid}/circuit_data",
        headers={"Accept": "application/json",
                 **({"Authorization": f"Token {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit(f"HTTP {e.code}: the project is private — get a token with "
                     f"`pull_cv.py --login <email>` and pass --token / set CV_API_TOKEN")
        sys.exit(f"HTTP {e.code} fetching project {pid}: {e.read().decode()[:200]}")

    # the payload sometimes arrives as a JSON string of the data itself
    if isinstance(data, str):
        data = json.loads(data)
    scopes = data.get("scopes")
    if not (isinstance(scopes, list) and scopes and all(s.get("name") for s in scopes)):
        sys.exit("response doesn't look like a project export (no named scopes) — "
                 "left the existing file untouched")

    if os.path.exists(target):
        with open(target) as f:
            try:
                old = json.load(f)
            except json.JSONDecodeError:
                old = None
        if old is not None and json.dumps(old, sort_keys=True) == json.dumps(data, sort_keys=True):
            print(f"unchanged: {target} already matches project {pid} "
                  f"({len(scopes)} scopes)")
            return
        shutil.copy2(target, target + ".bak")

    tmp = target + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, target)
    print(f"pulled project {pid} -> {target} ({len(scopes)} scopes: "
          + ", ".join(s["name"] for s in scopes[:6])
          + (", …" if len(scopes) > 6 else "") + ")")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("project", nargs="?", help="CircuitVerse project id or URL")
    p.add_argument("-o", "--out", default=DEFAULT_TARGET)
    p.add_argument("--token", default=os.environ.get("CV_API_TOKEN"))
    p.add_argument("--login", metavar="EMAIL",
                   help="log in and print a CV_API_TOKEN export line, then exit")
    a = p.parse_args()
    if a.login:
        login(a.login)
        return
    pull(project_id(a.project), a.token, a.out)


if __name__ == "__main__":
    main()
