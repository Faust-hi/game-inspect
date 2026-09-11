/**
 * Экран «Кейсы игр».
 *
 * Кейс подтверждает, что механизм применён в реальном проекте, и показывает
 * инженерный компромисс. Он НЕ переносит производительность: 60 FPS одной игры
 * не означает 60 FPS в другом проекте. Поэтому предел переноса выводится
 * отдельным блоком, а не мелким примечанием.
 */
import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading, Metric, SourceLink } from '../components/ui';
import { ClaimBlocks } from '../components/Evidence';
import type { GameCase } from '../types';

const MATCH_TONE: Record<string, 'ok' | 'info' | 'warn'> = {
  exact: 'ok',
  direct: 'ok',
  partial: 'info',
  analogous: 'warn',
};

const MATCH_LABEL: Record<string, string> = {
  exact: 'точное соответствие',
  direct: 'прямое применение',
  partial: 'частичное соответствие',
  analogous: 'аналогия',
};

function CaseCard({ item, inBasket }: { item: GameCase; inBasket: boolean }) {
  return (
    <div className="method-row">
      <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <strong>{item.title}</strong>
        {item.release_year != null && <span className="xsmall faint">{item.release_year}</span>}
        <Badge tone="neutral">{item.studio || 'студия не указана'}</Badge>
        {inBasket && <Badge tone="ok">связан с корзиной</Badge>}
      </div>

      <div className="xsmall faint" style={{ marginTop: 3 }}>
        {[item.technology, item.engine_code, item.world_type, item.network_mode]
          .filter(Boolean)
          .join(' · ') || 'технология не указана'}
      </div>

      {item.summary && <p className="small muted" style={{ marginTop: 6 }}>{item.summary}</p>}

      <ClaimBlocks
        fact={item.summary || undefined}
        inference={item.relevance || undefined}
        assumption={undefined}
      />

      {item.transfer_limits && (
        <div className="subtle-box" style={{ marginTop: 9 }}>
          <div className="xsmall" style={{ fontWeight: 700 }}>Что нельзя переносить на другой проект</div>
          <div className="small" style={{ marginTop: 3 }}>{item.transfer_limits}</div>
        </div>
      )}

      {item.evidence.map((fact) => (
        <div key={fact.code} className="subtle-box" style={{ marginTop: 9 }}>
          <div className="xsmall" style={{ display: 'flex', gap: 7, flexWrap: 'wrap', alignItems: 'baseline' }}>
            <Badge tone={MATCH_TONE[fact.match_level] ?? 'warn'}>
              {MATCH_LABEL[fact.match_level] ?? fact.match_level}
            </Badge>
            <span>{fact.fact}</span>
          </div>
          <div className="xsmall faint" style={{ marginTop: 5 }}>
            {fact.locator || 'локатор не указан'}
            {fact.source && (
              <>
                {' · '}
                <SourceLink url={fact.source.url} title={fact.source.title} />
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export function CasesScreen() {
  const { result } = useStore();
  const [cases, setCases] = useState<GameCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [engine, setEngine] = useState('');
  const [match, setMatch] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    void api.cases()
      .then((next) => { if (active) setCases(next); })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Не удалось загрузить кейсы');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const inBasket = useMemo(() => new Set(result?.practice_check.case_codes ?? []), [result]);

  const engines = useMemo(
    () => Array.from(new Set(cases.map(c => c.engine_code).filter(Boolean))).sort(),
    [cases],
  );

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return cases.filter((item) => {
      if (engine && item.engine_code !== engine) return false;
      if (match && !item.evidence.some(f => f.match_level === match)) return false;
      if (!q) return true;
      return `${item.title} ${item.studio} ${item.technology} ${item.summary} ${item.relevance}`
        .toLowerCase()
        .includes(q);
    });
  }, [cases, query, engine, match]);

  if (loading) return <Loading text="Загрузка игровых кейсов…" />;
  if (error) return <Callout tone="danger" title="Кейсы недоступны">{error}</Callout>;

  const withLimits = cases.filter(c => c.transfer_limits).length;

  return (
    <>
      <Card
        title="Реальные игровые кейсы"
        hint="Кейс подтверждает факт применения механизма и инженерный компромисс. Он не является паспортом производительности и не переносится на другой проект автоматически."
      >
        <div className="stat-grid">
          <Metric label="Кейсов" value={cases.length} />
          <Metric label="С ограничением переноса" value={withLimits} />
          <Metric label="Связано с корзиной" value={inBasket.size} />
          <Metric label="Показано" value={visible.length} />
        </div>
      </Card>

      <Card title="Выборка">
        <div className="filter-row">
          <input
            className="input"
            style={{ minWidth: 240 }}
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Поиск по названию, студии, технологии"
          />
          <select className="select" value={engine} onChange={e => setEngine(e.target.value)}>
            <option value="">Все движки</option>
            {engines.map(code => <option key={code} value={code}>{code}</option>)}
          </select>
          <select className="select" value={match} onChange={e => setMatch(e.target.value)}>
            <option value="">Любая степень соответствия</option>
            <option value="exact">точное</option>
            <option value="direct">прямое</option>
            <option value="partial">частичное</option>
            <option value="analogous">аналогия</option>
          </select>
        </div>
        {visible.length === 0
          ? <Empty>Подходящих кейсов не найдено.</Empty>
          : visible.map(item => <CaseCard key={item.code} item={item} inBasket={inBasket.has(item.code)} />)}
      </Card>

      <Callout tone="warn" title="Как читать кейсы">
        Кейс не увеличивает и не уменьшает числовые оценки метода. Он подтверждает
        применение, устройство или компромисс, но перенос FPS одной игры на другую
        системой не утверждается.
      </Callout>
    </>
  );
}
