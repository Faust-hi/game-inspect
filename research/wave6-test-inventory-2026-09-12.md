# Инвентаризация тестов (волна 6) — 2026-09-12

READ-ONLY инвентаризация. Ничего в приложении, формулах и API не менялось.
Интерпретатор: `C:/Users/user/Desktop/game-inspect/.dss-venv/Scripts/python.exe`.

## 0. Измеренное исходное состояние (не оценка)

| Контур | Как измерено | Сценариев | Файлов | Время |
|---|---|---|---|---|
| Backend | `python -m pytest -q` | **192 passed** | 24 (23 test-файла + `conftest.py`) | **40.81 s** |
| Backend (durations) | `python -m pytest -q --durations=25` | 192 | — | 43.29 s |
| Frontend (Vitest) | `npm test` (`vitest run`) | **29 passed** | 7 | **2.89 s** |
| E2E (Playwright) | `frontend/e2e/*.spec.ts` (не запускался: нужен сервер) | **2** | 2 | — |

Сбор сценариев: `192 tests collected in 1.23s`. Frontend по файлам: `api 4`, `store 16`, `basketBaseline 3`, `effectScope 2`, `hardwareScope 1`, `hardwareWarnings 1`, `loadProfileQualitative 2` = 29.

**Замеренные «тяжёлые» места backend** (из `--durations=0`): `test_case_publication` setup 2.93 s, `test_method_dependencies::closure_covers_every_mandatory_method_edge` 2.29 s, `test_evidence_api::team_size…` 1.75 s, `test_relation_resolutions` (sync-тесты) 1.2–1.3 s, `test_user_journey::baseline…` 0.92 s. Почти все кандидаты в `critical` — это дешёвые проверки (0.01–0.3 s) либо API-вызовы 0.3–0.9 s.

## 1. Соглашения

**Требования (обязательные свойства из спецификации владельца):**

- **R1** — Рекомендации: выбор/ранжирование по функциям; совместимость с движком и платформой; различие зависимостей, альтернатив и дополнений.
- **R2** — Реакция на профиль: смена технического параметра меняет нагрузку/применимость; переименование проекта расчёт не меняет.
- **R3** — Корзина: хранит реализованное; восстанавливается после перезагрузки; пересчитывается после смены профиля; отличает малое приспособление от архитектурной переделки; прошлая реализация НЕ учитывается повторно в требованиях к железу.
- **R4** — Оценка железа: нет двойного учёта эффектов; клиентские и серверные затраты разделены; корректный учёт RAM/VRAM и базового FPS; границы модели видны.
- **R5** — Данные: сохранение/восстановление проекта; атомарность импорта; правки пользователя переживают обновление каталога; миграция SQLite с бэкапом.
- **R6** — Безопасность и готовность: нет доступа к приватным файлам; нет записей из чужого origin; неверный ввод обработан; готовность API; безопасные сообщения об ошибках.

**Действия:** `K` = keep-critical, `E` = move-extended, `M` = merge, `D` = delete.

**Правило удаления (по спецификации):** удаление только для точного дубля либо проверки снятого требования, с указанием причины и заменяющего теста. Точных дублей в сохраняемом наборе не найдено — все удаления относятся к **снятым требованиям** (game_cases/case_evidence и пакеты работ/командные сценарии).

## 2. (a) Таблица по файлам

