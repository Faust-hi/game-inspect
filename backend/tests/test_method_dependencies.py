"""Обязательные зависимости решений: одно замыкание для всех расчётов.

Дефект этого класса: правило «обязательная зависимость достраивается в набор»
было записано дважды и по-разному. В `rules` оно существовало, но не вызывалось
ниоткуда, а в модуле расписания трудоёмкости было продублировано для него одного
(модуль с тех пор удалён). Из-за расхождения расписание и профиль нагрузки
считали разные наборы методов: у сценария S16 в расписании было 15 методов, а в
нагрузке — 0, и «профиль нагрузки» показывал нейтральные 50/50 при непустой
корзине.

Тесты фиксируют свойства самого правила: замыкание транзитивно, идемпотентно, не
подставляет неизвестные методы и применяется одинаково расписанием и нагрузкой.
"""
from __future__ import annotations

from app import repositories
from app.schemas.catalog import ProjectProfile
from app.services import method_dependencies, rules


def _profile(**overrides) -> ProjectProfile:
    data = dict(
        name="Проверка замыкания",
        format="3D",
        world_type="open_world",
        scale="large",
        stage="prototype",
        engine="unreal",
        platforms=["pc_windows"],
        functions=["open_world_streaming"],
        target_resolution="1080p",
        target_quality="high",
        target_fps=60,
    )
    data.update(overrides)
    return ProjectProfile(**data)


# --- свойства правила -----------------------------------------------------


def test_closure_is_transitive(db_session):
    """Зависимость добавленного метода тоже достраивается.

    `gpu_instancing_vegetation` → `gpu_compute_culling` → `mesh_index_optimization`.
    Остановка на первом шаге оставила бы второй метод вне расчёта.
    """
    closure = method_dependencies.mandatory_closure(
        db_session, ["gpu_instancing_vegetation"]
    )

    assert "gpu_compute_culling" in closure.added
    assert "mesh_index_optimization" in closure.added, "цепочка оборвана на первом шаге"
    assert closure.added["mesh_index_optimization"] == "gpu_compute_culling"


def test_closure_is_idempotent(db_session):
    """Повторное замыкание уже расширенного набора ничего не добавляет."""
    once = method_dependencies.mandatory_closure(db_session, ["world_partition_streaming"])

    again = method_dependencies.mandatory_closure(db_session, once.codes)

    assert again.added == {}
    assert again.codes == once.codes


def test_closure_keeps_declared_codes(db_session):
    """Исходные коды остаются в наборе: замыкание только добавляет."""
    closure = method_dependencies.mandatory_closure(db_session, ["heightmap_compression"])

    assert "heightmap_compression" in closure.codes
    assert set(closure.declared) <= set(closure.codes)


def test_closure_does_not_invent_unknown_methods(db_session):
    """Неизвестный код не превращается в известный метод.

    Подставить вместо неизвестного входа другой метод — выдумывание данных,
    которое проектом запрещено. Неизвестный код при этом не выбрасывается молча:
    он остаётся в наборе как есть, а расчёт его просто не находит.
    """
    closure = method_dependencies.mandatory_closure(db_session, ["нет-такого-метода"])

    assert closure.added == {}
    assert closure.codes == ["нет-такого-метода"]


def test_closure_notes_explain_the_addition(db_session):
    """Пояснения называют добавленное решение и того, кто его потребовал."""
    names = {method.code: method.name for method in repositories.methods(db_session)}

    closure = method_dependencies.mandatory_closure(db_session, ["static_shadow_caching"])

    assert closure.added == {"virtual_shadow_maps": "static_shadow_caching"}
    assert len(closure.notes) == 1
    assert names["virtual_shadow_maps"] in closure.notes[0]
    assert names["static_shadow_caching"] in closure.notes[0]


