/** Экран 1. Создание профиля игры. */
import { useStore } from '../store';
import { Card, Field, NumberInput, Select, Toggle } from '../components/ui';

/**
 * Скоуп проекта — Windows и Linux ПК. Остальные значения enum Platform
 * живут только для честности данных и в API, но в анкету не предлагаются.
 */
const QUESTIONNAIRE_PLATFORMS = ['pc_windows', 'pc_linux'];

const RESOLUTIONS = [
  { value: '720p', label: '720p' },
  { value: '1080p', label: '1080p (Full HD)' },
  { value: '1440p', label: '1440p (2K)' },
  { value: '2160p', label: '2160p (4K)' },
];

const QUALITY = [
  { value: 'low', label: 'низкое' },
  { value: 'medium', label: 'среднее' },
  { value: 'high', label: 'высокое' },
  { value: 'ultra', label: 'ультра' },
];

export function ProfileScreen() {
  const { profile, updateProfile, catalog } = useStore();
  const { enums, engines, functions } = catalog;

  if (!enums) return null;

  const selectedEngine = engines.find((engine) => engine.code === profile.engine);

  return (
    <>
      <Card
        title="Общие сведения о проекте"
        hint="Опишите будущую игру: формат, структуру мира, технологии и целевые показатели."
      >
        <div className="grid grid-2">
          <Field label="Название проекта">
            <input
              type="text"
              value={profile.name}
              onChange={(e) => updateProfile({ name: e.target.value })}
            />
          </Field>

          <Field label="Формат изображения">
            <Select
              value={profile.format}
              options={enums.formats}
              onChange={(value) => updateProfile({ format: value })}
            />
          </Field>

          <Field label="Структура игрового мира">
            <Select
              value={profile.world_type}
              options={enums.world_types}
              onChange={(value) => updateProfile({ world_type: value })}
            />
          </Field>

          <Field label="Масштаб мира">
            <Select
              value={profile.scale}
              options={enums.scales}
              onChange={(value) => updateProfile({ scale: value })}
            />
          </Field>

          <Field
            label="Масштаб проекта"
            hint={
              'Объём производства: сколько продукт делает и продолжает делать. '
              + 'Задаётся вручную и не зависит от других полей. Влияет только на базис '
              + 'памяти — стоянку движка и инструментов; объём мира учитывается отдельно, '
              + 'полем «Масштаб мира».'
            }
          >
            <Select
              value={profile.project_scale ?? 'medium'}
              options={enums.scales}
              onChange={(value) => updateProfile({ project_scale: value })}
            />
          </Field>

          <Field label="Игровой движок">
            <Select
              value={profile.engine}
              options={engines.map((engine) => ({ value: engine.code, label: engine.name }))}
              onChange={(value) => updateProfile({ engine: value, engine_version: null })}
            />
          </Field>

          <Field
            label="Версия движка"
            hint={selectedEngine ? `Доступные версии: ${selectedEngine.versions.join(', ')}` : undefined}
          >
            <Select
              value={profile.engine_version ?? ''}
              options={(selectedEngine?.versions ?? []).map((version) => ({
                value: version,
                label: version,
              }))}
              placeholder="версия не указана"
              onChange={(value) => updateProfile({ engine_version: value || null })}
            />
          </Field>
        </div>

        <div className="divider" />
        <Field
          label="Целевые платформы"
          hint="Решения, не поддерживаемые хотя бы одной платформой, будут исключены из рекомендаций."
        >
          <div className="chip-row">
            {enums.platforms
              .filter((platform) => QUESTIONNAIRE_PLATFORMS.includes(platform.value))
              .map((platform) => {
                const active = profile.platforms.includes(platform.value);
                return (
                  <button
                    key={platform.value}
                    className={`chip ${active ? 'selected' : ''}`}
                    onClick={() =>
                      updateProfile({
                        platforms: active
                          ? profile.platforms.filter((p) => p !== platform.value)
                          : [...profile.platforms, platform.value],
                      })
                    }
                  >
                    {platform.label}
                  </button>
                );
              })}
          </div>
        </Field>
      </Card>

      <Card title="Целевые показатели качества и производительности">
        <div className="grid grid-4">
          <Field label="Целевое разрешение">
            <Select
              value={profile.target_resolution}
              options={RESOLUTIONS}
              onChange={(value) => updateProfile({ target_resolution: value })}
            />
          </Field>
          <Field label="Целевое качество">
            <Select
              value={profile.target_quality}
              options={QUALITY}
              onChange={(value) => updateProfile({ target_quality: value })}
            />
          </Field>
            {profile.functions.includes('split_screen_rendering') && <Field label="Локальных камер" hint="Независимо от сетевых игроков; 1–8">
              <NumberInput value={profile.local_view_count ?? null} min={1} max={8}
                onChange={value => updateProfile({ local_view_count: value })} />
            </Field>}
            <Field label="Целевой FPS" hint="Допустимый диапазон 15–480">
            <NumberInput
              value={profile.target_fps}
              min={15}
              max={480}
              onChange={(value) => updateProfile({ target_fps: value ?? 60 })}
            />
          </Field>
          <Field
            label="Приоритет"
            hint="Определяет веса критериев при ранжировании решений."
          >
            <Select
              value={profile.priority}
              options={enums.priorities}
              onChange={(value) => updateProfile({ priority: value })}
            />
          </Field>
        </div>
      </Card>

      <Card
        title="Технический профиль исполнения"
        hint="Эти параметры отделяют реальную стоимость реализации от общей сложности игры. Если значение неизвестно, оставьте «не указано» — результат будет помечен как приблизительный."
      >
        <div className="grid grid-4">
          <Field label="Графический API / RHI">
            <Select
              value={profile.render_api}
              options={enums.render_apis}
              onChange={(value) => updateProfile({ render_api: value })}
            />
          </Field>
          <Field label="Накопитель">
            <Select
              value={profile.storage_type}
              options={enums.storage_types}
              onChange={(value) => updateProfile({ storage_type: value })}
            />
          </Field>
          <Field label="Модель памяти">
            <Select
              value={profile.memory_model}
              options={enums.memory_models}
              onChange={(value) => updateProfile({ memory_model: value })}
            />
          </Field>
          <Field label="Масштабирование">
            <Select
              value={profile.upscaling_method}
              options={enums.upscalers}
              onChange={(value) => updateProfile({ upscaling_method: value })}
            />
          </Field>
          <Field label="Streaming pool, ГБ" hint="Необязательно">
            <NumberInput
              value={profile.streaming_pool_gb ?? null}
              min={0.5}
              max={512}
              step={0.5}
              placeholder="не задан"
              onChange={(value) => updateProfile({ streaming_pool_gb: value })}
            />
          </Field>
          <Field label="Бюджет draw calls" hint="Необязательно">
            <NumberInput
              value={profile.draw_call_budget ?? null}
              min={100}
              max={1_000_000}
              step={100}
              placeholder="не задан"
              onChange={(value) => updateProfile({ draw_call_budget: value })}
            />
          </Field>
          <Field label="Радиус симуляции, м" hint="Необязательно">
            <NumberInput
              value={profile.simulation_radius_m ?? null}
              min={0}
              max={100_000}
              step={10}
              placeholder="не задан"
              onChange={(value) => updateProfile({ simulation_radius_m: value })}
            />
          </Field>
          <Field label="Частота физической симуляции, Гц" hint="Сетевой tick задаётся отдельно от физики; здесь он не моделируется">
            <NumberInput
              value={profile.physics_tick_hz ?? null}
              min={15}
              max={480}
              step={0.1}
              placeholder="не задан"
              onChange={(value) => updateProfile({ physics_tick_hz: value })}
            />
          </Field>
          <Field label="Сложность аудио" hint="Необязательно">
            <Select
              value={profile.audio_complexity ?? ''}
              options={enums.levels}
              placeholder="не указана"
              onChange={(value) => updateProfile({ audio_complexity: value || null })}
            />
          </Field>
          <div style={{ display: 'flex', alignItems: 'end', paddingBottom: 8 }}>
            <Toggle
              checked={profile.frame_generation}
              onChange={(value) => updateProfile({ frame_generation: value })}
              label="Генерация кадров"
            />
          </div>
          {profile.frame_generation && (
            <Field label="Целевой базовый FPS" hint="Реальные кадры до генерации. Без этого параметра требования не снижаются; стоимость генератора неизвестна.">
              <NumberInput
                value={profile.base_render_fps ?? null}
                min={15}
                max={profile.target_fps}
                step={1}
                placeholder="не задан"
                onChange={(value) => updateProfile({ base_render_fps: value })}
              />
            </Field>
          )}
        </div>
      </Card>

      <Card
        title="Обязательные ограничения"
        hint="Допустимая сложность исключает решения выше указанной. Предел размера сравнивается с оценочным объёмом сборки. Заполняйте только действительно заданные."
      >
        <div className="grid grid-4">
          <Field
            label="Предел размера игры, ГБ"
            hint="Сравнивается с оценочным объёмом установки: расхождение показывается как предупреждение, а при очень жёстком пределе решения, увеличивающие размер, исключаются"
          >
            <NumberInput
              value={profile.size_limit_gb ?? null}
              min={1}
              placeholder="не задан"
              onChange={(value) => updateProfile({ size_limit_gb: value })}
            />
          </Field>
        </div>

        <div className="divider" />
        <Field
          label="Допустимая сложность внедрения"
          hint={`Решения со сложностью выше ${profile.complexity_tolerance ?? 5} из 5 будут исключены.`}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <input
              type="range"
              min={1}
              max={5}
              value={profile.complexity_tolerance ?? 5}
              onChange={(e) => {
                const value = Number(e.target.value);
                updateProfile({ complexity_tolerance: value === 5 ? null : value });
              }}
            />
            <span className="mono nowrap">
              {profile.complexity_tolerance ?? 5} / 5
              {profile.complexity_tolerance === null && <span className="faint"> — без ограничения</span>}
            </span>
          </div>
        </Field>
      </Card>

      <Card
        title="Пределы для проверки"
        hint="Не фильтруют решения: система сравнивает с ними требуемое железо и показывает расхождение как предупреждение."
      >
        <div className="grid grid-4">
          <Field label="Предел RAM, ГБ">
            <NumberInput
              value={profile.ram_limit_gb ?? null}
              min={1}
              placeholder="не задан"
              onChange={(value) => updateProfile({ ram_limit_gb: value })}
            />
          </Field>
          <Field label="Предел VRAM, ГБ">
            <NumberInput
              value={profile.vram_limit_gb ?? null}
              min={1}
              placeholder="не задан"
              onChange={(value) => updateProfile({ vram_limit_gb: value })}
            />
          </Field>
        </div>
      </Card>

      <Card
        title="Сетевой режим"
        hint="Влияет на оценку сетевой нагрузки и на подбор решений репликации."
      >
        <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <Toggle
            checked={profile.multiplayer}
            onChange={(value) => updateProfile({ multiplayer: value, player_count: value ? Math.max(2, profile.player_count) : 1 })}
            label="Мультиплеер предусмотрен"
          />
          {profile.multiplayer && (
            <div style={{ minWidth: 180 }}>
              <Field label="Игроков в сессии">
                <NumberInput
                  value={profile.player_count}
                  min={2}
                  onChange={(value) => updateProfile({ player_count: Math.max(1, value ?? 1) })}
                />
              </Field>
            </div>
          )}
          {profile.multiplayer && (
            <div style={{ minWidth: 220 }}>
              <Field label="Сетевая схема">
                <Select
                  value={profile.network_topology}
                  options={enums.network_topologies}
                  onChange={(value) => updateProfile({ network_topology: value })}
                />
              </Field>
            </div>
          )}
        </div>
      </Card>

      <Card
        title="Масштаб сцены"
        hint="Указываются одновременно активные сущности, а не всё содержимое проекта. Точное число имеет приоритет над уровнем. Масштаб мира влияет на стриминг и память, но не увеличивает стоимость кадра при том же числе активных сущностей."
      >
        <div className="grid grid-2">
          <Field label="Активные объекты (уровень)">
            <Select
              value={profile.object_count_level}
              options={enums.levels}
              onChange={(value) => updateProfile({ object_count_level: value })}
            />
          </Field>
          <Field label="Активные NPC (уровень)">
            <Select
              value={profile.npc_count_level}
              options={enums.levels}
              onChange={(value) => updateProfile({ npc_count_level: value })}
            />
          </Field>
          <Field label="Точное число активных объектов" hint="Необязательно">
            <NumberInput
              value={profile.object_count ?? null}
              min={0}
              placeholder="не задано"
              onChange={(value) => updateProfile({ object_count: value })}
            />
          </Field>
          <Field label="Точное число активных NPC" hint="Необязательно">
            <NumberInput
              value={profile.npc_count ?? null}
              min={0}
              placeholder="не задано"
              onChange={(value) => updateProfile({ npc_count: value })}
            />
          </Field>
        </div>
        <p className="xsmall faint" style={{ marginTop: 10 }}>
          Доступно игровых функций в базе знаний: {functions.length}.
        </p>
      </Card>
    </>
  );
}