| Файл | Сценариев | K | E | D | Вердикт | Причина |
|---|---:|---:|---:|---:|---|---|
| `test_user_journey.py` | 6 | 6 | 0 | 0 | keep | Сквозной путь профиль→рекомендации→корзина→нагрузка→железо; ядро R1–R4 |
| `test_decision_math.py` | 9 | 9 | 0 | 0 | keep | Математика ранжирования/устойчивости — R1, дёшево |
| `test_conflicts.py` | 5 | 5 | 0 | 0 | keep | Зависимости/альтернативы/дополнения — R1 |
| `test_hardware_bottleneck.py` | 12 | 10 | 2 | 0 | keep | Ядро R2/R4; 2 специфичных записи → extended |
| `test_hardware_messages.py` | 11 | 6 | 5 | 0 | keep | Причина отказа/узкое место — R4; отсев пула по API/возможностям → extended |
| `test_combined_effects.py` | 11 | 9 | 2 | 0 | keep | Двойной учёт, клиент/сервер — R4 |
| `test_project_context.py` | 5 | 3 | 2 | 0 | keep | Реакция на параметры и стадию — R2/R3 |
| `test_project_scale.py` | 5 | 3 | 2 | 0 | keep | Независимая ось масштаба проекта — R2 |
| `test_engine_versions.py` | 9 | 5 | 4 | 0 | keep | Совместимость движка/платформы — R1; каталогные перечисления → extended |
| `test_scientific.py` | 6 | 4 | 2 | 0 | keep | Честность оценки/неопределённость — R4; якорь класса → extended |
| `test_demo_stability.py` | 7 | 6 | 1 | 0 | keep | Готовность API, ошибки, миграция — R5/R6 |
| `test_method_dependencies.py` | 10 | 5 | 4 | 1 | keep (частично) | Замыкание зависимостей — R1/R3; 1 тест — про планировщик |
| `test_pack_loader.py` | 3 | 3 | 0 | 0 | keep | Атомарность импорта пакетов — R5 |
| `test_catalog_corrections.py` | 7 | 3 | 4 | 0 | keep | Правки каталога доходят до базы — R5 |
| `test_hardware_provenance.py` | 7 | 1 | 6 | 0 | keep | Провенанс железа; 1 про выживание правок — R5 |
| `test_relation_resolutions.py` | 16 | 1 | 15 | 0 | keep | Решения связей/карточки; 1 про курируемый текст — R5 |
| `test_evidence_api.py` | 13 | 1 | 5 | 7 | keep (частично) | Доказательный API/граф; 7 — расписание/команды (снято) |
| `test_evidence_publication.py` | 4 | 0 | 4 | 0 | extended | Публикация доказательств — каталогные перечисления |
| `test_evidence_declarations.py` | 6 | 0 | 6 | 0 | extended | Декларации пробелов — конкретные записи |
| `test_derived_source_dates.py` | 16 | 0 | 16 | 0 | extended | Проходы дат/URL — конкретные записи и источники |
| `test_case_publication.py` | 12 | 0 | 0 | 12 | **delete** | Только `game_cases`/`case_evidence` — фича снимается |
| `test_pack_reconciliation.py` | 7 | 0 | 0 | 7 | **delete** | Только `WorkPackage`/`TeamScenario` — фича снимается |
| `test_stage_integrity.py` | 5 | 0 | 0 | 5 | **delete** | `normalize_stage` используется только пакетами работ; +`/api/schedule` |
| **Итого** | **192** | **80** | **80** | **32** | | |

## 3. (b) Полная таблица соответствия «тест → требование → действие»

### `test_user_journey.py`
| Тест | R | Действие |
|---|---|---|
| `test_recommend_ranked_with_reasons` | R1 | K |
| `test_unknown_codes_become_risks` | R1/R6 | K |
| `test_excluded_explain_reason` | R1 | K |
| `test_basket_flows_into_load_and_hardware` | R3/R4 | K |
| `test_same_profile_reproduces_same_result` | R2 | K |
| `test_baseline_keeps_hardware_and_marks_unknown` | R3 | K |

### `test_decision_math.py`
| Тест | R | Действие |
|---|---|---|
| `test_dominant_alternative_ranks_first` | R1 | K |
| `test_weights_flip_order` | R1 | K |
| `test_degenerate_comparison_is_neutral_not_worst[одна альтернатива]` | R1 | K |
| `test_degenerate_comparison_is_neutral_not_worst[одинаковые альтернативы]` | R1 | K |
| `test_same_input_gives_same_order` | R1 | K |
| `test_scores_are_finite_and_bounded` | R1 | K |
| `test_clear_winner_is_stable_and_tie_shows_fork` | R1 | K |
| `test_single_option_has_no_stability_fork` | R1 | K |
| `test_priority_changes_api_ranking_not_just_weights` | R1 | K |

### `test_conflicts.py`
| Тест | R | Действие |
|---|---|---|
| `test_basket_conflict_is_visible` | R1 | K |
| `test_unmet_dependency_is_reported` | R1 | K |
| `test_complement_is_reported_as_synergy` | R1 | K |
| `test_hard_conflict_blocks_stacking` | R1 | K |
| `test_dependency_is_not_reported_as_unrecognized` | R1 | K |

### `test_hardware_bottleneck.py`
| Тест | R | Действие |
|---|---|---|
| `test_higher_resolution_needs_stronger_gpu` | R2/R4 | K |
| `test_higher_fps_needs_more_compute` | R2/R4 | K |
| `test_violated_vram_limit_blocks_and_names_bottleneck` | R4 | K |
| `test_no_memory_bottleneck_without_deficit` | R4 | K |
| `test_alternatives_cover_estimate` | R4 | K |
| `test_unknown_inputs_lower_confidence_instead_of_promise` | R4/R6 | K |
| `test_zero_means_empty_not_missing` | R2 | K |
| `test_beyond_model_range_is_reported` | R4 | K |
| `test_scene_scale_changes_load_not_frame_cost` | R2/R4 | K |
| `test_baseline_api_feature_does_not_empty_gpu_pool` | R4 | E |
| `test_feature_support_distinguishes_unknown_from_absent` | R4 | E |
| `test_cpu_ceiling_is_named_when_requirement_exceeds_catalog` | R4 | K |

