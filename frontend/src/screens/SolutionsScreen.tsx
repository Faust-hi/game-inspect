/** Экран 4. Вкладки вариантов реализации функций. */
import { useEffect, useMemo, useState } from 'react';
import { useEnsureResult, useStore } from '../store';
import { RecommendationList } from '../components/RecommendationList';
import { Badge, Callout, Card, Empty, Loading, Tabs } from '../components/ui';

export function SolutionsScreen({ onCompare }: { onCompare: (codes: string[]) => void }) {
  const { profile, basket, result, calculating, calculateError, calculate, toggleBasket, catalog } =
    useStore();
  const [tab, setTab] = useState<string>('');

  const methodsByCode = useMemo(
    () => Object.fromEntries(catalog.methods.map((method) => [method.code, method])),
    [catalog.methods],
  );

  const engineName =
    catalog.engines.find((engine) => engine.code === profile.engine)?.name ?? profile.engine;

  const functionName = (code: string | null) =>
    catalog.functions.find((fn) => fn.code === code)?.name ?? 'Общие методы';

  // Результат сбрасывается при любом изменении профиля или корзины, поэтому
  // пересчёт запускается здесь: на экране всегда данные текущего входа.
  useEnsureResult();

  const recommendations = result?.recommendations ?? [];

  const byFunction = useMemo(() => {
    const groups = new Map<string, typeof recommendations>();
    for (const item of recommendations) {
      const key = item.function_code ?? '__general__';
      groups.set(key, [...(groups.get(key) ?? []), item]);
    }
    return groups;
  }, [recommendations]);

  const tabs = useMemo(() => {
    const ordered = profile.functions
      .filter((code) => byFunction.has(code))
      .map((code) => ({ key: code, label: functionName(code), count: byFunction.get(code)?.length }));
    if (byFunction.has('__general__')) {
      ordered.push({
        key: '__general__',
        label: 'Общие методы',
        count: byFunction.get('__general__')?.length,
      });
    }
    return ordered;
  }, [profile.functions, byFunction]);

  useEffect(() => {
    if (tabs.length > 0 && !tabs.some((item) => item.key === tab)) {
      setTab(tabs[0].key);
    }
  }, [tabs, tab]);

  if (calculating) return <Loading text="Расчёт рекомендаций…" />;

  if (calculateError) {
    return (
      <Callout tone="danger" title="Расчёт не выполнен">
        {calculateError}
      </Callout>
    );
  }

  if (profile.functions.length === 0) {
    return (
      <Empty>
        Функции не выбраны. Вернитесь к шагу «Функции» и отметьте, что должно работать в игре.
      </Empty>
    );
  }

  if (!result) {
    return (
      <Empty>
        <div style={{ marginBottom: 10 }}>Расчёт ещё не выполнен.</div>
        <button className="btn btn-primary" onClick={() => void calculate()}>
          Рассчитать рекомендации
        </button>
      </Empty>
    );
  }

  const current = byFunction.get(tab) ?? [];

  return (
    <>
      <Card
        title="Рекомендации по реализации функций"
        hint="Решения отранжированы методом TOPSIS с учётом стадии проекта, ограничений и приоритета."
        actions={
          <div className="btn-row">
            <Badge tone="info">подобрано: {result.recommendations.length}</Badge>
            <Badge tone="neutral">исключено: {result.excluded.length}</Badge>
            <button className="btn btn-sm" onClick={() => void calculate()}>
              Пересчитать
            </button>
          </div>
        }
      >
        {current.length > 1 && (
          <div className="btn-row" style={{ marginBottom: 12 }}>
            <button className="btn btn-sm" onClick={() => onCompare(current.map((item) => item.method_code))}>
              Сравнить решения этой функции
            </button>
          </div>
        )}
        <RecommendationList
          recommendations={current}
          selected={basket}
          onToggle={toggleBasket}
          methodsByCode={methodsByCode}
          engineName={engineName}
          showCriteria
        />
      </Card>

      <Card title="Варианты по функциям">
        <Tabs tabs={tabs} active={tab} onChange={setTab} />
        {tabs.length === 0 ? (
          <p className="muted">Для выбранных функций не найдено применимых решений.</p>
        ) : (
          <RecommendationList
            recommendations={current}
            selected={basket}
            onToggle={toggleBasket}
            methodsByCode={methodsByCode}
            engineName={engineName}
          />
        )}
      </Card>

      {result.excluded.length > 0 && (
        <Card
          title="Исключённые решения"
          hint="Решения нарушают обязательные ограничения проекта или не применимы к его характеристикам."
        >
          {result.excluded.map((item) => (
            <div key={item.method_code} className="method-row">
              <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap' }}>
                <strong>{item.method_name}</strong>
                <span className="faint small">{functionName(item.function_code)}</span>
              </div>
              <ul className="reason-list">
                {item.excluded_reasons.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </div>
          ))}
        </Card>
      )}
    </>
  );
}
