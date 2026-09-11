/**
 * Экран «Зависимости и конфликты».
 *
 * Показывает технологический граф и связи между методами, а также результаты
 * проверок графа. Главное правило экрана: отсутствие ребра или находки не
 * означает совместимость. Непроверенные сочетания выводятся отдельным списком,
 * а неизвестная связь никогда не подписывается как «совместимо».
 */
import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading, Metric, SourceLink, Tabs } from '../components/ui';
import { EvidenceBadge } from '../components/Evidence';
import type { Conflict, Dependency, GraphChecks } from '../types';

type TabKey = 'checks' | 'graph' | 'relations';

const TABS = [
  { key: 'checks', label: 'Проверки графа' },
  { key: 'graph', label: 'Технологический граф' },
  { key: 'relations', label: 'Связи методов' },
];

const RELATION_LABEL: Record<string, string> = {
  hard_conflict: 'жёсткая несовместимость',
  risk: 'условный риск',
  alternative: 'альтернатива',
  dependency: 'обязательная зависимость',
  complement: 'дополнение',
  overlap: 'перекрытие',
  unknown: 'не проверено',
};

const RELATION_TONE: Record<string, 'danger' | 'warn' | 'info' | 'neutral' | 'ok'> = {
  hard_conflict: 'danger',
  dependency: 'warn',
  risk: 'warn',
  alternative: 'info',
  complement: 'ok',
  overlap: 'info',
  unknown: 'warn',
};

const CHECK_LABEL: Record<string, string> = {
  missing_node: 'отсутствующий узел',
  cyclic_mandatory: 'циклическая обязательная зависимость',
  unsupported_version: 'зависимость от неподдерживаемой версии',
  version_unknown: 'версия не указана',
  api_incompatibility: 'несовместимость с выбранным API',
  basket_hard_conflict: 'жёсткий конфликт в корзине',
  unresolved_dependency: 'незакрытая транзитивная зависимость',
  unknown_relation: 'непроверенная связь',
  user_defined_tool: 'пользовательский инструмент',
};

const SEVERITY_TONE: Record<string, 'danger' | 'warn' | 'info'> = {
  error: 'danger',
  warning: 'warn',
  info: 'info',
};

const SEVERITY_LABEL: Record<string, string> = {
  error: 'ошибка',
  warning: 'предупреждение',
  info: 'к сведению',
};

