"""Обязательные зависимости набора решений: одно замыкание для всех расчётов.

Обязательная зависимость «method → method» означает «без B эффект A не
реализуется». Такие связи лежат в графе технологий (`dependency_edges`,
`mandatory=1`, оба конца — узлы `method`); сейчас их 80.

Раньше это правило было записано дважды и по-разному:

* `rules.mandatory_dependency_closure` умел достраивать набор до неподвижной
  точки, но **не вызывался ниоткуда** — исправление существовало и не работало;
* отдельный расчёт в модуле расписания трудоёмкости делал то же самое
  самостоятельно и только для него (модуль с тех пор удалён вместе с
  планированием трудоёмкости).

Из-за расхождения расписание и профиль нагрузки считали разные наборы: у
сценария S16 в расписании было 15 методов, а в нагрузке — 0, и «профиль
нагрузки» показывал нейтральные 50/50 при непустой корзине. У Horizon Zero Dawn
так пропадали все 6 решений из 6.

Модуль держит одно правило в одном месте, чтобы расхождение не возникло снова.
Зависимость, которой нет в опубликованном каталоге, **не подставляется**: её
нельзя посчитать, а подменять неизвестный вход известным запрещено.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from .. import repositories

#: Код узла-метода в графе технологий отличается от кода метода префиксом.
METHOD_NODE_PREFIX = "method:"


@dataclass(frozen=True)
class Closure:
    """Результат достройки набора по обязательным зависимостям.

    * `codes` — расширенный отсортированный набор кодов методов;
    * `added` — какие коды добавлены и по чьему требованию;
    * `notes` — то же человекочитаемо, для пояснений в ответе.
    """

    codes: list[str] = field(default_factory=list)
    added: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def declared(self) -> list[str]:
        """Коды, которые были в наборе до достройки."""
        return [code for code in self.codes if code not in self.added]


def mandatory_closure(db: Session, codes: Iterable[str]) -> Closure:
    """Достроить набор кодов методов по обязательным зависимостям (транзитивно).

    Идёт до неподвижной точки: зависимость добавленного метода тоже
    достраивается. Добавление видно вызывающему (`Closure.added`), потому что
    расширение корзины обязано быть явным, а не выглядеть самовольным.
    """
    declared = {code for code in codes if code}
    selected = set(declared)

    nodes = {node.id: node for node in repositories.technology_nodes(db)}
    edges = [edge for edge in repositories.dependency_edges(db) if edge.mandatory]
    known = {method.code for method in repositories.methods(db)}

    required_by: dict[str, str] = {}
    changed = True
    while changed:
        changed = False
        for edge in edges:
            source = nodes.get(edge.source_node_id)
            target = nodes.get(edge.target_node_id)
            if source is None or target is None:
                continue
            if source.node_type != "method" or target.node_type != "method":
                continue
            source_code = source.code.removeprefix(METHOD_NODE_PREFIX)
            target_code = target.code.removeprefix(METHOD_NODE_PREFIX)
            if source_code not in selected or target_code in selected:
                continue
            if target_code not in known:
                # Зависимость, которой нет в каталоге, посчитать нельзя.
                # Подставить вместо неё другой метод — выдумывание входа.
                continue
            selected.add(target_code)
            required_by[target_code] = source_code
            changed = True

    names = {method.code: method.name for method in repositories.methods(db)}

    def name_of(code: str) -> str:
        return names.get(code, code)

    notes = [
        f"«{name_of(code)}» добавлено в расчёт как обязательная зависимость "
        f"для «{name_of(required_by[code])}»."
        for code in sorted(required_by)
    ]
    return Closure(codes=sorted(selected), added=required_by, notes=notes)