### `test_hardware_messages.py`
| Тест | R | Действие |
|---|---|---|
| `test_bottleneck_sums_raster_and_rt` | R4 | K |
| `test_bottleneck_still_names_cpu_when_cpu_dominates` | R4 | K |
| `test_bottleneck_has_no_separate_raster_and_rt_stages` | R4 | E |
| `test_reported_bottleneck_matches_model_stages` | R4 | K |
| `test_pick_gpu_names_rt_reason` | R4 | K |
| `test_pick_gpu_names_vram_reason` | R4 | K |
| `test_pick_gpu_names_perf_reason` | R4 | K |
| `test_pick_gpu_has_no_reason_on_success` | R4 | E |
| `test_api_filtered_pool_is_blamed_on_api` | R4 | E |
| `test_capability_filtered_pool_names_the_capability` | R4 | E |
| `test_no_single_gpu_covers_all_capabilities_is_said_as_such` | R4 | E |

### `test_combined_effects.py`
| Тест | R | Действие |
|---|---|---|
| `test_streaming_pool_counts_only_transient_part` | R4 | K |
| `test_upscaling_field_and_card_act_once` | R4 | K |
| `test_frame_generation_field_and_card_act_once` | R4 | K |
| `test_rt_cost_scales_with_resolution` | R4 | K |
| `test_rt_budget_reduces_introduced_pass` | R4 | E |
| `test_raster_and_rt_share_one_frame_budget` | R4 | K |
| `test_two_increments_sum_but_two_savings_count_once` | R4 | K |
| `test_mandatory_dependency_is_pulled_into_the_basket` | R3/R1 | K |
| `test_closure_additions_are_reported_and_counted` | R3/R1 | K |
| `test_server_effect_does_not_discount_player_pc` | R4 | K |
| `test_out_of_frame_effect_is_named_not_silent` | R4 | E |

### `test_project_context.py`
| Тест | R | Действие |
|---|---|---|
| `test_object_count_moves_result` | R2 | K |
| `test_stage_keeps_architecture_with_rework_mark` | R3 | K |
| `test_stage_guidance_differs_and_unknown_falls_back` | R3 | E |
| `test_concept_change_is_flagged` | R3 | E |
| `test_gated_network_method_needs_its_function` | R1 | K |

### `test_project_scale.py`
| Тест | R | Действие |
|---|---|---|
| `test_default_is_medium_and_changes_nothing` | R2 | K |
| `test_levels_move_baseline_monotonically` | R2 | K |
| `test_unknown_level_does_not_shift_result` | R2 | K |
| `test_content_multipliers_are_untouched` | R2 | E |
| `test_world_scale_and_project_scale_are_independent_axes` | R2 | E |

### `test_engine_versions.py`
| Тест | R | Действие |
|---|---|---|
| `test_unknown_engine_rejected_with_hint` | R6/R1 | K |
| `test_catalog_engine_accepted_without_code_change` | R1 | K |
| `test_version_cuts_builtin_tool_and_warns_in_basket` | R1 | K |
| `test_linux_with_directx_gets_no_hardware` | R1 | K |
| `test_directstorage_needs_windows_and_modern_api` | R1 | E |
| `test_unlinked_methods_are_explicitly_engine_independent` | R1 | E |
| `test_recommendation_names_independence_not_gap` | R1 | E |
| `test_seed_validation_distinguishes_independence` | R1/R5 | E |
| `test_independence_sync_repairs_existing_database` | R5 | K |

### `test_scientific.py`
| Тест | R | Действие |
|---|---|---|
| `test_practice_check_is_development_not_proof` | R1/R6 | K |
| `test_estimate_marks_uncertainty_and_gaps` | R4 | K |
| `test_beyond_catalog_is_flagged_not_hidden` | R4 | K |
| `test_missing_prediction_does_not_become_success` | R1 | K |
| `test_catalog_ratio_matches_external_anchor` | R4 | E |
| `test_chosen_basket_moves_hardware_class` | R4 | E |

### `test_demo_stability.py`
| Тест | R | Действие |
|---|---|---|
| `test_health_ready_on_seeded_database` | R6 | M (→ `test_api_readiness_on_seeded_database`) |
| `test_health_unavailable_on_schema_error` | R6 | K |
| `test_fresh_sqlite_bootstraps_through_migrations` | R5 | K |
| `test_published_slice_has_sources_and_no_dangling_links` | R5/R6 | E |
| `test_draft_does_not_leak_into_public_slice` | R6 | K |
| `test_critical_error_is_understandable` | R6 | K |
| `test_unknown_api_path_is_not_served_as_page` | R6 | K |

