/** Корневой компонент: навигация по этапам работы, экспорт и административный раздел. */
import { useMemo, useState, type ReactNode } from 'react';
import { useEnsureResult, useStore } from './store';
import { api } from './api';
import { Callout, Loading, Toast } from './components/ui';
import { exportProjectJson, exportProjectPdf } from './export';
import { ProfileScreen } from './screens/ProfileScreen';
import { StageScreen } from './screens/StageScreen';
import { FunctionsScreen } from './screens/FunctionsScreen';
import { SolutionsScreen } from './screens/SolutionsScreen';
import { CompareScreen } from './screens/CompareScreen';
import { BasketScreen } from './screens/BasketScreen';
import { LoadProfileScreen } from './screens/LoadProfileScreen';
import { HardwareScreen } from './screens/HardwareScreen';
import { SimilarGamesScreen } from './screens/SimilarGamesScreen';
import { PlanScreen } from './screens/PlanScreen';
import { RisksScreen } from './screens/RisksScreen';
import { AdminScreen } from './screens/AdminScreen';

/** Этапы работы с проектом (экраны 1–11 раздела 7 плана). */
type StepKey =
  | 'profile'
  | 'stage'
  | 'functions'
  | 'solutions'
  | 'risks'
  | 'basket'
  | 'load'
  | 'hardware'
  | 'similar'
  | 'plan';

interface StepDef {
  key: StepKey;
  label: string;
  hint: string;
}

const STEPS: StepDef[] = [
  { key: 'profile', label: 'Профиль игры', hint: 'Формат, мир, движок, платформы' },
  { key: 'stage', label: 'Стадия и бюджеты', hint: 'Стадия разработки и приоритеты' },
  { key: 'functions', label: 'Игровые функции', hint: 'Что должно работать в игре' },
  { key: 'solutions', label: 'Варианты реализации', hint: 'Подбор и ранжирование решений' },
  { key: 'risks', label: 'Риски проекта', hint: 'Что может стать проблемой на текущей стадии' },
  { key: 'basket', label: 'Корзина решений', hint: 'Выбранный набор и совместимость' },
  { key: 'load', label: 'Профиль нагрузки', hint: 'Сводное влияние набора' },
  { key: 'hardware', label: 'Оборудование', hint: 'Референсный минимальный класс' },
  { key: 'similar', label: 'Похожие игры', hint: 'Сверка с подтверждёнными примерами' },
  { key: 'plan', label: 'Итоговый план', hint: 'Отчёт по проекту' },
];

/** Этапы, которым необходим уже выполненный расчёт. */
const RESULT_STEPS: StepKey[] = ['risks', 'load', 'hardware', 'similar', 'plan'];

/** Каркас экранов-заглушек: загрузка каталога и ошибка без сайдбара. */
function ShellMessage({ children }: { children: ReactNode }) {
  return (
    <div className="app">
      <div className="layout">
        <main className="content">
          <div className="content-inner">{children}</div>
        </main>
      </div>
    </div>
  );
}

