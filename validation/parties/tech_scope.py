"""Отбор решений по технической значимости (критерий включения в отчёт).

Зачем отдельный модуль
----------------------
Партии 01–11 описывают игру целиком: в разделе «Инженерные решения» рядом с
виртуальным текстурированием стоят «микротранзакции», «перенос даты выхода»,
«развилки сюжета» и «четыре концовки». Пока всё это попадает в знаменатель,
покрытие каталога не означает ровным счётом ничего: доля «представимых в
каталоге решений» падает из-за решений, которые база знаний описывать не
должна по своей предметной области.

Критерий включения (единственный)
---------------------------------
Решение попадает в расчёт, если оно влияет хотя бы на одно из трёх:

1. **архитектуру** — как устроены подсистемы, данные и конвейер;
2. **вычислительную нагрузку** — стоимость кадра, объём работы CPU/GPU;
3. **потребление ресурсов** — RAM, VRAM, диск, сеть.

Не влияет ни на одно из трёх — не попадает, даже если решение для игры важное.
Монетизация влияет на выручку, дата выхода — на график, число концовок — на
объём контента; к архитектуре и стоимости кадра это отношения не имеет.

Геймплейные решения, задающие технические требования, **сохраняются**:
разрушаемость окружения, масштаб мира, число NPC, мультиплеер, физика,
процедурная генерация, транспорт. Это не «игра в целом», а прямые входы
расчёта: они определяют объём симуляции, бюджет кадра и трафик.

Порядок разбора
---------------
1. `PROCEDURAL_RULES` — частный случай: «процедурная генерация» технична,
   только когда генерируется мир, уровень или контент; «процедурный сюжет»
   техническим не становится.
2. `TECH_STRONG` — явная техническая подсистема. Побеждает нетехнические
   совпадения: строка «locked_dlss_controversy» записана про спор вокруг
   монетизации, но упоминает DLSS — это решение про масштабирование кадра.
3. `NON_TECHNICAL` — издательские, сюжетные, музыкальные, околорыночные
   решения, контентная прогрессия и споры вокруг них.
4. `TECH_WEAK` — общие технические слова без явной подсистемы.
5. Ничего не совпало — `unknown`. Такие решения **не отбрасываются молча**:
   они уходят в отдельный список на разбор, иначе пропуск выглядел бы как
   «в каталоге нет аналога».
"""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass

HERE = pathlib.Path(__file__).resolve().parent

#: «Процедурная генерация» — технична только для мира, уровня и контента.
PROCEDURAL_TECH = re.compile(
    r"generation|generat|terrain|world|chunk|placement|level|map|dungeon|resource|"
    r"content|texture|vegetation|mesh|building|layout|city|planet|biome|"
    r"генерац|мир|уровн|локац|контент|ландшафт|растительн",
    re.I,
)
PROCEDURAL_CONTENT = re.compile(
    r"narrative|story|quest|dialog|branch|character|name|"
    r"сюжет|истори|квест|диалог|персонаж|имян",
    re.I,
)

