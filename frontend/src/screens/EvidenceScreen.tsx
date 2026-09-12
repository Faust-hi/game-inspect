/** Реестр источников и технологических зависимостей. */
import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { Badge, Callout, Card, Loading, Metric, SourceLink, Tabs } from '../components/ui';
import type { Dependency, EvidenceClaim, EvidenceSource, EvidenceSummary } from '../types';

type EvidenceTab = 'claims' | 'dependencies' | 'sources';

/** Предел числа строк утверждений в таблице: реестр целиком в DOM не помещается. */
const CLAIM_ROW_LIMIT = 120;

const TABS = [
  { key: 'claims', label: 'Claims' },
  { key: 'dependencies', label: 'Зависимости' },
  { key: 'sources', label: 'Источники' },
];

function basisTone(basis: string): 'ok' | 'info' | 'warn' | 'danger' | 'neutral' {
  if (basis === 'documented' || basis === 'measured') return 'ok';
  if (basis === 'derived') return 'info';
  if (basis === 'expert_estimate' || basis === 'unknown') return 'warn';
  return 'neutral';
}

function EvidenceSummaryCard({ summary }: { summary: EvidenceSummary }) {
  return (
    <Card
      title="Состояние доказательной базы"
      hint="Источник подтверждает механизм только вместе с локатором; экспертные числовые оценки не выдаются за измерения."
    >
      <div className="stat-grid">
        <Metric label="Источников" value={summary.source_count} />
        <Metric label="Claims" value={summary.claim_count} />
        <Metric label="Claims с источником" value={summary.claims_with_sources} hint={summary.coverage_label} />
        <Metric label="Числовых опубликовано" value={summary.numeric_claims_published} />
        <Metric label="Числовых неизвестно" value={summary.numeric_claims_unknown} />
      </div>
      <p className="xsmall faint" style={{ marginBottom: 0 }}>
        Калибровка runtime: {summary.calibration_status === 'not_calibrated' ? 'не выполнена' : summary.calibration_status}.
        {' '}Наличие URL не означает измеренный FPS, latency или объём памяти.
      </p>
      {summary.unconfirmed_numeric_factors.length > 0 && (
        <details style={{ marginTop: 10 }}>
          <summary className="small">Факторы, требующие ручной проверки ({summary.unconfirmed_numeric_factors.length})</summary>
          <ul className="reason-list">
            {summary.unconfirmed_numeric_factors.slice(0, 24).map(item => <li key={item}>{item}</li>)}
          </ul>
        </details>
      )}
    </Card>
  );
}

function ClaimRow({ item }: { item: EvidenceClaim }) {
  return (
    <tr>
      <td className="small"><strong>{item.entity_code}</strong><div className="xsmall faint">{item.field}</div></td>
      <td className="small">{item.claim}<div className="xsmall faint">{item.context}</div></td>
      <td className="small"><Badge tone={basisTone(item.basis)}>{item.basis}</Badge><div className="xsmall faint">{item.verification_status}</div></td>
      <td className="small">
        {item.value_num != null ? <span className="mono">{item.value_num} {item.unit}</span> : item.value_text || '—'}
        {item.range_min != null && <div className="mono xsmall">{item.range_min}–{item.range_max} {item.unit}</div>}
      </td>
      <td className="small">
        {item.source ? <SourceLink url={item.source.url} title={item.source.title} /> : <span className="faint">нет источника</span>}
        <div className="xsmall faint">{item.locator || 'локатор не указан'}</div>
      </td>
    </tr>
  );
}

function DependencyRow({ item }: { item: Dependency }) {
  return (
    <tr>
      <td className="small"><strong>{item.source_name}</strong><div className="xsmall faint">{item.source_type}</div></td>
      <td className="small">{item.target_name}<div className="xsmall faint">{item.target_type}</div></td>
      <td className="small"><Badge tone={item.mandatory ? 'danger' : 'warn'}>{item.mandatory ? 'обязательная' : 'условная'}</Badge><div className="xsmall faint">{item.dependency_type}</div></td>
      <td className="small">{item.platform || '—'}<div className="xsmall faint">{item.scope}{item.min_version ? ` · от ${item.min_version}` : ''}</div></td>
      <td className="small">{item.description}<div className="xsmall faint" style={{ marginTop: 3 }}>Обход: {item.workaround || 'не указан'}</div></td>
    </tr>
  );
}

