/** Экран 7. Корзина выбранных решений и совместимость набора. */
import { useMemo, useState } from 'react';
import { useStore } from '../store';
import { Badge, Callout, Card, Empty, ImpactGrid } from '../components/ui';
import { ConflictEntry, DependencyEntry, SynergyEntry } from '../components/Compatibility';
import { MethodCard } from '../components/MethodCard';
import { methodsByCode as buildMethodMap, selectedMethods } from '../catalogUtils';
import type { Method } from '../types';

export function BasketScreen() {
  const { profile, basket, result, catalog, toggleBasket, clearBasket, calculate, calculating } =
    useStore();
  const [openCode, setOpenCode] = useState<string | null>(null);

  const methodsByCode = useMemo(() => buildMethodMap(catalog.methods), [catalog.methods]);

  const selected: Method[] = useMemo(
    () => selectedMethods(basket, methodsByCode),
    [basket, methodsByCode],
  );

  const openMethod = openCode ? methodsByCode[openCode] : null;

  const stageNames = useMemo(
    () => Object.fromEntries((catalog.enums?.stages ?? []).map((s) => [s.value, s.label])),
    [catalog.enums],
  );

  if (selected.length === 0) {
    return (
      <Empty>
        <div style={{ marginBottom: 10 }}>
          Корзина пуста. Добавьте решения на шаге «Варианты реализации».
        </div>
      </Empty>
    );
  }

  const totalGain = selected.reduce((sum, m) => sum + m.performance_gain, 0) / selected.length;
  const totalCost = selected.reduce((sum, m) => sum + m.implementation_cost, 0);

  return (
    <>
      <Card
        title="Корзина проекта"
        hint="После изменения набора система пересчитывает сводный профиль нагрузки и совместимость решений."
        actions={
          <div className="btn-row">
            <Badge tone="info">решений: {selected.length}</Badge>
            <Badge tone="neutral">суммарные трудозатраты: {totalCost}</Badge>
            <button className="btn btn-sm" onClick={() => void calculate()} disabled={calculating}>
              {calculating ? 'Пересчёт…' : 'Пересчитать'}
            </button>
            <button className="btn btn-sm btn-danger" onClick={clearBasket}>
              Очистить
            </button>
          </div>
        }
      >
        <div className="callout" style={{ marginBottom: 14 }}>
          Средний ожидаемый эффект выбранного набора: <strong>{Math.round(totalGain * 100)}%</strong>.
          Оценка усреднённая: эффект решений не всегда складывается аддитивно, часть решений
          усиливают друг друга, часть — перекрываются.
        </div>

        {selected.map((method) => (
          <div key={method.code} className="method-row selected">
            <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
                  <strong>{method.name}</strong>
                  <Badge tone="neutral">{method.level_label}</Badge>
                  <Badge tone={method.late_cost === 'critical' ? 'danger' : 'neutral'}>
                    позднее внедрение — {method.late_cost_label}
                  </Badge>
                  {method.concept_impact < 0 && <Badge tone="danger">затрагивает концепцию</Badge>}
                </div>
                <p className="small muted" style={{ marginTop: 4 }}>{method.summary}</p>
                <div className="xsmall faint" style={{ marginBottom: 6 }}>
                  Рекомендуемая стадия: {method.recommended_stage_label}. Текущая стадия проекта:{' '}
                  {stageNames[profile.stage] ?? profile.stage}.
                </div>
                <ImpactGrid
                  impacts={{
                    cpu: method.impact_cpu,
                    gpu: method.impact_gpu,
                    ram: method.impact_ram,
                    vram: method.impact_vram,
                    disk: method.impact_disk,
                    network: method.impact_network,
                  }}
                />
              </div>
              <div className="btn-row" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
                <button className="btn btn-sm" onClick={() => setOpenCode(method.code)}>
                  Карточка
                </button>
                <button className="btn btn-sm btn-danger" onClick={() => toggleBasket(method.code)}>
                  Убрать
                </button>
              </div>
            </div>
          </div>
        ))}
      </Card>

      {result && result.basket_conflicts.length > 0 && (
        <Card
          title="Конфликты и незакрытые зависимости"
          hint="Набор содержит решения, которые взаимно исключают друг друга или требуют дополнения."
        >
          {result.basket_conflicts.map((item, index) => (
            <ConflictEntry key={index} item={item} />
          ))}
        </Card>
      )}

      {result && result.basket_dependencies.length > 0 && (
        <Card title="Зависимости набора" hint="Решения, которые осмысленны только в паре.">
          {result.basket_dependencies.map((item, index) => (
            <DependencyEntry key={index} item={item} />
          ))}
        </Card>
      )}

      {result && result.basket_synergies.length > 0 && (
        <Card title="Усиливающие сочетания" hint="Решения, которые выгодно применять совместно.">
          {result.basket_synergies.map((item, index) => (
            <SynergyEntry key={index} item={item} />
          ))}
        </Card>
      )}

      {result &&
        result.basket_conflicts.length === 0 &&
        result.basket_dependencies.length === 0 &&
        result.basket_synergies.length === 0 && (
          <Callout tone="ok" title="Совместимость набора">
            В выбранном наборе не обнаружено конфликтов и незакрытых зависимостей.
          </Callout>
        )}

      {openMethod && <MethodCard method={openMethod} onClose={() => setOpenCode(null)} />}
    </>
  );
}
