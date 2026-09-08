/** Блок «что означает текущая стадия проекта». */
import { Badge, Callout } from './ui';
import type { StageGuidance } from '../types';

const LEVEL_TONE = { blocked: 'danger', restricted: 'warn', available: 'ok' } as const;

/**
 * Содержание стадии: сводка, доступность уровней решений, предупреждения и
 * предложения.
 *
 * Блок общий для экранов: раньше подсказка по стадии была константой внутри
 * экрана стадии, и разделы рисков и плана не показывали её вовсе.
 */
export function StageGuidanceBlock({ guidance }: { guidance: StageGuidance }) {
  return (
    <>
      <Callout tone="info" title={`Стадия «${guidance.stage_label}»`}>
        {guidance.summary}
      </Callout>

      <div className="btn-row" style={{ margin: '10px 0 14px' }}>
        <Badge tone={LEVEL_TONE.available}>доступны: {joinLabels(guidance.available_level_labels)}</Badge>
        {guidance.restricted_level_labels.length > 0 && (
          <Badge tone={LEVEL_TONE.restricted} title="Часть решений этого уровня стадией закрыта">
            частично закрыты: {joinLabels(guidance.restricted_level_labels)}
          </Badge>
        )}
        {guidance.blocked_level_labels.length > 0 && (
          <Badge tone={LEVEL_TONE.blocked} title="Решения этого уровня исключены из расчёта">
            закрыты: {joinLabels(guidance.blocked_level_labels)}
          </Badge>
        )}
      </div>

      {guidance.warnings.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <div className="xsmall faint" style={{ marginBottom: 6 }}>
            Чем грозит стадия
          </div>
          {guidance.warnings.map((note) => (
            <Callout key={note.code} tone="warn" title={note.title}>
              {note.text}
            </Callout>
          ))}
        </div>
      )}

      {guidance.suggestions.length > 0 && (
        <div>
          <div className="xsmall faint" style={{ marginBottom: 6 }}>
            Что имеет смысл решить сейчас
          </div>
          <ul className="reason-list">
            {guidance.suggestions.map((note) => (
              <li key={note.code}>
                <strong>{note.title}</strong> — {note.text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

function joinLabels(labels: string[]): string {
  return labels.length > 0 ? labels.join(', ') : '—';
}
