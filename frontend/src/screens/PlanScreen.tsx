/** Экран 11. Итоговый план проекта. Одновременно является печатной формой отчёта. */
import { useMemo } from 'react';
import { useStore } from '../store';
import {
  Badge,
  Callout,
  Card,
  Empty,
  ImpactGrid,
  Loading,
  Metric,
  SourceLink,
} from '../components/ui';
import type { Method } from '../types';

/** Порядок внедрения: от архитектуры к настройкам. */
const LEVEL_ORDER = ['architecture', 'production', 'algorithm', 'setting'];

const LEVEL_COMMENT: Record<string, string> = {
  architecture: 'Требует закладки на ранней стадии: изменение после наполнения контента дорого.',
  production: 'Связано с производственным процессом: определяет, как создаются ассеты.',
  algorithm: 'Алгоритмическое решение: внедряется без переработки готового контента.',
  setting: 'Настройка: применима на любой стадии, эффект ограничен.',
};

const STAGE_ORDER: Record<string, number> = {
  concept: 0,
  preproduction: 1,
  prototype: 2,
  production: 3,
  alpha: 4,
  beta: 5,
  release: 6,
  post_release: 7,
};

const SEVERITY_LABEL: Record<string, string> = {
  high: 'высокий',
  medium: 'средний',
  low: 'низкий',
};

function impactsOf(method: Method): Record<string, number> {
  return {
    cpu: method.impact_cpu,
    gpu: method.impact_gpu,
    ram: method.impact_ram,
    vram: method.impact_vram,
    disk: method.impact_disk,
    network: method.impact_network,
  };
}

interface Props {
  onExportJson: () => void;
  onExportPdf: () => void;
}

