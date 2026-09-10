/**
 * Отображение области эффекта решения.
 *
 * Процент ожидаемого эффекта допустим только для решений, влияющих на
 * компьютер игрока. Для серверной экономии и ускорения разработки он относится
 * к другой машине или к производству, поэтому интерфейс обязан отличать эти
 * случаи, а не показывать их как прирост FPS.
 */
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { RecommendationList } from '../components/RecommendationList';
import type { Recommendation } from '../types';

function recommendation(effectScope: string, effectScopeLabel: string): Recommendation {
  return {
    method_code: 'headless_dedicated_server',
    method_name: 'Выделенный сервер без графики',
    function_code: 'multiplayer_netcode',
    function_name: 'Сетевой код',
    kind: 'optimization',
    score: 0.5,
    rank: 1,
    flags: [],
    flag_labels: [],
    reasons: [],
    excluded_reasons: [],
    criteria: [],
    engine_support: null,
    engine_alternatives: [],
    engine_tool_independent: false,
    summary: 'Серверная сборка без рендера.',
    performance_gain: 0.6,
    implementation_cost: 3,
    complexity: 3,
    late_cost: 'high',
    recommended_stage: 'production',
    quality_impact: 0,
    concept_impact: 0,
    source_url: 'https://example.org/server',
    effect_scope: effectScope,
    effect_scope_label: effectScopeLabel,
  };
}

function renderList(item: Recommendation) {
  render(
    <RecommendationList
      recommendations={[item]}
      selected={[]}
      onToggle={vi.fn()}
      methodsByCode={{}}
      engineName='Unreal Engine'
    />,
  );
}

describe('область эффекта в списке рекомендаций', () => {
  afterEach(cleanup);

  it('для клиентского решения показывает экспертный балл без обещания ускорения', () => {
    renderList(recommendation('client', 'клиент'));
    expect(screen.getByText(/Экспертный балл эффекта 0.60 \/ 1/)).toBeTruthy();
    expect(screen.queryByText(/60%/)).toBeNull();
  });

  it('для серверного решения не выдает процент за ускорение игры', () => {
    renderList(recommendation('server', 'сервер'));
    expect(screen.getByText(/Эффект: сервер/)).toBeTruthy();
    expect(screen.queryByText(/Ожидаемый эффект/)).toBeNull();
  });
});
