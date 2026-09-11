/**
 * Экран «Трудоёмкость и календарный план».
 *
 * Ключевые правила расчёта, которые экран обязан показывать явно:
 *  - human-days не уменьшаются от роста команды — растёт только параллелизм;
 *  - календарный срок определяется графом зависимостей и доступностью ролей;
 *  - P50 — наиболее вероятный сценарий, P80 включает риск переработки;
 *  - при отсутствии данных диапазон расширяется, а не заменяется точным числом.
 */
import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading, Metric, Tabs } from '../components/ui';
import { EstimateRange, EvidenceBadge } from '../components/Evidence';
import type { Schedule, TeamScenario } from '../types';

const PACKAGE_LABEL: Record<string, string> = {
  design: 'проектирование',
  feasibility: 'прототип и проверка осуществимости',
  integration: 'интеграция',
  content: 'подготовка контента',
  optimization: 'оптимизация',
  qa: 'QA и регрессия',
  release: 'стабилизация релиза',
  documentation: 'документация и поддержка',
};

const ROLE_LABEL: Record<string, string> = {
  designer: 'дизайнер',
  engineer: 'инженер',
  artist: 'художник / технический художник',
  qa: 'QA',
  writer: 'технический писатель',
};

const BASIS_LABEL: Record<string, string> = {
  expert_estimate: 'экспертная оценка',
  derived: 'выведено',
  measured: 'измерено',
  documented: 'документировано',
};

