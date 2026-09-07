"""Inventory only; does not seed or connect to the working DB."""
from pathlib import Path
import sys, json, re, hashlib, collections
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'backend'))
from app.seed import methods_data, functions_data
import os
os.environ['DATABASE_URL'] = 'sqlite://'
from app.models.entities import GameExample
from app.api.admin import _coerce
from app.services.publication import enum_problems
methods, _ = methods_data.with_sources()
known = {m['code'] for m in methods}
functions = {f['code'] for f in functions_data.with_sources()}
inventory = []
seed_examples = []
seed_dir = ROOT/'backend/app/seed/data'
for source in [seed_dir/'game_examples.json', *sorted((seed_dir/'track1').glob('*.json')), *sorted((seed_dir/'track2').glob('*.json'))]:
    for row in json.loads(source.read_text(encoding='utf-8')):
        seed_examples.append({'title':row['title'],'file':source.relative_to(ROOT).as_posix(),'status':row.get('status','draft' if source.parent.name=='track2' else 'published')})
for n in range(1, 12):
    p = ROOT / f'партия-{n:02}.md'
    text = p.read_text(encoding='utf-8-sig')
    lines = text.splitlines()
    sections = []
    starts = [(i, l) for i, l in enumerate(lines) if re.match(r'^## \d+[.)]', l)]
    for j, (i, heading) in enumerate(starts):
        end = next((x for x in range(i+1,len(lines)) if lines[x].startswith('## ')),len(lines))
        part = lines[i:end]
        method_rows = []
        in_methods = False
        feature_codes = []
        for k, line in enumerate(part):
            if line.startswith('#'):
                in_methods = 'Инженерные решения' in line
            if in_methods and line.startswith('|'):
                first = line.split('|')[1].strip().strip('`')
                code = re.match(r'^([A-Za-z0-9]+_[A-Za-z0-9_]+)', first)
                if code:
                    c = code.group(1)
                    method_rows.append({'line': i+k+1, 'code': c, 'known_exact': c in known, 'text': line})
            if line.strip() == '### Features' and k+1 < len(part):
                for fl in part[k+1:k+4]:
                    if fl.startswith('- '):
                        feature_codes += re.findall(r'\b[a-z][a-z0-9]+(?:_[a-z0-9]+)+\b', fl)
        sources = []
        for k, line in enumerate(part):
            if line.startswith('### Источник'):
                for z, sl in enumerate(part[k+1:]):
                    if sl.startswith('##'): break
                    if sl.startswith('- '): sources.append({'line': i+k+z+2, 'text':sl})
        title = re.sub(r'^## \d+[.)]\s*','',heading).split(' (')[0]
        exact_examples = [r for r in seed_examples if r['title'].casefold()==title.casefold()]
        sections.append({'heading': heading, 'line': i+1, 'end': end, 'methods': method_rows, 'features': feature_codes, 'unknown_features': sorted(set(feature_codes)-functions), 'sources': sources, 'exact_title_in_seed':exact_examples})
    inventory.append({'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'lines':len(lines), 'sections':sections, 'method_rows':sum(len(s['methods']) for s in sections), 'known_method_rows':sum(m['known_exact'] for s in sections for m in s['methods']), 'url_count':len(re.findall(r'https?://', text))})
prior = json.loads((ROOT/'audit-2026-09-07/evidence.json').read_text(encoding='utf-8'))['source_sha256']
extra_fields = {'title':'Audit only', 'api_versions':['dx12'], 'min_hw':{'gpu':'example'}, 'rec_hw':{}, 'antipiracy':'example', 'loading_profiles':[], 'engine_limits':[], 'mod_support':'example', 'frame_budget':16.67, 'streaming_io':{}}
all_rows = [m for b in inventory for s in b['sections'] for m in s['methods']]
output = {'batches':inventory, 'source_baseline':{'checked':len(prior), 'changed':[p for p,h in prior.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]}, 'stats':{'profiles':sum(len(b['sections']) for b in inventory),'method_rows':len(all_rows),'unique_codes':len({m['code'] for m in all_rows}),'known_rows':sum(m['known_exact'] for m in all_rows),'known_unique':len({m['code'] for m in all_rows if m['known_exact']})}, 'coerce_gameexample_passport':_coerce(GameExample,extra_fields), 'enum_examples':enum_problems({'format':'3D voxel','world_type':'infinite procedural','scale':'infinite','npc_count_level':'very_high','platforms':['PC','macOS']}), 'catalog_impacts':{m['code']:{k:m[k] for k in ['impact_cpu','impact_gpu','impact_ram','impact_vram','impact_disk','impact_network']} for m in methods if m['code'] in ['hierarchical_lod','lightmap_atlas_baking','flow_field_pathing','animation_lod_budget','distance_field_shadows','deterministic_lockstep']}}
(Path(__file__).parent/'inventory.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
coverage = ['# Структурное сопоставление всех 58 профилей','', 'Автоматический точный поиск кодов в таблицах «Инженерные решения». Это не оценка семантического покрытия: разные названия могут описывать уже имеющийся метод, а некоторые строки описывают сюжет/маркетинг. Коды не добавлены в приложение. Все строки и исходные номера сохранены в inventory.json.', '', '| Партия / строка | Профиль | Строк методов | Совпало кодов | Неизвестные коды Features |', '|---|---|---:|---:|---|']
for b in inventory:
    for s in b['sections']:
        coverage.append(f"| {b['file']}:{s['line']} | {s['heading'].removeprefix('## ')} | {len(s['methods'])} | {sum(m['known_exact'] for m in s['methods'])} | {', '.join(s['unknown_features']) or '—'} |")
(Path(__file__).parent/'COVERAGE.md').write_text('\n'.join(coverage)+'\n',encoding='utf-8')
for b in inventory:
    print(b['file'], 'sections',len(b['sections']), 'rows',b['method_rows'],'exact',b['known_method_rows'],'urls',b['url_count'])
    for s in b['sections']: print(s['line'],s['heading'])
