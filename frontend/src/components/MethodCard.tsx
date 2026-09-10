/** Карточка метода: классификация, влияние, проверка, аналоги в движках. */
import { impactsOf } from '../catalogUtils';
import type { Method } from '../types';
import { Badge, ImpactGrid, Modal, SourceLink } from './ui';

const LEVEL_TONE: Record<string, 'info' | 'ok' | 'warn' | 'danger' | 'neutral'> = {
  architecture: 'danger',
  production: 'warn',
  algorithm: 'info',
  setting: 'ok',
};

export function MethodCard({ method, onClose }: { method: Method; onClose: () => void }) {
  const impacts = impactsOf(method);

  return (
    <Modal
      title={method.name}
      subtitle={method.summary}
      onClose={onClose}
      footer={
        <a className="btn" href={method.source_url} target="_blank" rel="noreferrer">
          Открыть источник
        </a>
      }
    >
      <div className="flag-row" style={{ marginBottom: 14 }}>
        <Badge tone={LEVEL_TONE[method.level] ?? 'neutral'}>{method.level_label}</Badge>
        <Badge tone={method.kind === 'optimization' ? 'info' : 'neutral'}>
          {method.kind === 'optimization' ? 'метод оптимизации' : 'вариант реализации'}
        </Badge>
        <Badge tone="neutral">{method.calc_mode_label}</Badge>
        {method.effect_scope !== 'client' && (
          <Badge tone="warn" title="Эффект не меняет требования к компьютеру игрока">
            область эффекта: {method.effect_scope_label}
          </Badge>
        )}
        {method.requires_prototype && <Badge tone="warn">требует прототипа</Badge>}
      </div>

      {method.problem && (
        <>
          <h4>Какую проблему решает</h4>
          <p className="muted">{method.problem}</p>
        </>
      )}

      {method.description && (
        <>
          <h4>Описание</h4>
          <p className="muted">{method.description}</p>
        </>
      )}

      <div className="divider" />
      <h4 style={{ marginBottom: 8 }}>Классификация решения</h4>
      <dl className="kv">
        <dt>Уровень решения</dt>
        <dd>{method.level_label}</dd>
        <dt>Рекомендуемая стадия</dt>
        <dd>{method.recommended_stage_label}</dd>
        <dt>Стоимость позднего внедрения</dt>
        <dd>{method.late_cost_label}</dd>
        <dt>Способ расчёта</dt>
        <dd>{method.calc_mode_label}</dd>
        <dt>Область эффекта</dt>
        <dd>
          {method.effect_scope_label}
          {method.effect_scope !== 'client' && ' — требования к компьютеру игрока не меняет'}
        </dd>
        <dt>Сложность внедрения</dt>
        <dd>{method.complexity} из 5</dd>
        <dt>Трудозатраты</dt>
        <dd>{method.implementation_cost} из 5</dd>
        <dt>Достоверность оценки</dt>
        <dd>{Math.round(method.confidence * 100)}%</dd>
      </dl>

      <div className="divider" />
      <h4 style={{ marginBottom: 8 }}>Влияние на подсистемы</h4>
      <ImpactGrid impacts={impacts} />
      <p className="xsmall faint" style={{ marginTop: 6 }}>
        Отрицательные значения — снижение нагрузки, положительные — увеличение.
      </p>

      <dl className="kv" style={{ marginTop: 12 }}>
        <dt>Влияние на качество</dt>
        <dd>{method.quality_impact === 0 ? 'не влияет' : `${method.quality_impact > 0 ? '+' : ''}${method.quality_impact}`}</dd>
        <dt>Влияние на концепцию</dt>
        <dd>{method.concept_impact === 0 ? 'не затрагивает' : 'затрагивает исходную концепцию'}</dd>
      </dl>

      {(method.pros.length > 0 || method.cons.length > 0) && (
        <>
          <div className="divider" />
          <div className="grid grid-2">
            <div>
              <h4>Преимущества</h4>
              <ul className="reason-list">
                {method.pros.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4>Недостатки</h4>
              <ul className="reason-list">
                {method.cons.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}

      {method.limitations.length > 0 && (
        <>
          <div className="divider" />
          <h4>Ограничения</h4>
          <ul className="reason-list">
            {method.limitations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </>
      )}

      {method.requires_conditions.length > 0 && (
        <>
          <div className="divider" />
          <h4>Условия применимости</h4>
          <ul className="reason-list">
            {method.requires_conditions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </>
      )}

      <div className="divider" />
      {(method.application_steps ?? []).length > 0 && <>
        <h4>Шаги применения</h4>
        <ol>{(method.application_steps ?? []).map(step => <li key={step}>{step}</li>)}</ol>
      </>}
      <h4>Последующая проверка</h4>
      <p className="muted">{method.verification_method || 'Способ проверки не указан.'}</p>
      {method.verification_tools.length > 0 && (
        <div className="chip-row" style={{ marginTop: 6 }}>
          {method.verification_tools.map((tool) => (
            <span key={tool} className="chip">
              {tool}
            </span>
          ))}
        </div>
      )}

      <div className="divider" />
      <h4 style={{ marginBottom: 8 }}>Аналоги в игровых движках</h4>
      {method.engine_links.length === 0 ? (
        method.engine_tool_independent ? (
          <p className="muted">
            Метод реализуется своими средствами и не опирается на встроенные инструменты
            движка — привязка к версии не требуется.
          </p>
        ) : (
          <p className="muted">Связи с инструментами движков не заданы.</p>
        )
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Движок</th>
              <th>Инструмент</th>
              <th>Тип связи</th>
              <th>Пояснение</th>
            </tr>
          </thead>
          <tbody>
            {method.engine_links.map((link) => (
              <tr key={`${link.engine_code}-${link.tool_code}`}>
                <td className="nowrap">{link.engine_name}</td>
                <td className="nowrap">
                  {link.docs_url ? (
                    <a href={link.docs_url} target="_blank" rel="noreferrer">
                      {link.tool_name}
                    </a>
                  ) : (
                    link.tool_name
                  )}
                </td>
                <td className="nowrap">{link.relation_label}</td>
                <td className="small muted">{link.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ marginTop: 14 }}>
        <SourceLink url={method.source_url} title={method.source_title} />
      </div>
    </Modal>
  );
}
