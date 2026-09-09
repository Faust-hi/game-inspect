import type { ImplementationTransition as Transition } from '../types';

const labels: Record<string, string> = {
  new: 'Новое внедрение', retained: 'Уже реализовано', adaptation: 'Адаптация',
  replacement: 'Замена реализации', migration: 'Перенос', removal: 'Удаление реализации',
  possible_replacement: 'Возможная замена — требуется уточнение',
};
const scopes: Record<string, string> = {
  none: 'без повторного внедрения', local_adjustment: 'локальная корректировка',
  subsystem_rework: 'переработка подсистемы', implementation_rework: 'переработка реализации',
  architecture_migration: 'перенос архитектуры', initial_integration: 'исходное внедрение',
  decommission: 'отключение и проверка зависимостей',
  dependency_rework: 'адаптация зависимой реализации', interface_review: 'проверка совместимости интерфейсов',
};

export function TransitionDetails({ item }: { item: Transition }) {
  return <div className="small" style={{ marginTop: 10 }}>
    <strong>{labels[item.status] ?? item.status}: {scopes[item.scope] ?? item.scope}</strong>
    <div>Относительные трудозатраты: {item.cost_min}–{item.cost_max} балла. Это экспертный диапазон, не часы.</div>
    <div>Сложность интеграции: {item.complexity_min}–{item.complexity_max} из 5 (экспертная оценка).</div>
    {item.replaces.length > 0 && <div>Заменяет: {item.replaces.join(', ')}</div>}
    <ul className="reason-list">{item.reasons.map((reason, i) => <li key={i}>{reason}</li>)}</ul>
  </div>;
}
