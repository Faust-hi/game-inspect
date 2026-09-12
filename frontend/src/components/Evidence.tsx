/**
 * Маркеры доказательности.
 *
 * Система построена на одном правиле: числовой результат нельзя показывать
 * так, будто он измерен, если измерения не было. Поэтому каждый числовой
 * элемент интерфейса несёт пометку основания, а не только значение.
 *
 * Отдельно различаются:
 *  - `measured`         — опубликованное измерение;
 *  - `documented`       — механизм описан источником, числа нет;
 *  - `derived`          — значение получено формулой из исходных параметров;
 *  - `expert_estimate`  — экспертная оценка, не измерение;
 *  - `unknown`          — данных нет. Это не ноль и не «совместимо».
 */
import type { ReactNode } from 'react';
import { Badge } from './ui';

type Tone = 'neutral' | 'ok' | 'warn' | 'danger' | 'info';

interface BasisMeta {
  label: string;
  tone: Tone;
  hint: string;
}

export const BASIS_META: Record<string, BasisMeta> = {
  measured: {
    label: 'измерено',
    tone: 'ok',
    hint: 'Опубликованное численное измерение. Переносится на другой проект только с оговорками.',
  },
  documented: {
    label: 'документировано',
    tone: 'info',
    hint: 'Механизм описан источником, но численного измерения в источнике нет.',
  },
  derived: {
    label: 'выведено',
    tone: 'info',
    hint: 'Значение получено формулой из исходных параметров; формула должна быть указана.',
  },
  expert_estimate: {
    label: 'экспертная оценка',
    tone: 'warn',
    hint: 'Суждение каталога, а не измерение. Пригодно для ранжирования, не для обещания срока.',
  },
  unknown: {
    label: 'неизвестно',
    tone: 'warn',
    hint: 'Данных нет. Отсутствие данных не означает совместимость или нулевой эффект.',
  },
};

/** Пометка основания доказательства. Неизвестное основание показывается честно. */
export function EvidenceBadge({ basis, title }: { basis?: string | null; title?: string }) {
  const key = (basis ?? '').trim().toLowerCase();
  const meta = BASIS_META[key];
  if (!meta) {
    return (
      <Badge tone="warn" title={`Основание «${basis || '—'}» не распознано; считать непроверенным.`}>
        не проверено
      </Badge>
    );
  }
  return (
    <Badge tone={meta.tone} title={title ?? meta.hint}>
      {meta.label}
    </Badge>
  );
}

/**
 * Три блока, которые нельзя смешивать: факт, аналитический вывод, допущение.
 * Смешение — самая частая причина, по которой отчёт выглядит точнее, чем есть.
 */
export function ClaimBlocks({
  fact,
  inference,
  assumption,
}: {
  fact?: ReactNode;
  inference?: ReactNode;
  assumption?: ReactNode;
}) {
  if (!fact && !inference && !assumption) return null;
  return (
    <div className="claim-blocks">
      {fact && (
        <div className="claim-block claim-block-fact">
          <div className="claim-block-title">Факт</div>
          <div className="small">{fact}</div>
        </div>
      )}
      {inference && (
        <div className="claim-block claim-block-inference">
          <div className="claim-block-title">Аналитический вывод</div>
          <div className="small">{inference}</div>
        </div>
      )}
      {assumption && (
        <div className="claim-block claim-block-assumption">
          <div className="claim-block-title">Допущение</div>
          <div className="small">{assumption}</div>
        </div>
      )}
    </div>
  );
}

/** Список неучтённых или неподтверждённых факторов. Пустой список тоже важен. */
export function UnconfirmedFactors({ items, title }: { items: string[]; title?: string }) {
  if (!items || items.length === 0) {
    return (
      <p className="xsmall faint" style={{ marginBottom: 0 }}>
        Неподтверждённых числовых факторов не зарегистрировано.
      </p>
    );
  }
  return (
    <details style={{ marginTop: 8 }}>
      <summary className="small">{title ?? 'Неучтённые и неподтверждённые факторы'} ({items.length})</summary>
      <ul className="reason-list">
        {items.slice(0, 60).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </details>
  );
}