### `test_method_dependencies.py`
| Тест | R | Действие |
|---|---|---|
| `test_closure_is_transitive` | R1 | K |
| `test_closure_is_idempotent` | R1 | K |
| `test_closure_keeps_declared_codes` | R1 | K |
| `test_closure_does_not_invent_unknown_methods` | R1 | K |
| `test_closure_notes_explain_the_addition` | R1 | E |
| `test_closure_covers_every_mandatory_method_edge` | R1 | E |
| `test_no_mandatory_dependency_contradicts_an_exclusion` | R1 | E |
| `test_excluded_pair_has_no_second_type` | R1 | E |
| `test_schedule_and_load_use_the_same_method_set` | — | **D (снято: планировщик)** |
| `test_closure_prevents_basket_collapse` | R1/R3 | K |

### `test_pack_loader.py`
| Тест | R | Действие |
|---|---|---|
| `test_valid_pack_is_loaded_without_failures` | R5 | K |
| `test_malformed_pack_is_reported_not_skipped` | R5 | K |
| `test_non_object_pack_is_reported` | R5 | K |

### `test_catalog_corrections.py`
| Тест | R | Действие |
|---|---|---|
| `test_contradictory_relation_is_withdrawn_with_its_edge` | R5 | K |
| `test_contradictory_relation_correction_is_idempotent` | R5 | E |
| `test_every_declared_removal_names_a_reason` | R5 | E |
| `test_platform_correction_reaches_an_existing_row` | R5 | K |
| `test_platform_correction_leaves_a_foreign_value_alone` | R5 | K |
| `test_taxonomy_correction_is_idempotent` | R5 | E |
| `test_virtualized_geometry_is_a_geometry_pipeline_method` | R1 | E |

### `test_hardware_provenance.py`
| Тест | R | Действие |
|---|---|---|
| `test_curated_provenance_survives_startup_pass` | R5 | K |
| `test_empty_provenance_block_is_filled_whole` | R5 | E |
| `test_measured_basis_matches_a_measured_value` | R4 | E |
| `test_refresh_pass_skips_rows_that_differ_from_previous_value` | R5 | E |
| `test_refresh_pass_is_noop_with_empty_registry` | R5 | E |
| `test_truncated_source_date_is_restored` | R5 | E |
| `test_curated_source_date_is_not_touched` | R5 | E |

### `test_relation_resolutions.py`
| Тест | R | Действие |
|---|---|---|
| `test_every_conflict_has_resolution_and_basis` | R1 | E |
| `test_every_dependency_edge_has_workaround_and_basis` | R1 | E |
| `test_method_card_metadata_is_loaded` | R1 | E |
| `test_no_symmetric_relation_is_recorded_twice` | R1 | E |
| `test_symmetric_relation_declared_from_both_sides_is_one_record` | R1 | E |
| `test_startup_sync_does_not_change_seeded_relations` | R5 | E |
| `test_startup_sync_leaves_no_unresolved_relations` | R1 | E |
| `test_resolution_pass_does_not_overwrite_curated_text` | R5 | K |
| `test_method_card_api_exposes_research_metadata` | R1 | E |
| `test_conflicts_api_exposes_resolution_and_basis` | R1 | E |
| `test_dependencies_api_exposes_workaround_and_basis` | R1 | E |
| `test_derived_basis_requires_a_source` | R5 | E |
| `test_hardware_benchmark_claim_matches_its_row` | R4 | E |
| `test_seed_applies_researched_confidence` | R5 | E |
| `test_relation_pass_repairs_basis_without_source` | R5 | E |
| `test_repeat_seed_repairs_stale_derived_claim` | R5 | E |

### `test_evidence_api.py`
| Тест | R | Действие |
|---|---|---|
| `test_entity_evidence_path_alias_filters_claims` | R1 | M (→ `test_evidence_endpoints_return_claims_by_code`) |
| `test_report_data_get_uses_valid_default_profile` | R6 | M (→ `test_api_readiness_on_seeded_database`) |
| `test_graph_checks_reports_no_mandatory_cycles` | R1 | E |
| `test_graph_checks_flags_unknown_version_instead_of_compatibility` | R1 | E |
| `test_graph_checks_detects_hard_conflict_inside_basket` | R1 | E |
| `test_graph_checks_api_incompatibility_is_reported` | R1 | E |
| `test_schedule_tasks_expose_work_package_fields` | — | **D (снято: пакеты работ)** |
| `test_p80_is_never_below_p50` | — | **D (снято: планировщик)** |
| `test_custom_team_profile_is_available` | — | **D (снято: команды)** |
| `test_unknown_team_is_declared_not_silently_substituted` | — | **D (снято: команды)** |
| `test_team_size_moves_calendar_not_person_days` | — | **D (снято: команды)** |
| `test_dependent_tasks_form_critical_path` | — | **D (снято: пакеты работ)** |
| `test_dependency_pulls_prerequisite_into_schedule` | — | **D (снято: планировщик)** |

