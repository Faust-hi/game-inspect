import type { HardwareEstimate } from '../types';
import { Callout } from './ui';

/** The same limitations survive navigation and browser printing. */
export function HardwareWarnings({ hardware }: { hardware: HardwareEstimate }) {
  const messages = [...new Set([
    ...(hardware.unmet_limits ?? []), ...(hardware.applicability_limits ?? []),
    ...(hardware.modeling_gaps ?? []), ...hardware.caveats,
  ])];
  return <>
    {hardware.exceeds_catalog && <Callout tone="danger" title="Подходящая конфигурация не найдена">
      Каталог не покрывает все требования. Причины и ограничения перечислены ниже.
    </Callout>}
    {messages.length > 0 && <Callout tone="warn" title="Ограничения аппаратной оценки">
      <ul>{messages.map(message => <li key={message}>{message}</li>)}</ul>
    </Callout>}
  </>;
}