function TaskTable({ schedule }: { schedule: Schedule }) {
  const [onlyCritical, setOnlyCritical] = useState(false);
  const tasks = useMemo(
    () => (onlyCritical ? schedule.tasks.filter(t => t.critical) : schedule.tasks),
    [schedule.tasks, onlyCritical],
  );
  const horizon = useMemo(
    () => Math.max(1, ...schedule.tasks.map(t => Math.max(t.finish_p50, t.finish_p80))),
    [schedule.tasks],
  );

  return (
    <>
      <div className="filter-row">
        <label className="small" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <input type="checkbox" checked={onlyCritical} onChange={e => setOnlyCritical(e.target.checked)} />
          только критический путь
        </label>
        <span className="xsmall faint">Показано {tasks.length} из {schedule.tasks.length} пакетов работ</span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Пакет работ</th>
              <th>Роль</th>
              <th>Стадия</th>
              <th>Оценка</th>
              <th>Окно P50 / P80</th>
              <th>Диаграмма</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map(task => (
              <tr key={task.code}>
                <td className="small">
                  <strong>{PACKAGE_LABEL[task.package_type] ?? task.package_type}</strong>
                  <div className="xsmall faint mono">{task.method_code}</div>
                </td>
                <td className="small">
                  {ROLE_LABEL[task.role] ?? task.role}
                  {task.dependencies.length > 0 && (
                    <div className="xsmall faint">зависит от: {task.dependencies.length}</div>
                  )}
                </td>
                <td className="small">
                  {task.recommended_stage}
                  {task.stage_note && (
                    <div className="xsmall faint" title={task.stage_note}>
                      из пакета: {task.stage_note}
                    </div>
                  )}
                  {task.critical && <div><Badge tone="danger">критический путь</Badge></div>}
                </td>
                <td className="small">
                  <EstimateRange minimum={task.minimum_days} p50={task.p50_days} p80={task.p80_days} unit=" чел.-дн." basis={task.basis} />
                </td>
                <td className="small mono xsmall">
                  P50 {task.start_p50}–{task.finish_p50}
                  <div>P80 {task.start_p80}–{task.finish_p80}</div>
                </td>
                <td style={{ minWidth: 160 }}>
                  <div className="schedule-bar">
                    <span className="p80" style={{
                      left: `${(task.start_p80 / horizon) * 100}%`,
                      width: `${((task.finish_p80 - task.start_p80) / horizon) * 100}%`,
                    }} />
                    <span className="p50" style={{
                      left: `${(task.start_p50 / horizon) * 100}%`,
                      width: `${((task.finish_p50 - task.start_p50) / horizon) * 100}%`,
                    }} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export function ScheduleScreen() {
  const { profile, basket } = useStore();
  const [team, setTeam] = useState('small_2_5');
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [teams, setTeams] = useState<TeamScenario[]>([]);
  const [teamsError, setTeamsError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState('packages');

  useEffect(() => {
    let active = true;
    void api.teams()
      .then(list => { if (active) setTeams(list); })
      .catch((cause: unknown) => {
        // Список профилей команд влияет на календарь. Раньше сбой молча
        // подставлял пустой сценарий с нулями, и карточка команды показывала
        // «0%» как реальные значения профиля. Теперь сбой объявляется.
        if (active) {
          setTeamsError(cause instanceof Error ? cause.message : 'Не удалось загрузить профили команд');
        }
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (basket.length === 0) {
      setSchedule(null);
      return;
    }
    let active = true;
    setLoading(true);
    setError(null);
    void api.schedule(profile, basket, team)
      .then(next => { if (active) setSchedule(next); })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Не удалось построить план');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [profile, basket, team]);

  const activeTeam = schedule?.team ?? teams.find(t => t.code === team) ?? null;
  const p80Inconsistent = !!schedule
    && schedule.effort.p50 != null
    && schedule.effort.p80 != null
    && schedule.effort.p80 < schedule.effort.p50;

  const byPackage = useMemo(() => {
    if (!schedule) return [];
    const map = new Map<string, { count: number; p50: number; p80: number; basis: string }>();
    schedule.tasks.forEach((task) => {
      const entry = map.get(task.package_type) ?? { count: 0, p50: 0, p80: 0, basis: task.basis };
      entry.count += 1;
      entry.p50 += task.p50_days;
      entry.p80 += task.p80_days;
      map.set(task.package_type, entry);
    });
    return Array.from(map.entries());
  }, [schedule]);

  if (basket.length === 0) {
    return (
      <Empty>
        <div style={{ marginBottom: 10 }}>
          Корзина пуста. Трудоёмкость и календарный план рассчитываются для выбранного набора решений.
        </div>
      </Empty>
    );
  }

  return (
    <>
      <Card
        title="Трудоёмкость и календарный план"
        hint="Трудоёмкость измеряется в человеко-днях и не зависит от размера команды. Команда влияет на календарный срок, а не на объём работы."
        actions={
          teams.length > 0 ? (
            <select className="select" value={team} onChange={e => setTeam(e.target.value)}>
              {teams.map(t => <option key={t.code} value={t.code}>{t.name}</option>)}
            </select>
          ) : (
            <span className="small faint">
              {teamsError ? `Профили команд недоступны: ${teamsError}` : 'Загрузка профилей команд…'}
            </span>
          )
        }
      >
        {teamsError && (
          <Callout tone="warn" title="Профили команд не загрузились">
            Календарь рассчитан для профиля «{team}» с параметрами по умолчанию;
            список доступных профилей и их характеристики не показаны.
          </Callout>
        )}
        {loading && <Loading text="Расчёт плана…" />}
        {error && <Callout tone="danger" title="План не построен">{error}</Callout>}
        {p80Inconsistent && (
          <Callout tone="danger" title="Нарушена монотонность оценок">
            P80 меньше P50. Это признак противоречивых данных: результат нельзя показывать
            как план, пока расхождение не устранено.
          </Callout>
        )}
        {schedule && !loading && (
          <>
            <div className="stat-grid">
              <Metric
                label="Трудоёмкость P50"
                value={`${schedule.effort.p50 ?? '—'} чел.-дн.`}
                hint={`P80: ${schedule.effort.p80 ?? '—'} чел.-дн.`}
              />
              <Metric
                label="Календарь P50"
                value={`${schedule.calendar.p50 ?? '—'} дн.`}
                hint={`P80: ${schedule.calendar.p80 ?? '—'} дн.`}
              />
              <Metric label="Пакетов работ" value={schedule.tasks.length} />
              <Metric label="Критический путь" value={schedule.critical_path.length} />
              <Metric
                label="Незакрытых зависимостей"
                value={schedule.unresolved_dependencies.length}
              />
            </div>
            <p className="xsmall faint">
              Основание расчёта: <EvidenceBadge basis={schedule.evidence_basis} />
            </p>
          </>
        )}
      </Card>

      {activeTeam && (
        <Card title={`Профиль команды: ${activeTeam.name}`} hint={activeTeam.description}>
          <div className="stat-grid">
            <Metric label="Численность" value={activeTeam.team_size} />
            <Metric label="Параллельных задач" value={activeTeam.parallel_tracks} />
            <Metric label="Время на коммуникацию" value={`${Math.round(activeTeam.communication_pct * 100)}%`} />
            <Metric label="Незапланированная работа" value={`${Math.round(activeTeam.unplanned_pct * 100)}%`} />
          </div>
          <p className="xsmall faint" style={{ marginBottom: 0 }}>
            Профиль команды — сценарный шаблон, а не отраслевой стандарт: фактическую численность
            можно переопределить. Увеличение команды не уменьшает человеко-дни.
          </p>
        </Card>
      )}

      {schedule && schedule.unresolved_dependencies.length > 0 && (
        <Callout tone="warn" title="Незакрытые зависимости">
          <ul className="reason-list">
            {schedule.unresolved_dependencies.map(item => <li key={item}>{item}</li>)}
          </ul>
        </Callout>
      )}

      {schedule && (
        <Card title="Работы и сроки">
          <Tabs
            tabs={[
              { key: 'packages', label: 'Пакеты работ', count: schedule.tasks.length },
              { key: 'summary', label: 'Сводка по типам', count: byPackage.length },
              { key: 'critical', label: 'Критический путь', count: schedule.critical_path.length },
            ]}
            active={tab}
            onChange={setTab}
          />
          {tab === 'packages' && <TaskTable schedule={schedule} />}
          {tab === 'summary' && (
            <div style={{ overflowX: 'auto' }}>
              <table className="table">
                <thead>
                  <tr><th>Тип работ</th><th>Пакетов</th><th>Трудоёмкость</th><th>Основание</th></tr>
                </thead>
                <tbody>
                  {byPackage.map(([type, entry]) => (
                    <tr key={type}>
                      <td className="small">{PACKAGE_LABEL[type] ?? type}</td>
                      <td className="small mono">{entry.count}</td>
                      <td className="small">
                        <EstimateRange p50={Math.round(entry.p50 * 10) / 10} p80={Math.round(entry.p80 * 10) / 10} unit=" чел.-дн." basis={entry.basis} />
                      </td>
                      <td className="small">
                        {BASIS_LABEL[entry.basis] ?? entry.basis}
                        {entry.basis === 'expert_estimate' && (
                          <div className="xsmall faint">не измерение; для ранжирования, не для обещания срока</div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {tab === 'critical' && (
            schedule.critical_path.length === 0
              ? <Empty>Критический путь не выделен: обязательных последовательных зависимостей нет.</Empty>
              : (
                <ol className="reason-list">
                  {schedule.critical_path.map((code, index) => (
                    <li key={`${code}-${index}`}><span className="mono small">{code}</span></li>
                  ))}
                </ol>
              )
          )}
        </Card>
      )}

      {schedule && schedule.stage_notes.length > 0 && (
        <Card title="Влияние стадии проекта" hint="Поздняя стадия не скрывает метод: она увеличивает риск и объём переработки.">
          <ul className="reason-list">
            {schedule.stage_notes.map(note => <li key={note}>{note}</li>)}
          </ul>
        </Card>
      )}
    </>
  );
}
