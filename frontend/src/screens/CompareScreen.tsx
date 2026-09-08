/** Экран 6. Сравнение решений. */
import { useMemo } from 'react';
import { useStore } from '../store';
import { Badge, Bar, Empty, Flag, Modal } from '../components/ui';
import type { Method } from '../types';

const COMPARISON_ROWS: { label: string; render: (m: Method) => string }[] = [
  { label: 'Уровень решения', render: (m) => m.level_label },
  { label: 'Рекомендуемая стадия', render: (m) => m.recommended_stage_label },
  { label: 'Стоимость позднего внедрения', render: (m) => m.late_cost_label },
  { label: 'Способ расчёта', render: (m) => m.calc_mode_label },
  { label: 'Экспертный балл эффекта', render: (m) => `${m.performance_gain.toFixed(2)} / 1` },
  { label: 'Трудозатраты', render: (m) => `${m.implementation_cost} из 5` },
  { label: 'Сложность внедрения', render: (m) => `${m.complexity} из 5` },
  { label: 'Достоверность оценки', render: (m) => `${Math.round(m.confidence * 100)}%` },
  { label: 'Влияние на CPU', render: (m) => formatImpact(m.impact_cpu) },
  { label: 'Влияние на GPU', render: (m) => formatImpact(m.impact_gpu) },
  { label: 'Влияние на RAM', render: (m) => formatImpact(m.impact_ram) },
  { label: 'Влияние на VRAM', render: (m) => formatImpact(m.impact_vram) },
  { label: 'Влияние на накопитель', render: (m) => formatImpact(m.impact_disk) },
  { label: 'Влияние на сеть', render: (m) => formatImpact(m.impact_network) },
  { label: 'Влияние на качество', render: (m) => formatImpact(m.quality_impact) },
  { label: 'Влияние на концепцию', render: (m) => (m.concept_impact < 0 ? 'затрагивает' : 'не затрагивает') },
  { label: 'Требуется прототип', render: (m) => (m.requires_prototype ? 'да' : 'нет') },
];

function formatImpact(value: number): string {
  if (value === 0) return 'не влияет';
  return value < 0 ? `снижает (${value})` : `повышает (+${value})`;
}

/** Ячейка сравнения: отличающиеся от лучшего значения подсвечиваются. */
function bestValue(methods: Method[], extract: (m: Method) => number, lowerBetter: boolean): number {
  const values = methods.map(extract);
  return lowerBetter ? Math.min(...values) : Math.max(...values);
}

export function CompareScreen({
  codes,
  onClose,
  onToggle,
}: {
  codes: string[];
  onClose: () => void;
  onToggle: (code: string) => void;
}) {
  const { catalog, basket, profile } = useStore();

  const methods = useMemo(
    () => codes.map((code) => catalog.methods.find((m) => m.code === code)).filter(Boolean) as Method[],
    [codes, catalog.methods],
  );

  if (methods.length === 0) {
    return (
      <Modal title="Сравнение решений" onClose={onClose}>
        <Empty>Решения для сравнения не найдены.</Empty>
      </Modal>
    );
  }

  const engineName = (code: string) =>
    catalog.engines.find((engine) => engine.code === code)?.name ?? code;

  return (
    <Modal
      title={`Сравнение решений (${methods.length})`}
      subtitle="Наилучшее значение в строке выделено цветом."
      onClose={onClose}
    >
      <div style={{ overflowX: 'auto' }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ minWidth: 200 }}>Характеристика</th>
              {methods.map((method) => (
                <th key={method.code} style={{ minWidth: 210 }}>
                  {method.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {COMPARISON_ROWS.map((row) => (
              <tr key={row.label}>
                <td className="muted">{row.label}</td>
                {methods.map((method) => (
                  <td key={method.code}>{row.render(method)}</td>
                ))}
              </tr>
            ))}

            <tr>
              <td className="muted">Аналог в движке</td>
              {methods.map((method) => {
                const link = method.engine_links.find(item => item.engine_code === profile.engine);
                return (
                  <td key={method.code} className="small">
                    {link ? (
                      <>
                        {engineName(link.engine_code)}: <strong>{link.tool_name}</strong>
                        <div className="faint">{link.relation_label}</div>
                      </>
                    ) : (
                      <span className="faint">нет данных</span>
                    )}
                  </td>
                );
              })}
            </tr>

            <tr>
              <td className="muted">Действие</td>
              {methods.map((method) => {
                const selected = basket.includes(method.code);
                return (
                  <td key={method.code}>
                    <button
                      className={`btn btn-sm ${selected ? 'btn-danger' : 'btn-primary'}`}
                      onClick={() => onToggle(method.code)}
                    >
                      {selected ? 'Убрать' : 'В корзину'}
                    </button>
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>

      <div className="divider" />
      <h4>Сравнение ключевых показателей</h4>
      <div className="grid grid-3" style={{ marginTop: 8 }}>
        {methods.map((method) => {
          const bestGain = bestValue(methods, (m) => m.performance_gain, false);
          const bestCost = bestValue(methods, (m) => m.implementation_cost, true);
          const bestQuality = bestValue(methods, (m) => m.quality_impact, false);
          return (
            <div key={method.code} className="method-row" style={{ margin: 0 }}>
              <strong style={{ fontSize: 13 }}>{method.name}</strong>
              <div style={{ marginTop: 8 }}>
                <div className="xsmall faint">
                  Экспертный балл эффекта {method.performance_gain.toFixed(2)} / 1
                  {method.performance_gain === bestGain && <Badge tone="ok">лучший</Badge>}
                </div>
                <Bar value={method.performance_gain * 100} />
              </div>
              <div style={{ marginTop: 8 }}>
                <div className="xsmall faint">
                  Трудозатраты {method.implementation_cost} / 5
                  {method.implementation_cost === bestCost && <Badge tone="ok">минимальные</Badge>}
                </div>
                <Bar value={method.implementation_cost * 20} tone="danger" />
              </div>
              <div style={{ marginTop: 8 }}>
                <div className="xsmall faint">
                  Качество {formatImpact(method.quality_impact)}
                  {method.quality_impact === bestQuality && <Badge tone="ok">лучшее</Badge>}
                </div>
              </div>
              <div className="flag-row">
                {method.concept_impact < 0 && <Flag code="may_change_concept" label="может изменить концепцию" />}
                {method.quality_impact < 0 && <Flag code="may_reduce_quality" label="может снизить качество" />}
                {method.requires_prototype && <Flag code="needs_prototyping" label="требует прототипирования" />}
              </div>
            </div>
          );
        })}
      </div>
    </Modal>
  );
}
