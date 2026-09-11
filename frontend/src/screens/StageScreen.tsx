/** Экран 2. Выбор стадии разработки и проектных бюджетов. */
import { useEffect, useState } from 'react';
import { useStore } from '../store';
import { Callout, Card, Field, Select } from '../components/ui';
import { StageGuidanceBlock } from '../components/StageGuidance';
import { api } from '../api';
import type { ProjectProfile, StageGuidance } from '../types';

const BUDGET_FIELDS: { key: keyof ProjectProfile; label: string }[] = [
  { key: 'cpu_budget', label: 'Бюджет CPU' },
  { key: 'gpu_budget', label: 'Бюджет GPU' },
  { key: 'ram_budget', label: 'Бюджет RAM' },
  { key: 'vram_budget', label: 'Бюджет VRAM' },
];

export function StageScreen() {
  const { profile, updateProfile, catalog, result } = useStore();
  const { enums } = catalog;
  const [guidance, setGuidance] = useState<StageGuidance | null>(null);
  // Сбой запроса нельзя показывать как «загружается…»: без отдельного признака
  // ошибки пользователь видел бесконечную загрузку без объяснения и без
  // возможности повторить запрос.
  const [guidanceError, setGuidanceError] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  /**
   * Подсказка запрашивается отдельным маршрутом, а не берётся из результата
   * расчёта: пользователь должен видеть ограничения стадии сразу после выбора,
   * а не после нажатия «рассчитать». Результат расчёта используется, когда он
   * уже есть для этой же стадии, — лишний запрос ни к чему.
   */
  useEffect(() => {
    if (!enums) return;
    if (result?.stage_guidance && result.profile.stage === profile.stage) {
      setGuidance(result.stage_guidance);
      setGuidanceError(false);
      return;
    }
    let cancelled = false;
    setGuidanceError(false);
    void api
      .stageGuidance(profile.stage)
      .then((next) => {
        if (!cancelled) setGuidance(next);
      })
      .catch(() => {
        if (!cancelled) {
          setGuidance(null);
          setGuidanceError(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [enums, profile.stage, result, reloadKey]);

  if (!enums) return null;

  return (
    <>
      <Card
        title="Стадия разработки"
        hint="Стадия уточняет риск и стоимость изменений. Реализованная корзина служит основой сравнения: сохранение решения, настройка и замена требуют разного объёма работ. Сама стадия не исключает работающие решения из аппаратного расчёта."
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
        {guidance ? (
          <StageGuidanceBlock guidance={guidance} />
        ) : guidanceError ? (
          <Callout tone="warn" title="Описание стадии не загрузилось">
            Сервер не отдал подсказку по этой стадии. Выбор стадии и расчёт это не
            блокирует, но ограничения стадии ниже не показаны.{' '}
            <button className="btn btn-sm" onClick={() => setReloadKey((key) => key + 1)}>
              Повторить запрос
            </button>
          </Callout>
        ) : (
          <Callout tone="info" title="Что это означает">
            Описание стадии загружается…
          </Callout>
        )}
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