function SourceRow({ item }: { item: EvidenceSource }) {
  return (
    <tr>
      <td className="small"><strong>{item.title}</strong><div className="xsmall faint">{item.code}</div></td>
      <td className="small">{item.authors || item.publisher || '—'}<div className="xsmall faint">{item.publisher}{item.publisher && item.source_type ? ' · ' : ''}{item.source_type}</div></td>
      <td className="small">{item.published_date || '—'}<div className="xsmall faint">проверен {item.checked_at || '—'}</div></td>
      <td className="small">{item.platform || '—'}<div className="xsmall faint">{item.locator}</div></td>
      <td className="small"><SourceLink url={item.url} title="Открыть источник" /></td>
    </tr>
  );
}

export function EvidenceScreen() {
  const [tab, setTab] = useState<EvidenceTab>('claims');
  const [summary, setSummary] = useState<EvidenceSummary | null>(null);
  const [sources, setSources] = useState<EvidenceSource[]>([]);
  const [claims, setClaims] = useState<EvidenceClaim[]>([]);
  const [dependencies, setDependencies] = useState<Dependency[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    void Promise.all([api.evidenceSummary(), api.sources(), api.evidence(), api.dependencies()])
      .then(([nextSummary, nextSources, nextClaims, nextDependencies]) => {
        if (!active) return;
        setSummary(nextSummary);
        setSources(nextSources);
        setClaims(nextClaims);
        setDependencies(nextDependencies);
      })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Не удалось загрузить доказательную базу');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const normalizedQuery = query.trim().toLowerCase();
  const visibleClaims = useMemo(() => claims.filter(item => !normalizedQuery ||
    `${item.entity_code} ${item.field} ${item.claim} ${item.context}`.toLowerCase().includes(normalizedQuery)), [claims, normalizedQuery]);
  const visibleDependencies = useMemo(() => dependencies.filter(item => !normalizedQuery ||
    `${item.source_name} ${item.target_name} ${item.description} ${item.platform}`.toLowerCase().includes(normalizedQuery)), [dependencies, normalizedQuery]);
  const visibleSources = useMemo(() => sources.filter(item => !normalizedQuery ||
    `${item.title} ${item.publisher} ${item.source_type} ${item.code}`.toLowerCase().includes(normalizedQuery)), [sources, normalizedQuery]);

  if (loading) return <Loading text="Загрузка источников и зависимостей…" />;
  if (error) return <Callout tone="danger" title="Доказательная база недоступна">{error}</Callout>;

  return (
    <>
      {summary && <EvidenceSummaryCard summary={summary} />}
      <Card
        title="Доказательства и переносимость"
        hint="Источник подтверждает механизм только вместе с локатором; экспертные числовые оценки не выдаются за измерения."
        actions={<input className="input" style={{ minWidth: 220 }} value={query} onChange={event => setQuery(event.target.value)} placeholder="Поиск по реестру" />}
      >
        <Tabs tabs={TABS} active={tab} onChange={value => setTab(value as EvidenceTab)} />
        {tab === 'claims' && (
          <div style={{ overflowX: 'auto' }}>
            {/* Реестр не помещается в DOM целиком; об усечении нужно сообщать,
                иначе неполный список читается как полный (как в других вкладках). */}
            {visibleClaims.length > CLAIM_ROW_LIMIT && (
              <p className="small faint">
                Показаны первые {CLAIM_ROW_LIMIT} из {visibleClaims.length} утверждений.
                Уточните поиск, чтобы увидеть остальные.
              </p>
            )}
            <table className="table"><thead><tr><th>Сущность</th><th>Утверждение</th><th>Основание</th><th>Значение</th><th>Источник и локатор</th></tr></thead><tbody>{visibleClaims.slice(0, CLAIM_ROW_LIMIT).map(item => <ClaimRow key={item.code} item={item} />)}</tbody></table>
          </div>
        )}
        {tab === 'dependencies' && (
          <div style={{ overflowX: 'auto' }}>
            <table className="table"><thead><tr><th>Источник</th><th>Цель</th><th>Тип</th><th>Область</th><th>Пояснение</th></tr></thead><tbody>{visibleDependencies.map(item => <DependencyRow key={item.code} item={item} />)}</tbody></table>
          </div>
        )}
        {tab === 'sources' && (
          <div style={{ overflowX: 'auto' }}>
            <table className="table"><thead><tr><th>Источник</th><th>Издатель / тип</th><th>Дата</th><th>Применимость</th><th>Ссылка</th></tr></thead><tbody>{visibleSources.map(item => <SourceRow key={item.code} item={item} />)}</tbody></table>
          </div>
        )}
      </Card>
    </>
  );
}
