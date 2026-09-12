/** Экран 11. Итоговый план проекта. Одновременно является печатной формой отчёта. */
import { useMemo } from 'react';
import { useStore } from '../store';
import { TransitionDetails } from '../components/ImplementationTransition';
import {
  Badge,
  Callout,
  Card,
  Empty,
  ImpactGrid,
  Loading,
  Metric,
  SourceLink,
  severityLabel,
  severityTone,
} from '../components/ui';
import { impactsOf, methodsByCode as buildMethodMap, selectedMethods } from '../catalogUtils';
import { ConflictEntry, DependencyEntry, SynergyEntry } from '../components/Compatibility';
import type { Method } from '../types';
import { HardwareWarnings } from '../components/HardwareWarnings';

/** Порядок внедрения: от архитектуры к настройкам. */
const LEVEL_ORDER = ['architecture', 'production', 'algorithm', 'setting'];

/**
 * Вклад фактора с единицей измерения.
 *
 * Раньше выводилось только число: доля «0.35» читалась как «0.35», а бюджет
 * кадра «16.667» — как доля. Теперь единица берётся из ответа и подставляется
 * явно, поэтому число нельзя прочитать неправильно.
 */
function formatContribution(item: { delta: number; unit: string }): string {
  const sign = item.delta > 0 ? '+' : '';
  if (item.unit === 'доля') return `${sign}${(item.delta * 100).toFixed(1)} %`;
  return `${sign}${item.delta} ${item.unit}`;
}

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