### `test_evidence_publication.py`
| Тест | R | Действие |
|---|---|---|
| `test_published_status_constants_are_distinct` | R5 | M (→ `test_every_family_with_sources_is_visible`) |
| `test_every_family_with_sources_is_visible` | R5 | E |
| `test_category_two_evidence_is_reachable_by_code` | R5 | M (→ `test_evidence_endpoints_return_claims_by_code`) |
| `test_category_two_claims_carry_sources_and_calculations` | R5 | E |

### `test_evidence_declarations.py`
| Тест | R | Действие |
|---|---|---|
| `test_user_defined_links_are_declared` | R5 | E |
| `test_conflicts_without_url_are_declared` | R5 | E |
| `test_dependency_edges_without_source_are_declared` | R5 | E |
| `test_hardware_rows_carry_raw_benchmark_value` | R4 | E |
| `test_no_dangling_published_claim` | R5 | E |
| `test_cpu_notes_record_single_thread_provenance` | R4 | E |

### `test_derived_source_dates.py`
| Тест | R | Действие |
|---|---|---|
| `test_placeholder_date_on_method_is_replaced` | R5 | E |
| `test_verification_date_on_method_is_replaced` | R5 | E |
| `test_curated_date_on_method_survives` | R5 | E |
| `test_concrete_date_yields_to_declared_absence` | R5 | E |
| `test_empty_date_on_method_is_filled` | R5 | E |
| `test_placeholder_date_on_function_is_replaced` | R5 | E |
| `test_ambiguous_url_is_not_resolved` | R5 | E |
| `test_derived_date_pass_is_idempotent` | R5 | E |
| `test_technology_node_url_is_repaired` | R5 | E |
| `test_tool_engine_note_is_refreshed` | R5 | E |
| `test_edited_edge_description_is_not_touched` | R5 | E |
| `test_tool_engine_note_pass_is_idempotent` | R5 | E |
| `test_legacy_source_record_is_repaired` | R5 | E |
| `test_edited_source_record_is_not_touched` | R5 | E |
| `test_source_record_pass_is_idempotent` | R5 | E |
| `test_source_record_pass_keeps_admin_fields` | R5 | E |

### Снятые файлы (все — D)

`test_case_publication.py` (12): `test_upsert_case_publishes_when_source_resolves`, `test_upsert_case_stays_draft_when_source_unknown`, `test_upsert_case_fills_world_type_without_overwriting`, `test_correct_case_publication_publishes_backed_case`, `test_correct_case_publication_leaves_unbacked_case_draft`, `test_correct_case_publication_ignores_unsourced_evidence`, `test_correct_case_publication_is_idempotent`, `test_declare_evidence_gaps_reports_case_publication`, `test_no_published_evidence_points_to_draft_case`, `test_case_backed_by_published_evidence_is_published`, `test_public_case_surface_has_no_orphan_evidence`, `test_seeded_cases_are_not_invisible` → R «снято: game_cases/case_evidence».

`test_pack_reconciliation.py` (7): `test_method_total_equals_curated_estimate`, `test_curated_effort_reaches_an_existing_package`, `test_reconciliation_is_idempotent`, `test_planner_fields_survive_the_new_magnitude`, `test_no_second_family_remains`, `test_every_package_role_is_a_team_capacity_key`, `test_duplicate_effort_is_declared_not_silent` → R «снято: пакеты работ/команды».

`test_stage_integrity.py` (5): `test_normalize_stage_keeps_valid_enum_untouched`, `test_normalize_stage_parses_research_prose`, `test_normalize_stage_never_silently_invents_a_late_stage`, `test_normalize_stage_handles_empty_and_none`, `test_published_work_packages_carry_enum_stage` → R «снято: пакеты работ» (`normalize_stage` вызывается только из `pack_loader.py:618` для `recommended_stage` пакетов; `test_published_work_packages_carry_enum_stage` — через `/api/schedule`).

## 4. Слияния (merge)