#: Явные технические подсистемы: побеждают любые нетехнические совпадения.
TECH_STRONG: list[tuple[str, str]] = [
    (
        r"render|shader|gpu|raster|draw_?call|vulkan|dx1[0-9]|dx9|directx|opengl|mantle|"
        r"pso|mesh|vertex|triangle|poly|geom|lod|cul+ing|occlu|shadow|light|lightmap|"
        r"irradiance|probe|reflection|refraction|water|particle|volumetric|fog|cloud|"
        r"post_?process|bloom|taa|upscal|dlss|fsr|xess|frame_?gen|resolution|hdr|"
        r"tonemap|denois|ray_?trac|rtx|path_?trac|texture|mipmap|atlas|sprite|bake|"
        r"voxel|sdf|distance_field|cluster|tile|fill|overdraw|antialias|msaa|smaa|"
        r"motion_blur|dof|vrs|material|decal|deferred|forward|nanite|"
        r"tesselat|tessellat|megatexture|clipmap|heightmap|terrain|"
        r"camera|fov|viewport|post_?effect|post_?fx|postprocess|"
        r"phong|fresnel|specular|brdf|pbr|shading|lighting|albedo|"
        r"skybox|color_correction|color_grading|grading|film_grain|vignett|"
        r"lens|chromatic|aberration|"
        r"цветокоррекц|виньет|небесн\w*\s+бокс|скайбокс|"
        r"рендер|шейдер|отрисовк|трассировк|текстур|освещ|тен[ьеи]|отраж|частиц|"
        r"объ[её]мн|туман|разреш|апскейл|сглаж|геометр|полигон|лод|отсечен|окклюз|"
        r"запеч|материал|видеопамят|кадр|камер",
        "рендер и геометрия",
    ),
    (
        r"memory|ram|vram|alloc|garbage|gc_|\bgc\b|heap|leak|"
        r"64bit|64-bit|32bit|32-bit|x64|address_space|"
        r"памят|аллокац|сборк\w*\s+мусор|утечк|адресн\w*\s+пространств",
        "память",
    ),
    (
        r"stream|load|chunk|partition|disk|ssd|hdd|compress|patch|build_size|"
        r"save|autosave|cache|prefetch|"
        r"потоков|загруз|чанк|сжат|сохран|диск|накопител|патч|кэш",
        "загрузка и накопитель",
    ),
    (
        r"physic|collision|ragdoll|destruct|havok|physx|simulat|tick|timestep|"
        r"determin|broadphase|npc|crowd|pathfind|navmesh|flow_field|behaviou?r|"
        r"stealth|ai_|_ai\b|aggress|perception|ecs|data_oriented|entity_system|"
        r"hot_?path|job_|task_graph|coroutine|async|multithread|multi_?thread|"
        r"thread|parallel|core_count|smt|hyperthread|"
        r"gravity|force_field|excursion|tractor|sleep|wake|гравитац|силов\w*\s+пол|"
        r"физик|разруш|симуляц|столкнов|поиск\w*\s+пути|навигац|толп|агент|"
        r"дерев\w*\s+повед|искусственн|детермин|многопоточ|поток\w*\s+cpu|"
        r"параллельн|горяч\w*\s+путь",
        "симуляция и ИИ",
    ),
    (
        r"anim|skeletal|skinning|motion_match|\bik\b|bone|euphoria|motion|"
        r"facs|faceposer|facial|lip_?sync|"
        r"анимац|скиннинг|скелетн|лицев|мимик",
        "анимация",
    ),
    (
        r"audio|sound|reverb|occlusion\w*\s*(?:звук|audio)|"
        r"звук|аудио|реверб",
        "звук",
    ),
    (
        r"netcode|multiplayer|server|tickrate|sub_?tick|latency|lag|prediction|"
        r"rollback|replication|network|packet|snapshot|dedicated|peer|lockstep|"
        r"anti_?cheat|eac|battleye|"
        r"мультиплеер|сетев|сеть|сервер|синхронизац|репликац|тикрейт|задержк|античит",
        "сеть и мультиплеер",
    ),
    (
        r"engine|unreal|unity|cryengine|source_?2|id_?tech|tech_[56]|"
        r"frostbite|anvil|redengine|decima|creation_engine|"
        r"modular|mod_support|modding|mod_api|workshop|\bmods?\b|sdk|editor|"
        r"toolset|tool|pipeline|script|blueprint|lua|visual_programming|plugin|"
        r"profiler|telemetry|benchmark|fps|frame_?time|frametime|stutter|hitch|"
        r"freeze|crash|overhead|budget|optimi|bottleneck|"
        r"движок|архитектур|инструмент|редактор|пайплайн|мод-поддерж|моддинг|"
        r"мастерск|производительн|оптимиз|бюджет|нагрузк|стоимост\w*\s+кадра|"
        r"подтормаж|вылет|завис",
        "движок и архитектура",
    ),
    (
        r"art_direction|styliz|art_style|visual_style|retopolog|normal_?bake|"
        r"стилизац|художественн\w*\s+стиль|репотоп",
        "art-пайплайн",
    ),
    # Геймплейные решения, задающие техтребования (сохраняем сознательно).
    (
        r"destruct|разруш|scale|масштаб|world_size|open_world|npc_count|"
        r"player_count|vehicle|транспорт|машин|автомобил|horse|лошад|"
        r"ship(?![a-z])|spaceship|кораб|traffic|трафик|swarm|рой|"
        r"ability|abilities|augmentation|modifier|"
        r"player|coop|co_op|cross_?play|versus|split_?screen|"
        r"игрок|кооператив|кооп|совместн\w*\s+прохожден|"
        r"процедурн\w*\s+генерац|процедурн\w*\s+мир|процедурн\w*\s+размещ",
        "геймплей, задающий техтребования",
    ),
]

