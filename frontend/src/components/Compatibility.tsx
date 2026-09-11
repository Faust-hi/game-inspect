/** Одна запись совместимости набора: конфликт, зависимость или усиление.
 *
 * Единый рендер для экранов корзины и итогового плана — раньше разметка
 * Callout была скопирована в оба экрана в шести местах и разъезжалась
 * при правках (отступы, жирность «Что делать»).
 */
import type { ReactNode } from 'react';
import { Badge, Callout } from './ui';
import { EvidenceBadge } from './Evidence';
import type { BasketConflict } from '../types';

export function conflictTone(severity: number): 'danger' | 'warn' {
  return severity >= 3 ? 'danger' : 'warn';
}

export function CompatibilityEntry({
  tone,
  head,
  badge,
  description,
  resolution,
  basis,
}: {
  tone: 'danger' | 'warn' | 'info' | 'ok';
  head: ReactNode;
  badge?: ReactNode;
  description: string;
  resolution?: string;
  basis?: string;
}) {
  return (
    <div style={{ marginBottom: 10 }}>
      <Callout tone={tone}>
        <strong>{head}</strong> {badge}
        <div style={{ marginTop: 6 }}>{description}</div>
        {resolution && (
          <div style={{ marginTop: 6 }}>
            Что делать: {resolution}
            {basis && (
              <span style={{ marginLeft: 6 }}>
                <EvidenceBadge basis={basis} title="Основание рекомендации: выведено из типа связи, документировано или экспертное допущение." />
              </span>
            )}
          </div>
        )}
      </Callout>
    </div>
  );
}

/** Строка конфликта «A ↔ B» с бейджем серьёзности. */
export function ConflictEntry({ item }: { item: BasketConflict }) {
  const tone = conflictTone(item.severity);
  return (
    <CompatibilityEntry
      tone={tone}
      head={`${item.a_name} ↔ ${item.b_name}`}
      badge={<Badge tone={tone}>{item.conflict_label}</Badge>}
      description={item.description}
      resolution={item.resolution}
      basis={item.basis}
    />
  );
}

/** Строка зависимости «A → B». */
export function DependencyEntry({ item }: { item: BasketConflict }) {
  return (
    <CompatibilityEntry
      tone="info"
      head={`${item.a_name} → ${item.b_name}`}
      badge={<Badge tone="info">{item.conflict_label}</Badge>}
      description={item.description}
      resolution={item.resolution}
      basis={item.basis}
    />
  );
}

/** Строка усиления «A + B» (разрешения проблемы здесь нет по смыслу). */
export function SynergyEntry({ item }: { item: BasketConflict }) {
  return (
    <CompatibilityEntry
      tone="info"
      head={`${item.a_name} + ${item.b_name}`}
      badge={<Badge tone="info">{item.conflict_label}</Badge>}
      description={item.description}
      resolution={item.resolution}
      basis={item.basis}
    />
  );
}
