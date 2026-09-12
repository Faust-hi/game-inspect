/** Экран 7. Корзина выбранных решений и совместимость набора. */
import { useMemo, useState } from 'react';
import { useEnsureResult, useStore } from '../store';
import { Badge, Callout, Card, Empty, ImpactGrid } from '../components/ui';
import { ConflictEntry, DependencyEntry, SynergyEntry } from '../components/Compatibility';
import { MethodCard } from '../components/MethodCard';
import { TransitionDetails } from '../components/ImplementationTransition';
import { methodsByCode as buildMethodMap, selectedMethods } from '../catalogUtils';
import type { Method } from '../types';

export function BasketScreen() {
  useEnsureResult();
  const {
    profile,
    basket,
    result,
    catalog,
    toggleBasket,
    clearBasket,
    calculate,
    calculating,
    baseline,
    saveBaseline,
  } = useStore();
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

  if (selected.length === 0 && !baseline) {
    return (
      <Empty>
        <div style={{ marginBottom: 10 }}>
          Корзина пуста. Добавьте решения на шаге «Варианты реализации».
        </div>
      </Empty>
    );
  }

  const totalCost = selected.reduce((sum, m) => sum + m.implementation_cost, 0);

  // Гейт «зафиксировать основу» проверяет САМО свойство, а не его прокси:
  // каждый заявленный метод должен попасть в расчёт. Проверка длины списка
  // (было `accounted.length !== basket.length`) ложна в обе стороны — она
  // блокирует корзину с достроенной зависимостью и, наоборот, пропускает
  // корзину, из которой метод выпал, если взамен достроился другой.
  const accountedCodes = useMemo(
    () => new Set(result?.accounted_method_codes ?? []),
    [result],
  );
  const droppedFromCalculation = basket.filter((code) => !accountedCodes.has(code));
  const blockingConflicts = (result?.basket_conflicts ?? []).filter(
    (item) => item.conflict_type !== 'risk',
  );
  const canSaveBaseline =
    Boolean(result) && !calculating && droppedFromCalculation.length === 0 && blockingConflicts.length === 0;

  return (
    <>
      <Card title="Реализованная основа проекта">
        <p className="small muted">Зафиксируйте корзину после реализации решений. Следующие изменения будут оцениваться относительно этой основы. Черновые изменения корзины её не заменяют. Данные сохраняются в текущем сеансе браузера.</p>
        {baseline && <p>Зафиксировано решений: {baseline.basket.length}. Стадия: {stageNames[baseline.profile.stage] ?? baseline.profile.stage}.</p>}
        <button className="btn btn-primary" disabled={!canSaveBaseline}
          onClick={saveBaseline}>Зафиксировать корзину как реализованную</button>
        {result && !canSaveBaseline && (
          <p className="small muted" style={{ marginTop: 6 }}>
            Зафиксировать нельзя:{' '}
            {[
              blockingConflicts.length > 0
                ? `в наборе есть блокирующая связь (${blockingConflicts.length})`
                : null,
              droppedFromCalculation.length > 0
                ? `вне расчёта остались решения: ${droppedFromCalculation
                    .map((code) => methodsByCode[code]?.name ?? code)
                    .join(', ')}`
                : null,
            ]
              .filter(Boolean)
              .join('; ')}
            .
          </p>
        )}
        {result?.transitions?.map(item => <div key={item.method_code} style={{ marginTop: 12 }}>
          <strong>{methodsByCode[item.method_code]?.name ?? item.method_code}</strong>
          <TransitionDetails item={item} />
        </div>)}
      </Card>
      <Card
        title="Корзина проекта"
        hint="После изменения набора система пересчитывает сводный профиль нагрузки и совместимость решений."
        actions={
          <div className="btn-row">
            <Badge tone="info">решений: {selected.length}</Badge>
            <Badge tone="neutral">исходные баллы трудозатрат: {totalCost}</Badge>
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
          Эффекты относятся к разным подсистемам и областям работы. Общий процент ускорения
          без измерений не установлен; оценки каталога используются как экспертные баллы.
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

      {result && (result.required_additionally?.length ?? 0) > 0 && (
        <Card
          title="Достроено автоматически"
          hint="Обязательные зависимости выбранных решений. Они входят в расчёт, но ваш выбор не заменяют."
        >
          {(result.required_additionally ?? []).map((method) => (
            <div key={method.code} className="method-row">
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
                  <strong>{method.name}</strong>
                  <Badge tone="info">{method.level_label}</Badge>
                </div>
                <p className="small muted" style={{ marginTop: 4 }}>{method.summary}</p>
              </div>
              <button className="btn btn-sm" onClick={() => setOpenCode(method.code)}>
                Карточка
              </button>
            </div>
          ))}
          {(result.required_additionally_notes ?? []).map((note, index) => (
            <p key={index} className="xsmall faint" style={{ marginTop: 6 }}>{note}</p>
          ))}
        </Card>
      )}

      {result && result.basket_conflicts.length > 0 && (
        <Card
          title="Совместимость и риски набора"
          hint="Проверьте тип каждой связи: условный риск допускает совместное применение; несовместимость или отсутствующая зависимость требуют изменения набора."
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
        <Card title="Дополнения и перекрытия" hint="Связь не доказывает дополнительное ускорение. Проверяйте условия совместного применения.">
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