#: Нетехнические решения: монетизация, дата выхода, сюжет, концовки и споры.
NON_TECHNICAL: list[tuple[str, str]] = [
    (
        r"microtransaction|monetiz|loot_?box|loot_|loots_|\bdlc\b|premium|season_pass|"
        r"battle_pass|atoms_|shard_|gacha|free_?to_?play|f2p|shop|purchase|"
        r"price|cosmetic|bundle|membership|subscription|currenc|credits_|"
        r"horse_armor|supply_drop|expansion|pass_|trade|market|economy|"
        r"монетизац|покупк|премиум|внутриигров\w*\s+валюта|валюта|подписк|торгов",
        "монетизация",
    ),
    (
        r"release_date|release_window|release_\d|delayed|delay|launch_date|"
        r"shipped|early_access|crowdfund|day_one|launcher|pulled_from|sale|"
        r"exclusiv\w*\s+(?:store|platform)|store_exclusiv|epic_store|steam_release|"
        r"publisher|marketing|promo|viral|drm|denuvo|"
        r"дата\s+выхода|выпуск|релиз\w*\s+\d|перенос|задержк\w*\s+релиз|"
        r"снят\s+с\s+продаж|издател|продвижени|реклам",
        "дата выхода и издание",
    ),
    (
        r"ending|endings|story|narrative|branch|choic|dialog|quest|cutscene|"
        r"karma|morality|protagonist|lore|new_game_plus|ng_plus|war_stor|"
        r"campaign|epilogue|charact\w*\s+arc|"
        r"концовк|сюжет|развилк|выбор|диалог|квест|повествован|истори\w*\s+кампан|"
        r"персонаж\w*\s+арк",
        "сюжет и концовки",
    ),
    (
        r"soundtrack|composer|score_|music|song|radio|voice_acting|voice_over|"
        r"localization|dub|"
        r"музык|саундтрек|композитор|радио|лицензи\w*\s+трек|озвуч|дубляж|локализац",
        "музыка, озвучение, локализация",
    ),
    (
        r"controvers|scandal|backlash|review|reception|critic|outrag|"
        r"negative|mixed|metacritic|award|esports|tournament|community|"
        r"скандал|критик|отзыв|репутац|негатив|турнир|киберспорт|сообществ",
        "реакция и продвижение",
    ),
    (
        r"perk|skill_tree|skill_|talent|unlock|leveling|level_up|progression|"
        r"class_|hero_|loadout|skin|emote|graffiti|collectible|achievement|"
        r"trophy|challenge|ranked|leaderboard|inventory|craft|recipe|drop_rate|"
        r"\bxp\b|experience_point|tutorial|onboarding|map_|level_design|"
        r"mission_|game_mode|round|matchmaking|customization|customisation|"
        r"puzzle|enemy|event_|fate|structure|combat|weapon|item_|health|"
        r"damage|death|hacking|survival|exploration|movement|parkour|climbing|"
        r"level_scaling|scaling_enem|gimmick|"
        r"уровн\w*\s+персонаж|навык|способност\w*\s+дерев|прогресс|разблокир|"
        r"класс\w*\s+персонаж|инвентар|крафт|достижен|обучен|режим\w*\s+игр|"
        r"головоломк|враг|событи|бо[её]в|оружи|здоров|урон|смерт|взлом|выживан|"
        r"исследован|передвижен|паркур",
        "контент и прогрессия",
    ),
]

