"""Граф технологических зависимостей.

Граф строится из уже проверенных данных каталога, а не из новых утверждений:

* **метод → инструмент** — из `method_engine_links`; тип связи уже задан
  каталогом, здесь он только переводится в ребро графа;
* **инструмент → движок** — инструмент существует только внутри движка;
* **инструмент → графический API / плагин / SDK / библиотека** — из
  курируемой таблицы `TECH_REQUIREMENTS`, где каждая строка обязана иметь
  код источника; строка без существующего источника не создаёт ребро;
* **метод → метод** — из таблицы связей между методами (риск, альтернатива,
  обязательная зависимость, дополнение, перекрытие, жёсткая несовместимость).

Ключевой принцип: **отсутствие ребра не означает совместимость**.
Неизвестные сочетания попадают в отчёт проверок как `unknown`, а не как
«можно». Поэтому проверки графа возвращают не только ошибки, но и явные
списки непроверенного.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import (
    Conflict, DependencyEdge, Engine, EngineTool, EvidenceSource,
    Method, MethodEngineLink, TechnologyNode,
)
from .relation_resolutions import (
    DIRECT_TOOL_WORKAROUND, TOOL_ENGINE_CUSTOM_WORKAROUND, TOOL_ENGINE_WORKAROUND,
)

# ── Тип связи «метод-инструмент» → обязательность и критичность ──
# Прямая реализация — самый сильный сигнал, но всё равно не обязательство:
# метод можно реализовать другим инструментом, поэтому mandatory=0.
_LINK_SEVERITY: dict[str, int] = {
    "direct": 1,
    "complement": 2,
    "automation": 2,
    "diagnostic": 3,
    "partial": 2,
    "limited": 2,
    "alternative": 3,
}
# «Отсутствие встроенного аналога» — не зависимость, а её отсутствие:
# ребро не создаётся, иначе граф утверждал бы связь там, где её нет.
_SKIP_LINK_RELATIONS = {"missing"}

# ── Тип связи «метод-метод» → обязательность и критичность ──
_RELATION_EDGE: dict[str, tuple[int, int]] = {
    "dependency": (1, 3),      # обязательная зависимость
    "hard_conflict": (0, 3),   # жёсткая несовместимость
    "risk": (0, 2),
    "overlap": (0, 1),
    "alternative": (0, 1),
    "complement": (0, 1),
    "unknown": (0, 2),
}


# ── Дополнительные узлы: плагины, SDK и внешние библиотеки ──
# В каталоге их не было, хотя методы на них опираются. Узел без ребра
# безвреден, а вот ребро без узла сделало бы проверку графа ложной.
EXTRA_NODES: list[dict[str, str]] = [
    {"code": "plugin:unity.entities", "name": "Unity Entities (DOTS) package", "platform": "pc_windows,pc_linux"},
    {"code": "plugin:unity.netcode", "name": "Unity Netcode for Entities", "platform": "pc_windows,pc_linux"},
    {"code": "plugin:unity.transport", "name": "Unity Transport package", "platform": "pc_windows,pc_linux"},
    {"code": "plugin:unity.addressables", "name": "Unity Addressables package", "platform": "pc_windows,pc_linux"},
    {"code": "plugin:unity.burst", "name": "Unity Burst compiler", "platform": "pc_windows,pc_linux"},
    {"code": "plugin:unity.srp", "name": "Unity Scriptable Render Pipeline", "platform": "pc_windows,pc_linux"},
    {"code": "plugin:ue.world_partition", "name": "Unreal World Partition / OFPA", "platform": "pc_windows,pc_linux"},
    {"code": "plugin:ue.replication_graph", "name": "Unreal Replication Graph", "platform": "pc_windows,pc_linux"},
    {"code": "sdk:steamworks", "name": "Steamworks SDK", "platform": "pc_windows,pc_linux"},
    {"code": "sdk:directstorage", "name": "Microsoft DirectStorage", "platform": "pc_windows"},
    {"code": "lib:acl", "name": "Animation Compression Library (ACL)", "platform": "pc_windows,pc_linux"},
    {"code": "lib:meshoptimizer", "name": "meshoptimizer", "platform": "pc_windows,pc_linux"},
    {"code": "lib:rvo2", "name": "RVO2 / ORCA library", "platform": "pc_windows,pc_linux"},
    {"code": "lib:tracy", "name": "Tracy Profiler", "platform": "pc_windows,pc_linux"},
    {"code": "lib:opus", "name": "Opus / Ogg audio codec", "platform": "pc_windows,pc_linux"},
    {"code": "lib:physx", "name": "NVIDIA PhysX", "platform": "pc_windows,pc_linux"},
    {"code": "api:dxr", "name": "DirectX Raytracing (DXR)", "platform": "pc_windows"},
]


# ── Курируемые требования: инструмент → API / плагин / SDK / библиотека ──
# Каждая строка обязана ссылаться на реально существующий код источника.
# Если источник отсутствует, ребро не создаётся, а попадает в отчёт.
TECH_REQUIREMENTS: list[dict[str, Any]] = [
    # Unreal: путь рендеринга и шейдерная модель
    {
        "source": "tool:ue_nanite", "target": "api:directx12",
        "dependency_type": "runtime_api", "mandatory": 1, "min_version": "SM6",
        "platform": "pc_windows", "scope": "runtime", "severity": 1,
        "description": "Nanite требует пути рендеринга с поддержкой Shader Model 6; на desktop это DirectX 12.",
        "workaround": "Отказаться от Nanite для цели или выбрать совместимый путь рендеринга.",
        "source_code": "UE_NANITE",
    },
    {
        "source": "tool:ue_nanite", "target": "api:vulkan",
        "dependency_type": "runtime_api", "mandatory": 1, "min_version": "SM6",
        "platform": "pc_linux", "scope": "runtime", "severity": 2,
        "description": "На Linux путь Nanite идёт через Vulkan с Shader Model 6; матрица поддержки зависит от RHI.",
        "workaround": "Проверить матрицу поддерживаемых возможностей для выбранного пути рендеринга.",
        "source_code": "UE_FEATURE_MATRIX",
    },
    {
        "source": "tool:ue_vsm", "target": "api:directx12",
        "dependency_type": "runtime_api", "mandatory": 1, "min_version": "SM6",
        "platform": "pc_windows", "scope": "runtime", "severity": 2,
        "description": "Virtual Shadow Maps завязаны на путь рендеринга с Shader Model 6.",
        "workaround": "Выбрать совместимый путь теней и отдельно проверить качество.",
        "source_code": "UE_VSM",
    },
    {
        "source": "tool:ue_lumen", "target": "api:directx12",
        "dependency_type": "runtime_api", "mandatory": 0, "min_version": "SM6",
        "platform": "pc_windows", "scope": "runtime", "severity": 2,
        "description": "Аппаратная трассировка лучей Lumen требует DX12 и RT-способной видеокарты; программный путь использует mesh distance fields.",
        "workaround": "Программная трассировка по distance fields (требует их генерации) либо другой путь GI.",
        "source_code": "UE_LUMEN",
    },
    {
        "source": "tool:ue_lumen", "target": "api:dxr",
        "dependency_type": "runtime_api", "mandatory": 0, "min_version": "DXR 1.0",
        "platform": "pc_windows", "scope": "runtime", "severity": 2,
        "description": "Аппаратный путь Lumen опирается на трассировку лучей уровня API (DXR) при доступном оборудовании.",
        "workaround": "Программный путь трассировки по distance fields.",
        "source_code": "SRC-RND-014",
    },
    {
        "source": "tool:ue_virtual_texturing", "target": "api:dx11",
        "dependency_type": "runtime_api", "mandatory": 0, "min_version": "SM5",
        "platform": "pc_windows", "scope": "runtime", "severity": 3,
        "description": "Виртуальное текстурирование работает и на DirectX 11, но с ограничениями по формату и пути рендеринга.",
        "workaround": "Использовать классические мип-уровни вместо виртуального текстурирования.",
        "source_code": "UE_FEATURE_MATRIX",
    },
    # Unity: пакетные зависимости
    {
        "source": "tool:u_dots", "target": "plugin:unity.entities",
        "dependency_type": "package", "mandatory": 1, "min_version": "1.0",
        "platform": "pc_windows,pc_linux", "scope": "runtime", "severity": 2,
        "description": "Entities/DOTS — это пакет Unity, а не переключатель движка; он задаёт собственную модель мира.",
        "workaround": "Остаться на GameObject-модели или выбрать другой data-oriented слой.",
        "source_code": "UNITY_ENTITIES",
    },
    {
        "source": "tool:u_dots", "target": "plugin:unity.burst",
        "dependency_type": "package", "mandatory": 1, "min_version": "1.0",
        "platform": "pc_windows,pc_linux", "scope": "runtime", "severity": 2,
        "description": "Практическая производительность DOTS опирается на Burst-компиляцию job-кода.",
        "workaround": "Отказ от Burst снижает выигрыш; измерить отдельно.",
        "source_code": "UNITY_ENTITIES",
    },
    {
        "source": "tool:u_jobs", "target": "plugin:unity.burst",
        "dependency_type": "package", "mandatory": 0, "min_version": "1.0",
        "platform": "pc_windows,pc_linux", "scope": "runtime", "severity": 3,
        "description": "Burst не обязателен для Job System, но именно он даёт основной прирост на горячем коде.",
        "workaround": "Работать без Burst и принять меньший выигрыш.",
        "source_code": "RESEARCH_S31_UNITY_JOB_OVERVIEW",
    },
    {
        "source": "tool:u_netcode", "target": "plugin:unity.entities",
        "dependency_type": "package", "mandatory": 1, "min_version": "1.0",
        "platform": "pc_windows,pc_linux", "scope": "server", "severity": 2,
        "description": "Netcode for Entities завязан на семейство пакетов Entities и требует согласованных версий.",
        "workaround": "Использовать другой сетевой слой или собственную репликацию.",
        "source_code": "UNITY_NETCODE",
    },
    {
        "source": "tool:u_netcode", "target": "plugin:unity.transport",
        "dependency_type": "package", "mandatory": 1, "min_version": "1.0",
        "platform": "pc_windows,pc_linux", "scope": "server", "severity": 2,
        "description": "Транспорт — обязательная часть сетевого стека Netcode for Entities.",
        "workaround": "Проверить совместимые версии пакетов и lockfile до интеграции.",
        "source_code": "UNITY_NETCODE",
    },
    {
        "source": "tool:u_addressables", "target": "plugin:unity.addressables",
        "dependency_type": "package", "mandatory": 1, "min_version": "1.0",
        "platform": "pc_windows,pc_linux", "scope": "build", "severity": 2,
        "description": "Addressables — пакет управления ассетами и сборкой, а не универсальный механизм стриминга.",
        "workaround": "Использовать штатный streaming/build pipeline выбранного движка.",
        "source_code": "UNITY_ADDRESSABLES",
    },
    {
        "source": "tool:u_srp", "target": "plugin:unity.srp",
        "dependency_type": "package", "mandatory": 1, "min_version": "1.0",
        "platform": "pc_windows,pc_linux", "scope": "runtime", "severity": 2,
        "description": "URP/HDRP — это Scriptable Render Pipeline; выбор пайплайна задаёт доступные возможности рендеринга.",
        "workaround": "Built-in pipeline имеет другой набор возможностей; проверить до выбора методов.",
        "source_code": "UNITY_GFX_PERF",
    },
    # Внешние библиотеки и SDK
    {
        "source": "method:directstorage_io", "target": "sdk:directstorage",
        "dependency_type": "sdk", "mandatory": 1, "min_version": "",
        "platform": "pc_windows", "scope": "runtime", "severity": 2,
        "description": "DirectStorage — отдельный Windows SDK; без него метод нереализуем.",
        "workaround": "Классический ввод-вывод через потоки ОС.",
        "source_code": "SRC-WRS-054",
    },
    {
        "source": "tool:c_manual", "target": "lib:meshoptimizer",
        "dependency_type": "library", "mandatory": 0, "min_version": "",
        "platform": "pc_windows,pc_linux", "scope": "build", "severity": 3,
        "description": "Оптимизация индексов меша на пользовательском движке обычно опирается на внешнюю библиотеку.",
        "workaround": "Собственная реализация оптимизации вершинного кэша.",
        "source_code": "",
    },
    {
        "source": "tool:c_profiler", "target": "lib:tracy",
        "dependency_type": "library", "mandatory": 0, "min_version": "",
        "platform": "pc_windows,pc_linux", "scope": "development", "severity": 3,
        "description": "Инструментальные маркеры пользовательского профилировщика привязываются к внешней библиотеке трассировки.",
        "workaround": "Собственные счётчики и запись в файл.",
        "source_code": "",
    },
]


def sync_dependency_graph(db: Session) -> dict[str, int]:
    """Достроить узлы и рёбра графа зависимостей."""
    created_nodes = created_edges = 0
    skipped: list[str] = []

    # 1. Дополнительные узлы (плагины, SDK, библиотеки)
    for spec in EXTRA_NODES:
        exists = db.scalar(select(TechnologyNode).where(TechnologyNode.code == spec["code"]))
        if exists:
            continue
        db.add(
            TechnologyNode(
                code=spec["code"],
                node_type=spec["code"].split(":", 1)[0],
                name=spec["name"],
                version="",
                platform=spec.get("platform", ""),
                scope="runtime",
                docs_url="",
                source_id=None,
                status="published",
            )
        )
        created_nodes += 1
    db.flush()

    nodes = {n.code: n for n in db.scalars(select(TechnologyNode))}
    sources = {s.code: s for s in db.scalars(select(EvidenceSource))}
    by_url = {s.url: s for s in sources.values() if s.url}
    existing = {
        (e.source_node_id, e.target_node_id, e.dependency_type)
        for e in db.scalars(select(DependencyEdge))
    }

    def add_edge(
        src_code: str,
        dst_code: str,
        dependency_type: str,
        *,
        mandatory: int = 0,
        min_version: str = "",
        max_version: str = "",
        platform: str = "",
        scope: str = "runtime",
        severity: int = 2,
        source_code: str = "",
        source_url: str = "",
        description: str = "",
        workaround: str = "",
        no_source_note: str = "",
    ) -> bool:
        nonlocal created_edges
        src = nodes.get(src_code)
        dst = nodes.get(dst_code)
        if src is None or dst is None:
            skipped.append(f"{src_code} -> {dst_code} (узел отсутствует)")
            return False
        key = (src.id, dst.id, dependency_type)
        if key in existing:
            return False
        source = sources.get(source_code) if source_code else None
        if source is None and source_url:
            source = by_url.get(source_url)
        if source_code and source is None:
            skipped.append(f"{src_code} -> {dst_code} (источник {source_code} отсутствует)")
            return False
        # Ребро без публичного источника допустимо только тогда, когда это
        # прямо объяснено: иначе «нет источника» читалось бы как «всё в порядке».
        text = description[:4000]
        if source is None:
            if not no_source_note:
                skipped.append(f"{src_code} -> {dst_code} (нет источника и нет пояснения)")
                return False
            text = (text + " " + no_source_note).strip()[:4000]
        db.add(
            DependencyEdge(
                source_node_id=src.id,
                target_node_id=dst.id,
                dependency_type=dependency_type,
                mandatory=mandatory,
                min_version=min_version,
                max_version=max_version,
                platform=platform,
                scope=scope,
                severity=severity,
                source_id=source.id if source else None,
                description=text,
                workaround=workaround[:2000],
                status="published",
            )
        )
        existing.add(key)
        created_edges += 1
        return True

    # 2. метод → инструмент (из уже заданных связей каталога)
    links = list(db.scalars(select(MethodEngineLink)))
    tools = {t.id: t for t in db.scalars(select(EngineTool))}
    for link in links:
        if link.relation_type in _SKIP_LINK_RELATIONS:
            continue
        tool = tools.get(link.tool_id)
        method = db.get(Method, link.method_id)
        if tool is None or method is None:
            continue
        add_edge(
            f"method:{method.code}",
            f"tool:{tool.code}",
            "engine_tool",
            mandatory=0,
            severity=_LINK_SEVERITY.get(link.relation_type, 2),
            scope=tool.tool_type or "runtime",
            source_url=link.source_url or "",
            description=link.note or f"Метод реализуется инструментом «{tool.name}» ({link.relation_type}).",
            workaround=(
                DIRECT_TOOL_WORKAROUND
                if link.relation_type in {"direct", "complement"}
                else "Рассмотреть альтернативный инструмент или собственную реализацию."
            ),
            no_source_note=(
                "Публичного источника не существует: инструмент помечен как пользовательская "
                "технология, связь является экспертной оценкой, а не подтверждённой совместимостью."
            ),
        )

    # 3. инструмент → движок
    engines = {e.id: e for e in db.scalars(select(Engine))}
    for tool in tools.values():
        engine = engines.get(tool.engine_id)
        if engine is None:
            continue
        add_edge(
            f"tool:{tool.code}",
            f"engine:{engine.code}",
            "engine",
            mandatory=1,
            severity=1,
            scope=tool.tool_type or "runtime",
            source_url=tool.docs_url or engine.docs_url or "",
            description=(
                f"Инструмент «{tool.name}» существует только внутри движка {engine.name}"
                + (" и помечен как пользовательская технология." if tool.is_user_defined else ".")
            ),
            workaround=(
                TOOL_ENGINE_WORKAROUND
                if not tool.is_user_defined
                else TOOL_ENGINE_CUSTOM_WORKAROUND
            ),
            no_source_note=(
                "Публичного источника не существует: инструмент пользовательского движка "
                "описан самой командой, а не внешним вендором."
            ),
        )

    # 4. курируемые требования: API / плагин / SDK / библиотека
    for req in TECH_REQUIREMENTS:
        add_edge(
            req["source"],
            req["target"],
            req["dependency_type"],
            mandatory=req.get("mandatory", 0),
            min_version=req.get("min_version", ""),
            max_version=req.get("max_version", ""),
            platform=req.get("platform", ""),
            scope=req.get("scope", "runtime"),
            severity=req.get("severity", 2),
            source_code=req.get("source_code", ""),
            description=req.get("description", ""),
            workaround=req.get("workaround", ""),
            no_source_note=(
                "Публичного источника нет: это инженерное допущение каталога, "
                "требующее проверки перед принятием решения."
            ),
        )

    # 5. метод → метод (из связей между методами)
    for rel in db.scalars(select(Conflict)):
        mandatory, severity = _RELATION_EDGE.get(rel.conflict_type, (0, 2))
        add_edge(
            f"method:{rel.a_code}",
            f"method:{rel.b_code}",
            rel.conflict_type,
            mandatory=mandatory,
            severity=rel.severity or severity,
            scope="runtime",
            source_url=rel.source_url or "",
            description=rel.description,
            workaround=rel.resolution,
            no_source_note=(
                "Связь зафиксирована без публичного источника: это экспертное суждение "
                "каталога, а не подтверждённая документацией зависимость."
            ),
        )

    db.flush()
    return {
        "dependency_nodes_created": created_nodes,
        "dependency_edges_created": created_edges,
        "dependency_edges_skipped": len(skipped),
    }


# ── Разрешение циклов обязательных зависимостей ──
# Пакеты исследований местами пометили как «обязательную зависимость» не
# предварительное условие, а совместную разработку («два метода проектируются
# вместе»). Из-за этого возникают циклы: A требует B и B требует A.
# Цикл обязательных зависимостей неразрешим по определению, поэтому одна связь
# в каждом цикле понижается до «дополнения»: отношение сохраняется, но перестаёт
# быть жёстким предусловием. Понижение детерминировано и записывается в
# `resolution`, чтобы его нельзя было принять за исходные данные.

def break_dependency_cycles(db: Session) -> dict[str, int]:
    """Разорвать циклы обязательных зависимостей, понизив одну связь в каждом."""
    all_rows = list(db.scalars(select(Conflict)))
    rows = [r for r in all_rows if r.conflict_type == "dependency"]
    # Пары, для которых дополнение уже существует: уникальность задана тройкой
    # (a_code, b_code, conflict_type), поэтому повторное понижение невозможно.
    existing_complement = {
        (r.a_code, r.b_code) for r in all_rows if r.conflict_type == "complement"
    }
    demoted = 0
    # Итерации ограничены: каждый проход обязан понизить хотя бы одну связь.
    for _ in range(len(rows) + 1):
        adjacency: dict[str, list[str]] = {}
        for rel in rows:
            if rel.conflict_type == "dependency":
                adjacency.setdefault(rel.a_code, []).append(rel.b_code)

        cycle = _find_cycle(adjacency)
        if cycle is None:
            break
        pairs = list(zip(cycle, cycle[1:] + cycle[:1]))
        candidates = [
            rel
            for rel in rows
            if rel.conflict_type == "dependency" and (rel.a_code, rel.b_code) in pairs
        ]
        if not candidates:
            break
        # Детерминированный выбор: наибольший a_code, затем b_code.
        victim = max(candidates, key=lambda r: (r.a_code, r.b_code))
        # Уникальность задана тройкой (a_code, b_code, conflict_type), поэтому
        # дополнение с такой же парой уже может существовать. В этом случае
        # связь уже описана как дополнение — обязательную строку нужно убрать,
        # а не переписывать. Дополнение симметрично («A дополняет B» и
        # «B дополняет A» — одно отношение), поэтому проверяются оба
        # направления: иначе понижение создавало вторую запись об уже описанной
        # связи и второе ребро, которых нет при сборке с нуля.
        twin = (
            (victim.a_code, victim.b_code) in existing_complement
            or (victim.b_code, victim.a_code) in existing_complement
        )
        if twin:
            db.delete(victim)
            rows.remove(victim)
        else:
            existing_complement.add((victim.a_code, victim.b_code))
            victim.conflict_type = "complement"
            victim.severity = 1
            victim.resolution = (
                "Связь понижена из обязательной зависимости до дополнения автоматической "
                "проверкой: исходные данные объявляли взаимную обязательную зависимость, "
                "которая образует неразрешимый цикл. Методы следует проектировать вместе, "
                "но ни один из них не является строгим предусловием другого."
            )
        # Ребро графа могло быть построено до понижения связи: тогда в
        # `dependency_edges` остаётся обязательная зависимость, которой в
        # каталоге уже нет, и проверка циклов продолжает находить цикл.
        # Ребро приводится в соответствие со связью: у дополнения обязательность
        # снимается, а пониженная до дополнения пара убирается из графа, если
        # обратное направление уже описано дополнением.
        _follow_edge_demotion(db, victim.a_code, victim.b_code, complemented=twin)
        demoted += 1
    if demoted:
        db.flush()
    return {"dependency_cycles_broken": demoted}


def _follow_edge_demotion(
    db: Session, a_code: str, b_code: str, *, complemented: bool
) -> None:
    """Привести ребро графа в соответствие с пониженной связью.

    Проверка циклов читает `dependency_edges`, а понижение выполняется над
    `conflicts`. Если ребро уже построено, одной правки связи недостаточно:
    цикл остаётся видимым. Связь «дополнение» не является обязательным
    предусловием, поэтому ребро теряет признак обязательности.
    """
    src = db.scalar(
        select(TechnologyNode.id).where(TechnologyNode.code == f"method:{a_code}")
    )
    dst = db.scalar(
        select(TechnologyNode.id).where(TechnologyNode.code == f"method:{b_code}")
    )
    if src is None or dst is None:
        return
    edge = db.scalar(
        select(DependencyEdge).where(
            DependencyEdge.source_node_id == src,
            DependencyEdge.target_node_id == dst,
            DependencyEdge.dependency_type == "dependency",
        )
    )
    if edge is None:
        return
    if complemented:
        # Пара «A дополняет B» уже описана встречным ребром: обязательная
        # зависимость в этом направлении противоречит ей и удаляется.
        db.delete(edge)
        return
    edge.dependency_type = "complement"
    edge.mandatory = 0
    edge.severity = 1


#: Типы связей без направления: «A дополняет B» и «B дополняет A» — одно
#: отношение, а не два. Уникальность в базе задана тройкой с направлением,
#: поэтому обе записи могут сосуществовать, хотя описывают одну связь.
_SYMMETRIC_CONFLICT_TYPES = frozenset({"complement", "alternative", "hard_conflict", "risk"})


def dedupe_symmetric_relations(db: Session) -> dict[str, int]:
    """Убрать симметричные связи, записанные в обе стороны.

    База, собранная до того, как понижение цикла перестало создавать встречное
    дополнение, содержит по две записи об одной связи. Дубль не безобиден: пара
    показывается дважды — в таблице связей и в блоке усилений корзины, — и даёт
    лишнее ребро в графе. Остаётся детерминированно меньшая пара (по коду A,
    затем B): при сборке с нуля создаётся именно она. Встречная запись и её
    ребро удаляются.

    Функция идемпотентна: на базе без дублей не делает ничего.
    """
    rows = list(db.scalars(select(Conflict)))
    by_key = {(r.a_code, r.b_code, r.conflict_type): r for r in rows}

    victims: list[Conflict] = []
    for (a_code, b_code, ctype) in sorted(by_key):
        if ctype not in _SYMMETRIC_CONFLICT_TYPES:
            continue
        # Встречная пара обрабатывается в своей итерации, поэтому берётся
        # только канонический (лексикографически меньший) порядок.
        if (a_code, b_code) > (b_code, a_code):
            continue
        if (b_code, a_code, ctype) in by_key:
            victims.append(by_key[(b_code, a_code, ctype)])

    if not victims:
        return {"symmetric_relation_duplicates_removed": 0,
                "symmetric_relation_edges_removed": 0}

    removed_edges = 0
    for victim in victims:
        src = db.scalar(
            select(TechnologyNode.id).where(TechnologyNode.code == f"method:{victim.a_code}")
        )
        dst = db.scalar(
            select(TechnologyNode.id).where(TechnologyNode.code == f"method:{victim.b_code}")
        )
        if src is not None and dst is not None:
            edge = db.scalar(
                select(DependencyEdge).where(
                    DependencyEdge.source_node_id == src,
                    DependencyEdge.target_node_id == dst,
                    DependencyEdge.dependency_type == victim.conflict_type,
                )
            )
            if edge is not None:
                db.delete(edge)
                removed_edges += 1
        db.delete(victim)
    db.flush()
    return {"symmetric_relation_duplicates_removed": len(victims),
            "symmetric_relation_edges_removed": removed_edges}


def _find_cycle(adjacency: dict[str, list[str]]) -> list[str] | None:
    """Найти один цикл в ориентированном графе (итеративный DFS)."""
    WHITE, GREY, BLACK = 0, 1, 2
    color: dict[str, int] = {}

    def node_color(n: str) -> int:
        return color.get(n, WHITE)

    for start in adjacency:
        if node_color(start) != WHITE:
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        path: list[str] = []
        while stack:
            node, idx = stack.pop()
            if idx == 0:
                color[node] = GREY
                path.append(node)
            neighbours = adjacency.get(node, [])
            if idx < len(neighbours):
                stack.append((node, idx + 1))
                nxt = neighbours[idx]
                if node_color(nxt) == GREY:
                    cut = path.index(nxt) if nxt in path else 0
                    return path[cut:]
                if node_color(nxt) == WHITE:
                    stack.append((nxt, 0))
            else:
                color[node] = BLACK
                if path:
                    path.pop()
    return None