export function PlanScreen({ onExportJson, onExportPdf }: Props) {
  const { profile, basket, result, catalog, calculating } = useStore();

  const methodsByCode = useMemo(() => {
    const map: Record<string, Method> = {};
    for (const method of catalog.methods) map[method.code] = method;
    return map;
  }, [catalog.methods]);

  const selected = useMemo(
    () => basket.map((code) => methodsByCode[code]).filter((m): m is Method => Boolean(m)),
    [basket, methodsByCode],
  );

  const grouped = useMemo(() => {
    const byLevel = new Map<string, Method[]>();
    for (const method of selected) {
      const list = byLevel.get(method.level) ?? [];
      list.push(method);
      byLevel.set(method.level, list);
    }
    return [...byLevel.entries()].sort(
      (a, b) => LEVEL_ORDER.indexOf(a[0]) - LEVEL_ORDER.indexOf(b[0]),
    );
  }, [selected]);

  if (calculating) return <Loading text="Формирование итогового плана…" />;

  if (!result) {
    return <Empty>Расчёт ещё не выполнен. Выполните расчёт на этапе «Варианты реализации».</Empty>;
  }

  const totalCost = selected.reduce((sum, m) => sum + m.implementation_cost, 0);
  const avgGain = selected.length
    ? selected.reduce((sum, m) => sum + m.performance_gain, 0) / selected.length
    : 0;
  const conceptChanging = selected.filter((m) => m.concept_impact < 0);
  const hw = result.hardware;

  return (
    <>
      <Card
        title={`Итоговый план: ${profile.name}`}
        hint={`${profile.format} · ${profile.world_type} · масштаб ${profile.scale} · ${profile.engine} · ${profile.target_resolution} / ${profile.target_quality} / ${profile.target_fps} FPS`}
        actions={
          <div className="btn-row no-print">
            <button className="btn btn-sm" onClick={onExportJson}>
              Скачать JSON
            </button>
            <button className="btn btn-sm btn-primary" onClick={onExportPdf}>
              Сохранить в PDF
            </button>
          </div>
        }
      >
        <div className="xsmall faint">
          Сформирован {new Date().toLocaleDateString('ru-RU')} · стадия проекта:{' '}
          {profile.stage} · приоритет: {profile.priority} · платформы:{' '}
          {profile.platforms.join(', ') || 'не указаны'}
        </div>

        <div className="stat-grid" style={{ marginTop: 14 }}>
          <Metric label="Решений" value={selected.length} />
          <Metric label="Средний эффект" value={`${Math.round(avgGain * 100)}%`} />
          <Metric label="Трудозатраты" value={totalCost} hint="сумма баллов из 5" />
          <Metric label="Рисков" value={result.risks.length} />
        </div>
      </Card>

      {result.risks.length > 0 && (
        <Card
          title="Риски и предупреждения"
          hint="Выявлены до подбора решений: показывают противоречия между стадией проекта, его масштабом и составом функций."
        >
          {result.risks.map((risk) => (
            <div key={risk.code} className="method-row">
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
                <strong>{risk.title}</strong>
                <Badge
                  tone={risk.severity === 'high' ? 'danger' : risk.severity === 'medium' ? 'warn' : 'info'}
                >
                  {SEVERITY_LABEL[risk.severity] ?? risk.severity}
                </Badge>
              </div>
              <p className="small muted" style={{ marginTop: 4 }}>
                {risk.description}
              </p>
              <div className="xsmall faint" style={{ marginTop: 4 }}>
                Что делать: {risk.advice}
              </div>
            </div>
          ))}
        </Card>
      )}

      {conceptChanging.length > 0 && (
        <Callout tone="danger" title="Внимание: решения затрагивают исходную концепцию">
          {conceptChanging.map((m) => m.name).join(', ')}. Эффект достигается за счёт изменения
          игрового замысла — решение требует согласования с дизайн-документом.
        </Callout>
      )}

      <Card
        title="Порядок внедрения"
        hint="Решения сгруппированы по уровню: от архитектурных к настройкам. Внутри группы — по рекомендуемой стадии."
      >
        {selected.length === 0 && (
          <Empty>Корзина пуста. Добавьте решения на этапе «Варианты реализации».</Empty>
        )}

        {grouped.map(([level, methods]) => (
          <div key={level} style={{ marginBottom: 18 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
              <h4>{methods[0]?.level_label ?? level}</h4>
              <Badge tone="neutral">{methods.length}</Badge>
            </div>
            <p className="xsmall faint" style={{ marginBottom: 8 }}>
              {LEVEL_COMMENT[level] ?? ''}
            </p>

            {[...methods]
              .sort(
                (a, b) =>
                  (STAGE_ORDER[a.recommended_stage] ?? 9) - (STAGE_ORDER[b.recommended_stage] ?? 9),
              )
              .map((method) => (
                <div key={method.code} className="method-row">
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
                    <strong>{method.name}</strong>
                    <Badge tone={method.late_cost === 'critical' ? 'danger' : 'neutral'}>
                      позднее внедрение — {method.late_cost_label}
                    </Badge>
                    {method.concept_impact < 0 && <Badge tone="danger">затрагивает концепцию</Badge>}
                    {method.quality_impact < 0 && <Badge tone="warn">снижает качество</Badge>}
                    {method.requires_prototype && <Badge tone="warn">требует прототипа</Badge>}
                  </div>

                  <p className="small muted" style={{ marginTop: 4 }}>
                    {method.summary}
                  </p>

                  <div className="xsmall faint" style={{ marginBottom: 6 }}>
                    Рекомендуемая стадия: {method.recommended_stage_label} · способ расчёта:{' '}
                    {method.calc_mode_label} · эффект {Math.round(method.performance_gain * 100)}% ·
                    трудозатраты {method.implementation_cost} из 5 · сложность {method.complexity} из 5
                  </div>

                  <ImpactGrid impacts={impactsOf(method)} />

                  <div className="xsmall faint" style={{ marginTop: 6 }}>
                    Проверка: {method.verification_method || 'способ проверки не указан'}
                    {method.verification_tools.length > 0
                      ? ` · инструменты: ${method.verification_tools.join(', ')}`
                      : ''}
                  </div>
                </div>
              ))}
          </div>
        ))}
      </Card>

      {(result.basket_conflicts.length > 0 || result.basket_synergies.length > 0) && (
        <Card title="Совместимость набора">
          {result.basket_conflicts.map((item, index) => (
            <div key={`c-${index}`} style={{ marginBottom: 10 }}>
              <Callout tone={item.severity >= 3 ? 'danger' : 'warn'}>
                <strong>
                  {item.a_name} ↔ {item.b_name}
                </strong>{' '}
                <Badge tone={item.severity >= 3 ? 'danger' : 'warn'}>{item.conflict_label}</Badge>
                <div style={{ marginTop: 6 }}>{item.description}</div>
                <div style={{ marginTop: 6 }}>Что делать: {item.resolution}</div>
              </Callout>
            </div>
          ))}
          {result.basket_synergies.map((item, index) => (
            <div key={`s-${index}`} style={{ marginBottom: 10 }}>
              <Callout tone="ok">
                <strong>
                  {item.a_name} + {item.b_name}
                </strong>
                <div style={{ marginTop: 6 }}>{item.description}</div>
              </Callout>
            </div>
          ))}
        </Card>
      )}

      <Card title="Сводный профиль нагрузки">
        <div className="stat-grid">
          <Metric label="CPU" value={result.load_profile.cpu.toFixed(0)} hint="50 — без изменений" />
          <Metric label="GPU" value={result.load_profile.gpu.toFixed(0)} hint="50 — без изменений" />
          <Metric label="RAM" value={result.load_profile.ram.toFixed(0)} hint="50 — без изменений" />
          <Metric label="VRAM" value={result.load_profile.vram.toFixed(0)} hint="50 — без изменений" />
          <Metric label="Диск" value={result.load_profile.disk.toFixed(0)} hint="50 — без изменений" />
          <Metric label="Сеть" value={result.load_profile.network.toFixed(0)} hint="50 — без изменений" />
        </div>
      </Card>

      {hw && (
        <Card title="Референсное оборудование">
          <div className="stat-grid">
            <Metric label="Класс GPU" value={hw.gpu_class} hint="из 5" />
            <Metric label="Класс CPU" value={hw.cpu_class} hint="из 5" />
            <Metric label="VRAM" value={`${hw.estimated_vram_gb} ГБ`} />
            <Metric label="RAM" value={`${hw.estimated_ram_gb} ГБ`} />
          </div>
          <div className="small muted" style={{ marginTop: 10 }}>
            {hw.reference_gpu && <>Видеокарта: {hw.reference_gpu.model}. </>}
            {hw.reference_cpu && <>Процессор: {hw.reference_cpu.model}. </>}
            Уверенность оценки — {hw.confidence_label} ({Math.round(hw.confidence * 100)}%).
          </div>
          <div style={{ marginTop: 8 }}>
            <Callout tone="warn">
              Оценка ориентировочная и не гарантирует достижение целевого FPS: требуется проверка на
              прототипе.
            </Callout>
          </div>
        </Card>
      )}

      {result.similar_games.length > 0 && (
        <Card title="Сверка с практикой" hint="Ближайшие подтверждённые примеры.">
          <ul className="reason-list">
            {[...result.similar_games]
              .sort((a, b) => b.similarity - a.similarity)
              .slice(0, 5)
              .map((item) => (
                <li key={`${item.example.title}-${item.example.year}`}>
                  <strong>
                    {item.example.title} ({item.example.year})
                  </strong>{' '}
                  — сходство {Math.round(item.similarity * 100)}%.{' '}
                  {item.matching_optimizations.length > 0
                    ? `Совпадает с вашим набором: ${item.matching_optimizations.length} решений.`
                    : `Применённые решения: ${item.example.optimizations_used.join(', ')}.`}{' '}
                  {item.example.performance_outcome}
                </li>
              ))}
          </ul>
        </Card>
      )}

      {selected.length > 0 && (
        <Card title="Источники" hint="Каждое опубликованное решение сопровождается источником.">
          <ul className="reason-list">
            {[...new Set(selected.map((m) => m.source_url).filter(Boolean))].map((url) => (
              <li key={url}>
                <SourceLink url={url} />
              </li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}