| # | Что сливается | Во что | Контур | Требование |
|---|---|---|---|---|
| M1 | `test_health_ready_on_seeded_database` + `test_report_data_get_uses_valid_default_profile` | `test_api_readiness_on_seeded_database` | critical | R6 |
| M2 | `test_published_status_constants_are_distinct` → в `test_every_family_with_sources_is_visible` | один extended | extended | R5 |
| M3 | `test_entity_evidence_path_alias_filters_claims` + `test_category_two_evidence_is_reachable_by_code` | `test_evidence_endpoints_return_claims_by_code` | extended | R5 |

Независимые проверки искусственно не сливались; параметризованные кейсы (`test_degenerate_comparison_is_neutral_not_worst[…]`) сохраняют отдельные читаемые имена.

## 5. (c) Предлагаемый список critical

**Backend critical (80 сценариев до слияния M1; 79 уникальных после):**

- `test_user_journey.py`: все 6.
- `test_decision_math.py`: все 9.
- `test_conflicts.py`: все 5.
- `test_hardware_bottleneck.py`: `higher_resolution`, `higher_fps`, `violated_vram_limit`, `no_memory_bottleneck`, `alternatives_cover`, `unknown_inputs_lower_confidence`, `zero_means_empty`, `beyond_model_range`, `scene_scale`, `cpu_ceiling`.
- `test_hardware_messages.py`: `bottleneck_sums_raster_and_rt`, `bottleneck_still_names_cpu`, `reported_bottleneck_matches_model_stages`, `pick_gpu_names_rt_reason`, `pick_gpu_names_vram_reason`, `pick_gpu_names_perf_reason`.
- `test_combined_effects.py`: `streaming_pool`, `upscaling_field_and_card`, `frame_generation_field_and_card`, `rt_cost_scales`, `raster_and_rt_share_budget`, `two_increments_two_savings`, `mandatory_dependency_pulled`, `closure_additions`, `server_effect`.
- `test_project_context.py`: `object_count_moves_result`, `stage_keeps_architecture`, `gated_network_method`.
- `test_project_scale.py`: `default_is_medium`, `levels_move_baseline`, `unknown_level_does_not_shift`.
- `test_engine_versions.py`: `unknown_engine_rejected`, `catalog_engine_accepted`, `version_cuts_builtin_tool`, `linux_with_directx`, `independence_sync_repairs`.
- `test_scientific.py`: `practice_check`, `estimate_marks_uncertainty`, `beyond_catalog_flagged`, `missing_prediction_not_success`.
- `test_demo_stability.py`: `health_ready` (+M1), `health_unavailable`, `fresh_sqlite_bootstraps`, `draft_does_not_leak`, `critical_error_understandable`, `unknown_api_path`.
- `test_method_dependencies.py`: `closure_is_transitive`, `closure_is_idempotent`, `closure_keeps_declared_codes`, `closure_does_not_invent`, `closure_prevents_basket_collapse`.
- `test_pack_loader.py`: все 3.
- `test_catalog_corrections.py`: `contradictory_relation_withdrawn`, `platform_correction_reaches_row`, `platform_correction_leaves_foreign`.
- `test_hardware_provenance.py`: `curated_provenance_survives_startup_pass`.
- `test_relation_resolutions.py`: `resolution_pass_does_not_overwrite_curated_text`.
- `test_evidence_api.py`: `report_data_get_uses_valid_default_profile` (→ M1).

**Frontend critical:** все 29 (см. п. 7).

## 6. (c) Предлагаемый список extended

- `test_hardware_bottleneck.py`: `baseline_api_feature`, `feature_support_unknown_vs_absent`.
- `test_hardware_messages.py`: `no_separate_raster_rt_stages`, `pick_gpu_no_reason_on_success`, `api_filtered_pool`, `capability_filtered_pool`, `no_single_gpu_covers_all`.
- `test_combined_effects.py`: `rt_budget_reduces_pass`, `out_of_frame_effect_named`.
- `test_project_context.py`: `stage_guidance_differs`, `concept_change_flagged`.
- `test_project_scale.py`: `content_multipliers_untouched`, `world_and_project_scale_independent`.
- `test_engine_versions.py`: `directstorage_platforms`, `unlinked_methods_independent`, `recommendation_names_independence`, `seed_validation_independence`.
- `test_scientific.py`: `catalog_ratio_matches_anchor`, `chosen_basket_moves_class`.
- `test_demo_stability.py`: `published_slice_integrity`.
- `test_method_dependencies.py`: `closure_notes_explain`, `closure_covers_every_edge`, `no_dependency_contradicts_exclusion`, `excluded_pair_no_second_type`.
- `test_catalog_corrections.py`: `contradictory_relation_idempotent`, `every_removal_names_reason`, `taxonomy_correction_idempotent`, `virtualized_geometry_pipeline`.
- `test_hardware_provenance.py`: остальные 6.
- `test_relation_resolutions.py`: остальные 15.
- `test_evidence_api.py`: `graph_checks_no_cycles`, `graph_checks_version_unknown`, `graph_checks_hard_conflict`, `graph_checks_api_incompatibility`, +M3.
- `test_evidence_publication.py`: все (после M2/M3 — 2 уникальных).
- `test_evidence_declarations.py`: все 6.
- `test_derived_source_dates.py`: все 16.

