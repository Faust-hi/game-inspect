/** Экран 10. Похожие игры: сверка проекта с подтверждёнными примерами. */
import { useMemo } from 'react';
import { useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading, SourceLink } from '../components/ui';
import type { GameExample, SimilarGame } from '../types';

function similarityTone(value: number): 'ok' | 'info' | 'warn' | 'neutral' {
  if (value >= 0.75) return 'ok';
  if (value >= 0.6) return 'info';
  if (value >= 0.45) return 'warn';
  return 'neutral';
}

function ExampleCard({
  item,
  methodNames,
}: {
  item: SimilarGame;
  methodNames: Record<string, string>;
}) {
  const example: GameExample = item.example;
  const percent = Math.round(item.similarity * 100);

  return (
    <div className="method-row">
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
        <strong>{example.title}</strong>
        <span className="xsmall faint">{example.year}</span>
        <Badge tone="neutral">{example.developer}</Badge>
        <Badge tone="info">{example.engine}</Badge>
        <Badge tone={similarityTone(item.similarity)}>сходство {percent}%</Badge>
      </div>

      <div style={{ maxWidth: 260, marginTop: 8 }}>
        <div className="bar-track">
          <div
            className="bar-fill"
            style={{
              width: `${percent}%`,
              background:
                item.similarity >= 0.75
                  ? 'var(--ok)'
                  : item.similarity >= 0.45
                    ? 'var(--accent)'
                    : 'var(--border-strong)',
            }}
          />
        </div>
      </div>

      <p className="small muted" style={{ marginTop: 8 }}>
        {example.summary}
      </p>

      <dl className="kv" style={{ marginTop: 8 }}>
        <dt>Формат и мир</dt>
        <dd>
          {example.format} · {example.world_type} · масштаб {example.scale}
        </dd>
        <dt>Целевые показатели</dt>
        <dd>
          {example.target_resolution} · {example.target_fps} FPS
        </dd>
        <dt>Насыщенность сцены</dt>
        <dd>
          объекты — {example.object_count_level}, NPC — {example.npc_count_level}
        </dd>
        <dt>Сетевой режим</dt>
        <dd>
          {example.multiplayer ? `мультиплеер до ${example.player_count} игроков` : 'одиночный режим'}
        </dd>
        {example.performance_outcome && (
          <>
            <dt>Результат</dt>
            <dd>{example.performance_outcome}</dd>
          </>
        )}
      </dl>

      {example.optimizations_used.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div className="xsmall faint">Применённые решения</div>
          <div className="chip-row" style={{ marginTop: 4 }}>
            {example.optimizations_used.map((code) => (
              <span key={code} className="chip">
                {methodNames[code] ?? code}
              </span>
            ))}
          </div>
        </div>
      )}

      {item.matching_optimizations.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div className="xsmall faint">Совпадает с вашим набором</div>
          <div className="chip-row" style={{ marginTop: 4 }}>
            {item.matching_optimizations.map((code) => (
              <span key={code} className="chip selected">
                {methodNames[code] ?? code}
              </span>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 10 }}>
        <SourceLink url={example.source_url} title={example.source_title} />
        {example.verified_by && (
          <div className="xsmall faint" style={{ marginTop: 2 }}>
            Проверено: {example.verified_by}
          </div>
        )}
      </div>
    </div>
  );
}

export function SimilarGamesScreen() {
  const { result, catalog, calculating } = useStore();

  const methodNames = useMemo(() => {
    const map: Record<string, string> = {};
    for (const method of catalog.methods) map[method.code] = method.name;
    return map;
  }, [catalog.methods]);

  if (calculating) return <Loading text="Поиск похожих проектов…" />;

  if (!result) {
    return <Empty>Расчёт ещё не выполнен. Выполните расчёт на этапе «Варианты реализации».</Empty>;
  }

  const games = [...result.similar_games].sort((a, b) => b.similarity - a.similarity);

  return (
    <>
      <Card
        title="Похожие игры"
        hint="Подбор выполняется по расстоянию Гауэра: учитываются формат, структура и масштаб мира, насыщенность сцены, целевые показатели и совпадение состава функций."
        actions={<Badge tone="info">найдено: {games.length}</Badge>}
      >
        {games.length === 0 ? (
          <Callout tone="warn" title="Похожих проектов не найдено">
            В базе нет примеров, достаточно близких к текущему профилю. Сверка с практикой
            невозможна: ориентируйтесь на собственный прототип.
          </Callout>
        ) : (
          <Callout tone="info" title="Зачем это нужно">
            Примеры показывают, какие решения уже применялись в сопоставимых проектах и к какому
            результату это привело. У каждого опубликованного примера указан источник.
          </Callout>
        )}
      </Card>

      {games.length > 0 && (
        <Card title="Результаты подбора">
          {games.map((item) => (
            <ExampleCard
              key={`${item.example.title}-${item.example.year}`}
              item={item}
              methodNames={methodNames}
            />
          ))}
        </Card>
      )}
    </>
  );
}
