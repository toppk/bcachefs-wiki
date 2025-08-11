#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich import print_json
from rich.pretty import pprint

# Match merge subject like:
# "Merge tag 'bcachefs-2024-10-31' of git://evilpiepirate.org/bcachefs"
MERGE_SUBJECT_RE = re.compile(r"^Merge tag '(?P<tag>[^']+)' of (?P<repo>\S+)")

# Kernel tag normalization: v6.12-rc6, v6.12, etc.
KERNEL_TAG_RE = re.compile(r"^v?(?P<base>\d+\.\d+)(?:-(?P<rc>rc\d+))?")


def run(*args, cwd=None, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def ensure_repo(repo_dir: Path, url: str, offline: bool = False):
    if offline:
        return
    if (repo_dir / ".git").is_dir():
        run("git", "fetch", "--all", "--tags", "--prune", cwd=repo_dir)
    else:
        run("git", "clone", "--no-single-branch", url, str(repo_dir))


def kernel_tag_for_commit(repo_dir: Path, commit: str) -> Optional[str]:
    # Prefer describe --contains; fallback to name-rev --tags
    p = run(
        "git",
        "describe",
        "--contains",
        "--match",
        "v[0-9]*",
        commit,
        cwd=repo_dir,
        check=False,
    )
    cand = p.stdout.strip() if p.returncode == 0 else ""
    if not cand:
        p = run(
            "git",
            "name-rev",
            "--name-only",
            "--tags",
            commit,
            cwd=repo_dir,
            check=False,
        )
        cand = p.stdout.strip()
    if not cand:
        return None
    # Use first token and drop suffix (~N, ^M)
    tok = cand.split()[0].split("~", 1)[0].split("^", 1)[0]
    return tok


def split_kernel_tag(tag: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not tag:
        return None, None
    m = KERNEL_TAG_RE.match(tag)
    if not m:
        return None, None
    return m.group("base"), (m.group("rc") or None)


def parse_subject(subject: str) -> Tuple[Optional[str], Optional[str]]:
    m = MERGE_SUBJECT_RE.match(subject.strip())
    if not m:
        return None, None
    return m.group("tag"), m.group("repo")


def extract_commit_body(repo_dir: Path, commit: str) -> str:
    # True commit message body (%B)
    p = run("git", "show", "-s", "--pretty=format:%B", commit, cwd=repo_dir)
    return p.stdout.rstrip()


def extract_mergetag_messages(repo_dir: Path, commit: str) -> List[Dict[str, str]]:
    """
    Parse embedded 'mergetag' blocks directly from the commit object:
    $ git cat-file -p <commit>
      ...
      mergetag object <sha1>
       type tag
       tag <tagname>
       tagger ...

       <tag message>
       -----BEGIN PGP SIGNATURE-----
       ...
       -----END PGP SIGNATURE-----
      ...
    Returns a list of {tag, message}.
    """
    p = run("git", "cat-file", "-p", commit, cwd=repo_dir)
    lines = p.stdout.splitlines()

    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("mergetag object "):
            i += 1
            continue

        tag_name = None
        msg_lines: List[str] = []

        # Read mergetag header lines: they are indented by one space
        i += 1
        while i < len(lines) and lines[i].startswith(" "):
            hdr = lines[i][1:]
            if hdr.startswith("tag "):  # "tag v6.12-rc6"
                tag_name = hdr[len("tag ") :].strip()
            # Advance through header lines until blank line
            if hdr == "":
                break
            i += 1

        # Now optional blank line (already on it or next)
        # Move to the message body (still space-prefixed)
        if i < len(lines) and lines[i].startswith(" "):
            i += 1

        # Collect message (space-prefixed) until signature or next non-indented header
        while i < len(lines):
            l = lines[i]
            if not l.startswith(" "):
                break  # end of mergetag block
            text = l[1:]
            if text.startswith("-----BEGIN PGP SIGNATURE-----"):
                # Stop before signature block
                break
            msg_lines.append(text)
            i += 1

        blocks.append({"tag": tag_name or "", "message": "\n".join(msg_lines).rstrip()})
        # advance; 'i' now at signature or next header; skip signature block if present
        while i < len(lines) and lines[i].startswith(" "):
            if lines[i][1:].startswith("-----END PGP SIGNATURE-----"):
                i += 1
                break
            i += 1

    return blocks


def find_bcachefs_merges(repo_dir: Path) -> List[Dict[str, Any]]:
    """
    Return all bcachefs merge commits using robust 0x1E/0x1F separators.
    (0x1E = record separator, 0x1F = field separator)
    """
    rec_sep = "\x1e"
    fld_sep = "\x1f"
    fmt = f"{rec_sep}%H{fld_sep}%ad{fld_sep}%s{fld_sep}%B"
    p = run(
        "git",
        "log",
        "--merges",
        "--extended-regexp",
        "--grep",
        r"^Merge tag 'bcachefs-[0-9]{4}-[0-9]{2}-[0-9]{2}' of ",
        "--pretty=format:" + fmt,
        "--date=short",
        cwd=repo_dir,
    )

    rows: List[Dict[str, Any]] = []
    # Each record starts with rec_sep; split and skip the first empty chunk.
    records = [r for r in p.stdout.split(rec_sep) if r]
    for rec in records:
        fields = rec.split(fld_sep)
        # We expect 4 fields: H, ad, s, B — but be defensive
        if len(fields) < 3:
            continue
        h = fields[0]
        date = fields[1]
        subject = fields[2]
        body = fields[3] if len(fields) > 3 else ""
        source_tag, source_repo = parse_subject(subject)
        rows.append(
            {
                "hash": h,
                "date": date,
                "subject": subject,
                "source_tag": source_tag,
                "source_repo": source_repo,
                # %B already includes the subject line followed by the body;
                # don't prepend subject again to avoid duplication.
                "full_commit_message": body.rstrip(),
            }
        )
    return rows


def rc_sort_key(rcname: str) -> Tuple[int, str]:
    if rcname.startswith("rc"):
        try:
            return (int(rcname[2:]), "")
        except ValueError:
            return (9999, rcname)
    return (10000, rcname)  # finals/others last


def main():
    ap = argparse.ArgumentParser(
        description="Find bcachefs merge-tag commits and bucket them by kernel rc."
    )
    ap.add_argument(
        "--url",
        default="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        help="Linux kernel Git URL (torvalds mainline)",
    )
    ap.add_argument("--dir", default="linux", help="Local directory for the repo")
    ap.add_argument(
        "--include-mergetag",
        action="store_true",
        help="Also extract the embedded mergetag message from the merge commit.",
    )
    ap.add_argument(
        "--offline",
        action="store_true",
        help="Do not fetch/clone; use existing local repo only",
    )
    args = ap.parse_args()

    repo_dir = Path(args.dir).resolve()
    ensure_repo(repo_dir, args.url, offline=args.offline)

    commits = find_bcachefs_merges(repo_dir)

    # Enrich with kernel version + rc and mergetag messages
    for r in commits:
        raw_tag = kernel_tag_for_commit(repo_dir, r["hash"])
        base, rc = split_kernel_tag(raw_tag)
        r["kernel_tag_raw"] = raw_tag
        r["kernel_version"] = base  # e.g., "6.12" (no rc suffix)
        r["rc"] = rc or "final"  # bucket key
        if args.include_mergetag:
            mts = extract_mergetag_messages(repo_dir, r["hash"])
            # If multiple mergetags exist (rare), include them all
            if mts:
                r["mergetags"] = mts
                # Prefer the first mergetag message as the “rich” message
                if mts[0].get("message"):
                    r["full_commit_message"] = mts[0]["message"]

    # Group: kernel_version -> { rc1: [merges...], rc2: [...], final: [...] }
    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in commits:
        base = r.get("kernel_version") or "UNKNOWN"
        rc = r.get("rc") or "final"
        item = OrderedDict()
        item["hash"] = r["hash"]
        item["date"] = r["date"]
        item["rc"] = r["rc"]
        item["subject"] = r["subject"]
        item["source_tag"] = r["source_tag"]
        item["source_repo"] = r["source_repo"]
        item["full_commit_message"] = r["full_commit_message"]
        if "mergetags" in r:
            item["mergetags"] = r["mergetags"]
        grouped[base][rc].append(item)

    # Sort rc buckets and print per kernel_version
    def base_key(v: str) -> Tuple[int, int]:
        try:
            major, minor = v.split(".")
            return (int(major), int(minor))
        except Exception:
            return (9999, 9999)

    output_list = []
    for base in sorted(grouped.keys(), key=base_key):
        ordered = OrderedDict()
        for rcname in sorted(grouped[base].keys(), key=rc_sort_key):
            ordered[rcname] = grouped[base][rcname]
        # Convert to JSON for cleaner display
        output_list.append({"kernel_version": base, "merges": ordered})
    print_json(data=output_list)


if __name__ == "__main__":
    main()
