/** Экран 2. Выбор стадии разработки и проектных бюджетов. */
import { useStore } from '../store';
import { Callout, Card, Field, Select } from '../components/ui';

const STAGE_ADVICE: Record<string, string> = {
  concept:
    'На стадии концепта архитектурные решения стоят минимально. Сейчас имеет смысл закладывать решения уровня архитектуры и производственного процесса.',
  preproduction:
    'Предпроизводство — последний момент, когда архитектурные решения внедряются без переработки готовых материалов.',
  prototype:
    'Прототип позволяет проверить спорные решения экспериментом, но архитектурные изменения уже заметно дороже.',
  production:
    'Идёт массовое наполнение контента. Изменения архитектуры требуют переработки уже созданных материалов.',
  alpha:
    'Архитектура фактически зафиксирована. Доступны решения уровня алгоритмов, настроек и производственного процесса.',
  beta:
    'На стадии беты допустимы в основном настройки и точечные алгоритмические улучшения.',
  release:
    'До релиза изменения ограничены настройками и исправлениями, не влияющими на контент.',
  post_release:
    'После релиза доступны оптимизации настроек и выборочные алгоритмические улучшения, не требующие изменения контента.',
};

const BUDGET_FIELDS: { key: keyof import('../types').ProjectProfile; label: string }[] = [
  { key: 'cpu_budget', label: 'Бюджет CPU' },
  { key: 'gpu_budget', label: 'Бюджет GPU' },
  { key: 'ram_budget', label: 'Бюджет RAM' },
  { key: 'vram_budget', label: 'Бюджет VRAM' },
  { key: 'geometry_detail', label: 'Детализация геометрии' },
  { key: 'texture_quality', label: 'Качество текстур' },
  { key: 'view_distance', label: 'Дальность видимости' },
  { key: 'lighting_complexity', label: 'Сложность освещения' },
  { key: 'physics_complexity', label: 'Сложность физики' },
  { key: 'simulation_complexity', label: 'Сложность симуляций' },
  { key: 'npc_update_rate', label: 'Частота обновления NPC' },
  { key: 'network_update_rate', label: 'Частота сетевых обновлений' },
];

export function StageScreen() {
  const { profile, updateProfile, catalog } = useStore();
  const { enums } = catalog;
  if (!enums) return null;

  return (
    <>
      <Card
        title="Стадия разработки"
        hint="От стадии зависит стоимость внедрения: чем позже обнаружена необходимость оптимизации, тем дороже её внедрение."
      >
        <div className="chip-row" style={{ marginBottom: 14 }}>
          {enums.stages.map((stage) => (
            <button
              key={stage.value}
              className={`chip ${profile.stage === stage.value ? 'selected' : ''}`}
              onClick={() => updateProfile({ stage: stage.value })}
            >
              {stage.label}
            </button>
          ))}
        </div>
        <Callout tone="info" title="Что это означает">
          {STAGE_ADVICE[profile.stage] ?? ''}
        </Callout>
      </Card>

      <Card
        title="Проектные бюджеты"
        hint="Если точные значения неизвестны, задайте качественные уровни: они влияют на оценку соответствия решения дефицитным ресурсам."
      >
        <div className="grid grid-3">
          {BUDGET_FIELDS.map(({ key, label }) => (
            <Field key={String(key)} label={label}>
              <Select
                value={(profile[key] as string | null) ?? ''}
                options={enums.levels}
                placeholder="не задан"
                onChange={(value) => updateProfile({ [key]: value || null } as never)}
              />
            </Field>
          ))}
        </div>
      </Card>

      <Card title="Приоритет при сравнении решений">
        <div className="grid grid-2">
          <Field
            label="Что важнее для проекта"
            hint="Приоритет определяет веса критериев в методе TOPSIS."
          >
            <Select
              value={profile.priority}
              options={enums.priorities}
              onChange={(value) => updateProfile({ priority: value })}
            />
          </Field>
          <div>
            <div className="xsmall faint">Как это влияет на ранжирование</div>
            <ul className="reason-list">
              <li>
                <strong>Производительность</strong> — выше вес ожидаемого эффекта и соответствия
                ресурсным ограничениям.
              </li>
              <li>
                <strong>Качество</strong> — выше вес сохранения качества и соответствия исходной
                концепции.
              </li>
              <li>
                <strong>Стоимость разработки</strong> — выше вес трудозатрат и штрафа за позднее
                внедрение.
              </li>
            </ul>
          </div>
        </div>
      </Card>
    </>
  );
}
