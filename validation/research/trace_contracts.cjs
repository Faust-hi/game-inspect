/* Inspect the existing versions module in memory; no app/browser/live storage. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const ts = require(path.join(root, 'frontend/node_modules/typescript'));
const sourcePath = path.join(root, 'frontend/src/versions.ts');
const source = fs.readFileSync(sourcePath, 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 }
}).outputText;
const storage = new Map();
const context = { exports: {}, sessionStorage: {
  getItem: key => storage.get(key) ?? null,
  setItem: (key, value) => storage.set(key, value),
}};
vm.runInNewContext(compiled, context, { filename: 'versions.research.cjs' });
const input = {
  id: 'incomplete', number: 1, basket: [], profile: {},
};
storage.set('gamedev_dss_versions_v1', JSON.stringify([input]));
const loaded = context.exports.loadVersions();
const result = {
  snapshot_id: 'synthetic-snapshot', catalog_revision: 'synthetic-catalog',
  profile: { name: 'synthetic' }, meta: { algorithm_version: 'synthetic-version' },
  recommendations: [], basket_conflicts: [], hardware: null,
  risks: [{ code: 'must-preserve' }], contributions: { marker: 'must-preserve' },
  selected_methods: [{ code: 'method', source_url: 'synthetic-reference' }],
};
const summary = context.exports.summaryOf(result, []);
const evidence = {
  kind: 'deterministic_isolated_module_probe_not_browser_E2E',
  source: 'frontend/src/versions.ts',
  source_sha256: crypto.createHash('sha256').update(source).digest('hex'),
  typescript: ts.version,
  incomplete_record: { input, accepted: loaded.length === 1, loaded },
  summary: { input_keys: Object.keys(result), output: summary,
    absent_keys: ['snapshot_id', 'profile', 'risks', 'contributions', 'selected_methods']
      .filter(key => !(key in summary)) },
};
const output = path.resolve(root, 'validation/research/contracts-2026-09-09.json');
fs.writeFileSync(output, JSON.stringify(evidence, null, 2), { encoding: 'utf8', flag: 'wx' });
console.log(JSON.stringify(evidence, null, 2));
