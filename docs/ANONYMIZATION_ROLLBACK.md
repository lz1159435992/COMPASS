# Anonymization Rollback

This repository contains an anonymization script (`scripts/anonymize_repo.py`) that may rewrite many files in-place.

## Rollback Options

### Option A: Reset to a pre-anonymize tag

List tags:

```bash
git tag --list "pre-anonymize-*" | tail
```

Reset to a specific tag (example):

```bash
git reset --hard pre-anonymize-20260403_000218
```

### Option B: Switch to the backup branch

```bash
git switch backup/pre-anonymize
```

### Notes

- If you have local uncommitted changes, commit or stash them before rollback.
- Keep an original copy for full reproducibility if you anonymize paths in cached results.