function ChecksPanel({ checks }: { checks: GraphChecks }) {
  const grouped = useMemo(() => {
    const map = new Map<string, typeof checks.issues>();
    checks.issues.forEach((issue) => {
      const list = map.get(issue.check) ?? [];
      list.push(issue);
      map.set(issue.check, list);
    });
    return Array.from(map.entries());
  }, [checks]);

  return (
    <>
      <div className="stat-grid">
        <Metric label="Узлов графа" value={checks.counts.nodes ?? 0} />
        <Metric label="Рёбер" value={checks.counts.edges ?? 0} />
        <Metric label="Обязательных рёбер" value={checks.counts.mandatory_edges ?? 0} />
        <Metric label="Ошибок" value={checks.counts.severity_error ?? 0} />
        <Metric label="Предупреждений" value={checks.counts.severity_warning ?? 0} />
      </div>

      {grouped.length === 0 ? (
        <Callout tone="ok" title="Нарушений не найдено">
          Ошибок и предупреждений нет. Это не доказывает совместимость всех сочетаний:
          непроверенные связи перечисляются отдельным статусом «к сведению».
        </Callout>
      ) : (
        grouped.map(([check, issues]) => (
          <div key={check} className="subtle-box" style={{ marginTop: 10 }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
              <strong className="small">{CHECK_LABEL[check] ?? check}</strong>
              <Badge tone="neutral">{issues.length}</Badge>
              <Badge tone={SEVERITY_TONE[issues[0].severity] ?? 'info'}>
                {SEVERITY_LABEL[issues[0].severity] ?? issues[0].severity}
              </Badge>
            </div>
            <ul className="reason-list">
              {issues.slice(0, 25).map((issue, index) => (
                <li key={`${check}-${index}`}>{issue.message}</li>
              ))}
            </ul>
            {issues.length > 25 && (
              <div className="xsmall faint">Показаны первые 25 из {issues.length}.</div>
            )}
          </div>
        ))
      )}
    </>
  );
}

function GraphPanel({ dependencies }: { dependencies: Dependency[] }) {
  const [type, setType] = useState('');
  const [mandatoryOnly, setMandatoryOnly] = useState(false);

  const types = useMemo(
    () => Array.from(new Set(dependencies.map(d => d.dependency_type))).sort(),
    [dependencies],
  );

  const visible = useMemo(
    () => dependencies.filter(d =>
      (!type || d.dependency_type === type) && (!mandatoryOnly || d.mandatory)),
    [dependencies, type, mandatoryOnly],
  );

  return (
    <>
      <div className="filter-row">
        <select className="select" value={type} onChange={e => setType(e.target.value)}>
          <option value="">Все типы зависимостей</option>
          {types.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <label className="small" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <input type="checkbox" checked={mandatoryOnly} onChange={e => setMandatoryOnly(e.target.checked)} />
          только обязательные
        </label>
        <span className="xsmall faint">Показано {visible.length} из {dependencies.length}</span>
      </div>

      {visible.length === 0 ? <Empty>Связей с такими условиями нет.</Empty> : visible.map(item => (
        <div key={item.code} className="graph-edge">
          <div className="graph-node">
            <div>{item.source_name}</div>
            <div className="graph-node-type">{item.source_type}</div>
          </div>
          <div className="graph-edge-arrow">→</div>
          <div className="graph-node">
            <div>{item.target_name}</div>
            <div className="graph-node-type">{item.target_type}</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3, alignItems: 'flex-start' }}>
            <Badge tone={item.mandatory ? 'danger' : 'info'}>
              {item.mandatory ? 'обязательная' : 'условная'}
            </Badge>
            <span className="xsmall faint">{item.dependency_type}</span>
            {item.min_version && <span className="xsmall faint">от {item.min_version}</span>}
            {item.platform && <span className="xsmall faint">{item.platform}</span>}
          </div>
          <div className="small" style={{ gridColumn: '1 / -1' }}>
            {item.description}
            {item.workaround && (
              <div className="xsmall faint" style={{ marginTop: 3 }}>
                Обход: {item.workaround}{' '}
                {item.basis && <EvidenceBadge basis={item.basis} />}
              </div>
            )}
            <div className="xsmall faint" style={{ marginTop: 3 }}>
              {item.source
                ? <>Источник: <SourceLink url={item.source.url} title={item.source.title} /> · {item.source.locator || 'локатор не указан'}</>
                : 'Публичный источник отсутствует — связь является экспертным суждением каталога.'}
            </div>
          </div>
        </div>
      ))}
    </>
  );
}

