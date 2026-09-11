/** Экран 8. Сводный профиль нагрузки выбранного набора решений. */
import { useMemo } from 'react';
import { useEnsureResult, useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading, SourceLink } from '../components/ui';
import { ClaimBlocks, EvidenceBadge, UnconfirmedFactors } from '../components/Evidence';
import { impactsOf, methodsByCode as buildMethodMap, selectedMethods } from '../catalogUtils';
import type { LoadProfile, LoadResourceDetail } from '../types';

const RESOURCES: { key: keyof Omit<LoadProfile, 'per_resource' | 'notes'>; label: string }[] = [
  { key: 'cpu', label: 'CPU' },
  { key: 'gpu', label: 'GPU' },
  { key: 'ram', label: 'RAM' },
  { key: 'vram', label: 'VRAM' },
  { key: 'disk', label: 'Накопитель' },
  { key: 'network', label: 'Сеть' },
];

/**
 * Шкала с нейтральной серединой: значение 50 соответствует отсутствию изменений,
 * смещение влево — снижение нагрузки, вправо — рост.
 */
function CenteredBar({ value }: { value: number }) {
  const reduced = value < 50;
  const offset = reduced ? value : 50;
  const width = Math.abs(value - 50);
  const color = reduced ? 'var(--ok)' : 'var(--danger)';

  return (
    <div className="bar-track">
      <div
        className="bar-fill"
        style={{ marginLeft: `${offset}%`, width: `${width}%`, background: color }}
      />
      <div className="bar-center" />
    </div>
  );
}

function directionTone(direction: string): 'ok' | 'danger' | 'neutral' {
  if (direction === 'снижает') return 'ok';
  if (direction === 'повышает') return 'danger';
  return 'neutral';
}

/** Подпись справа от названия ресурса: процент изменения или экспертный балл. */
function scaleCaption(detail: LoadResourceDetail | undefined): string {
  if (!detail) return '';
  if (detail.quantitative === false) {
    return `экспертный балл ${detail.raw > 0 ? '+' : ''}${detail.raw}`;
  }
  const percent = Math.round(detail.raw * 100);
  return `изменение стоимости кадра ${percent > 0 ? '+' : ''}${percent}%`;
}

