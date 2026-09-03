/** Экран 8. Сводный профиль нагрузки выбранного набора решений. */
import { useMemo } from 'react';
import { useEnsureResult, useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading } from '../components/ui';
import type { LoadProfile, Method } from '../types';

const RESOURCES: { key: keyof Omit<LoadProfile, 'per_resource'>; label: string }[] = [
  { key: 'cpu', label: 'CPU' },
  { key: 'gpu', label: 'GPU' },
  { key: 'ram', label: 'RAM' },
  { key: 'vram', label: 'VRAM' },
  { key: 'disk', label: 'Накопитель' },
  { key: 'network', label: 'Сеть' },
];

/**
 * Шкала с нейтральной серединой: значение 50 соответствует отсутствию изменений,
 * смещение влево — снижение нагрузки, вправо — рост.
 */
function CenteredBar({ value }: { value: number }) {
  const reduced = value < 50;
  const offset = reduced ? value : 50;
  const width = Math.abs(value - 50);
  const color = reduced ? 'var(--ok)' : 'var(--danger)';

  return (
    <div className="bar-track">
      <div
        className="bar-fill"
        style={{ marginLeft: `${offset}%`, width: `${width}%`, background: color }}
      />
      <div className="bar-center" />
    </div>
  );
}

function directionTone(direction: string): 'ok' | 'danger' | 'neutral' {
  if (direction === 'снижает') return 'ok';
  if (direction === 'повышает') return 'danger';
  return 'neutral';
}

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

export function LoadProfileScreen() {
  const { result, basket, catalog, calculating } = useStore();

  useEnsureResult();

  const methodsByCode = useMemo(() => {
    const map: Record<string, Method> = {};
    for (const method of catalog.methods) map[method.code] = method;
    return map;
  }, [catalog.methods]);

  const selected = useMemo(
    () => basket.map((code) => methodsByCode[code]).filter((m): m is Method => Boolean(m)),
    [basket, methodsByCode],
  );

  if (calculating) return <Loading text="Расчёт профиля нагрузки…" />;

  if (!result) {
    return <Empty>Расчёт ещё не выполнен. Выполните расчёт на этапе «Варианты реализации».</Empty>;
  }

  const load = result.load_profile;

  return (
    <>
      <Card
        title="Сводный профиль нагрузки"
        hint="Система показывает суммарное влияние выбранного набора на подсистемы проекта, а не эффект отдельных решений по отдельности."
        actions={<Badge tone="info">решений: {selected.length}</Badge>}
      >
        {selected.length === 0 && (
          <Callout tone="warn" title="Корзина пуста">
            Профиль построен по базовым характеристикам проекта. Добавьте решения, чтобы увидеть их
            суммарное влияние.
          </Callout>
        )}

        <div style={{ display: 'grid', gap: 14, marginTop: selected.length === 0 ? 14 : 0 }}>
          {RESOURCES.map(({ key, label }) => {
            const detail = load.per_resource[key];
            const normalized = load[key];
            return (
              <div key={key}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'baseline',
                    gap: 8,
                    marginBottom: 5,
                    flexWrap: 'wrap',
                  }}
                >
                  <strong style={{ fontSize: 13, minWidth: 96 }}>{label}</strong>
                  {detail && (
                    <Badge tone={directionTone(detail.direction)}>{detail.direction}</Badge>
                  )}
                  <span className="xsmall faint" style={{ marginLeft: 'auto' }}>
                    {normalized.toFixed(0)} / 100
                    {detail ? ` · суммарный балл ${detail.raw > 0 ? '+' : ''}${detail.raw}` : ''}
                  </span>
                </div>
                <CenteredBar value={normalized} />
              </div>
            );
          })}
        </div>

        <div className="divider" />
        <p className="xsmall faint">
          Шкала нормирована так, что 50 соответствует отсутствию изменений: отклонение влево означает
          снижение нагрузки на подсистему, вправо — её рост. Оценка качественная и не заменяет
          профилирование конкретной сборки.
        </p>
      </Card>

      {selected.length > 0 && (
        <Card
          title="Вклад отдельных решений"
          hint="Из чего складывается суммарный профиль: отрицательные значения снижают нагрузку, положительные повышают."
        >
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ minWidth: 220 }}>Решение</th>
                  {RESOURCES.map(({ key, label }) => (
                    <th key={key}>{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {selected.map((method) => {
                  const impacts = impactsOf(method);
                  return (
                    <tr key={method.code}>
                      <td className="small">
                        {method.name}
                        <div className="xsmall faint">{method.level_label}</div>
                      </td>
                      {RESOURCES.map(({ key }) => {
                        const value = impacts[key];
                        return (
                          <td
                            key={key}
                            className="mono small"
                            style={{
                              color: value < 0 ? 'var(--ok)' : value > 0 ? 'var(--danger)' : undefined,
                            }}
                          >
                            {value === 0 ? '—' : value > 0 ? `+${value}` : value}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
                <tr>
                  <td className="small">
                    <strong>Суммарно</strong>
                  </td>
                  {RESOURCES.map(({ key }) => {
                    const total = selected.reduce((sum, m) => sum + impactsOf(m)[key], 0);
                    return (
                      <td key={key} className="mono small">
                        <strong>{total === 0 ? '—' : total > 0 ? `+${total}` : total}</strong>
                      </td>
                    );
                  })}
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </>
  );
}
