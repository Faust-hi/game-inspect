/** Экран 3. Выбор планируемых игровых функций. */
import { useMemo, useState } from 'react';
import { useStore } from '../store';
import { Badge, Callout, Card, Empty } from '../components/ui';
import type { GameFunction } from '../types';

export function FunctionsScreen() {
  const { profile, updateProfile, catalog } = useStore();
  const [filter, setFilter] = useState<'all' | 'relevant' | 'selected'>('relevant');

  const functions = catalog.functions;

  const relevance = useMemo(() => {
    const map: Record<string, 'typical' | 'possible' | 'unusual'> = {};
    for (const fn of functions) {
      if (fn.formats.includes(profile.format) && fn.typical_world_types.includes(profile.world_type)) {
        map[fn.code] = 'typical';
      } else if (fn.formats.includes(profile.format)) {
        map[fn.code] = 'possible';
      } else {
        map[fn.code] = 'unusual';
      }
    }
    return map;
  }, [functions, profile.format, profile.world_type]);

  const grouped = useMemo(() => {
    const visible = functions.filter((fn) => {
      if (filter === 'selected') return profile.functions.includes(fn.code);
      if (filter === 'relevant') return relevance[fn.code] !== 'unusual';
      return true;
    });
    const byCategory = new Map<string, GameFunction[]>();
    for (const fn of visible) {
      const list = byCategory.get(fn.category) ?? [];
      list.push(fn);
      byCategory.set(fn.category, list);
    }
    return [...byCategory.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [functions, filter, profile.functions, relevance]);

  const toggle = (code: string) => {
    const active = profile.functions.includes(code);
    updateProfile({
      functions: active ? profile.functions.filter((c) => c !== code) : [...profile.functions, code],
    });
  };

  return (
    <>
      <Card
        title="Игровые функции"
        hint="Выберите функции, влияющие на архитектуру, вычислительную нагрузку или ресурсы: например, разрушаемость, мир, NPC и мультиплеер. Монетизация, дата выхода и сюжетные развилки в технический подбор не входят."
        actions={
          <div className="btn-row">
            {(
              [
                ['relevant', 'Подходящие'],
                ['all', 'Все'],
                ['selected', `Выбранные (${profile.functions.length})`],
              ] as const
            ).map(([key, label]) => (
              <button
                key={key}
                className={`btn btn-sm ${filter === key ? 'btn-primary' : ''}`}
                onClick={() => setFilter(key)}
              >
                {label}
              </button>
            ))}
          </div>
        }
      >
        {grouped.length === 0 ? (
          <Empty>Ни одна функция не отобрана. Переключите фильтр или выберите функции вручную.</Empty>
        ) : (
          grouped.map(([category, items]) => (
            <div key={category} style={{ marginBottom: 16 }}>
              <h4 className="faint" style={{ marginBottom: 8 }}>
                {category}
              </h4>
              <div className="grid grid-2">
                {items.map((fn) => {
                  const selected = profile.functions.includes(fn.code);
                  const state = relevance[fn.code];
                  return (
                    <button
                      key={fn.code}
                      onClick={() => toggle(fn.code)}
                      style={{
                        textAlign: 'left',
                        border: `1px solid ${selected ? 'var(--accent)' : 'var(--border)'}`,
                        background: selected ? 'var(--accent-soft)' : '#fff',
                        borderRadius: 'var(--radius)',
                        padding: '10px 12px',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={() => toggle(fn.code)}
                          style={{ width: 'auto', margin: 0 }}
                        />
                        <strong style={{ fontSize: 13.5 }}>{fn.name}</strong>
                        {state === 'typical' && <Badge tone="ok">типично</Badge>}
                        {state === 'unusual' && <Badge tone="warn">редкое сочетание</Badge>}
                      </div>
                      <p className="xsmall muted" style={{ marginTop: 4 }}>
                        {fn.description}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </Card>

      {profile.functions.length === 0 && (
        <Callout tone="warn" title="Функции не выбраны">
          Без выбранных функций система не сможет сформировать рекомендации: подбор решений
          выполняется по функциям проекта.
        </Callout>
      )}
    </>
  );
}
