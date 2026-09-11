# Проверка достоверности доказательной базы

Автоматическая сверка всех источников, утверждений и связей на соответствие контракту исследования.

- Сетевые проверки URL: **включены**

## 1. Исследовательские пакеты

- пакетов: **14**
- источников: **647**
- утверждений (claims): **1897**
- игровых примеров: **600**
- derived-утверждений с формулой и входными параметрами: **70 / 70**
- уникальных URL: **525**

| Проверка | Нарушений |
|---|---|
| `url_error` | 25 |

### Дублирующиеся URL

- `https://cdn.akamai.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf` → pack_ai_sim.json:SRC-AIS-001, pack_method_proofs.json:SRC-MPR-011
- `https://www.gameaipro.com/gameaipro/gameaipro_chapter23_crowd_pathfinding_and_steering_using_flow_field_tiles.pdf` → pack_ai_sim.json:SRC-AIS-002, pack_functions.json:SRC-FUNC-053, pack_method_proofs.json:SRC-MPR-013
- `https://gamma.cs.unc.edu/rvo2/` → pack_ai_sim.json:SRC-AIS-004, pack_tech_nodes.json:SRC-TN-014
- `https://gameprogrammingpatterns.com/object-pool.html` → pack_ai_sim.json:SRC-AIS-005, pack_functions.json:SRC-FUNC-074
- `https://gameprogrammingpatterns.com/component.html` → pack_ai_sim.json:SRC-AIS-006, pack_functions.json:SRC-FUNC-073
- `https://advances.realtimerendering.com/s2020/renderingdoometernal.pdf` → pack_ai_sim.json:SRC-AIS-008, pack_functions.json:SRC-FUNC-054, pack_method_proofs.json:SRC-MPR-001, pack_rendering.json:SRC-RND-022
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/hair-rendering-and-simulation-in-unreal-engine` → pack_ai_sim.json:SRC-AIS-009, pack_functions.json:SRC-FUNC-025, pack_method_proofs.json:SRC-MPR-030
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine` → pack_ai_sim.json:SRC-AIS-014, pack_derivations.json:SRC-DER-018, pack_functions.json:SRC-FUNC-021, pack_method_proofs.json:SRC-MPR-045
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/significance-manager-in-unreal-engine` → pack_ai_sim.json:SRC-AIS-015, pack_engines_ue_unity.json:SRC-ENG-018
- `https://media.gdcvault.com/gdc2016/presentations/lheureux_julien_art_of_destruction.pdf` → pack_ai_sim.json:SRC-AIS-019, pack_method_proofs.json:SRC-MPR-014
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-destruction-in-unreal-engine` → pack_ai_sim.json:SRC-AIS-024, pack_engines_ue_unity.json:SRC-ENG-024, pack_functions.json:SRC-FUNC-032
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-vehicles` → pack_ai_sim.json:SRC-AIS-026, pack_engines_ue_unity.json:SRC-ENG-012
- `https://docs.unity3d.com/manual/class-wheelcollider.html` → pack_ai_sim.json:SRC-AIS-034, pack_functions.json:SRC-FUNC-040
- `https://unity.com/dots` → pack_ai_sim.json:SRC-AIS-038, pack_engines_ue_unity.json:SRC-ENG-043, pack_tech_nodes.json:SRC-TN-021
- `https://docs.unity3d.com/manual/gpuinstancing.html` → pack_ai_sim.json:SRC-AIS-039, pack_engines_ue_unity.json:SRC-ENG-028
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/physics-in-unreal-engine` → pack_ai_sim.json:SRC-AIS-041, pack_engines_ue_unity.json:SRC-ENG-023
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/water-system-in-unreal-engine` → pack_ai_sim.json:SRC-AIS-042, pack_functions.json:SRC-FUNC-026, pack_method_proofs.json:SRC-MPR-031
- `https://docs.godotengine.org/en/stable/classes/class_gpuparticles3d.html` → pack_ai_sim.json:SRC-AIS-045, pack_tools_godot_cry_source.json:SRC-GCS-018
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-budget-allocator-in-unreal-engine` → pack_character_content.json:SRC-CHC-001, pack_engines_ue_unity.json:SRC-ENG-019
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-lods-in-unreal-engine` → pack_character_content.json:SRC-CHC-003, pack_functions.json:SRC-FUNC-015
- `https://github.com/nfrechette/acl` → pack_character_content.json:SRC-CHC-004, pack_tech_nodes.json:SRC-TN-009
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-compression-library-in-unreal-engine` → pack_character_content.json:SRC-CHC-008, pack_tech_nodes.json:SRC-TN-010
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine` → pack_character_content.json:SRC-CHC-010, pack_method_proofs.json:SRC-MPR-064
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-for-unreal-engine` → pack_character_content.json:SRC-CHC-032, pack_engines_ue_unity.json:SRC-ENG-013, pack_functions.json:SRC-FUNC-028, pack_method_proofs.json:SRC-MPR-047
- `https://developer.valvesoftware.com/wiki/source_multiplayer_networking` → pack_derivations.json:SRC-DER-003, pack_netaudio.json:SRC-NTA-001

