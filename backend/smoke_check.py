"""Сквозная проверка работающего backend-приложения (раздел 8 плана).

Запуск:
    python backend/smoke_check.py [--base http://127.0.0.1:8000]

Скрипт обращается к уже запущенному uvicorn и проверяет:
  * доступность сервиса и наполнение каталога по нормам MVP;
  * восемь сценариев проверки из раздела 8;
  * наличие источника у каждой опубликованной записи;
  * пересчёт профиля нагрузки и аппаратную оценку;
  * стадийные подсказки: предупреждения и предложения для каждой стадии
    и закрытие уровней решений на поздних стадиях;
  * административный раздел и журнал целостности базы.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

BASE_DEFAULT = "http://127.0.0.1:8000"

# Сценарии из раздела 8 плана.
SCENARIOS = {
    "3d_open_world": dict(format="3D", world_type="open_world", scale="very_large",
                          functions=["open_world_streaming", "large_scale_terrain",
                                     "procedural_vegetation", "dynamic_shadows", "crowd_simulation"]),
    "linear_3d": dict(format="3D", world_type="linear", scale="medium", stage="production",
                      engine="unity", functions=["baked_lighting", "dynamic_shadows",
                                                 "character_animation", "post_processing"]),
    "game_2d": dict(format="2D", world_type="linear", scale="small", engine="godot",
                    functions=["particle_systems", "post_processing", "character_animation"]),
    "hybrid_25d": dict(format="2.5D", world_type="hub", scale="medium", engine="unity",
                       functions=["baked_lighting", "crowd_simulation", "post_processing"]),
    "multiplayer": dict(format="3D", world_type="arena", scale="small",
                        functions=["multiplayer_netcode", "physics_simulation",
                                   "character_animation"],
                        multiplayer=True, player_count=64, target_fps=120),
    "many_npc": dict(format="3D", world_type="open_world", scale="large",
                     functions=["crowd_simulation", "ai_pathfinding", "character_animation"],
                     npc_count_level="high"),
    "early_concept": dict(format="3D", world_type="open_world", scale="large", stage="concept",
                          functions=["open_world_streaming", "dynamic_global_illumination"]),
    "content_production": dict(format="3D", world_type="open_world", scale="large",
                               stage="production",
                               functions=["open_world_streaming", "large_scale_terrain",
                                          "baked_lighting"]),
}

BASE_PROFILE = {
    "stage": "prototype", "engine": "unreal", "platforms": ["pc_windows"],
    "target_resolution": "1080p", "target_quality": "high", "target_fps": 60,
    "object_count_level": "medium", "npc_count_level": "medium",
}

failures: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    """Фиксирует результат одной проверки."""
    global checks
    checks += 1
    if not condition:
        failures.append(message)


def call(method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(f"{args.base}{path}", data=data, method=method)
    request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:  # 4xx/5xx — возвращаем код как есть
        return error.code, {}


def main() -> int:
    status, health = call("GET", "/api/health")
    check(status == 200 and health.get("status") == "ok", f"health недоступен: {status}")
    if status != 200:
        print("Backend недоступен. Запустите uvicorn и повторите проверку.")
        return 1
    print(f"health: {health}")

    enums_status, enums = call("GET", "/api/meta/enums")
    check(enums_status == 200 and "relation_types" in enums, "перечисления предметной области недоступны")
    check(len(enums.get("relation_types", [])) == 8, "ожидается 8 типов связи метод—инструмент движка")

    _, functions = call("GET", "/api/catalog/functions")
    _, methods = call("GET", "/api/catalog/methods")
    _, engines = call("GET", "/api/catalog/engines")
    _, conflicts = call("GET", "/api/catalog/conflicts")
    _, hardware = call("GET", "/api/catalog/hardware")

    check(len(functions) >= 15, f"функций меньше 15: {len(functions)}")
    check(len(methods) >= 40, f"методов меньше 40: {len(methods)}")
    check(len(hardware.get("cpu", [])) >= 30, f"процессоров меньше 30: {len(hardware.get('cpu', []))}")
    check(len(hardware.get("gpu", [])) >= 30, f"видеокарт меньше 30: {len(hardware.get('gpu', []))}")
    check(len(conflicts) >= 10, f"конфликтов меньше 10: {len(conflicts)}")
    codes = {engine["code"] for engine in engines}
    for required in ("unreal", "unity", "godot", "custom"):
        check(required in codes, f"в каталоге нет движка {required}")

    no_source = [m["code"] for m in methods if m.get("status") == "published" and not m.get("source_url")]
    check(not no_source, f"у опубликованных методов нет источника: {no_source[:5]}")

    print(f"\nКаталог: функций {len(functions)}, методов {len(methods)}, движков {len(engines)}, "
          f"CPU {len(hardware.get('cpu', []))}, GPU {len(hardware.get('gpu', []))}, "
          f"связей конфликтов {len(conflicts)}")

    print("\nСценарии раздела 8:")
    for name in sorted(SCENARIOS):
        profile = dict(BASE_PROFILE)
        profile.update(SCENARIOS[name])
        status, data = call("POST", "/api/recommend", {"profile": profile, "basket": []})
        ok = status == 200
        check(ok, f"сценарий {name}: ошибка запроса {status}")
        if not ok:
            print(f"  {name:<20} ОШИБКА {status}")
            continue
        recommendations = data.get("recommendations", [])
        excluded = data.get("excluded", [])
        hw = data.get("hardware") or {}
        check(bool(recommendations), f"сценарий {name}: нет рекомендаций")
        check(all(item.get("reasons") for item in recommendations), f"сценарий {name}: нет объяснений")
        check(all(item.get("flags") for item in recommendations), f"сценарий {name}: нет пометок")
        check(bool(hw), f"сценарий {name}: нет аппаратной оценки")
        check(hw.get("confidence", 1.0) <= 1.0, f"сценарий {name}: некорректная уверенность")
        top = recommendations[0]["method_name"] if recommendations else "—"
        print(f"  {name:<20} рекомендаций {len(recommendations):>2}, исключено {len(excluded):>2}, "
              f"уверенность {hw.get('confidence', 0):.2f}, первый: {top}")

    # Воспроизводимость TOPSIS.
    profile = dict(BASE_PROFILE)
    profile.update(SCENARIOS["3d_open_world"])
    _, first = call("POST", "/api/recommend", {"profile": profile, "basket": []})
    _, second = call("POST", "/api/recommend", {"profile": profile, "basket": []})
    order_one = [item["method_code"] for item in first["recommendations"]]
    order_two = [item["method_code"] for item in second["recommendations"]]
    check(order_one == order_two, "TOPSIS не воспроизводится при повторном расчёте")
    print(f"\nВоспроизводимость TOPSIS: {'да' if order_one == order_two else 'НЕТ'}")

    # Корзина, профиль нагрузки, аппаратная оценка.
    basket = order_one[:3]
    status, load = call("POST", "/api/load-profile", {"profile": profile, "basket": basket})
    check(status == 200 and load.get("per_resource"), "профиль нагрузки не рассчитан")
    check(
        status == 200 and all(key in load for key in ("cpu", "gpu", "ram", "vram", "disk", "network")),
        "профиль нагрузки не содержит всех подсистем",
    )
    status, estimate = call("POST", "/api/hardware-estimate", {"profile": profile, "basket": basket})
    check(status == 200 and estimate.get("reference_gpu") and estimate.get("reference_cpu"),
          "аппаратная оценка не сформирована")
    check(bool(estimate.get("caveats")), "нет оговорки об ориентировочном характере оценки")
    reference_cpu = estimate.get("reference_cpu") or {}
    reference_gpu = estimate.get("reference_gpu") or {}
    print(f"Корзина из {len(basket)} решений: CPU «{reference_cpu.get('model', '—')}», "
          f"GPU «{reference_gpu.get('model', '—')}», VRAM {estimate.get('estimated_vram_gb', 0):.1f} ГБ, "
          f"RAM {estimate.get('estimated_ram_gb', 0):.1f} ГБ, "
          f"уверенность {estimate.get('confidence', 0):.2f} ({estimate.get('confidence_label', '—')})")
    check(estimate.get("confidence_label"), "не указан уровень уверенности аппаратной оценки")

    # Стадийные подсказки: у каждой стадии свои предупреждения и предложения.
    print("\nСтадии проекта:")
    for stage in ("concept", "preproduction", "prototype", "production",
                  "alpha", "beta", "release", "post_release"):
        status, guide = call("GET", f"/api/catalog/stage-guidance?stage={stage}")
        ok = status == 200 and guide.get("summary") and guide.get("warnings") and guide.get("suggestions")
        check(ok, f"стадия {stage}: нет сводки, предупреждений или предложений")
        print(f"  {stage:<16} требуют переработки {len(guide.get('rework_levels', []))}, "
              f"предупреждений {len(guide.get('warnings', []))}, "
              f"предложений {len(guide.get('suggestions', []))}")
    check(
        call("GET", "/api/catalog/stage-guidance?stage=unknown_stage")[1].get("stage") == "prototype",
        "неизвестная стадия не сводится к прототипу",
    )

    # Смена стадии меняет расчёт: архитектурные решения остаются в выдаче,
    # но получают пометку о переработке и уступают в порядке внедрения.
    # Календарный запрет удалял решение из списка, оставляя его в корзине.
    early_profile = dict(BASE_PROFILE)
    early_profile.update(SCENARIOS["3d_open_world"])
    early_profile["stage"] = "concept"
    late_profile = dict(early_profile)
    late_profile["stage"] = "release"
    _, early = call("POST", "/api/recommend", {"profile": early_profile, "basket": []})
    _, late = call("POST", "/api/recommend", {"profile": late_profile, "basket": []})
    check(early.get("stage_guidance", {}).get("rework_levels") == [],
          "на концепте ни один уровень не требует переработки")
    check(late.get("stage_guidance", {}).get("rework_levels") == ["architecture"],
          "на релизе архитектурный уровень не помечен как требующий переработки")
    early_codes = {item["method_code"] for item in early.get("recommendations", [])}
    late_codes = {item["method_code"] for item in late.get("recommendations", [])}
    architecture = set()
    for code in early_codes:
        _, card = call("GET", f"/api/catalog/methods/{code}")
        if card.get("level") == "architecture":
            architecture.add(code)
    check(bool(architecture), "в выдаче концепта нет архитектурных решений — проверка стадии пуста")
    check(architecture <= late_codes,
          "архитектурное решение исчезло из выдачи релиза: стадия не должна удалять реализацию")
    flagged = {item["method_code"] for item in late.get("recommendations", [])
               if "needs_rework" in item.get("flags", [])}
    check(bool(flagged & architecture),
          "архитектурные решения на релизе не помечены как требующие переработки")
    # Состав выдачи от стадии не зависит: физическая стоимость реализации не
    # меняется от даты. Меняется пометка и порядок внедрения — этим стадия и
    # влияет на выбор, а не удалением решения из списка.
    early_flagged = {item["method_code"] for item in early.get("recommendations", [])
                     if "needs_rework" in item.get("flags", [])}
    check(
        not early_flagged and flagged,
        "смена стадии не меняет выдачу: пометка о переработке не появилась на релизе",
    )
    early_order = [item["method_code"] for item in early.get("recommendations", [])]
    late_order = [item["method_code"] for item in late.get("recommendations", [])]
    check(
        early_order != late_order,
        "смена стадии не меняет порядок: решения с переработкой идут после прямых",
    )
    print(f"Смена стадии: концепт {len(early_codes)} решений → релиз {len(late_codes)}, "
          f"архитектурных в выдаче релиза {len(architecture & late_codes)} "
          f"из {len(architecture)}, помечено переработкой {len(flagged)}")

    # Административный раздел (локально открыт).
    status, overview = call("GET", "/api/admin/overview")
    check(status == 200 and overview, "обзор административного раздела недоступен")
    status, validation = call("POST", "/api/admin/validate", {})
    check(status == 200, "проверка целостности базы не выполнена")
    print(f"Административный раздел: записей в обзоре {len(overview)}, "
          f"замечаний целостности {validation.get('total', 0)}")

    print(f"\nВыполнено проверок: {checks}")
    if failures:
        print(f"Не пройдено: {len(failures)}")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("Все проверки пройдены.")
    return 0


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base", default=BASE_DEFAULT, help="адрес backend-приложения")
args = parser.parse_args()

if __name__ == "__main__":
    sys.exit(main())
