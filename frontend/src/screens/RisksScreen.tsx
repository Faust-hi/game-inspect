/** Экран рисков проекта (шаг 2 алгоритма раздела 4). */
import { useEnsureResult, useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading, severityLabel, severityTone } from '../components/ui';
import type { Risk } from '../types';

const SEVERITY_ORDER: Record<string, number> = { high: 0, medium: 1, low: 2 };

function RiskItem({ risk }: { risk: Risk }) {
  return (
    <div className="method-row">
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
        <strong>{risk.title}</strong>
        <Badge tone={severityTone(risk.severity)}>{severityLabel(risk.severity)}</Badge>
      </div>
      <p className="small muted" style={{ marginTop: 6 }}>
        {risk.description}
      </p>
      <div className="xsmall faint" style={{ marginTop: 4 }}>
        <strong>Что делать:</strong> {risk.advice}
      </div>
    </div>
  );
}

export function RisksScreen() {
  const { result, calculating, calculate, profile } = useStore();

  // Без выбранных функций расчёт не запускается: ниже показана подсказка.
  useEnsureResult(profile.functions.length > 0);

  if (calculating) return <Loading text="Расчёт рекомендаций…" />;

  if (!result) {
    if (profile.functions.length === 0) {
      return (
        <Empty>
          Функции не выбраны. Вернитесь к шагу «Игровые функции»: риски выявляются по составу
          функций и характеристикам проекта.
        </Empty>
      );
    }
    return (
      <Empty>
        <div style={{ marginBottom: 10 }}>Расчёт ещё не выполнен.</div>
        <button className="btn btn-primary" onClick={() => void calculate()}>
          Рассчитать
        </button>
      </Empty>
    );
  }

  const risks = [...result.risks].sort(
    (a, b) => (SEVERITY_ORDER[a.severity] ?? 3) - (SEVERITY_ORDER[b.severity] ?? 3),
  );

  const highCount = risks.filter((risk) => risk.severity === 'high').length;

  return (
    <>
      <Card
        title="Риски проекта"
        hint="Риски выявляются до подбора решений: они показывают, где текущие характеристики проекта противоречат его стадии и масштабу."
        actions={
          <div className="btn-row">
            <Badge tone="neutral">всего: {risks.length}</Badge>
            {highCount > 0 && <Badge tone="danger">высоких: {highCount}</Badge>}
            <button className="btn btn-sm" onClick={() => void calculate()}>
              Пересчитать
            </button>
          </div>
        }
      >
        {risks.length === 0 ? (
          <Callout tone="ok" title="Критических рисков не выявлено">
            По текущим характеристикам проекта не найдено противоречий между стадией разработки,
            масштабом мира и выбранными функциями.
          </Callout>
        ) : (
          risks.map((risk) => <RiskItem key={risk.code} risk={risk} />)
        )}
      </Card>

      {highCount > 0 && (
        <Card title="Порядок действий">
          <Callout tone="warn" title="С чего начать">
            Высокие риски связаны со стадией разработки: чем позже обнаружена необходимость
            архитектурного решения, тем дороже его внедрение. В первую очередь закройте риски,
            помеченные как высокие, либо зафиксируйте ограничение проекта, которое делает риск
            неактуальным.
          </Callout>
        </Card>
      )}
    </>
  );
}