export function App() {
  const {
    profile,
    basket,
    result,
    resultStale,
    catalog,
    calculating,
    calculate,
    calculateError,
    toggleBasket,
    loadProject,
    reloadCatalog,
  } = useStore();

  const [step, setStep] = useState<StepKey>('profile');
  const [showAdmin, setShowAdmin] = useState(false);
  const [compareCodes, setCompareCodes] = useState<string[] | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [projectId, setProjectId] = useState('');

  const hasFunctions = profile.functions.length > 0;
  const hasResult = result !== null;

  const available = useMemo<Record<StepKey, boolean>>(
    () => ({
      profile: true,
      stage: true,
      functions: true,
      solutions: hasFunctions,
      risks: hasResult,
      basket: hasFunctions,
      load: hasResult,
      hardware: hasResult,
      similar: hasResult,
      plan: hasResult,
    }),
    [hasFunctions, hasResult],
  );

  // Экраны, строящиеся по результатам расчёта, при переходе на них
  // расчёт выполняется автоматически, если он ещё не был сделан.
  useEnsureResult(!showAdmin && hasFunctions && RESULT_STEPS.includes(step));

  const stepBadge = (key: StepKey): number | null => {
    if (key === 'functions') return profile.functions.length;
    if (key === 'solutions' && result) return result.recommendations.length;
    if (key === 'basket') return basket.length;
    if (key === 'risks' && result) return result.risks.length;
    return null;
  };

  const handleSave = async () => {
    try {
      const { public_id } = await api.saveProject(profile, basket);
      setProjectId(public_id);
      setToast(`Проект сохранён. Идентификатор: ${public_id}`);
    } catch (error) {
      setToast(`Не удалось сохранить проект: ${(error as Error).message}`);
    }
  };

  const handleLoad = async () => {
    const entered = window.prompt('Идентификатор сохранённого проекта', projectId);
    if (!entered) return;
    try {
      const project = await api.loadProject(entered.trim());
      loadProject(project.profile, project.basket);
      setProjectId(project.public_id);
      setStep('profile');
      setToast(`Проект «${project.name}» загружен`);
    } catch (error) {
      setToast(`Проект не найден: ${(error as Error).message}`);
    }
  };

  const handleExportJson = () => {
    exportProjectJson(profile, basket, result);
    setToast('Файл JSON сформирован');
  };

  const handleExportPdf = () => {
    setToast('Откроется диалог печати: выберите «Сохранить как PDF»');
    exportProjectPdf();
  };

  if (catalog.loading) {
    return (
      <ShellMessage>
        <Loading text="Загрузка базы инженерных знаний…" />
      </ShellMessage>
    );
  }

  if (catalog.error) {
    return (
      <ShellMessage>
        <Callout tone="danger" title="Не удалось загрузить каталоги">
          {catalog.error}
        </Callout>
        <p className="muted" style={{ marginTop: 12 }}>
          Убедитесь, что backend запущен и доступен по адресу <code>/api</code>.
        </p>
        <button className="btn btn-primary" onClick={() => void reloadCatalog()}>
          Повторить
        </button>
      </ShellMessage>
    );
  }

  const renderStep = () => {
    switch (step) {
      case 'profile':
        return <ProfileScreen />;
      case 'stage':
        return <StageScreen />;
      case 'functions':
        return <FunctionsScreen />;
      case 'solutions':
        return <SolutionsScreen onCompare={setCompareCodes} />;
      case 'risks':
        return <RisksScreen />;
      case 'basket':
        return <BasketScreen />;
      case 'load':
        return <LoadProfileScreen />;
      case 'hardware':
        return <HardwareScreen />;
      case 'similar':
        return <SimilarGamesScreen />;
      case 'plan':
        return (
          <PlanScreen
            onExportJson={handleExportJson}
            onExportPdf={handleExportPdf}
            projectId={projectId || null}
            onSave={handleSave}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          ИС оптимизации разработки игр
          {/* Фоновый пересчёт после правки анкеты должен быть заметен. */}
          <small>{calculating ? 'расчёт…' : profile.name}</small>
        </div>
        <div className="spacer" />
        <div className="header-actions no-print">
          <button
            className={`header-link ${!showAdmin ? 'active' : ''}`}
            onClick={() => setShowAdmin(false)}
          >
            Проект
          </button>
          <button
            className={`header-link ${showAdmin ? 'active' : ''}`}
            onClick={() => setShowAdmin(true)}
          >
            Администрирование
          </button>
          <button className="header-link" onClick={() => void handleSave()}>
            Сохранить
          </button>
          <button className="header-link" onClick={() => void handleLoad()}>
            Загрузить
          </button>
          <button className="header-link" onClick={handleExportJson}>
            Экспорт JSON
          </button>
          <button className="header-link" onClick={handleExportPdf}>
            Экспорт PDF
          </button>
        </div>
      </header>

      <div className="layout">
        {!showAdmin && (
          <aside className="sidebar">
            <div className="sidebar-title">Этапы работы</div>
            <div className="step-list">
              {STEPS.map((item, index) => {
                const enabled = available[item.key];
                const count = stepBadge(item.key);
                return (
                  <button
                    key={item.key}
                    className={`step-item ${step === item.key ? 'active' : ''}`}
                    disabled={!enabled}
                    title={enabled ? item.hint : 'Этап станет доступен после заполнения предыдущих'}
                    onClick={() => setStep(item.key)}
                  >
                    <span className="num">{index + 1}</span>
                    {item.label}
                    {count !== null && <span className="badge-count">{count}</span>}
                  </button>
                );
              })}
            </div>
          </aside>
        )}

        <main className="content">
          <div className="content-inner">
            {showAdmin ? (
              <AdminScreen />
            ) : (
              <>
                {calculateError && (
                  <Callout tone="danger" title="Расчёт не выполнен">
                    {calculateError}
                  </Callout>
                )}
                {resultStale && (
                  <Callout tone="warn" title="Данные изменены, результат нужно обновить">
                    Показан расчёт для предыдущих значений профиля или корзины.
                    <button
                      className="btn btn-primary"
                      style={{ marginTop: 10 }}
                      onClick={() => void calculate()}
                    >
                      Пересчитать
                    </button>
                  </Callout>
                )}
                {renderStep()}
              </>
            )}
          </div>
        </main>
      </div>

      {compareCodes && compareCodes.length > 0 && (
        <CompareScreen
          codes={compareCodes}
          onClose={() => setCompareCodes(null)}
          onToggle={toggleBasket}
        />
      )}

      {toast && <Toast message={toast} onDone={() => setToast(null)} />}
    </div>
  );
}
