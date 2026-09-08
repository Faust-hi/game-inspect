# -*- coding: utf-8 -*-
"""Прогон игр из партий 1-11 через расчётную модель: разброс железа и итоги по решениям.

Каждая игра из партия-XX.md превращается в анкету ProjectProfile (ПК-платформа,
стадия release), прогоняется через POST /api/recommend с пустой корзиной.
Собираются: подобранное железо, индексы, классы, узкое место, топ-рекомендации.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

BASE = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]

VALID_FUNCTIONS = {
    "open_world_streaming", "large_scale_terrain", "procedural_vegetation",
    "storage_streaming", "dynamic_global_illumination", "baked_lighting",
    "dynamic_shadows", "particle_systems", "physics_simulation",
    "character_animation", "crowd_simulation", "ai_pathfinding",
    "water_simulation", "volumetric_effects", "post_processing",
    "rendering_architecture", "render_scalability", "geometry_pipeline",
    "upscaling_frame_generation", "multiplayer_netcode", "save_system",
    "audio_system", "build_delivery", "runtime_memory",
    "destruction_simulation", "project_architecture", "art_pipeline",
    "split_screen_rendering",
    # Добавлены по итогам аудита: трассировка лучей, меш-шейдеры,
    # процедурный мир и геймплейные подсистемы.
    "path_tracing", "ray_traced_effects", "dynamic_lighting", "mesh_shaders",
    "procedural_terrain", "gameplay_ability_system", "vehicle_simulation",
    "advanced_npc_ai",
}

# Отображение «неизвестный признак → ближайший известный».
#
# Признаки в партиях записаны свободным текстом: часть совпадает с кодами
# каталога, часть названа иначе, часть вообще не влияет на производительность
# (диалоги, крафт, монетизация). Для последних указан пустой список: признак
# осознанно не отображается, а не «потерян». Всё, чего нет ни в каталоге, ни
# здесь, попадает в отчёт о нераспознанном — молча отбрасывать нельзя.
FEATURE_SYNONYMS: dict[str, list[str]] = {
    # --- Трассировка лучей ---
    "ray_tracing": ["ray_traced_effects"],
    "real_time_ray_tracing": ["ray_traced_effects"],
    "ray_tracing_global_illumination": ["ray_traced_effects", "dynamic_global_illumination"],
    "ray_tracing_path_tracing": ["path_tracing"],
    "rtx_dx12": ["ray_traced_effects"],
    "weather_ray_tracing_enhanced": ["ray_traced_effects", "volumetric_effects"],
    # --- Освещение и погода ---
    "dynamic_lighting": ["dynamic_lighting"],
    "dynamic_weather_day_night": ["volumetric_effects"],
    "weather_conditions": ["volumetric_effects"],
    "extreme_weather_events": ["volumetric_effects"],
    "volumetric_smoke": ["volumetric_effects"],
    "cinematic_post_processing": ["post_processing"],
    # --- Мир, геометрия, процедурная генерация ---
    "procedural_generation": ["procedural_terrain"],
    "procedural_terrain": ["procedural_terrain"],
    "procedural_heist_approach": ["procedural_terrain"],
    "procedural_textures": ["art_pipeline"],
    "voxel_chunks": ["procedural_terrain"],
    "large_terrain_streaming": ["large_scale_terrain", "open_world_streaming"],
    "mesh_shaders": ["mesh_shaders"],
    "path_tracing": ["path_tracing"],
    "temporal_upscaling": ["upscaling_frame_generation"],
    "networked_water": ["water_simulation", "multiplayer_netcode"],
    # --- Разрушения ---
    "destruction_system": ["destruction_simulation"],
    "destruction_engine": ["destruction_simulation"],
    "destructible_demons": ["destruction_simulation"],
    "urban_destructible": ["destruction_simulation"],
    "ww1_setting_destruction": ["destruction_simulation"],
    "ww2_destruction": ["destruction_simulation"],
    # --- Геймплейные подсистемы персонажа ---
    "nanosuit_mechanics": ["gameplay_ability_system"],
    "nanosuit_2": ["gameplay_ability_system"],
    "augmentation_system": ["gameplay_ability_system"],
    "hero_abilities": ["gameplay_ability_system"],
    "hero_shooter_abilities": ["gameplay_ability_system"],
    "hero_classes": ["gameplay_ability_system"],
    "weapon_skills": ["gameplay_ability_system"],
    "plus_weapon_system": ["gameplay_ability_system"],
    "melee_weapons": ["gameplay_ability_system"],
    "melee_combat": ["gameplay_ability_system"],
    "real_combat": ["gameplay_ability_system"],
    "compound_bow": ["gameplay_ability_system"],
    # --- Транспорт ---
    "vehicle_simulation": ["vehicle_simulation"],
    "vehicle_physics": ["vehicle_simulation"],
    "vehicular_combat": ["vehicle_simulation"],
    "naval_combat": ["vehicle_simulation"],
    "horse_combat": ["vehicle_simulation"],
    "mech_combat": ["vehicle_simulation"],
    "mech_customization": ["vehicle_simulation"],
    # --- ИИ ---
    "advanced_npc_ai": ["advanced_npc_ai"],
    "stealth_ai": ["advanced_npc_ai"],
    "stealth_gameplay": ["advanced_npc_ai"],
    "ai_companion": ["advanced_npc_ai"],
    "ai_director": ["advanced_npc_ai"],
    "ai_director_2": ["advanced_npc_ai"],
    "ai_squad_fsm": ["advanced_npc_ai"],
    "crowd_ai": ["crowd_simulation", "advanced_npc_ai"],
    "ecological_simulation": ["advanced_npc_ai"],
    "platforming_mechanics": ["physics_simulation"],
    "grappling_hook_movement": ["character_animation", "physics_simulation"],
    "procedural_facial_animation": ["character_animation"],
    # --- Архитектура, сеть, поставка ---
    "ecs_simulation": ["project_architecture"],
    "tickrate_netcode": ["multiplayer_netcode"],
    "rollback_favor_shooter": ["multiplayer_netcode"],
    "subtick_input": ["multiplayer_netcode"],
    "lag_compensation": ["multiplayer_netcode"],
    "dedicated_servers": ["multiplayer_netcode"],
    "dedicated_server_multiplayer": ["multiplayer_netcode"],
    "dedicated_server_modding": ["multiplayer_netcode"],
    "crossplay_bedrock": ["multiplayer_netcode"],
    "modding_ecosystem": ["build_delivery"],
    "mod_api_fabric_forge": ["build_delivery"],
    "eden_editor": ["build_delivery"],
    # ---Осознанно не отображаются: влияния на стоимость кадра нет ---
    "procedural_narrative": [],
    "procedural_quests": [],
    "branching_dialogue": [],
    "dialogue": [],
    "choices": [],
    "voice_acting": [],
    "crafting": [],
    "settlement_building": [],
    "settlement_management": [],
    "resource_management": [],
    "survival_mechanics": [],
    "hacking_mechanics": [],
    "extraction_shooter_mechanics": [],
    "contraband_system": [],
    "rap_battles": [],
    "dice_game": [],
    "three_protagonist_system": [],
    "spaceship_modular_build": [],
    "outposts": [],
    "atomic_shop_monetization": [],
    "live_service_evolution": [],
    "microtransaction_controversy": [],
    "historical_realism_simulation": [],
    "nvidia_gameworks_partnership": [],
}
LEVEL_MAP = {"low": "low", "medium": "medium", "mid": "medium", "high": "high",
             "very_high": "high", "extreme": "high", "very high": "high",
             "huge": "high", "massive": "high"}
SCALE_MAP = {"small": "small", "medium": "medium", "large": "large",
             "very_large": "very_large", "unique": "very_large", "huge": "very_large",
             "massive": "very_large", "very large": "very_large"}
WORLD_MAP = {"linear": "linear", "hub": "hub", "hub_based": "hub", "arena": "arena",
             "open_world": "open_world", "procedural": "procedural",
             "sandbox": "sandbox", "multiplayer": "arena",
             "multiplayer-only": "arena", "semi_open": "hub",
             "semi-open": "hub", "level_based": "linear"}
FORMAT_MAP = {"3d": "3D", "2d": "2D", "2.5d": "2.5D", "2.5d/hybrid": "2.5D",
              "hybrid": "2.5D"}


def map_engine(raw: str) -> str:
    s = raw.lower()
    if "source" in s:
        return "source"
    if "unreal" in s or "ue4" in s or "ue5" in s or "ue 4" in s or "ue 5" in s:
        return "unreal"
    if "unity" in s:
        return "unity"
    if "cryengine" in s or "cry engine" in s:
        return "cryengine"
    if "godot" in s:
        return "godot"
    if "heroengine" in s or "hero engine" in s:
        return "heroengine"
    return "custom"


_RESOLUTION_RE = re.compile(r"(\d{3,4})\s*[pP]|\b4[kK]\b")
_FPS_RE = re.compile(r"(\d{2,3})\s*fps")
_PC_RE = re.compile(r"\bpc\b|windows", re.IGNORECASE)
_CONSOLE_RE = re.compile(
    r"ps\d|xbox|switch|консол|next[- ]?gen|current[- ]?gen", re.IGNORECASE
)


def _canonical_resolution(token: str) -> str:
    """Привести найденное разрешение к поддерживаемому профилем ряду."""
    token = token.strip().lower()
    if token == "4k":
        return "2160p"
    if not token.isdigit():
        return "1080p"
    height = int(token)
    if height <= 800:
        return "720p"
    if height <= 1300:
        return "1080p"
    if height <= 1900:
        return "1440p"
    return "2160p"


def parse_resolution_fps(raw: str) -> tuple[str, int]:
    """'1080p / 60 fps; ...' -> ('1080p', 60).

    В партиях цели часто перечислены по платформам: «720p (PS3) / 1080p (PC) /
    30 fps». Раньше бралось первое совпадение, и в расчёт уходила консольная
    цель — то есть не та, под которую оценивается конфигурация. Теперь
    предпочитается фрагмент с пометкой PC; фрагмент с явным указанием консоли
    отбрасывается, если есть альтернатива.
    """
    candidates: list[tuple[int, int, str, str]] = []
    for order, piece in enumerate(re.split(r"[;,]", raw)):
        # Пометка консоли действует на весь фрагмент цели: «4K / 30 fps
        # (Xbox Series X)» — консольная цель, даже если маркер стоит после
        # косой черты. Пометка PC, наоборот, точечная: «720p (PS3) / 1080p
        # (PC)» — платформы перечислены в одном фрагменте.
        piece_console = 1 if _CONSOLE_RE.search(piece) else 0
        for sub in piece.split("/"):
            m = _RESOLUTION_RE.search(sub)
            if not m:
                continue
            score = (
                (1 if _PC_RE.search(sub) else 0)
                - (1 if _CONSOLE_RE.search(sub) else 0)
                - piece_console
            )
            candidates.append((score, -order, _canonical_resolution(m.group(1) or m.group(0)), piece))
    if not candidates:
        fps_match = _FPS_RE.search(raw)
        return "1080p", int(fps_match.group(1)) if fps_match else 60

    # При равном приоритете выигрывает первое по порядку упоминания.
    _, _, resolution, piece = max(candidates, key=lambda item: (item[0], item[1]))
    # Частота берётся из того же фрагмента цели, что и разрешение.
    fps_match = _FPS_RE.search(piece) or _FPS_RE.search(raw)
    return resolution, int(fps_match.group(1)) if fps_match else 60


def map_features(raw: str) -> tuple[list[str], list[str]]:
    """Разобрать блок Features: известные коды и то, что осталось неизвестным.

    Токен вырезается по границам слов: без `\b` регулярное выражение
    откусывало хвосты от слов с большой буквы («Havok» → «avok»), и такие
    обрывки попадали в отчёт как нераспознанные признаки.
    """
    codes: list[str] = []
    unknown: list[str] = []
    for token in re.findall(r"\b[a-z][a-z0-9_]+\b", raw):
        if token in VALID_FUNCTIONS:
            if token not in codes:
                codes.append(token)
        elif token in FEATURE_SYNONYMS:
            for code in FEATURE_SYNONYMS[token]:
                if code not in codes:
                    codes.append(code)
        else:
            unknown.append(token)
    return codes, unknown


def parse_level(raw: str) -> str:
    token = raw.strip().split("(")[0].strip().split()[0].strip(",;").lower()
    return LEVEL_MAP.get(token, "medium")


def parse_games(text: str) -> list[dict]:
    games = []
    # Разделители между играми — заголовки "## N. Name (Year, ...) ..."
    blocks = re.split(r"(?m)^## ", text)
    for block in blocks[1:]:
        lines = block.splitlines()
        header = lines[0].strip()
        m = re.match(r"\d+\.\s*(.+?)\s*\((\d{4})", header)
        if not m:
            continue
        name = m.group(1).strip()
        year = int(m.group(2))
        game = {"name": name, "year": year, "batch": None}
        body = "\n".join(lines)

        em = re.search(r"\*\*Engine:\*\*\s*(.+)", body)
        game["engine"] = map_engine(em.group(1)) if em else "custom"

        fm = re.search(r"\*\*Format:\*\*\s*(\S+)", body)
        fmt = (fm.group(1).strip() if fm else "3D").lower()
        game["format"] = FORMAT_MAP.get(fmt, "3D")

        wm = re.search(r"\*\*World:\*\*\s*(\S+)", body)
        world = (wm.group(1).strip() if wm else "linear").strip("(,").lower()
        game["world_type"] = WORLD_MAP.get(world, "linear")

        sm = re.search(r"\*\*Scale:\*\*\s*(\S+)", body)
        scale = (sm.group(1).strip() if sm else "medium").lower()
        game["scale"] = SCALE_MAP.get(scale, "medium")

        tm = re.search(r"\*\*Targets?:\*\*\s*(.+)", body)
        game["resolution"], game["fps"] = parse_resolution_fps(tm.group(1)) if tm else ("1080p", 60)

        om = re.search(r"\*\*Object/NPC level:\*\*\s*(.+)", body)
        if om:
            parts = om.group(1).split("|")[0].split("/")
            game["object_level"] = parse_level(parts[0]) if parts else "medium"
            game["npc_level"] = parse_level(parts[1]) if len(parts) > 1 else "medium"
        else:
            game["object_level"] = "medium"
            game["npc_level"] = "medium"

        mm = re.search(r"\*\*Multiplayer:\*\*\s*(true|false)", body)
        game["multiplayer"] = bool(mm and mm.group(1) == "true")
        pm = re.search(r"\*\*Multiplayer:\*\*[^|]*?\((?:до\s*)?(\d+)", body)
        game["player_count"] = int(pm.group(1)) if pm else (16 if game["multiplayer"] else 1)

        feats = re.search(r"### Features\s*\n((?:\s*-\s*.+\n?)+)", body)
        raw_features = feats.group(1) if feats else ""
        game["functions"], game["unknown_features"] = map_features(raw_features)

        pm2 = re.search(r"\*\*Platforms:\*\*\s*(.+)", body)
        platforms = []
        if pm2:
            pl = pm2.group(1).lower()
            if "windows" in pl or "pc" in pl:
                platforms.append("pc_windows")
            if "linux" in pl:
                platforms.append("pc_linux")
        if not platforms:
            platforms = ["pc_windows"]
        game["platforms"] = platforms
        games.append(game)
    return games


def profile_of(game: dict) -> dict:
    return {
        "name": game["name"],
        "format": game["format"],
        "world_type": game["world_type"],
        "scale": game["scale"],
        "stage": "release",
        "engine": game["engine"],
        "engine_version": None,
        "platforms": game["platforms"],
        "object_count_level": game["object_level"],
        "object_count": None,
        "npc_count_level": game["npc_level"],
        "npc_count": None,
        "player_count": game["player_count"],
        "local_view_count": None,
        "multiplayer": game["multiplayer"],
        "functions": game["functions"],
        "target_resolution": game["resolution"],
        "target_quality": "high",
        "target_fps": game["fps"],
        "render_api": "auto",
        "storage_type": "auto",
        "memory_model": "dedicated",
        "upscaling_method": "auto",
        "network_topology": "client_server",
        "frame_generation": False,
        "base_render_fps": None,
        "physics_tick_hz": None,
        "ai_tick_hz": None,
        "streaming_pool_gb": None,
        "draw_call_budget": None,
        "simulation_radius_m": None,
        "audio_complexity": "medium",
        "vram_limit_gb": None,
        "ram_limit_gb": None,
        "size_limit_gb": None,
        "priority": "balanced",
    }


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_all() -> list[dict]:
    results = []
    for path in sorted(ROOT.glob("партия-*.md")):
        batch_id = path.stem.replace("партия-", "")
        text = path.read_text(encoding="utf-8")
        for game in parse_games(text):
            game["batch"] = batch_id
            profile = profile_of(game)
            try:
                data = post("/api/recommend", {"profile": profile, "basket": []})
            except Exception as exc:  # noqa: BLE001
                results.append({"game": game, "error": str(exc)})
                continue
            hw = data.get("hardware") or {}
            results.append({
                "game": game,
                "hardware": {
                    "reference_gpu": hw.get("reference_gpu", {}).get("model") if hw.get("reference_gpu") else None,
                    "gpu_class": hw.get("gpu_class"),
                    "reference_cpu": hw.get("reference_cpu", {}).get("model") if hw.get("reference_cpu") else None,
                    "cpu_class": hw.get("cpu_class"),
                    "vram_gb": hw.get("estimated_vram_gb"),
                    "ram_gb": hw.get("estimated_ram_gb"),
                    "required_gpu_index": hw.get("required_gpu_index"),
                    "required_cpu_index": hw.get("required_cpu_index"),
                    "bottleneck": hw.get("bottleneck_label"),
                    "storage": hw.get("storage_requirement"),
                    "exceeds": hw.get("exceeds_catalog"),
                },
                "recommendations": [
                    {"code": r["method_code"], "name": r["method_name"], "score": r["score"]}
                    for r in (data.get("recommendations") or [])[:8]
                ],
                "excluded_count": len(data.get("excluded") or []),
                "risks_count": len(data.get("risks") or []),
                "load": data.get("load_profile") or {},
            })
    return results


def main() -> None:
    results = run_all()
    out = ROOT / "audit-2026-09-07" / "batch-run-results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    print(f"Прогнано игр: {len(results)} (успешно {len(ok)}, ошибок {len(failed)})")
    print(f"Результаты: {out}")
    for r in failed:
        print("  ОШИБКА:", r["game"]["name"], "->", r["error"])

    # Признаки, которых нет ни в каталоге, ни в таблице синонимов: молча
    # отбрасывать их нельзя — это и есть список для расширения каталога.
    leftover = Counter(
        token for r in results for token in r["game"].get("unknown_features", [])
    )
    empty = [r["game"]["name"] for r in results if not r["game"]["functions"]]
    print(f"Игр без распознанных функций: {len(empty)}")
    for name in empty:
        print("  ПУСТО:", name)
    print(f"Нераспознанных признаков: {sum(leftover.values())} ({len(leftover)} уникальных)")
    for token, count in leftover.most_common():
        print(f"  {count:3d}  {token}")


if __name__ == "__main__":
    sys.exit(main())
