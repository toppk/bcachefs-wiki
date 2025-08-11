#!/usr/bin/env python3
"""
Generate a News markdown file from merges.json (bcachefs merge feed).

Usage:
  python3 scripts/news_from_merges.py --kernel 6.5 --input merges.json \
      --output content/news/kernel-6.5.md

Behavior:
  - Reads merges.json as produced by scripts/find_bcache_merges.py
  - Filters for the requested kernel base version (e.g., "6.5")
  - Writes a markdown file with front matter and sections per rc bucket
    (rc1, rc2, ...), including each merge subject, date, and a link.

Notes:
  - Front matter keeps title + date only (no slug/url overrides).
  - Date defaults to the latest merge date in that cycle (UTC ISO 8601).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate news from merges.json")
    ap.add_argument("--kernel", help="Kernel base version, e.g. 6.5")
    ap.add_argument("--all", action="store_true", help="Generate for all kernel versions in the feed")
    ap.add_argument("--input", default="merges.json", help="Path to merges.json")
    ap.add_argument("--output", default=None, help="Output markdown path (single kernel only)")
    ap.add_argument("--output-dir", default="content/news", help="Output directory for bulk generation")
    ap.add_argument("--title", default=None, help="Override title")
    ap.add_argument("--date", default=None, help="Override date (YYYY-MM-DD or ISO8601)")
    return ap.parse_args()


def iso_date(s: str | None) -> str:
    if not s:
        return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            d = dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
        else:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        raise SystemExit(f"Invalid --date value '{s}': {e}")


def load_feed(path: Path) -> List[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Failed to read {path}: {e}")


def newest_date(items: List[Dict[str, Any]]) -> str:
    # items are per-rc arrays of merges; flatten and return max date
    dates: List[str] = []
    for rc, merges in items:
        for m in merges:
            dates.append(m.get("date", ""))
    # parse YYYY-MM-DD
    parsed = []
    for d in dates:
        try:
            parsed.append(dt.datetime.strptime(d, "%Y-%m-%d"))
        except Exception:
            pass
    if not parsed:
        return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = max(parsed).replace(tzinfo=dt.timezone.utc)
    return latest.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_markdown(kernel: str, rec: Dict[str, Any], title: str, date_iso: str) -> str:
    # TOML front matter with minimal fields
    lines: List[str] = []
    lines.append("+++")
    lines.append(f"title = \"{title}\"")
    lines.append(f"date = {date_iso}")
    lines.append("+++")
    lines.append("")
    lines.append(f"This post summarizes bcachefs merges that landed in Linux {kernel}.")
    lines.append("")
    # Order rc keys naturally (rc1..rcN, then final)
    def rc_key(k: str) -> tuple[int, str]:
        if k.startswith("rc"):
            try:
                return (int(k[2:]), "")
            except ValueError:
                return (9999, k)
        return (10000, k)

    for rc, merges in sorted(rec["merges"].items(), key=lambda kv: rc_key(kv[0])):
        header = rc.upper() if rc.startswith("rc") else rc
        lines.append(f"## {header}")
        lines.append("")
        def parse_ymd(s: str) -> dt.datetime:
            try:
                return dt.datetime.strptime(s, "%Y-%m-%d")
            except Exception:
                # Put unknown dates at the end while keeping stable order
                return dt.datetime.max

        # Sort merges within each RC by date ascending (earliest first)
        merges_sorted = sorted(merges, key=lambda m: (parse_ymd(m.get("date", "")), m.get("subject", "")))

        # Each merge renders as a markdown bullet with links, plus a collapsible
        # block attached to the list item containing the full commit message.
        for idx, m in enumerate(merges_sorted):
            date = m.get("date", "")
            subj = m.get("subject", "")
            h = m.get("hash", "")
            body = (m.get("full_commit_message") or "").rstrip("\n")
            # Hide the subject line in the details body if it matches the bullet
            if body:
                blines = body.splitlines()
                if blines and blines[0].strip() == subj.strip():
                    blines = blines[1:]
                    # Drop a leading blank line if present after removing subject
                    while blines and not blines[0].strip():
                        blines = blines[1:]
                body = "\n".join(blines)
            url = f"https://git.kernel.org/torvalds/c/{h}" if h else ""
            bullet = f"- **{date}**: {subj}{f' ([commit]({url}))' if url else ''}"
            lines.append(bullet)
            # Expand the first merge only for RC1; others start collapsed
            open_attr = " open" if (rc == "rc1" and idx == 0) else ""
            lines.append(f"  <details{open_attr}>")
            lines.append("  <summary><span class=\"summary-closed-label\">Show pull request</span><span class=\"summary-open-label\">Hide pull request</span></summary>")
            if body:
                lines.append("")
                lines.append("  ```text")
                # Do not include any links here; keep as plain text
                for ln in body.splitlines():
                    lines.append(f"  {ln}")
                lines.append("  ```")
            lines.append("  </details>")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ns = parse_args()
    inp = Path(ns.input)
    data = load_feed(inp)

    if not ns.all and not ns.kernel:
        raise SystemExit("Specify --kernel <ver> or --all")

    if ns.all:
        outdir = Path(ns.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        wrote = 0
        for rec in data:
            kern = rec.get("kernel_version")
            if not kern:
                continue
            t = ns.title or f"Linux {kern}: bcachefs merges"
            d = iso_date(ns.date) if ns.date else newest_date(list(rec["merges"].items()))
            md = build_markdown(kern, rec, t, d)
            outpath = outdir / f"kernel-{kern}.md"
            outpath.write_text(md, encoding="utf-8")
            print(f"Wrote {outpath}")
            wrote += 1
        if wrote == 0:
            raise SystemExit(f"No kernel entries found in {inp}")
    else:
        match = next((x for x in data if x.get("kernel_version") == ns.kernel), None)
        if not match:
            avail = [x.get("kernel_version") for x in data if x.get("kernel_version")]
            raise SystemExit(
                f"Kernel {ns.kernel} not found in {inp}. Available: {', '.join(avail)}"
            )

        # Determine title and date
        title = ns.title or f"Linux {ns.kernel}: bcachefs merges"
        if ns.date:
            date_iso = iso_date(ns.date)
        else:
            # compute from latest merge date in this cycle
            date_iso = newest_date(list(match["merges"].items()))

        # Output path
        outpath = Path(ns.output) if ns.output else Path(ns.output_dir) / f"kernel-{ns.kernel}.md"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        md = build_markdown(ns.kernel, match, title, date_iso)
        outpath.write_text(md, encoding="utf-8")
        print(f"Wrote {outpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
