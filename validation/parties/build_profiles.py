"""Сборка профилей ProjectProfile для всех игр партий 01-11.

Выход: validation/parties/profiles.json
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from method_map import match_methods  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

RAW = json.loads((HERE / "games_raw.json").read_text(encoding="utf-8"))
CATALOG = json.loads((HERE / "catalog.json").read_text(encoding="utf-8"))
FUNC_CODES = {f["code"] for f in CATALOG["functions"]}
METHOD_CODES = {m["code"] for m in CATALOG["methods"]}

RES_ORDER = ["720p", "768p", "900p", "1080p", "1200p", "1440p", "1600p", "2160p", "4k"]
RES_RX = re.compile(r"(720p|768p|900p|1080p|1200p|1440p|1600p|2160p|4[kK])")
FPS_GRID = [30, 50, 60, 75, 90, 100, 120, 144, 165, 240, 300, 360, 400]


def map_engine(raw: str) -> tuple[str, str | None]:
    r = (raw or "").lower()
    if "anvil" in r:
        return "custom", None  # AnvilNext — собственный движок Ubisoft
    if "source" in r:
        return "source", "2.0" if "source 2" in r else "1.0"
    if "unreal" in r:
        m = re.search(r"unreal engine\s*(\d)", r)
        return "unreal", f"{m.group(1)}.0" if m else None
    if "cryengine" in r:
        m = re.search(r"cryengine\s*(v|\d)", r)
        v = None
        if m:
            v = "5.0" if m.group(1) == "v" else f"{m.group(1)}.0"
        return "cryengine", v
    if "unity" in r:
        return "unity", None
    if "godot" in r:
        return "godot", None
    if "heroengine" in r:
        return "heroengine", None
    return "custom", None


def map_world(raw: str) -> str:
    r = (raw or "").lower()
    if "infinite" in r or "procedural" in r and "open" not in r:
        return "procedural"
    if "sandbox" in r or "песочниц" in r:
        return "sandbox"
    if "arena" in r or "арен" in r:
        return "arena"
    if "multiplayer" in r:
        return "arena"
    if "hub" in r:
        return "hub"
    if "linear" in r:
        return "linear"
    if "open" in r or "semi-open" in r or "открыт" in r:
        return "open_world"
    return "open_world"


def map_scale(raw: str) -> str:
    r = (raw or "").lower()
    if "very_large" in r or "infinite" in r or "unique" in r:
        return "very_large"
    if "medium-large" in r:
        return "large"
    if "small-medium" in r:
        return "medium"
    if "large" in r:
        return "large"
    if "medium" in r:
        return "medium"
    if "small" in r:
        return "small"
    return "unknown"


def map_level(raw: str, idx: int) -> str:
    parts = [p.strip() for p in (raw or "").split("/")]
    if len(parts) <= idx:
        return "unknown"
    tok = parts[idx].split("(")[0].strip().lower()
    tok = re.sub(r"[^a-z_]", "", tok)
    if tok in ("very_high", "extreme", "high"):
        return "high"
    if tok in ("medium", "med"):
        return "medium"
    if tok == "low":
        return "low"
    return "unknown"


def map_resolution(targets: str) -> str:
    found = [m.lower() for m in RES_RX.findall(targets or "")]
    if not found:
        return "1080p"
    uniq = []
    for f in found:
        if f not in uniq:
            uniq.append(f)
    # отбрасываем консольные 720p/768p/900p, если заявлено и более высокое
    while len(uniq) > 1 and uniq[0] in ("720p", "768p", "900p"):
        uniq = uniq[1:]
    res = uniq[0]
    return res if res in RES_ORDER else "1080p"


def map_fps(game: dict) -> int:
    """Кадровая цель: максимум из паспортного бюджета и первой заявленной цели."""
    # приоритет — паспортный кадровый бюджет; иначе первая заявленная цель
    if game.get("frame_budget_ms"):
        raw = 1000.0 / game["frame_budget_ms"]
        return min(FPS_GRID, key=lambda g: abs(g - raw))
    f = re.findall(r"(\d{2,3})\s*fps", (game.get("targets_raw") or "").lower())
    if f:
        return min(FPS_GRID, key=lambda g: abs(g - int(f[0])))
    return 60


# Графический API: в партиях 3-11 поле API отсутствует, поэтому задаётся явно
# по known-фактам из инженерных паспортов.
API_OVERRIDE: list[tuple[str, str]] = [
    ("Portal (2007", "dx9"), ("Portal 2", "dx9"), ("Garry's Mod", "dx9"),
    ("Modern Warfare (2007", "dx9"), ("Civilization V", "dx11"), ("World at War", "dx9"),
    ("Witcher 2", "dx9"), ("Oblivion", "dx9"), ("Arkham Asylum", "dx9"),
    ("Final Fantasy XIV", "dx11"),
    ("Half-Life 2 (2004", "dx9"), ("Episode One", "dx9"), ("Episode Two", "dx9"),
    ("Counter-Strike: Source", "dx9"), ("Left 4 Dead (2008", "dx9"), ("Left 4 Dead 2", "dx9"),
    ("Global Offensive (2012", "dx9"),
    ("Dark Souls: Remastered", "dx11"), ("Scholar of the First Sin", "dx11"),
    ("Dark Souls III", "dx11"), ("Sekiro", "dx11"), ("Elden Ring", "dx12"),
    ("Armored Core VI", "dx12"),
    ("Assassin's Creed Unity", "dx11"), ("Assassin's Creed Origins", "dx11"),
    ("Assassin's Creed Odyssey", "dx11"), ("Assassin's Creed Valhalla", "dx12"),
    ("For Honor", "dx11"),
    ("Skyrim Special", "dx11"), ("Fallout 4", "dx11"), ("Fallout 76", "dx11"),
    ("Starfield", "dx12"),
    ("Grand Theft Auto IV", "dx9"), ("Grand Theft Auto V", "dx11"),
    ("Red Dead Redemption 2", "vulkan"), ("Trilogy", "dx12"),
    ("DOOM (2016", "vulkan"), ("DOOM Eternal", "vulkan"), ("Rage (2011", "opengl"),
    ("Quake Champions", "vulkan"),
    ("Crysis (2007", "dx11"), ("Crysis 2", "dx9"), ("Crysis 3", "dx11"),
    ("Hunt: Showdown", "dx12"),
    ("Battlefield 4", "dx11"), ("Battlefield 1 (", "dx11"), ("Battlefield V", "dx12"),
    ("Battlefield 2042", "dx12"), ("Battlefront II", "dx11"),
    ("Metro Exodus", "dx12"), ("Mankind Divided", "dx12"), ("Kingdom Come", "dx11"),
    ("Alan Wake 2", "dx12"),
    ("Cyberpunk 2077", "dx12"), ("Overwatch", "dx11"), ("Minecraft", "opengl"),
    ("Counter-Strike: GO", "dx11"), ("Arma 3", "dx11"),
]


def map_api(game: dict) -> str:
    title = game["title"]
    for frag, api in API_OVERRIDE:
        if frag in title:
            return api
    raw = (game.get("api_raw") or "").lower()
    for token in ("dx12", "vulkan", "dx11", "dx9", "opengl", "dx8"):
        if token in raw:
            return "dx9" if token == "dx8" else token
    year = game.get("year") or 2010
    if year >= 2016:
        return "dx12"
    if year >= 2010:
        return "dx11"
    return "dx9"


def map_multiplayer(raw: str) -> bool:
    return (raw or "").strip().lower().startswith("true")


def player_count(game: dict) -> int:
    raw = (game.get("multiplayer_raw") or "")
    m = re.search(r"до\s*(\d+)", raw)
    if not map_multiplayer(raw):
        return 1
    if m:
        return min(int(m.group(1)), 128)
    return 16


# Фичи партий, которых нет в каталоге, но которые однозначно соответствуют
# функции каталога (только технические; геймплейные/контентные отброшены).
FEATURE_ALIASES: dict[str, str] = {
    "procedural_generation": "procedural_terrain",
    "procedural_textures": "procedural_terrain",
    "voxel_chunks": "procedural_terrain",
    "tickrate_netcode": "multiplayer_netcode",
    "subtick_input": "multiplayer_netcode",
    "lag_compensation": "multiplayer_netcode",
    "rollback_favor_shooter": "multiplayer_netcode",
    "dedicated_servers": "multiplayer_netcode",
    "dedicated_server_multiplayer": "multiplayer_netcode",
    "dedicated_server_modding": "project_architecture",
    "modding_ecosystem": "project_architecture",
    "mod_api_fabric_forge": "project_architecture",
    "eden_editor": "project_architecture",
    "ai_director": "advanced_npc_ai",
    "ai_director_2": "advanced_npc_ai",
    "ai_companion": "advanced_npc_ai",
    "stealth_ai": "advanced_npc_ai",
    "ai_squad_fsm": "advanced_npc_ai",
    "crowd_ai": "crowd_simulation",
    "ecs_simulation": "crowd_simulation",
    "destruction_system": "destruction_simulation",
    "destruction_engine": "destruction_simulation",
    "destructible_demons": "destruction_simulation",
    "urban_destructible": "destruction_simulation",
    "ww1_setting_destruction": "destruction_simulation",
    "ww2_destruction": "destruction_simulation",
    "ray_tracing": "ray_traced_effects",
    "real_time_ray_tracing": "ray_traced_effects",
    "rtx_dx12": "ray_traced_effects",
    "weather_ray_tracing_enhanced": "ray_traced_effects",
    "ray_tracing_path_tracing": "path_tracing",
    "ray_tracing_global_illumination": "dynamic_global_illumination",
    "temporal_upscaling": "upscaling_frame_generation",
    "vehicle_physics": "vehicle_simulation",
    "vehicular_combat": "vehicle_simulation",
    "naval_combat": "water_simulation",
    "networked_water": "water_simulation",
    "volumetric_smoke": "volumetric_effects",
    "dynamic_weather_day_night": "volumetric_effects",
    "weather_conditions": "volumetric_effects",
    "extreme_weather_events": "volumetric_effects",
    "large_terrain_streaming": "large_scale_terrain",
    "hero_abilities": "gameplay_ability_system",
    "hero_shooter_abilities": "gameplay_ability_system",
    "augmentation_system": "gameplay_ability_system",
    "weapon_skills": "gameplay_ability_system",
    "mech_customization": "gameplay_ability_system",
    "cinematic_post_processing": "post_processing",
    "procedural_facial_animation": "character_animation",
    "historical_realism_simulation": "physics_simulation",
    "real_combat": "physics_simulation",
    "melee_combat": "physics_simulation",
    "melee_weapons": "physics_simulation",
    "ecological_simulation": "procedural_vegetation",
}


def derive_functions(game: dict, world: str, scale: str) -> list[str]:
    feats = []
    for f in game["features"]:
        if f in FUNC_CODES:
            feats.append(f)
        elif f in FEATURE_ALIASES:
            feats.append(FEATURE_ALIASES[f])
    out = list(dict.fromkeys(feats))
    if world == "open_world" and "open_world_streaming" not in out:
        out.append("open_world_streaming")
    if world == "procedural" and "procedural_terrain" not in out:
        out.append("procedural_terrain")
    if scale in ("large", "very_large") and "large_scale_terrain" not in out:
        out.append("large_scale_terrain")
    if map_multiplayer(game.get("multiplayer_raw")) and "multiplayer_netcode" not in out:
        out.append("multiplayer_netcode")
    if not out:
        out = ["rendering_architecture", "post_processing"]
    return out


def main() -> None:
    profiles = []
    for g in RAW:
        engine, ever = map_engine(g["engine_raw"])
        world = map_world(g["world_raw"])
        scale = map_scale(g["scale_raw"])
        obj = map_level(g["levels_raw"], 0)
        npc = map_level(g["levels_raw"], 1)
        funcs = derive_functions(g, world, scale)
        basket, unmatched = [], []
        matched_decisions = 0
        for m in g["methods"]:
            hits = match_methods(m["code"], m["impl"])
            if hits:
                basket.extend(hits)
                matched_decisions += 1
            else:
                unmatched.append(m["code"])
        basket = sorted(set(basket))
        profile = {
            "name": g["title"],
            "format": "3D",
            "world_type": world,
            "scale": scale,
            "stage": "release",
            "engine": engine,
            "engine_version": ever,
            "platforms": ["pc_windows"],
            "object_count_level": obj,
            "npc_count_level": npc,
            "player_count": player_count(g),
            "multiplayer": map_multiplayer(g.get("multiplayer_raw")),
            "functions": funcs,
            "target_resolution": map_resolution(g["targets_raw"]),
            "target_quality": "high" if (g.get("year") or 2010) >= 2013 else "medium",
            "target_fps": map_fps(g),
            "render_api": map_api(g),
            "storage_type": "auto",
            "memory_model": "auto",
            "upscaling_method": "auto",
            "network_topology": "dedicated" if map_multiplayer(g.get("multiplayer_raw")) else "auto",
            "priority": "balanced",
        }
        profiles.append(
            {
                "id": f"p{g['party']:02d}-{len(profiles) + 1:02d}",
                "party": g["party"],
                "title": g["title"],
                "year": g["year"],
                "engine_dss": engine,
                "engine_raw": g["engine_raw"],
                "frame_budget_ms": g["frame_budget_ms"],
                "hw": g["hw"],
                "profile": profile,
                "basket": basket,
                "n_decisions": len(g["methods"]),
                "n_matched": len(set(basket)),
                "n_decisions_matched": matched_decisions,
                "unmatched": unmatched,
            }
        )
    (HERE / "profiles.json").write_text(
        json.dumps(profiles, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"профилей: {len(profiles)}")
    tot_m = sum(p["n_matched"] for p in profiles)
    tot_d = sum(p["n_decisions"] for p in profiles)
    print(f"решений всего: {tot_d}, сопоставлено с каталогом: {tot_m}")
    for p in profiles:
        print(
            f"  {p['id']} {p['title'][:38:]:40s} {p['engine_dss']:10s} "
            f"{p['profile']['world_type']:11s} {p['profile']['scale']:10s} "
            f"{p['profile']['target_resolution']:6s}/{p['profile']['target_fps']:3d} "
            f"{p['profile']['render_api']:7s} funcs={len(p['profile']['functions']):2d} "
            f"basket={len(p['basket']):2d}/{p['n_decisions']:2d}"
        )


if __name__ == "__main__":
    main()
