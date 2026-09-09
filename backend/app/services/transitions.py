"""Qualitative migration scenarios, never measured effort or runtime multipliers.

Only explicit alternatives/conflicts imply replacement. Sharing a function does
not: light culling and shader warmup, for example, can coexist.
"""
from ..schemas.catalog import TransitionOut
from . import rules

FUNCTION_FIELDS = {
    "open_world_streaming": {"world_type", "scale", "storage_type", "streaming_pool_gb"},
    "large_scale_terrain": {"world_type", "scale"},
    "crowd_simulation": {"npc_count", "npc_count_level", "simulation_radius_m"},
    "physics_simulation": {"physics_tick_hz", "simulation_radius_m", "object_count"},
    "destruction_simulation": {"physics_tick_hz", "object_count", "object_count_level"},
    "multiplayer_netcode": {"multiplayer", "player_count", "network_topology", "physics_tick_hz"},
    "split_screen_rendering": {"local_view_count"},
    "audio_system": {"audio_complexity"},
    "upscaling_frame_generation": {"upscaling_method", "frame_generation", "base_render_fps"},
    "cloth_simulation": {"physics_tick_hz", "npc_count", "npc_count_level"},
    "hair_rendering": {"npc_count", "npc_count_level"},
    "character_animation": {"npc_count", "npc_count_level"},
    "ai_pathfinding": {"npc_count", "npc_count_level", "simulation_radius_m", "world_type", "scale"},
    "advanced_npc_ai": {"npc_count", "npc_count_level", "simulation_radius_m"},
}
RENDER_FIELDS = {"target_resolution", "target_quality", "target_fps", "render_api", "draw_call_budget"}
METHOD_FIELDS = {
    'ai_director_pacing': {'multiplayer', 'network_topology', 'world_type', 'scale'},
    'directstorage_io': {'render_api', 'storage_type', 'streaming_pool_gb'},
    'async_compute_overlap': RENDER_FIELDS,
}