def test_closure_covers_every_mandatory_method_edge(db_session):
    """Ни одно обязательное ребро method→method не остаётся необслуженным.

    Проверка по данным, а не по списку в тесте: если в графе появится новая
    обязательная зависимость, она обязана попадать в замыкание.
    """
    nodes = {node.id: node for node in repositories.technology_nodes(db_session)}
    method_edges = [
        (nodes[edge.source_node_id], nodes[edge.target_node_id])
        for edge in repositories.dependency_edges(db_session)
        if edge.mandatory
        and edge.source_node_id in nodes
        and edge.target_node_id in nodes
        and nodes[edge.source_node_id].node_type == "method"
        and nodes[edge.target_node_id].node_type == "method"
    ]
    assert method_edges, "в графе нет обязательных рёбер method→method"

    for source, target in method_edges:
        source_code = source.code.removeprefix(method_dependencies.METHOD_NODE_PREFIX)
        target_code = target.code.removeprefix(method_dependencies.METHOD_NODE_PREFIX)
        closure = method_dependencies.mandatory_closure(db_session, [source_code])
        assert target_code in closure.codes, f"{source_code} не достраивает {target_code}"


def test_no_mandatory_dependency_contradicts_an_exclusion(db_session):
    """Метод не может требовать того, с чем он несовместим (N6).

    Проверка по данным, а не по списку: если в каталоге или паке появится
    обязательная зависимость, противоречащая запрету той же пары, тест обязан
    упасть. Без него движок честно применял обе связи и выдавал корзине два
    взаимоисключающих сообщения: «исключить оба метода» от `hard_conflict` и
    «сначала внедрить зависимость» от `dependency`.
    """
    nodes = {node.id: node for node in repositories.technology_nodes(db_session)}
    prefix = method_dependencies.METHOD_NODE_PREFIX

    exclusions: set[frozenset[str]] = set()
    for relation in repositories.conflicts(db_session):
        if relation.conflict_type in ("hard_conflict", "alternative"):
            exclusions.add(frozenset((relation.a_code, relation.b_code)))

    contradictions = []
    for edge in repositories.dependency_edges(db_session):
        if not edge.mandatory:
            continue
        source, target = nodes.get(edge.source_node_id), nodes.get(edge.target_node_id)
        if source is None or target is None:
            continue
        if source.node_type != "method" or target.node_type != "method":
            continue
        pair = frozenset((source.code.removeprefix(prefix), target.code.removeprefix(prefix)))
        if pair in exclusions:
            contradictions.append(sorted(pair))

    assert contradictions == [], (
        "обязательная зависимость между несовместимыми методами: "
        + "; ".join(" ↔ ".join(pair) for pair in contradictions)
    )


def test_excluded_pair_has_no_second_type(db_session):
    """У пары с запретом совместного применения нет второго, мягкого типа.

    `hard_conflict` требует оставить один метод, `risk` предлагает оставить оба
    и снять риск замером. Обе связи в одной паре — это два разных ответа на
    один вопрос, и пользователь видит тот, который выбрал порядок обхода.
    """
    by_pair: dict[frozenset[str], set[str]] = {}
    for relation in repositories.conflicts(db_session):
        by_pair.setdefault(frozenset((relation.a_code, relation.b_code)), set()).add(
            relation.conflict_type
        )

    contradictory = sorted(
        " ↔ ".join(sorted(pair)) + ": " + ", ".join(sorted(types))
        for pair, types in by_pair.items()
        if "hard_conflict" in types and (types & {"risk", "dependency"})
    )

    assert contradictory == [], "противоречивые типы в одной паре: " + "; ".join(contradictory)


# --- применение правила ---------------------------------------------------


def test_closure_prevents_basket_collapse(db_session):
    """Без достройки корзина схлопывается, с ней — считается.

    Это и есть причина нейтральных 50/50 при непустой корзине: метод с
    отсутствующей обязательной зависимостью исключался вместе с ней, и от
    корзины не оставалось ничего.
    """
    relations = repositories.conflicts(db_session)
    profile = _profile()
    basket = ["world_partition_streaming"]

    declared = repositories.methods_by_codes(db_session, basket)
    without, without_notes = rules.assess_selected_methods(declared, profile, relations)
    assert without == [], "предпосылка теста неверна: метод учтён и без зависимости"
    assert any("обязательная зависимость" in note for note in without_notes)

    closure = method_dependencies.mandatory_closure(db_session, basket)
    expanded = repositories.methods_by_codes(db_session, closure.codes)
    with_closure, _ = rules.assess_selected_methods(expanded, profile, relations)

    assert len(with_closure) > len(without)
    assert "world_partition_streaming" in {method.code for method in with_closure}