export function LoadProfileScreen() {
  const { result, basket, catalog, calculating } = useStore();

  useEnsureResult();

  const methodsByCode = useMemo(() => buildMethodMap(catalog.methods), [catalog.methods]);

  const selected = useMemo(
    () => (result?.selected_methods ?? selectedMethods(basket, methodsByCode))
      .filter(method => (result?.accounted_method_codes?.includes(method.code) ?? true)
        && !['server', 'development', 'offline'].includes(method.effect_scope)),
    [basket, methodsByCode, result],
  );

  if (calculating) return <Loading text="Расчёт профиля нагрузки…" />;

  if (!result) {
    return <Empty>Расчёт ещё не выполнен. Выполните расчёт на этапе «Варианты реализации».</Empty>;
  }

  const load = result.load_profile;

  return (
    <>
      <Card
        title="Сводный профиль нагрузки"
        hint="Система показывает суммарное влияние выбранного набора на подсистемы проекта, а не эффект отдельных решений по отдельности."
        actions={<Badge tone="info">решений: {selected.length}</Badge>}
      >
        {(load.notes ?? []).map((note, index) => (
          <Callout key={index} tone="warn">{note}</Callout>
        ))}
        {selected.length === 0 && (
          <Callout tone="warn" title="Корзина пуста">
            Профиль построен по базовым характеристикам проекта. Добавьте решения, чтобы увидеть их
            суммарное влияние.
          </Callout>
        )}

        <div style={{ display: 'grid', gap: 14, marginTop: selected.length === 0 ? 14 : 0 }}>
          {RESOURCES.map(({ key, label }) => {
            const detail = load.per_resource[key];
            const normalized = load[key];
            const qualitative = detail?.quantitative === false;
            return (
              <div key={key}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'baseline',
                    gap: 8,
                    marginBottom: 5,
                    flexWrap: 'wrap',
                  }}
                >
                  <strong style={{ fontSize: 13, minWidth: 96 }}>{label}</strong>
                  {detail && (
                    <Badge tone={directionTone(detail.direction)}>{detail.direction}</Badge>
                  )}
                  {qualitative && detail?.level && (
                    <Badge tone={directionTone(detail.direction)}>{detail.level}</Badge>
                  )}
                  <span className="xsmall faint" style={{ marginLeft: 'auto' }}>
                    {qualitative ? '' : `${normalized.toFixed(0)} / 100 · `}
                    {scaleCaption(detail)}
                  </span>
                </div>
                {qualitative ? (
                  <p className="xsmall faint" style={{ margin: 0 }}>
                    {detail?.explanation}
                  </p>
                ) : (
                  <CenteredBar value={normalized} />
                )}
              </div>
            );
          })}
        </div>

        <div className="divider" />
        <p className="xsmall faint">
          Шкала нормирована так, что 50 соответствует отсутствию изменений: отклонение влево означает
          снижение нагрузки на подсистему, вправо — её рост. Шкала есть только у CPU, GPU, RAM и
          VRAM — для них считается стоимость кадра. Накопитель и сеть показаны качественно
          (направление и уровень влияния): модель не оценивает объём данных и трафик, поэтому
          числового требования по ним нет. Оценка не заменяет профилирование конкретной сборки.
        </p>
      </Card>

      {selected.length > 0 && (
        <Card
          title="Вклад отдельных решений"
          hint="Из чего складывается суммарный профиль: отрицательные значения снижают нагрузку, положительные повышают. Для накопителя и сети это экспертный балл каталога (от −3 до +3), а не объём данных и не трафик."
        >
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ minWidth: 220 }}>Решение</th>
                  {RESOURCES.map(({ key, label }) => (
                    <th key={key}>{label}</th>
                  ))}
                  <th style={{ minWidth: 170 }}>Основание</th>
                </tr>
              </thead>
              <tbody>
                {selected.map((method) => {
                  const impacts = impactsOf(method);
                  const qualitativeOnly = ['disk', 'network'].every(
                    key => load.per_resource[key]?.quantitative === false,
                  );
                  return (
                    <tr key={method.code}>
                      <td className="small">
                        {method.name}
                        <div className="xsmall faint">{method.level_label}</div>
                      </td>
                      {RESOURCES.map(({ key }) => {
                        const value = impacts[key];
                        return (
                          <td
                            key={key}
                            className="mono small"
                            style={{
                              color: value < 0 ? 'var(--ok)' : value > 0 ? 'var(--danger)' : undefined,
                            }}
                          >
                            {value === 0 ? '—' : value > 0 ? `+${value}` : value}
                          </td>
                        );
                      })}
                      <td className="small">
                        <EvidenceBadge
                          basis={method.source_url ? 'documented' : 'expert_estimate'}
                          title={method.source_url
                            ? 'У решения есть опубликованный источник; числовой эффект всё равно требует проверки на прототипе.'
                            : 'Публичного источника у решения нет: вклад является экспертной оценкой каталога.'}
                        />
                        <div className="xsmall faint" style={{ marginTop: 3 }}>
                          {qualitativeOnly ? 'балл каталога' : 'вклад в стоимость кадра'}
                        </div>
                        {method.source_url && (
                          <div className="xsmall">
                            <SourceLink url={method.source_url} title={method.source_title || 'Источник'} />
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
                <tr>
                  <td className="small">
                    <strong>Суммарно</strong>
                  </td>
                  {RESOURCES.map(({ key }) => {
                    const total = selected.reduce((sum, m) => sum + impactsOf(m)[key], 0);
                    return (
                      <td key={key} className="mono small">
                        <strong>{total === 0 ? '—' : total > 0 ? `+${total}` : total}</strong>
                      </td>
                    );
                  })}
                  <td className="small faint">—</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="divider" />
          <ClaimBlocks
            fact={`Набор состоит из ${selected.length} решений, учтённых в расчёте нагрузки.`}
            inference="Суммарный профиль получен сложением вкладов отдельных решений по подсистемам."
            assumption="Сложение вкладов предполагает отсутствие взаимодействия между решениями. Перекрывающиеся эффекты и синергии учитываются отдельно, но числовой бонус за дополнение не начисляется без отдельного измерения совместного эффекта."
          />

          <UnconfirmedFactors
            items={[
              'Числовой эффект совместного применения двух и более решений не подтверждён измерением.',
              ...(load.notes ?? []),
            ]}
            title="Неучтённые и неподтверждённые факторы нагрузки"
          />
        </Card>
      )}
    </>
  );
}