def assess(method, profile, baseline, methods, relations, planned_codes=None):
    base_cost = float(method.implementation_cost)
    result = TransitionOut(method_code=method.code, status="new", scope="initial_integration",
                           cost_min=base_cost, cost_max=base_cost,
                           complexity_min=getattr(method, 'complexity', base_cost),
                           complexity_max=getattr(method, 'complexity', base_cost))
    if baseline is None:
        result.reasons = ["Реализованная основа не зафиксирована: показана исходная экспертная трудоёмкость."]
        return result
    old = set(baseline.basket)
    engine_changed = baseline.profile.engine != profile.engine
    version_changed = baseline.profile.engine_version != profile.engine_version
    function = method.function.code if method.function else None
    fields = set(FUNCTION_FIELDS.get(function, set()))
    fields |= METHOD_FIELDS.get(method.code, set())
    fields |= {"format", "platforms", "memory_model"}
    if method.impact_gpu or method.impact_vram:
        fields |= RENDER_FIELDS
    def effective(p, field):
        if field in {"npc_count", "npc_count_level"}:
            return p.npc_count_effective
        if field in {"object_count", "object_count_level"}:
            return p.object_count_effective
        if field == "platforms":
            return sorted(set(p.platforms))
        return getattr(p, field)
    changed = sorted(f for f in fields if effective(baseline.profile, f) != effective(profile, f))
    function_changed = bool(function and ((function in baseline.profile.functions) != (function in profile.functions)))
    retained = method.code in old
    # Follow dependencies from dependent to prerequisite, including indirect ones.
    prerequisites = {method.code}
    while True:
        expanded = prerequisites | {r.b_code for r in relations if r.conflict_type == 'dependency' and r.a_code in prerequisites}
        if expanded == prerequisites:
            break
        prerequisites = expanded
    removed_prerequisites = sorted((prerequisites - {method.code}) & old - set(planned_codes)) if planned_codes is not None else []
    if retained and not engine_changed and not version_changed and not changed and not function_changed and not removed_prerequisites:
        result.status, result.scope = "retained", "none"
        result.cost_min = result.cost_max = 0
        result.complexity_min = result.complexity_max = 0
        result.reasons = ["Решение уже реализовано; повторная стоимость внедрения не начисляется.",
                          "Смена стадии сама по себе не меняет реализацию и потребление ресурсов."]
        return result
    replacements = set()
    for relation in relations:
        if relation.conflict_type not in {"alternative", "hard_conflict"}:
            continue
        if method.code == relation.a_code and relation.b_code in old:
            replacements.add(relation.b_code)
        if method.code == relation.b_code and relation.a_code in old:
            replacements.add(relation.a_code)
    result.replaces = sorted(replacements)
    possible_replacements = []
    if not retained and not replacements and planned_codes is not None and method.code in planned_codes:
        related = {r.b_code if r.a_code == method.code else r.a_code for r in relations
                   if method.code in {r.a_code, r.b_code}}
        possible_replacements = sorted(c for c in old - set(planned_codes) - related
                                       if c in methods and methods[c].function and methods[c].function.code == function)
    # Traverse explicit dependencies in their declared direction, to a fixed point.
    affected = set(replacements)
    while True:
        expanded = affected | {r.a_code for r in relations if r.conflict_type == "dependency"
                               and r.b_code in affected and r.a_code in old}
        if expanded == affected:
            break
        affected = expanded
    result.affected_methods = sorted((affected - replacements) | set(removed_prerequisites))
    if engine_changed:
        result.status, result.scope = "migration", "architecture_migration"
        result.cost_min, result.cost_max = base_cost, base_cost * 2
        result.complexity_max = 5
        result.reasons.append("Движок изменён: проверить перенос кода, ассетов, инструментов и форматов данных.")
    elif retained:
        result.status, result.scope = "adaptation", "dependency_rework" if removed_prerequisites else "local_adjustment"
        result.cost_min, result.cost_max = 0, max(1.0, base_cost)
        result.complexity_min = 0
        if removed_prerequisites or 'format' in changed:
            result.complexity_max = 5
        if removed_prerequisites:
            result.reasons.append("Удалены исходные зависимости: " + ", ".join(removed_prerequisites) + ". Проверить замену интерфейсов и данных.")
        if changed:
            result.reasons.append("Изменились технические параметры: " + ", ".join(changed) + ". Проверить запас реализации и бюджеты.")
        if version_changed:
            result.reasons.append("Версия движка изменена: объём адаптации зависит от совместимости API и ассетов.")
        if function_changed:
            result.reasons.append("Изменилась потребность в функции: проверить применимость сохранённого решения.")
    elif replacements:
        old_methods = [methods[c] for c in replacements if c in methods]
        local = method.level == "setting" and all(m.level == "setting" for m in old_methods)
        architectural = method.level == "architecture" or any(m.level == "architecture" for m in old_methods)
        result.status = "replacement"
        result.scope = "local_adjustment" if local else "subsystem_rework" if architectural else "implementation_rework"
        result.cost_min = max(0.5, base_cost * (0.5 if local else 1))
        result.cost_max = base_cost * (1 if local else 2)
        result.complexity_min = 1 if local else result.complexity_min
        result.complexity_max = max(result.complexity_min, 2) if local else 5
        result.reasons.append("Замена установлена по явной связи альтернативы/несовместимости каталога.")
        result.reasons.append("Проверить сохранение интерфейсов, данных и ассетов; полная перепись проекта из этой связи не следует.")
    elif possible_replacements:
        result.status, result.scope = 'possible_replacement', 'interface_review'
        result.replaces = possible_replacements
        result.cost_min, result.cost_max = base_cost, base_cost * 2
        result.complexity_max = 5
        result.evidence = 'needs_interface_review'
        result.reasons.append('Из той же функции убрана прежняя реализация, но связь замены в каталоге не подтверждена. Проверить, что именно переиспользуется и что переписывается.')
    else:
        result.reasons.append("Это добавление решения. Одинаковая функция ещё не означает замену существующего метода.")
    if result.affected_methods:
        result.cost_max += min(3, len(result.affected_methods))
        result.complexity_max = 5
        result.reasons.append("Проверить зависимые реализации: " + ", ".join(result.affected_methods) + ".")
    if result.status != "retained":
        pressure = rules.stage_pressure(profile.stage, baseline.profile.stage)
        result.cost_max *= 1 + pressure * 0.5
        result.reasons.append("Диапазон — экспертный сценарий относительных трудозатрат, не часы. Уточнить прототипом и аудитом интерфейсов.")
    result.cost_min, result.cost_max = round(result.cost_min, 2), round(result.cost_max, 2)
    return result


def removed(baseline, basket, relations):
    if baseline is None:
        return []
    remaining = set(basket)
    result = []
    for code in sorted(set(baseline.basket) - remaining):
        dependents = sorted({r.a_code for r in relations if r.conflict_type == "dependency"
                             and r.b_code == code and r.a_code in remaining})
        result.append(TransitionOut(method_code=code, status="removal", scope="decommission",
                                   cost_min=0.25, cost_max=3 if dependents else 1,
                                   affected_methods=dependents,
                                   reasons=["Реализованное решение убрано из плана: учесть отключение, очистку данных и регрессионную проверку.",
                                            "Его прежний аппаратный эффект не переносится в новую корзину."]))
    return result
