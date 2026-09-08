/** Список рекомендаций с пометками, объяснением и аналогами в движке. */
import { useState } from 'react';
import type { Method, Recommendation } from '../types';
import { MethodCard } from './MethodCard';
import { Badge, Bar, Callout, Flag } from './ui';

interface Props {
  recommendations: Recommendation[];
  selected: string[];
  onToggle: (code: string) => void;
  methodsByCode: Record<string, Method>;
  engineName: string;
  showCriteria?: boolean;
}

export function RecommendationList({
  recommendations,
  selected,
  onToggle,
  methodsByCode,
  engineName,
  showCriteria = false,
}: Props) {
  const [openCode, setOpenCode] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const openMethod = openCode ? methodsByCode[openCode] : null;

  if (recommendations.length === 0) {
    return (
      <Callout tone="warn">
        Нет решений, прошедших проверку обязательных ограничений проекта. Проверьте исключённые
        решения: возможно, заданные ограничения слишком жёсткие.
      </Callout>
    );
  }

  return (
    <>
      {recommendations.map((item) => {
        const isSelected = selected.includes(item.method_code);
        const isExpanded = expanded === item.method_code;
        const support = item.engine_support;
        // Серверная экономия и ускорение разработки не ускоряют кадр: процент
        // эффекта в этом случае относится не к игре, а к другой машине или
        // к производству, и показывать его как прирост FPS нельзя.
        const isClientEffect = item.effect_scope === 'client';

        return (
          <div key={item.method_code} className={`method-row ${isSelected ? 'selected' : ''}`}>
            <div className="method-row-head">
              <div className={`method-rank ${item.rank <= 3 ? 'top' : ''}`}>{item.rank}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
                  <h3>{item.method_name}</h3>
                  <span className="faint small">
                    коэффициент близости {item.score.toFixed(3)}
                  </span>
                </div>
                <p className="small muted" style={{ marginTop: 2 }}>{item.summary}</p>

                <div className="flag-row">
                  {item.flags.map((flag, index) => (
                    <Flag key={flag} code={flag} label={item.flag_labels[index] ?? flag} />
                  ))}
                  {item.stability && (
                    <span
                      className="faint xsmall"
                      title="Ранг при изменении каждого веса TOPSIS на ±10% по одному"
                    >
                      {item.stability.stable
                        ? 'ранг устойчив к ±10% весов'
                        : `ранг ${item.stability.rank_min}–${item.stability.rank_max} при ±10% весов`}
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', gap: 16, marginTop: 10, flexWrap: 'wrap' }}>
                  <div style={{ minWidth: 160, flex: 1 }}>
                    <div className="xsmall faint">
                      {isClientEffect
                        ? `Ожидаемый эффект ${Math.round(item.performance_gain * 100)}%`
                        : `Эффект: ${item.effect_scope_label} — не относится к компьютеру игрока`}
                    </div>
                    <Bar value={isClientEffect ? item.performance_gain * 100 : 0} />
                  </div>
                  <div style={{ minWidth: 160, flex: 1 }}>
                    <div className="xsmall faint">
                      Трудозатраты {item.implementation_cost} / 5 · сложность {item.complexity} / 5
                    </div>
                    <Bar value={item.implementation_cost * 20} tone="danger" />
                  </div>
                </div>

                <div className="small muted" style={{ marginTop: 8 }}>
                  {engineName}:{' '}
                  {support ? (
                    <>
                      <strong>{support.tool_name}</strong>{' '}
                      <Badge tone={support.relation_type === 'direct' ? 'ok' : 'neutral'}>
                        {support.relation_label}
                      </Badge>
                    </>
                  ) : (
                    <span className="faint">встроенного аналога нет</span>
                  )}
                </div>

                <div className="btn-row" style={{ marginTop: 10 }}>
                  <button
                    className={`btn btn-sm ${isSelected ? 'btn-danger' : 'btn-primary'}`}
                    onClick={() => onToggle(item.method_code)}
                  >
                    {isSelected ? 'Убрать из корзины' : 'В корзину'}
                  </button>
                  <button className="btn btn-sm" onClick={() => setExpanded(isExpanded ? null : item.method_code)}>
                    {isExpanded ? 'Скрыть объяснение' : 'Почему рекомендуется'}
                  </button>
                  <button className="btn btn-sm btn-ghost" onClick={() => setOpenCode(item.method_code)}>
                    Карточка метода
                  </button>
                </div>

                {isExpanded && (
                  <div style={{ marginTop: 10 }}>
                    <ul className="reason-list">
                      {item.reasons.map((reason, index) => (
                        <li key={index}>{reason}</li>
                      ))}
                    </ul>

                    {item.engine_alternatives.length > 0 && (
                      <div style={{ marginTop: 10 }}>
                        <div className="xsmall faint">Аналоги в других движках</div>
                        <div className="chip-row" style={{ marginTop: 4 }}>
                          {item.engine_alternatives.map((link) => (
                            <span key={`${link.engine_code}-${link.tool_code}`} className="chip">
                              {link.engine_name}: {link.tool_name} — {link.relation_label}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {showCriteria && item.criteria.length > 0 && (
                      <div style={{ marginTop: 12 }}>
                        <div className="xsmall faint">Раскрытие расчёта TOPSIS</div>
                        <table className="table" style={{ marginTop: 4 }}>
                          <thead>
                            <tr>
                              <th>Критерий</th>
                              <th>Значение</th>
                              <th>Нормализованное</th>
                              <th>Вес</th>
                              <th>Взвешенное</th>
                            </tr>
                          </thead>
                          <tbody>
                            {item.criteria.map((criterion) => (
                              <tr key={criterion.key}>
                                <td>
                                  {criterion.label}{' '}
                                  <span className="faint xsmall">
                                    ({criterion.kind === 'benefit' ? 'больше лучше' : 'меньше лучше'})
                                  </span>
                                </td>
                                <td className="mono">{criterion.raw}</td>
                                <td className="mono">{criterion.normalized}</td>
                                <td className="mono">{criterion.weight}</td>
                                <td className="mono">{criterion.weighted}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}

      {openMethod && <MethodCard method={openMethod} onClose={() => setOpenCode(null)} />}
    </>
  );
}