function RelationsPanel({ conflicts }: { conflicts: Conflict[] }) {
  const [type, setType] = useState('');
  const types = useMemo(
    () => Array.from(new Set(conflicts.map(c => c.conflict_type))).sort(),
    [conflicts],
  );
  const visible = useMemo(
    () => conflicts.filter(c => !type || c.conflict_type === type),
    [conflicts, type],
  );

  return (
    <>
      <div className="filter-row">
        <select className="select" value={type} onChange={e => setType(e.target.value)}>
          <option value="">Все типы связей</option>
          {types.map(t => (
            <option key={t} value={t}>{RELATION_LABEL[t] ?? t}</option>
          ))}
        </select>
        <span className="xsmall faint">Показано {visible.length} из {conflicts.length}</span>
      </div>

      <div className="graph-legend">
        {types.map(t => (
          <Badge key={t} tone={RELATION_TONE[t] ?? 'neutral'}>
            {RELATION_LABEL[t] ?? t}: {conflicts.filter(c => c.conflict_type === t).length}
          </Badge>
        ))}
      </div>

      {visible.length === 0 ? <Empty>Связей с такими условиями нет.</Empty> : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Метод A</th>
                <th>Метод B</th>
                <th>Тип</th>
                <th>Пояснение</th>
              </tr>
            </thead>
            <tbody>
              {visible.map(item => (
                <tr key={`${item.a_code}-${item.b_code}-${item.conflict_type}`}>
                  <td className="small mono">{item.a_code}</td>
                  <td className="small mono">{item.b_code}</td>
                  <td className="small">
                    <Badge tone={RELATION_TONE[item.conflict_type] ?? 'neutral'}>
                      {RELATION_LABEL[item.conflict_type] ?? item.conflict_type}
                    </Badge>
                    <div className="xsmall faint">критичность {item.severity}</div>
                  </td>
                  <td className="small">
                    {item.description}
                    {item.resolution && (
                      <div className="xsmall" style={{ marginTop: 3 }}>
                        <strong>Что делать:</strong> {item.resolution}{' '}
                        {item.basis && <EvidenceBadge basis={item.basis} />}
                      </div>
                    )}
                    {item.conflict_type === 'unknown' && (
                      <div className="xsmall faint" style={{ marginTop: 3 }}>
                        Связь не проверена: отсутствие запрета не означает совместимость.
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export function DependenciesScreen() {
  const { profile, basket, result } = useStore();
  const [tab, setTab] = useState<TabKey>('checks');
  const [dependencies, setDependencies] = useState<Dependency[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [checks, setChecks] = useState<GraphChecks | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    void Promise.all([
      api.dependencies(),
      api.conflicts(),
      api.graphChecks({
        basket,
        engine: profile.engine,
        engineVersion: profile.engine_version ?? undefined,
        renderApi: profile.render_api !== 'auto' ? profile.render_api : undefined,
      }),
    ])
      .then(([nextDependencies, nextConflicts, nextChecks]) => {
        if (!active) return;
        setDependencies(nextDependencies);
        setConflicts(nextConflicts);
        setChecks(nextChecks);
      })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Не удалось загрузить граф зависимостей');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [basket, profile.engine, profile.engine_version, profile.render_api]);

  if (loading) return <Loading text="Загрузка зависимостей и конфликтов…" />;
  if (error) return <Callout tone="danger" title="Граф недоступен">{error}</Callout>;

  const unresolved = result?.basket_dependencies ?? [];

  return (
    <>
      <Card
        title="Зависимости, конфликты и альтернативы"
        hint="Ребро графа — проверяемое утверждение, а не подсказка. Неизвестная связь не считается совместимой, а жёсткий конфликт не попадает в рабочую корзину."
        actions={<EvidenceBadge basis="documented" title="Связи графа опираются на источник с локатором либо помечены как экспертное суждение." />}
      >
        <div className="stat-grid">
          <Metric label="Рёбер графа" value={dependencies.length} />
          <Metric label="Обязательных" value={dependencies.filter(d => d.mandatory).length} />
          <Metric label="Связей методов" value={conflicts.length} />
          <Metric label="Незакрытых в корзине" value={unresolved.length} />
        </div>
        {unresolved.length > 0 && (
          <Callout tone="warn" title="Незакрытые зависимости корзины">
            <ul className="reason-list">
              {unresolved.slice(0, 12).map(item => (
                <li key={`${item.a_code}-${item.b_code}`}>
                  <strong>{item.a_name || item.a_code}</strong> → {item.b_name || item.b_code}: {item.description}
                </li>
              ))}
            </ul>
          </Callout>
        )}
        <Tabs tabs={TABS} active={tab} onChange={key => setTab(key as TabKey)} />
        {tab === 'checks' && checks && <ChecksPanel checks={checks} />}
        {tab === 'graph' && <GraphPanel dependencies={dependencies} />}
        {tab === 'relations' && <RelationsPanel conflicts={conflicts} />}
      </Card>
    </>
  );
}
