"""Prepare a traceable review queue, not a claim of semantic verification."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare():
    inventory = json.loads((ROOT / 'audit-2026-09-07/batches/inventory.json').read_text(encoding='utf-8'))
    reviews, references = [], []
    for batch in inventory['batches']:
        source = ROOT / batch['file']
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        normalized_digest = hashlib.sha256(source.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        if batch['sha256'] not in (digest, normalized_digest):
            raise ValueError(f"Original changed: {source.name}; rebuild inventory explicitly")
        for section in batch['sections']:
            case_id = f"{source.stem}:{section['line']}"
            # Conservative franchise grouping; no related versions cross splits.
            heading = section['heading'].casefold()
            families = ['portal', 'half-life', 'dark souls', 'sekiro', 'elden ring',
                        'assassin', 'fallout', 'starfield', 'skyrim', 'gta', 'grand theft',
                        'rage', 'doom', 'crysis', 'battlefield', 'metro', 'alan wake',
                        'cyberpunk', 'arma', 'minecraft']
            family = next((name for name in families if name in heading),
                          re.sub(r'^##\s*\d+[.)]\s*', '', heading).split('(')[0].strip())
            if family == 'grand theft':
                family = 'gta'
            slot = int(hashlib.sha256(family.encode()).hexdigest()[:8], 16) % 10
            split = 'train' if slot < 6 else 'validation' if slot < 8 else 'test'
            references.append({
                'case_id': case_id, 'game_group': family, 'split': split,
                'kind': 'ineligible', 'source': f"{batch['file']}:{section['line']}",
                'exclusion_reason': 'Нет нормализованного измерительного сценария и независимой сопоставимой шкалы CPU/GPU. Требования издателя без режима не являются benchmark.',
            })
            for method in section['methods']:
                reviews.append({
                    'row_id': f"{source.stem}:{method['line']}", 'case_id': case_id,
                    'source_file': batch['file'], 'source_line': method['line'],
                    'source_sha256': digest, 'original': method['text'],
                    'code': method['code'], 'candidate_exact_code': method['code'] if method['known_exact'] else None,
                    'classification': 'insufficient_evidence', 'review_status': 'pending_manual_review',
                    'reason': 'Источник для существенных утверждений этой строки отдельно не проверен; совпадение кода не доказывает смысл или численный эффект.',
                    'profile_sources': section['sources'],
                })
    if len(references) != 58 or len(reviews) != 980:
        raise ValueError('Batch cardinality changed; investigate before generating reports')
    out = Path(__file__).resolve().parent
    for name, content in [('review-queue.json', reviews), ('references.json', references),
                          ('baseline.json', []), ('candidate.json', [])]:
        target = out / name
        # Never overwrite manual review, measured references or collected predictions.
        if target.exists():
            raise FileExistsError(f"Preserve existing work: {target}")
        target.write_text(json.dumps(content, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    prepare()