export function PlanScreen() {
  const { profile, basket, result, catalog, calculating } = useStore();

  // Автоматический расчёт выполняет каркас приложения (App.useEnsureResult).

  const methodsByCode = useMemo(() => buildMethodMap(catalog.methods), [catalog.methods]);

  const selected = useMemo(() => {
    // Итоговый план — весь учтённый набор: объявленные решения плюс обязательные
    // зависимости, достроенные движком. Раньше брались только объявленные, и
    // методы, без которых выбранные решения не работают, в план не попадали.
    const declared = result?.selected_methods ?? selectedMethods(basket, methodsByCode);
    const additionally = (result?.required_additionally ?? []).filter(
      extra => !declared.some(method => method.code === extra.code),
    );
    return [...declared, ...additionally]
      .filter(method => result?.accounted_method_codes?.includes(method.code) ?? true);
  }, [basket, methodsByCode, result]);

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
  const conceptChanging = selected.filter((m) => m.concept_impact < 0);
  const hw = result.hardware;

  return (
    <>
      <Card
        title={`Итоговый план: ${profile.name}`}
        hint={`${profile.format} · ${profile.world_type} · масштаб ${profile.scale} · ${profile.engine} · ${profile.target_resolution} / ${profile.target_quality} / ${profile.target_fps} FPS`}
      >
        <div className="xsmall faint">
          Сформирован {new Date().toLocaleDateString('ru-RU')} · стадия проекта:{' '}
          {profile.stage} · приоритет: {profile.priority} · платформы:{' '}
          {profile.platforms.join(', ') || 'не указаны'}
        </div>

        <div className="stat-grid" style={{ marginTop: 14 }}>
          <Metric label="Решений" value={selected.length} />
          <Metric label="Исходные трудозатраты" value={totalCost} hint="сумма баллов каталога; переход оценён отдельно" />
          <Metric label="Рисков" value={result.risks.length} />
        </div>
      </Card>

      {result.transitions?.some(item => item.status === 'removal') && <Card title="Вывод прежних решений из реализации">
        {result.transitions.filter(item => item.status === 'removal').map(item => <div key={item.method_code}>
          <strong>{methodsByCode[item.method_code]?.name ?? item.method_code}</strong>
          <TransitionDetails item={item} />
        </div>)}
      </Card>}

      {result.risks.length > 0 && (
        <Card
          title="Риски и предупреждения"
          hint="Выявлены до подбора решений: показывают противоречия между стадией проекта, его масштабом и составом функций."
        >
          {result.risks.map((risk) => (
            <div key={risk.code} className="method-row">
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
                <strong>{risk.title}</strong>
                <Badge tone={severityTone(risk.severity)}>{severityLabel(risk.severity)}</Badge>
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
                    {method.calc_mode_label} · область эффекта: {method.effect_scope_label} ·
                    исходные трудозатраты {method.implementation_cost} из 5 · сложность метода {method.complexity} из 5
                  </div>

                  <ImpactGrid impacts={impactsOf(method)} />
                  {result.transitions?.filter(item => item.method_code === method.code).map(item =>
                    <TransitionDetails key={item.method_code} item={item} />)}

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

      {(result.basket_conflicts.length > 0 ||
        result.basket_dependencies.length > 0 ||
        result.basket_synergies.length > 0) && (
        <Card
          title="Совместимость набора"
          hint="Конфликты требуют выбора одной из альтернатив, зависимости — сохранения обоих решений."
        >
          {result.basket_conflicts.map((item, index) => (
            <ConflictEntry key={`c-${index}`} item={item} />
          ))}
          {result.basket_dependencies.map((item, index) => (
            <DependencyEntry key={`d-${index}`} item={item} />
          ))}
          {result.basket_synergies.map((item, index) => (
            <SynergyEntry key={`s-${index}`} item={item} />
          ))}
        </Card>
      )}

      <Card title="Сводный профиль нагрузки">
        {(result.load_profile.notes ?? []).map(note => <p key={note}>{note}</p>)}
        <div className="stat-grid">
          {(
            [
              ['CPU', 'cpu'],
              ['GPU', 'gpu'],
              ['RAM', 'ram'],
              ['VRAM', 'vram'],
            ] as const
          ).map(([label, key]) => (
            <Metric
              key={label}
              label={label}
              value={result.load_profile[key].toFixed(0)}
              hint="50 — без изменений"
            />
          ))}
          {(['disk', 'network'] as const).map((key) => {
            const detail = result.load_profile.per_resource[key];
            const scored = detail && Math.abs(detail.raw) > 1e-6;
            return (
              <div key={key} className="metric">
                <div className="label">{detail?.label ?? key}</div>
                <div style={{ fontSize: 15, fontWeight: 650 }}>
                  {detail?.level ?? 'нет данных'}
                </div>
                <div className="xsmall muted">
                  {scored
                    ? `${detail.direction}, экспертный балл ${detail.raw > 0 ? '+' : ''}${detail.raw}`
                    : 'числовой оценки нет'}
                </div>
              </div>
            );
          })}
        </div>
        <p className="xsmall faint">
          Числовая шкала есть только у CPU, GPU, RAM и VRAM: по ним считается стоимость кадра.
          Накопитель и сеть оценены качественно — модель не оценивает объём данных и трафик.
        </p>
      </Card>

      {hw && (
        <Card title="Референсное оборудование">
          <HardwareWarnings hardware={hw} />
          <div className="stat-grid">
            {hw.gpu_class !== null && <Metric label="Класс GPU" value={hw.gpu_class} hint="из 5" />}
            {hw.cpu_class !== null && <Metric label="Класс CPU" value={hw.cpu_class} hint="из 5" />}
            <Metric label="VRAM" value={`${hw.estimated_vram_gb} ГБ`} />
            <Metric label="RAM" value={`${hw.estimated_ram_gb} ГБ`} />
          </div>
          {hw.bottleneck_label && (
            <div className="small muted" style={{ marginTop: 8 }}>
              Узкое место: <strong>{hw.bottleneck_label}</strong>
            </div>
          )}
          {hw.cpu_subsystems.length > 0 && (
            <div className="xsmall faint" style={{ marginTop: 8 }}>
              CPU (последовательная: {hw.cpu_main_thread_cost.toFixed(2)} мс, параллельная: {hw.cpu_parallel_cost.toFixed(2)} мс):{' '}
              {hw.cpu_subsystems.map(s => `${s.label} ${(s.share * 100).toFixed(0)}%`).join(', ')}
            </div>
          )}
          {hw.gpu_subsystems.length > 0 && (
            <div className="xsmall faint" style={{ marginTop: 4 }}>
              GPU (растр: {hw.gpu_raster_cost.toFixed(2)} мс, RT: {hw.gpu_rt_cost.toFixed(2)} мс):{' '}
              {hw.gpu_subsystems.map(s => `${s.label} ${(s.share * 100).toFixed(0)}%`).join(', ')}
            </div>
          )}
          {hw.memory_composition.length > 0 && (
            <div className="xsmall faint" style={{ marginTop: 4 }}>
              Память: {hw.memory_composition.map(m => `${m.label} RAM ${m.ram_gb} / VRAM ${m.vram_gb}`).join('; ')}
            </div>
          )}
          {hw.storage_requirement && (
            <div className="xsmall faint" style={{ marginTop: 4 }}>
              Накопитель: {hw.storage_requirement}
            </div>
          )}
          {hw.consequences.length > 0 && (
            <div className="xsmall faint" style={{ marginTop: 4 }}>
              Последствия: {hw.consequences.join(' ')}
            </div>
          )}
          <div className="small muted" style={{ marginTop: 10 }}>
            {hw.reference_gpu && <>Видеокарта: {hw.reference_gpu.model}. </>}
            {hw.reference_cpu && <>Процессор: {hw.reference_cpu.model}. </>}
            Полнота исходных данных — {hw.confidence_label}. Это не вероятность точности.
          </div>
          <div style={{ marginTop: 8 }}>
            <Callout tone="warn">
              Оценка ориентировочная и не гарантирует достижение целевого FPS: требуется проверка на
              прототипе.
            </Callout>
          </div>
        </Card>
      )}

      {result.contributions.parameters.length > 0 && (
        <Card title="Вклад параметров анкеты" hint="На сколько параметр меняет стоимость кадра; бюджет кадра — в миллисекундах.">
          <ul className="reason-list">
            {result.contributions.parameters.map((item, i) => (
              <li key={i}>
                <strong>{item.label}</strong> — {formatContribution(item)}. {item.detail}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {result.contributions.methods.length > 0 && (
        <Card title="Вклад выбранных решений">
          <ul className="reason-list">
            {result.contributions.methods.map((item, i) => (
              <li key={i}>
                <strong>{item.label}</strong> — {formatContribution(item)}. {item.detail}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {result.contributions.assumptions.length > 0 && (
        <Card title="Допущения расчёта">
          <ul className="reason-list">
            {result.contributions.assumptions.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </Card>
      )}

      {result.contributions.exclusions.length > 0 && (
        <Card title="Исключённые из расчёта эффекты">
          <ul className="reason-list">
            {result.contributions.exclusions.map((e, i) => (
              <li key={i}>{e}</li>
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