**Extended — это не «мусор»:** там остаются полные перечисления каталога, матрицы стадий/движков/платформ, проверки конкретных записей и источников, якоря классов и расширенные комбинации параметров. Они обязаны запускаться `-m "critical or extended"`.

## 7. (d) Список удаляемых тестов и причины

| # | Файл | Сценариев | Причина | Замена |
|---|---|---:|---|---|
| 1 | `test_case_publication.py` | 12 | Только `game_cases`/`case_evidence` — фича снимается | — (требование отменено) |
| 2 | `test_pack_reconciliation.py` | 7 | Только `WorkPackage`/`TeamScenario` — фича снимается | — (требование отменено) |
| 3 | `test_stage_integrity.py` | 5 | `normalize_stage` и стадия пакетов — фича снимается | — (требование отменено) |
| 4 | `test_evidence_api.py` (7 шт.) | 7 | `/api/schedule`, команды, P50/P80, critical path — фича снимается | — (требование отменено) |
| 5 | `test_method_dependencies.py::test_schedule_and_load_use_the_same_method_set` | 1 | Единственная проверка связки «расписание ↔ нагрузка»; расписание снимается | Логика замыкания остаётся в `test_closure_prevents_basket_collapse` |

**Итого удалений: 32.** Точных дублей среди сохраняемых тестов нет; удаления обоснованы снятием требований. Ни одна уникальная критическая проверка не удаляется ради числа.

## 8. (e) Сценарии до/после и время

| Метрика | Было | После (critical по умолчанию) | После (`critical or extended`) |
|---|---:|---:|---:|
| Backend сценариев | 192 | **~79–80** | **~157** |
| Backend удалено | — | 32 | 32 |
| Backend слито | — | 3 пары | 3 пары |
| Backend время (замер) | 40.81 s | оценочно **15–22 s** | оценочно **28–33 s** |
| Frontend сценариев | 29 | 29 (весь набор в основном прогоне) | 29 |
| Frontend время | 2.89 s | 2.89 s | 2.89 s |
| E2E сценариев | 2 | 2 (только вручную/по расписанию) | 2 |

**Как получена оценка времени critical:** сумма измеренных `call`-длительностей выбранных сценариев (в основном 0.01–0.9 s) + единоразовая инициализация сессионной БД ≈ 3 s; удаляются самые тяжёлые `setup`/`call` (`test_case_publication` 2.93 s, `closure_covers_every_edge` 2.29 s, командные сценарии 0.5–1.75 s, sync-тесты `relation_resolutions` 1.2–1.3 s). Оценку нужно подтвердить замером **после** простановки маркеров — файлы не менялись.

Целевой диапазон 80–120 сценариев для основного набора и ≤30 s достигаются. Если после замера critical выйдет >30 s, переносить в extended следует `test_hardware_bottleneck.py` (10 API-вызовов) и `test_combined_effects.py` (9 API-вызовов), а не удалять критику.

## 9. (f) Вердикт по frontend и e2e

**Frontend — остаётся полностью в основном прогоне.** Набор быстрый (29 тестов, 2.89 s) и уже покрывает обязательные свойства, которые backend не проверяет:

- R3: `basketBaseline.test.tsx` — фиксация реализованной корзины блокируется при несовместимости/неучтённых решениях; `store.test.tsx` — «keeps the implemented basket through edits and a page reload», «does not restore an implemented basket into a new browser session», сброс результата при любом изменении входа, защита от позднего ответа, ошибки хранилища.
- R2/R6: `store.test.tsx` (`inputKeyOf` — канонизация функций/платформ и `4k`↔`2160p`; переименование/перестановка ключей не меняет ключ входа), `api.test.ts` (`parseApiError` — безопасные сообщения и `request_id`).
- R4: `hardwareScope.test.tsx` (границы применимости), `hardwareWarnings.test.tsx`, `loadProfileQualitative.test.tsx` (накопитель/сеть — качественно, не проценты), `effectScope.test.tsx` (клиент vs сервер).