## 2. База данных

- источников: **936**
- утверждений: **2564**
- уникальных URL: **759**

| Проверка | Нарушений |
|---|---|
| `claim_dangling_source` | 0 |
| `claim_missing_locator` | 0 |
| `conflict_without_url` | 0 |
| `declared_gap_claims` | 28 |
| `dependency_edge_without_source` | 154 |
| `derived_missing_formula_or_inputs` | 0 |
| `method_engine_link_without_url` | 111 |
| `numeric_claim_without_source` | 0 |
| `source_without_published_date` | 0 |
| `url_dead` | 1 |
| `url_declared` | 30 |
| `url_error` | 50 |
| `work_package_p80_lt_p50` | 0 |

## 3. Доступность URL

- проверено уникальных URL: **759**
- доступны (2xx): **711**
- защищены ботом/авторизацией (403/401/429): **19**
- недоступны (404/410/DNS): **1**
- ошибки сети/таймаут: **27**
- объявленное отсутствие ссылки, не адрес: **1**

### Недоступные URL (требуют замены или пометки)

- `https://www.digitalfoundry.net/articles/digitalfoundry-2021-it-takes-two-tech-analysis` — not found

### Ошибки соединения (проверить вручную)

- `https://recastnav.com/` — Tunnel connection failed: 502 Bad Gateway
- `https://nvidia-omniverse.github.io/physx/physx/5.6.1/_api_build/structpxbroadphasetype.html` — Tunnel connection failed: 502 Bad Gateway
- `https://guillaumeblanc.github.io/ozz-animation/documentation/` — Tunnel connection failed: 502 Bad Gateway
- `https://docs.unity.cn/packages/com.unity.2d.animation@7.0/manual/characterrig.html` — _ssl.c:1015: The handshake operation timed out
- `https://www.remedygames.com/article/how-northlight-makes-alan-wake-2-shine` — Tunnel connection failed: 502 Bad Gateway
- `https://radwan92.github.io/assets/pdfs/fast-paced%20multiplayer%20-%20gabriel%20gambetta.pdf` — Tunnel connection failed: 502 Bad Gateway
- `https://valvesoftware.github.io/steam-audio/doc/capi/guide.html` — Tunnel connection failed: 502 Bad Gateway
- `https://devtrackers.gg/hunt-showdown/p/e4016122-developer-insight-did-you-hear-that` — Tunnel connection failed: 502 Bad Gateway
- `https://zzzremake.github.io/site/blog/translate-overwatch-architecture-netcode/` — Tunnel connection failed: 502 Bad Gateway
- `https://docs.vulkan.org/guide/latest/extensions/ray_tracing.html` — Tunnel connection failed: 502 Bad Gateway
- `https://docs.vulkan.org/features/latest/features/proposals/vk_ext_mesh_shader.html` — Tunnel connection failed: 502 Bad Gateway
- `https://microsoft.github.io/directx-specs/d3d/meshshader.html` — Tunnel connection failed: 502 Bad Gateway
- `https://docs.vulkan.org/samples/latest/samples/performance/async_compute/readme.html` — Tunnel connection failed: 502 Bad Gateway
- `https://microsoft.github.io/directx-specs/d3d/hlsl_sm_6_6_dynamicresources.html` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2013/http://www.heroengine.com/` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2014/http://www.heroengine.com/heroengine/heroblade/` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/20131227161309/http://www.heroengine.com/heroengine/world-building/` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2013/http://www.heroengine.com/features/server-systems/` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2013/http://www.heroengine.com/heroengine/game-systems/` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2013/http://www.heroengine.com/heroengine/licensing-options/` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2014/http://hewiki.heroengine.com/wiki/main_page` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2014/http://hewiki.heroengine.com/wiki/scalability_and_building_for_massive_multiplayer_audiences` — Tunnel connection failed: 502 Bad Gateway
- `https://web.archive.org/web/2014/http://www.heroengine.com/herocloud/tech-features/` — Tunnel connection failed: 502 Bad Gateway
- `https://microsoft.github.io/directx-specs/d3d/variablerateshading.html` — Tunnel connection failed: 502 Bad Gateway
- `https://ntrs.nasa.gov/api/citations/19870020777/downloads/19870020777.pdf` — Tunnel connection failed: 502 Bad Gateway
- `https://www.nasa.gov/ocfo/ppc-corner/ppc-glossary/` — Tunnel connection failed: 502 Bad Gateway
- `https://andrewaltimit.github.io/documentation/docs/gamedev/save-systems.html` — Tunnel connection failed: 502 Bad Gateway
