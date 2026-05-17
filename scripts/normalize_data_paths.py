#!/usr/bin/env python3
"""
Normalize absolute paths in experimental data files to relative identifiers.

This script scans JSON and text data files in the project and replaces
hardcoded absolute paths (like /home/<USER>/...) with relative paths
that are machine-independent.

Usage:
    python scripts/normalize_data_paths.py [--dry-run]
"""

import json
import os
import re
import sys
import glob
import argparse
from pathlib import Path

# Path prefix patterns to normalize
# Each entry: (regex_pattern, replacement_prefix, dataset_type)
PATH_PATTERNS = [
    # SMTimer dataset paths
    (r'^/home/<USER>/<CLOUD_DISK>/smt/', '', 'smtimer'),
    (r'^/home/yy/Downloads/smt/', '', 'smtimer'),
    (r'^/home/nju/Downloads/smt/', '', 'smtimer'),
    # QF_NIA dataset paths
    (r'^/path/to/Downloads/non-incremental_Hierarchy/non-incremental/QF_NIA/', '', 'qf_nia'),
    (r'^/home/[^/]+/Downloads/non-incremental_Hierarchy/non-incremental/QF_NIA/', '', 'qf_nia'),
    # QF_LIA dataset paths
    (r'^/path/to/Downloads/non-incremental_Hierarchy/non-incremental/QF_LIA/', '', 'qf_lia'),
    (r'^/home/[^/]+/Downloads/non-incremental_Hierarchy/non-incremental/QF_LIA/', '', 'qf_lia'),
    # QF_LRA dataset paths
    (r'^/path/to/Downloads/non-incremental_Hierarchy/non-incremental/QF_LRA/', '', 'qf_lra'),
    (r'^/home/[^/]+/Downloads/non-incremental_Hierarchy/non-incremental/QF_LRA/', '', 'qf_lra'),
    # QF_NRA dataset paths
    (r'^/path/to/Downloads/non-incremental_Hierarchy/non-incremental/QF_NRA/', '', 'qf_nra'),
    (r'^/home/[^/]+/Downloads/non-incremental_Hierarchy/non-incremental/QF_NRA/', '', 'qf_nra'),
    # Generic fallback for other /home/*/Downloads patterns
    (r'^/home/[^/]+/Downloads/smt/', '', 'smtimer'),
]


def normalize_key(key):
    """Normalize a single path key to a relative identifier."""
    for pattern, replacement, dataset in PATH_PATTERNS:
        if re.match(pattern, key):
            relative = re.sub(pattern, replacement, key)
            return relative, dataset
    return key, None


def normalize_json_file(filepath, dry_run=False):
    """Normalize paths in a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False, 0, 'not_json'
    except Exception as e:
        return False, 0, str(e)

    if not isinstance(data, dict):
        return False, 0, 'not_dict'

    modified = False
    count = 0
    new_data = {}

    for key, value in data.items():
        if isinstance(key, str) and ('/home/' in key or '/path/to' in key):
            new_key, dataset = normalize_key(key)
            if new_key != key:
                new_data[new_key] = value
                modified = True
                count += 1
            else:
                new_data[key] = value
        else:
            new_data[key] = value

    if modified:
        if not dry_run:
            # Backup original
            backup_path = filepath + '.bak'
            if not os.path.exists(backup_path):
                os.rename(filepath, backup_path)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
        return True, count, 'ok'

    return False, 0, 'no_changes'


def normalize_text_file(filepath, dry_run=False):
    """Normalize paths in text files that contain one path per line."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, 0, str(e)

    modified = False
    count = 0
    new_lines = []

    for line in lines:
        original = line
        # Try to find and replace paths in the line
        for pattern, replacement, dataset in PATH_PATTERNS:
            line = re.sub(pattern, replacement, line)
        if line != original:
            modified = True
            count += 1
        new_lines.append(line)

    if modified:
        if not dry_run:
            backup_path = filepath + '.bak'
            if not os.path.exists(backup_path):
                os.rename(filepath, backup_path)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        return True, count, 'ok'

    return False, 0, 'no_changes'


def find_data_files(repo_root):
    """Find all data files that might contain hardcoded paths."""
    patterns = [
        'test_rl/smtimer_experiments/*.json',
        'test_rl/smtimer_experiments/*/*.json',
        'test_rl/smtimer_experiments/*/*.txt',
        'test_rl/qf_nia_experiments/*.json',
        'test_rl/qf_nia_experiments/*/*.json',
        'test_rl/qf_nia_experiments/*/*.txt',
        'test_rl/test_script/*.json',
        'test_rl/test_script/*.txt',
        'test_rl/test_solve/*.json',
        'test_rl/test_solve/*.txt',
    ]

    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(repo_root, pattern)))

    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser(description='Normalize absolute paths in data files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--repo-root', default='.', help='Repository root directory')
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    files = find_data_files(repo_root)

    print(f"Found {len(files)} potential data files")
    print("-" * 60)

    total_modified = 0
    total_keys = 0

    for filepath in files:
        basename = os.path.basename(filepath)

        # Skip external reference placeholders and backup files
        if basename.endswith('.bak') or 'info_dict_rl' in filepath:
            continue

        # Skip empty files
        if os.path.getsize(filepath) == 0:
            continue

        # Try JSON first
        modified, count, status = normalize_json_file(filepath, dry_run=args.dry_run)

        if status == 'not_json':
            # Try as text file
            modified, count, status = normalize_text_file(filepath, dry_run=args.dry_run)

        if modified:
            action = 'WOULD MODIFY' if args.dry_run else 'MODIFIED'
            print(f"{action}: {os.path.relpath(filepath, repo_root)} ({count} paths)")
            total_modified += 1
            total_keys += count
        elif status not in ('no_changes', 'not_dict'):
            print(f"ERROR: {os.path.relpath(filepath, repo_root)} - {status}")

    print("-" * 60)
    print(f"Total files {'that would be' if args.dry_run else ''} modified: {total_modified}")
    print(f"Total paths {'that would be' if args.dry_run else ''} normalized: {total_keys}")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")
        print("Original files will be backed up with .bak extension.")


if __name__ == '__main__':
    main()
