#!/usr/bin/env python3

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


TEXT_EXTS = {
    ".py",
    ".md",
    ".tex",
    ".bib",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".sh",
    ".ini",
    ".cfg",
    ".xml",
    ".csv",
}

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    ".idea",
    "node_modules",
    "build",
    "dist",
    "paper/build",
    "paper/_minted-main",
    "paper/build/_minted-main",
    "archived/development_files/venv",
}


@dataclass(frozen=True)
class ReplacementRule:
    name: str
    pattern: re.Pattern
    replacement: str


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


def build_rules() -> List[ReplacementRule]:
    # Deterministic replacements. Order matters.
    fixed_rules: List[Tuple[str, str, str]] = [
        ("institution_nanjing_university", r"Anonymous Institution", "Anonymous Institution"),
        ("author_hongyu_chen", r"Anonymous Author", "Anonymous Author"),
        ("github_user_lz1159435992", r"https://github.com/<ANON_USER>", "https://github.com/<ANON_USER>"),
        ("github_user_prefix_lz", r"github.com/<ANON_USER>", "github.com/<ANON_USER>"),
        ("home_user_lz", r"/home/[^/]+", "/home/<USER>"),
        ("<CLOUD_DISK>_path", r"<CLOUD_DISK>", "<CLOUD_DISK>"),
        ("absolute_downloads", r"/path/to/Downloads", "/path/to/Downloads"),
    ]

    rules: List[ReplacementRule] = []
    for name, pat, repl in fixed_rules:
        rules.append(ReplacementRule(name=name, pattern=re.compile(pat), replacement=repl))
    return rules


def iter_target_files(repo_root: Path, include_exts: Sequence[str]) -> Iterable[Path]:
    for p in repo_root.rglob("*"):
        if not p.is_file():
            continue

        rel = p.relative_to(repo_root).as_posix()

        # Exclude directories by prefix match
        for ex in DEFAULT_EXCLUDE_DIRS:
            ex_norm = ex.strip("/")
            if rel == ex_norm or rel.startswith(ex_norm + "/"):
                break
        else:
            if p.suffix.lower() in include_exts or p.name == "Makefile":
                yield p


def apply_replacements(text: str, rules: Sequence[ReplacementRule]) -> Tuple[str, Dict[str, int]]:
    counts: Dict[str, int] = {}
    out = text
    for r in rules:
        out2, n = r.pattern.subn(r.replacement, out)
        if n:
            counts[r.name] = counts.get(r.name, 0) + n
        out = out2
    return out, counts


def is_probably_binary(path: Path) -> bool:
    try:
        data = path.read_bytes()[:2048]
    except Exception:
        return True
    if b"\x00" in data:
        return True
    nontext = sum(1 for b in data if b < 9 or (b > 13 and b < 32))
    return nontext > 200


def validate_key_alignment(repo_root: Path) -> Dict[str, object]:
    """Best-effort: check key uniqueness after anonymization in sampled JSONs."""

    sample_paths = [
        repo_root / "test_rl/smtimer_experiments/z3_smtimer_results.json",
        repo_root / "test_rl/smtimer_experiments/cvc5_smtimer_results.json",
        repo_root / "test_rl/qf_nia_experiments/cvc5_QF_NIA.json",
    ]

    report: Dict[str, object] = {"checked": [], "issues": []}
    rules = build_rules()

    for p in sample_paths:
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            report["issues"].append({"file": p.as_posix(), "error": f"parse failed: {e}"})
            continue
        if not isinstance(data, dict):
            continue

        new_keys = []
        for k in data.keys():
            kk, _ = apply_replacements(str(k), rules)
            new_keys.append(kk)

        report["checked"].append({
            "file": p.as_posix(),
            "key_count": len(new_keys),
            "unique_keys": len(set(new_keys)),
        })

        if len(set(new_keys)) != len(new_keys):
            report["issues"].append({
                "file": p.as_posix(),
                "collision_count": len(new_keys) - len(set(new_keys)),
                "hint": "Key collisions detected after anonymization; mapping rules may be too coarse.",
            })

    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Anonymize repo text files for double-blind review")
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent), help="Repo root")
    ap.add_argument("--dry-run", action="store_true", help="Report changes but do not write")
    ap.add_argument("--in-place", action="store_true", help="Write changes to files")
    ap.add_argument("--report", default="anonymize_report.json", help="Path to write JSON report")
    ap.add_argument("--validate", action="store_true", help="Run basic validation")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        raise SystemExit(f"Repo root not found: {repo_root}")

    if args.in_place and args.dry_run:
        raise SystemExit("Choose only one of --dry-run or --in-place")
    if not args.in_place and not args.dry_run:
        args.dry_run = True

    rules = build_rules()

    changed_files: List[Dict[str, object]] = []
    totals: Dict[str, int] = {}

    for path in iter_target_files(repo_root, sorted(TEXT_EXTS)):
        if is_probably_binary(path):
            continue

        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                raw = path.read_text(encoding="latin-1")
            except Exception:
                continue
        except Exception:
            continue

        new, counts = apply_replacements(raw, rules)
        if not counts:
            continue

        rel = path.relative_to(repo_root).as_posix()
        changed_files.append({
            "file": rel,
            "replacements": counts,
            "before_sha1": _sha1(raw),
            "after_sha1": _sha1(new),
        })

        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v

        if args.in_place:
            path.write_text(new, encoding="utf-8")

    report: Dict[str, object] = {
        "repo_root": repo_root.as_posix(),
        "mode": "in-place" if args.in_place else "dry-run",
        "totals": totals,
        "changed_file_count": len(changed_files),
        "changed_files": changed_files[:2000],
        "truncated": len(changed_files) > 2000,
    }

    if args.validate:
        report["validation"] = validate_key_alignment(repo_root)

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = repo_root / report_path
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Mode: {report['mode']}")
    print(f"Changed files: {report['changed_file_count']}")
    print("Totals:")
    for k in sorted(totals.keys()):
        print(f"  {k}: {totals[k]}")
    print(f"Report written to: {report_path}")

    if args.validate:
        issues = report.get("validation", {}).get("issues", [])
        if issues:
            print("Validation issues:")
            for it in issues[:20]:
                print(f"  - {it}")
        else:
            print("Validation: no issues detected in sampled files")


if __name__ == "__main__":
    main()