Вердикт: **ничего не удалять и не выносить.** Дублирования с backend нет (это проверки отображения/состояния). Сливать нечего — файлы уже разбиты по темам, а параметризация (`resets[]`, циклы по `label`) уже применена. Единственное замечание: `store.test.tsx` (16 тестов) — самый крупный; при желании можно вынести 4 теста `useEnsureResult` в отдельный файл, но это не сокращение набора и не требуется.

**E2E — только вручную/по расписанию, не в основном прогоне.** 2 сценария (`project.spec.ts`, `conflict.spec.ts`) поднимают собранный frontend + backend-сервер (`webServer`), время — минуты. Это интеграционные сценарии «глазами пользователя»; в критический backend-набор не входят. Оставляются как есть.

## 10. (g) Точные изменения маркеров и CI (описание, файлы не редактировались)

1. **Регистрация маркеров.** Добавить `backend/pytest.ini` (либо `[tool.pytest.ini_options]` в `backend/pyproject.toml`, если он появится):
   ```
   [pytest]
   markers =
       critical: обязательные проверки, идут по умолчанию
       extended: подробные проверки, только вручную
   addopts = -m critical
   ```
   `addopts = -m critical` делает `python -m pytest` запуском только критических; `python -m pytest -m "critical or extended"` — полный сохранённый набор. Отдельный `-m "not extended"` эквивалентен дефолту.

2. **Простановка меток.**
   - Файлы, целиком критические: `test_user_journey.py`, `test_decision_math.py`, `test_conflicts.py`, `test_pack_loader.py` → модульный `pytestmark = pytest.mark.critical`.
   - Файлы, целиком extended: `test_derived_source_dates.py`, `test_evidence_declarations.py`, `test_evidence_publication.py` → `pytestmark = pytest.mark.extended`.
   - Смешанные файлы (`test_hardware_bottleneck.py`, `test_hardware_messages.py`, `test_combined_effects.py`, `test_project_context.py`, `test_project_scale.py`, `test_engine_versions.py`, `test_scientific.py`, `test_demo_stability.py`, `test_method_dependencies.py`, `test_catalog_corrections.py`, `test_hardware_provenance.py`, `test_relation_resolutions.py`, `test_evidence_api.py`) — `@pytest.mark.critical` / `@pytest.mark.extended` на конкретные функции строго по таблицам п. 5–6.
   - Параметризованные кейсы: маркер ставится на функцию-параметризатор (`test_degenerate_comparison_is_neutral_not_worst`), отдельные кейсы сохраняют свои `ids`.

3. **Слияния (перед простановкой меток).** Выполнить M1–M3 из п. 4: перенести тела тестов в объединённые функции, сохранить проверяемые утверждения; для M1 из `report_data`-теста убрать обращение к `schedule`/`team` (снятая фича), оставив проверку валидного профиля по умолчанию и `evidence_summary.calibration_status`.

4. **Удаления.** Удалить 32 сценария из п. 7 (файлы `test_case_publication.py`, `test_pack_reconciliation.py`, `test_stage_integrity.py` — целиком; 7 функций из `test_evidence_api.py`; 1 функцию из `test_method_dependencies.py`).

5. **CI.**
   - На каждый PR: `cd backend && python -m pytest` (только `critical`, ожидаемо ≤30 s) + `cd frontend && npm test` (29, ~3 s).
   - Вручную/ночью: `cd backend && python -m pytest -m "critical or extended"` (≈157) + `npm run test:e2e` (2 сценария).
   - Не добавлять `-p no:cacheprovider` и подобное; маркеры — единственное изменение конфигурации.

6. **Приложение, формулы и API не меняются.** Удаление тестов не требует правок в `backend/app/`; если после снятия фичи из приложения уйдут `WorkPackage`/`TeamScenario`/`GameCase`/`CaseEvidence` и `/api/schedule`, соответствующие удалённые тесты просто перестанут существовать.

## 11. Пробелы покрытия (честно, без «доработки ради галочки»)

В R6 два свойства **не покрыты ни одним тестом** и после инвентаризации не покрыты:
- «нет доступа к приватным файлам» (path traversal / статические пути вне `dist`) — тестов нет;
- «нет записей из чужого browser origin» (CORS/CSRF) — тестов нет (поиск по `origin|CORS|traversal|private` в `backend/tests` не дал совпадений).

Остальные свойства R6 покрыты: неверный ввод (`test_critical_error_is_understandable`, `test_unknown_engine_rejected_with_hint`, `test_unknown_api_path_is_not_served_as_page`), готовность API (`test_health_ready…`, `test_health_unavailable…`), безопасные сообщения (`test_critical_error_is_understandable`, frontend `api.test.ts`). Добавлять новые тесты в рамках этой задачи не предлагается — только фиксируем пробел.
