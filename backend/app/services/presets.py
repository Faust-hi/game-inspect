"""Экспорт корзины решений в пресеты движков.

Инструмент-консультант не применяет оптимизации сам, но отдаёт стартовую
конфигурацию, которую разработчик копирует в проект. Правило честности:
строка пресета либо ссылается на выбранный метод (`; from <код>`), либо явно
помечена значением по умолчанию (`; default`). Ничего не выдумывается:
неизвестное остаётся закомментированным.
"""
from __future__ import annotations

from ..schemas.catalog import ProjectProfile

QUALITY_TIER = {"low": 0, "medium": 1, "high": 2, "ultra": 3}


def _tier(profile: ProjectProfile) -> int:
    return QUALITY_TIER.get(profile.target_quality, 2)


def unreal_scalability_ini(profile: ProjectProfile, basket: set[str]) -> str:
    """Группа [ScalabilitySettings] для DefaultScalability.ini."""
    tier = _tier(profile)

    def pick(codes: set[str], value: int, comment: str) -> str:
        used = sorted(codes & basket)
        if used:
            return f"{value} ; from {', '.join(used)} — {comment}"
        return f"{value} ; default — {comment}, в корзине нет связанных решений"

    lines = [
        "; Сгенерировано ИС поддержки принятия решений.",
        f"; Проект: {profile.name} | {profile.target_resolution} / {profile.target_quality} / {profile.target_fps} FPS",
        "; Строка со значением — активна; всё несвязанное помечено default.",
        "; Скопируйте нужное в Config/DefaultScalability.ini и проверьте на min-spec.",
        "[ScalabilitySettings]",
        f"sg.ResolutionQuality={pick({'temporal_upscaling', 'dynamic_resolution_scaling'}, 100 if tier >= 2 else 85, 'базовое разрешение кадра')}",
        f"sg.ViewDistance={pick({'world_partition_streaming', 'hierarchical_lod'}, 3 if tier >= 2 else 2, 'дальность прорисовки')}",
        f"sg.AntiAliasing={pick({'temporal_upscaling'}, 4 if tier >= 2 else 2, 'сглаживание')}",
        f"sg.ShadowQuality={pick({'cascaded_shadow_maps', 'static_shadow_caching', 'distance_field_shadows'}, 3 if tier >= 2 else 1, 'тени')}",
        f"sg.PostProcessQuality={pick({'temporal_upscaling', 'post_effect_selective'}, 3 if tier >= 2 else 1, 'постобработка')}",
        f"sg.TextureQuality={pick({'virtual_texturing', 'neural_texture_compression', 'lightmap_compression_streaming'}, 3 if tier >= 2 else 2, 'текстуры')}",
        f"sg.EffectsQuality={pick({'volumetric_half_resolution', 'froxel_volumetric_fog', 'gpu_particle_simulation'}, 3 if tier >= 2 else 1, 'эффекты')}",
        f"sg.FoliageQuality={pick({'gpu_instancing_vegetation', 'vegetation_atlas_lod'}, 3 if tier >= 2 else 1, 'растительность')}",
    ]
    if profile.vram_limit_gb:
        pool_mb = int(profile.vram_limit_gb * 1024 * 0.7)
        lines.append(
            f"r.Streaming.PoolSize={pool_mb} ; from profile.vram_limit_gb: "
            f"70% лимита под пул текстур, остальное — кадр и система"
        )
    else:
        lines.append(";r.Streaming.PoolSize=2048 ; default — задайте vram_limit_gb для точного значения")
    if "dynamic_resolution_scaling" in basket:
        lines.append("r.DynamicRes.OperationMode=2 ; from dynamic_resolution_scaling — динамическое разрешение")
    else:
        lines.append(";r.DynamicRes.OperationMode=0 ; default — dynamic_resolution_scaling не выбран")
    return "\n".join(lines) + "\n"


