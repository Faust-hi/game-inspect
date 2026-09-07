"""Reconciliation probes. No connection to the application database."""
import sys, os, json, hashlib
from pathlib import Path
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
sys.dont_write_bytecode = True
os.environ['DATABASE_URL'] = 'sqlite://'
from app.schemas.catalog import ProjectProfile, input_fingerprint
from app.services import hardware, gower, topsis, rules
from app.seed import methods_data
from app.api.admin import _coerce
from app.models.entities import Method

out = {}
p = ProjectProfile()
out['version_changes_fingerprint'] = input_fingerprint(p, [], '1', '1') != input_fingerprint(p, [], '2', '1')
a = ProjectProfile(functions=['dynamic_shadows', 'character_animation'])
b = ProjectProfile(functions=list(reversed(a.functions)))
out['function_order_changes_fingerprint'] = input_fingerprint(a, []) != input_fingerprint(b, [])
out['resolution_factors'] = {x: hardware._resolution_factor(x) for x in ['1080p', '2160p', '4k']}
methods, _ = methods_data.with_sources()
rt = SimpleNamespace(**next(m for m in methods if m['code'] == 'hardware_raytraced_gi'))
base = hardware._load_indices(p, [])
with_rt = hardware._load_indices(p, [rt])
out['rt'] = {k: {'base': base[k], 'with_method': with_rt[k]} for k in ['gpu_index', 'vram_gb', 'required_rt']}
out['fg_without_base_unchanged'] = hardware._load_indices(ProjectProfile(frame_generation=True), [])['gpu_index'] == base['gpu_index']
out['fg_cpu'] = {str(fps): hardware._load_indices(ProjectProfile(target_fps=fps, frame_generation=True, base_render_fps=60), [])['cpu_index'] for fps in [60, 144]}
try:
    _coerce(Method, {'impact_cpu': 'oops'})
    out['bad_number'] = 'accepted'
except ValueError as e:
    out['bad_number'] = str(e)
try:
    hardware._load_indices(ProjectProfile(audio_complexity='unknown'), [])
    out['unknown_audio'] = 'accepted'
except KeyError as e:
    out['unknown_audio'] = repr(e)
out['vega64_mobile'] = hardware._is_mobile_gpu('Radeon RX Vega 64')
out['gower_features'] = gower.FEATURES
out['engine_none'] = gower.canonical_engine(None)
fits = [rules.resource_fit(SimpleNamespace(**m), p) for m in methods]
out['resource_fit_default_profile'] = {'min': min(fits), 'max': max(fits), 'inside_04_06': sum(.4 <= x <= .6 for x in fits), 'total': len(fits)}
criteria = [topsis.Criterion('a', 'A', 'benefit'), topsis.Criterion('b', 'B', 'cost')]
out['topsis_scale'] = [topsis.topsis(matrix, criteria).scores for matrix in [[[1, 2], [3, 4], [2, 1]], [[100, 2], [300, 4], [200, 1]]]]
known = {m['code'] for m in methods}
out['raw_examples'] = {}
for folder in ['', 'track1', 'track2']:
    data_dir = ROOT / 'backend/app/seed/data' / folder
    files = [data_dir / 'game_examples.json'] if not folder else sorted(data_dir.glob('*.json'))
    rows = [r for f in files for r in json.loads(f.read_text(encoding='utf-8'))]
    out['raw_examples'][folder or 'legacy'] = {'rows': len(rows), 'platforms': sorted({x for r in rows for x in r.get('platforms', [])}), 'unknown_method_rows': sum(bool(set(r.get('optimizations_used', [])) - known) for r in rows)}
prior = json.loads((ROOT / 'audit-2026-09-07/evidence.json').read_text(encoding='utf-8'))['source_sha256']
import subprocess, tempfile, sqlite3
with tempfile.TemporaryDirectory(prefix='gameinspect_comparison_') as tmp:
    db_path = Path(tmp) / 'migration.db'
    env = dict(os.environ, DATABASE_URL='sqlite:///' + db_path.as_posix(), PYTHONDONTWRITEBYTECODE='1')
    def alembic(*args):
        run = subprocess.run([sys.executable, '-m', 'alembic', *args], cwd=ROOT / 'backend', env=env, capture_output=True, text=True, errors='replace')
        return {'returncode': run.returncode, 'output': run.stdout + run.stderr}
    upgraded = alembic('upgrade', 'head')
    assert upgraded['returncode'] == 0, upgraded
    clean = alembic('check')
    with sqlite3.connect(db_path) as con:
        con.execute('CREATE TABLE audit_unmapped (id INTEGER PRIMARY KEY)')
    con.close()
    drift = alembic('check')
    out['alembic_ddl_check'] = {'clean': clean, 'same_revision_with_extra_table': drift}
    assert clean['returncode'] == 0 and drift['returncode'] != 0
out['baseline'] = {'checked': len(prior), 'changed': [p for p, h in prior.items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]}
dest = Path(__file__).parent
out['reports'] = {}
for label, name in [('a', 'Текстовый документ (2).txt'), ('b', 'Текстовый документ.txt')]:
    source = ROOT.parent / name
    raw = source.read_bytes()
    (dest / ('audit-' + label + '.txt')).write_bytes(raw)
    out['reports'][label] = {'original': str(source), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
(dest / 'comparison_evidence.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(out, ensure_ascii=False, indent=2))
