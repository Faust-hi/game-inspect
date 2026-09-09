"""Inventory the user's reference without importing its claims or modifying it."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.seed.methods_data import with_sources
from app.seed.reviewed_methods import EFFECTS, CONFLICTS
from app.seed.verified_corrections import FIELD_CHANGES, SOURCE_CHANGES


def main():
    source = ROOT / 'validation/technical-integration/proven-methods.md'
    text = source.read_text(encoding='utf-8')
    mentions = []
    for line, value in enumerate(text.splitlines(), 1):
        match = re.match(r'(?:## |\- )`([^`]+)` \|', value)
        if match:
            mentions.append((match[1], line))
    catalog, _ = with_sources()
    by_code = {m['code']: m for m in catalog}
    assert len(mentions) == len({code for code, _ in mentions}) == 124
    assert {code for code, _ in mentions} == set(by_code)
    rows = []
    for code, line in mentions:
        row = by_code[code]
        rows.append(dict(code=code, input_line=line, function=row['function_code'],
                         action='added_after_review' if code in EFFECTS else 'existing_no_duplicate',
                         corrected_fields=list(FIELD_CHANGES.get(code, {})), source_replaced=code in SOURCE_CHANGES,
                         source_url=row['source_url'], numerical_effect_verified=False,
                         claims_auto_imported=False))
    report = dict(input_file=str(source.relative_to(ROOT)), input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  reviewed_at='2026-09-09', input_codes=len(rows), existing=119, added=5,
                  added_relations=len(CONFLICTS), rows=rows,
                  scope='Inventory covers every entry. Five additions fact-checked; existing entries are not all independently revalidated. Confidence is not proof.')
    destination = ROOT / 'validation/technical-integration/proven-methods-review.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Inventory: {len(rows)} entries, 119 existing, 5 additions, {len(CONFLICTS)} new relationships; input preserved.')


if __name__ == '__main__':
    main()