def unity_quality_preset(profile: ProjectProfile, basket: set[str]) -> dict:
    """Один рекомендуемый тир качества Unity: каждое поле знает свой источник."""

    def val(codes: set[str], chosen, default, comment: str) -> dict:
        used = sorted(codes & basket)
        if used:
            return {"value": chosen, "source": ", ".join(used), "comment": comment}
        return {"value": default, "source": "default", "comment": comment + " (в корзине нет связанных решений)"}

    tier = _tier(profile)
    return {
        "tier": profile.target_quality,
        "pixelLightCount": val({"deferred_forward_plus_choice"}, 4 if tier >= 2 else 2, 2, "пиксельных источников света"),
        "antiAliasing": val({"temporal_upscaling", "post_effect_selective"}, 4 if tier >= 2 else 2, 2, "сглаживание MSAA"),
        "shadows": val({"cascaded_shadow_maps", "static_shadow_caching"}, 2 if tier >= 2 else 1, 1, "режим теней 0/1/2"),
        "shadowResolution": val({"cascaded_shadow_maps"}, 2 if tier >= 2 else 1, 1, "разрешение карт теней"),
        "softParticles": val({"gpu_particle_simulation", "flipbook_particles"}, True, True, "мягкие частицы"),
        "vSyncCount": {"value": 1, "source": "default", "comment": "вертикальная синхронизация"},
        "renderScale": val({"dynamic_resolution_scaling"}, 0.8, 1.0, "масштаб рендера URP"),
        "srpBatcher": val({"bindless_uber_shaders"}, True, "consider", "SRP Batcher: true либо рассмотреть"),
        "textureStreaming": val({"virtual_texturing", "neural_texture_compression"}, True, False, "потоковая подгрузка мипов"),
    }


def godot_rendering_preset(profile: ProjectProfile, basket: set[str]) -> dict:
    """Ключи project.godot [rendering]: значение либо из корзины, либо default."""

    def val(codes: set[str], chosen, default, comment: str) -> dict:
        used = sorted(codes & basket)
        if used:
            return {"value": chosen, "source": ", ".join(used), "comment": comment}
        return {"value": default, "source": "default", "comment": comment + " (в корзине нет связанных решений)"}

    tier = _tier(profile)
    return {
        "rendering/anti_aliasing/quality/msaa_3d": val(set(), 2 if tier >= 2 else 1, 1, "MSAA 3D 0–3"),
        "rendering/anti_aliasing/quality/ssao_quality": val(
            {"screen_space_gi", "screen_space_contact_shadows"}, 2 if tier >= 2 else 1, 1, "качество SSAO"),
        "rendering/anti_aliasing/quality/ssil_quality": val(
            {"screen_space_gi"}, 2 if tier >= 2 else 0, 0, "качество SSIL"),
        "rendering/lights_and_shadows/directional_shadow/size": val(
            {"cascaded_shadow_maps"}, 4096 if tier >= 2 else 2048, 2048, "размер карт теней"),
        "rendering/scaling_3d/mode": val(
            {"temporal_upscaling"}, 1, 0, "0 — билинейно, 1 — FSR 1.0"),
        "rendering/scaling_3d/scale": val(
            {"dynamic_resolution_scaling"}, 0.8, 1.0, "масштаб 3D-вьюпорта"),
        "rendering/textures/vram_compression/import_etc2_astc": val(
            {"build_size_startup_budgets"}, True, False, "сжатие текстур для мобильных"),
    }


def build_preset_files(profile: ProjectProfile, basket: list[str]) -> list[dict]:
    """Три файла пресетов с заголовком о происхождении каждой строки."""
    codes = set(basket or [])
    header = (
        f"Проект: {profile.name} | {profile.target_resolution} / "
        f"{profile.target_quality} / {profile.target_fps} FPS | корзина: {len(codes)}"
    )
    return [
        {"name": "DefaultScalability.ini", "language": "ini",
         "content": f"; {header}\n" + unreal_scalability_ini(profile, codes)},
        {"name": "unity-quality-preset.json", "language": "json",
         "content": __import__("json").dumps(
             {"_meta": header, "preset": unity_quality_preset(profile, codes)},
             ensure_ascii=False, indent=2) + "\n"},
        {"name": "godot-rendering-preset.json", "language": "json",
         "content": __import__("json").dumps(
             {"_meta": header, "rendering": godot_rendering_preset(profile, codes)},
             ensure_ascii=False, indent=2) + "\n"},
    ]