#: Общие технические слова без явной подсистемы: в расчёт берём, в журнал пишем.
TECH_WEAK: list[tuple[str, str]] = [
    (
        r"perf|performance|throughput|scalab|quality|fidelity|pool|queue|batch|"
        r"instanc|profiling|latency_|"
        r"качеств\w*\s+график|пропускн|масштабир",
        "производительность (общее)",
    ),
]


@dataclass(frozen=True)
class Decision:
    """Разобранное решение из партии."""

    code: str
    impl: str
    #: ``technical`` | ``non_technical`` | ``unknown``
    scope: str
    #: Предметная область или причина исключения.
    category: str
    #: Какое правило сработало (для проверки решения вручную).
    matched: str

    @property
    def technical(self) -> bool:
        return self.scope == "technical"


def _find(patterns: list[tuple[str, str]], haystack: str) -> tuple[str, str] | None:
    for pattern, category in patterns:
        match = re.search(pattern, haystack)
        if match:
            return category, match.group(0)
    return None


def classify(code: str, impl: str = "") -> Decision:
    """Отнести решение к техническим, нетехническим или спорным."""
    hay = f"{code} {impl}".lower()
    if "procedur" in hay or "процедурн" in hay:
        if PROCEDURAL_TECH.search(hay):
            return Decision(code, impl, "technical", "процедурная генерация (мир/контент)", "procedur")
        if PROCEDURAL_CONTENT.search(hay):
            return Decision(code, impl, "non_technical", "сюжет и концовки", "procedur")
    hit = _find(TECH_STRONG, hay)
    if hit:
        return Decision(code, impl, "technical", hit[0], hit[1])
    hit = _find(NON_TECHNICAL, hay)
    if hit:
        return Decision(code, impl, "non_technical", hit[0], hit[1])
    hit = _find(TECH_WEAK, hay)
    if hit:
        return Decision(code, impl, "technical", hit[0], hit[1])
    return Decision(code, impl, "unknown", "не распознано", "")


def main() -> None:
    """Сводка по всем решениям партий: для проверки самого классификатора."""
    raw = json.loads((HERE / "games_raw.json").read_text(encoding="utf-8"))
    counts: dict[str, int] = {"technical": 0, "non_technical": 0, "unknown": 0}
    by_category: dict[str, int] = {}
    samples: dict[str, list[str]] = {"non_technical": [], "unknown": []}
    for game in raw:
        for item in game["methods"]:
            decision = classify(item["code"], item.get("impl") or "")
            counts[decision.scope] += 1
            by_category[decision.category] = by_category.get(decision.category, 0) + 1
            if decision.scope in samples and len(samples[decision.scope]) < 60:
                samples[decision.scope].append(f"{item['code']} [{decision.category}]")
    total = sum(counts.values())
    print(f"решений всего: {total}")
    for scope in ("technical", "non_technical", "unknown"):
        print(f"  {scope:14s} {counts[scope]:5d} ({100 * counts[scope] / total:.1f}%)")
    print("по категориям:")
    for category, n in sorted(by_category.items(), key=lambda kv: -kv[1]):
        print(f"  {category:44s} {n:5d}")
    for scope in ("non_technical", "unknown"):
        print(f"\nпримеры {scope}:")
        for line in samples[scope][:30]:
            print("  " + line)


if __name__ == "__main__":
    main()
