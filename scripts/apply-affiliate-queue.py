#!/usr/bin/env python3
"""
Apply marketing/affiliate-link-queue.md → Ingredients/json/{slug}.json.

For every "## {slug}" section in the queue file with all four fields
(url, name, qty, price) filled in, this updates that ingredient's
affiliateLinks. Sections with any blank field are skipped.

Usage:
  python3 scripts/apply-affiliate-queue.py
  python3 scripts/apply-affiliate-queue.py --dry-run
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
QUEUE = ROOT / "marketing" / "affiliate-link-queue.md"
JSON_DIR = ROOT / "Ingredients" / "json"

DRY_RUN = "--dry-run" in sys.argv

if not QUEUE.exists():
    print(f"Queue file not found: {QUEUE}")
    sys.exit(1)

text = QUEUE.read_text(encoding="utf-8")

# Split on each "## slug" header; process each chunk independently so
# the field-block regex can't cross section boundaries.
HEADER = re.compile(r"^## ([a-z0-9-]+)\s*$", re.MULTILINE)
BLOCK = re.compile(
    r"```\s*\n"
    r"url:\s*(.*?)\n"
    r"name:\s*(.*?)\n"
    r"qty:\s*(.*?)\n"
    r"price:\s*(.*?)\n"
    r"```",
    re.DOTALL,
)

# Slice the file into per-slug sections
matches = list(HEADER.finditer(text))
sections = []
for i, m in enumerate(matches):
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    sections.append((m.group(1), text[m.end():end]))

updates = 0
skips = 0
errors = []

for slug, body in sections:
    block = BLOCK.search(body)
    if not block:
        continue
    url, name, qty, price = (s.strip() for s in block.groups())

    # Skip sections where any field is blank
    if not all([url, name, qty, price]):
        skips += 1
        continue

    json_path = JSON_DIR / f"{slug}.json"
    if not json_path.exists():
        errors.append(f"{slug}: no JSON file at {json_path}")
        continue

    data = json.loads(json_path.read_text(encoding="utf-8"))
    new_link = {
        "retailer": "amazon",
        "url": url,
        "productName": name,
        "quantity": qty,
        "price": price,
    }

    existing = data.get("affiliateLinks") or []
    # If a link with the same URL already exists, leave the file alone.
    if any(l.get("url") == url for l in existing):
        skips += 1
        continue

    data["affiliateLinks"] = existing + [new_link]

    if DRY_RUN:
        print(f"[dry-run] would update {slug}: {name} ({qty}, {price})")
    else:
        json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"updated {slug}: {name} ({qty}, {price})")
    updates += 1

print()
print(f"{updates} updated, {skips} skipped (blank or already linked)")
if errors:
    print(f"\n{len(errors)} errors:")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)
