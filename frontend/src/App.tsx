/** Корневой компонент: навигация по этапам работы и административный раздел. */
import { useMemo, useState, type ReactNode } from 'react';
import { useEnsureResult, useStore } from './store';
import { Callout, Loading } from './components/ui';
import { ProfileScreen } from './screens/ProfileScreen';
import { StageScreen } from './screens/StageScreen';
import { FunctionsScreen } from './screens/FunctionsScreen';
import { SolutionsScreen } from './screens/SolutionsScreen';
import { CompareScreen } from './screens/CompareScreen';
import { BasketScreen } from './screens/BasketScreen';
import { LoadProfileScreen } from './screens/LoadProfileScreen';
import { HardwareScreen } from './screens/HardwareScreen';
import { PlanScreen } from './screens/PlanScreen';
import { RisksScreen } from './screens/RisksScreen';
import { AdminScreen } from './screens/AdminScreen';
import { EvidenceScreen } from './screens/EvidenceScreen';
import { DependenciesScreen } from './screens/DependenciesScreen';

/** Этапы работы с проектом (экраны раздела 7 плана, упрощённый MVP). */
type StepKey =
  | 'profile'
  | 'stage'
  | 'functions'
  | 'solutions'
  | 'evidence'
  | 'dependencies'
  | 'risks'
  | 'basket'
  | 'load'
  | 'hardware'
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
  { key: 'evidence', label: 'Доказательства', hint: 'Источники, утверждения и локаторы' },
  { key: 'dependencies', label: 'Зависимости и конфликты', hint: 'Граф технологий, проверки и связи методов' },
  { key: 'risks', label: 'Риски проекта', hint: 'Что может стать проблемой на текущей стадии' },
  { key: 'basket', label: 'Корзина решений', hint: 'Выбранный набор и совместимость' },
  { key: 'load', label: 'Профиль нагрузки', hint: 'Сводное влияние набора' },
  { key: 'hardware', label: 'Оборудование', hint: 'Референсный минимальный класс' },
  { key: 'plan', label: 'Итоговый план', hint: 'Отчёт по проекту' },
];

/** Этапы, которым необходим уже выполненный расчёт. */
const RESULT_STEPS: StepKey[] = ['risks', 'load', 'hardware', 'plan'];

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
    catalog,
    calculating,
    calculate,
    calculateError,
    toggleBasket,
    reloadCatalog,
    storageError,
  } = useStore();

  const [step, setStep] = useState<StepKey>('profile');
  const [showAdmin, setShowAdmin] = useState(false);
  const [compareCodes, setCompareCodes] = useState<string[] | null>(null);

  const hasFunctions = profile.functions.length > 0;
  const hasResult = result !== null;

  const available = useMemo<Record<StepKey, boolean>>(
    () => ({
      profile: true,
      stage: true,
      functions: true,
      solutions: hasFunctions,
      evidence: true,
      dependencies: true,
      risks: hasResult,
      basket: hasFunctions,
      load: hasResult,
      hardware: hasResult,
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
      case 'evidence':
        return <EvidenceScreen />;
      case 'dependencies':
        return <DependenciesScreen />;
      case 'risks':
        return <RisksScreen />;
      case 'basket':
        return <BasketScreen />;
      case 'load':
        return <LoadProfileScreen />;
      case 'hardware':
        return <HardwareScreen />;
      case 'plan':
        return <PlanScreen />;
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
          {storageError && <span role="alert">{storageError}</span>}
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
                    <button
                      className="btn btn-primary"
                      style={{ marginTop: 10 }}
                      onClick={() => void calculate()}
                    >
                      Повторить расчёт
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

    </div>
  );
}
