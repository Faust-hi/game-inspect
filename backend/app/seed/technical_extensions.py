"""Technical mechanisms missing from the party-derived functional catalogue.

Documentation supports mechanisms and conditions, not game-specific adoption,
FPS gains or migration effort. Scores remain explicit expert assumptions.
"""
SOURCES = {
    'TECH_CAPTURE': ('Epic: Scene Capture', 'https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/Rendering/SceneCapture/CaptureScene?lang=en-US'),
    'TECH_HAIR': ('Epic: Hair Rendering and Simulation', 'https://dev.epicgames.com/documentation/unreal-engine/hair-rendering-and-simulation-in-unreal-engine?lang=en-US'),
    'TECH_CLOTH': ('Unity 6: Cloth', 'https://docs.unity3d.com/6000.0/Documentation/Manual/class-Cloth.html'),
    'TECH_DESTRUCTION': ('Epic: Destruction Overview', 'https://dev.epicgames.com/documentation/unreal-engine/destruction-overview?lang=en-US'),
    'TECH_REVERB': ('Epic: Convolution Reverb', 'https://dev.epicgames.com/documentation/unreal-engine/convolution-reverb-in-unreal-engine'),
    'TECH_SECURITY': ('Epic: Anti-Cheat Interfaces', 'https://dev.epicgames.com/docs/epic-online-services/trust-and-safety/anti-cheat-interfaces'),
}

FUNCTIONS = [
    ('portal_rendering', 'Дополнительные виды и порталы', 'Рендер сцены из дополнительных камер в текстуры, с ограничением видимости и числа обновлений.', 'TECH_CAPTURE'),
    ('hair_rendering', 'Волосы: пряди или карточки', 'Представление волос, симуляция направляющих, прозрачность и уровни детализации.', 'TECH_HAIR'),
    ('cloth_simulation', 'Симуляция ткани', 'Деформация одежды, ограничения и коллизии либо подготовленное движение.', 'TECH_CLOTH'),
    ('runtime_security', 'Проверки целостности и античит', 'Техническая интеграция проверок клиента и сервера; бюджет работы зависит от конкретного SDK.', 'TECH_SECURITY'),
]


def functions():
    return [dict(code=code, name=name, description=description, category='Технические подсистемы',
                 formats=['3D', '2.5D', '2D'], typical_world_types=[], sort_order=400+i, source_key=source)
            for i, (code, name, description, source) in enumerate(FUNCTIONS)]


def methods(M):
    specs = [
        ('portal_scene_capture_budget', 'Порталы через рендер в текстуру', 'portal_rendering', 'TECH_CAPTURE', 'algorithm',
         'Дополнительная камера пишет вид в render target; обновление ограничивается видимостью и частотой.',
         ['Показывает удалённую часть сцены', 'Позволяет независимо задать разрешение захвата'],
         ['Дополнительный рендер и render targets', 'Ограничение частоты может быть заметно при движении'],
         ['Не обновлять захват двумя механизмами одновременно', 'Проверить рекурсию, clip plane, прозрачность и отражения'],
         ['Настроить преобразование камеры и clip plane.', 'Ограничить число видимых порталов, вложенность и разрешение.', 'Измерить CPU/GPU и render targets при входе в портал.'],
         dict(impact_cpu=1, impact_gpu=2, impact_vram=1, implementation_cost=3, complexity=4)),
        ('hair_strand_simulation', 'Волосы из прядей с симуляцией', 'hair_rendering', 'TECH_HAIR', 'algorithm',
         'Пряди и направляющие описывают движение волос; стоимость зависит от их количества и покрытия экрана.',
         ['Детализированный силуэт и движение'], ['Затраты на симуляцию, затенение и прозрачность'],
         ['Проверить поддержку представления и платформы', 'Согласовать LOD с анимацией и тенями'],
         ['Подготовить groom и направляющие.', 'Настроить LOD, коллизии и границы.', 'Замерить крупный план и группу персонажей.'],
         dict(impact_gpu=2, impact_vram=1, implementation_cost=4, complexity=4)),
        ('hair_cards_lod', 'Карточки волос и уровни детализации', 'hair_rendering', 'TECH_HAIR', 'production',
         'Карточки или меши представляют волосы с меньшим числом элементов вместо отдельных прядей.',
         ['Управляемая геометрическая сложность'], ['Возможна потеря деталей', 'Прозрачность и overdraw требуют проверки'],
         ['Нужны подготовленные карточки и текстуры', 'Переключение представлений зависит от движка'],
         ['Подготовить карты волос и текстуры.', 'Настроить расстояния LOD и тени.', 'Сравнить силуэт, overdraw и память с прядями.'],
         dict(impact_gpu=-1, quality_impact=-1, implementation_cost=2, complexity=2)),
        ('cloth_constraint_simulation', 'Ткань с ограничениями и коллизиями', 'cloth_simulation', 'TECH_CLOTH', 'algorithm',
         'Сетка ткани решается с ограничениями движения и поддерживаемыми коллайдерами.',
         ['Реакция одежды на движение и столкновения'], ['Нагрузка решателя и коллизий', 'Ограничения поддерживаемых коллайдеров'],
         ['Количество вершин, коллизий и итераций задаётся отдельно', 'Проверить взаимодействие с анимацией'],
         ['Задать маски подвижности и коллайдеры.', 'Ограничить вершины и итерации решателя.', 'Проверить быстрые движения, коллизии и группу персонажей.'],
         dict(impact_cpu=1, impact_ram=1, implementation_cost=3, complexity=3)),
        ('cloth_baked_animation', 'Подготовленное движение ткани', 'cloth_simulation', 'TECH_CLOTH', 'production',
         'Вместо решателя воспроизводится подготовленная анимация или геометрический кэш.',
         ['Можно ограничить работу решателя в рантайме'], ['Нет произвольной реакции на новые столкновения', 'Дополнительные анимационные данные'],
         ['Подходит для предсказуемого движения', 'Проверить память и стриминг подготовленных данных'],
         ['Определить допустимые движения.', 'Подготовить и сжать анимацию.', 'Проверить переходы, память и контакт с окружением.'],
         dict(impact_cpu=-1, impact_ram=1, impact_disk=1, concept_impact=-1, implementation_cost=2, complexity=2)),
        ('runtime_fracture_budget', 'Разрушение с бюджетом активных обломков', 'destruction_simulation', 'TECH_DESTRUCTION', 'architecture',
         'Заранее разделённая геометрия образует кластеры; связи разрушаются при взаимодействии в симуляции.',
         ['Разрушение реагирует на взаимодействия'], ['Активные обломки, контакты и эффекты требуют ресурсов'],
         ['Проверить навигацию и динамическую видимость', 'В сетевой игре отдельно проверить репликацию состояния'],
         ['Подготовить кластеры, связи и коллизии.', 'Задать предел активных тел, засыпание и удаление обломков.', 'Проверить физику, навигацию, эффекты и сетевую синхронизацию.'],
         dict(impact_cpu=2, impact_gpu=1, impact_ram=1, implementation_cost=4, complexity=4)),
        ('audio_convolution_reverb', 'Свёрточная реверберация', 'audio_system', 'TECH_REVERB', 'algorithm',
         'Аудиосигнал обрабатывается импульсным откликом; стоимость зависит от длины IR и числа каналов.',
         ['Воспроизводит акустический отклик помещения'], ['Дополнительная работа DSP и хранение IR'],
         ['Не заменяет геометрическую окклюзию звука', 'Проверить блок обработки, каналы и переходы зон'],
         ['Подготовить импульсные отклики.', 'Настроить submix и длину блока.', 'Сравнить DSP-время, задержку и память при пике голосов.'],
         dict(impact_cpu=1, impact_ram=1, implementation_cost=2, complexity=3)),
        ('runtime_security_budget', 'Интеграция проверок с отдельным бюджетом', 'runtime_security', 'TECH_SECURITY', 'architecture',
         'Проверки целостности подключаются к жизненному циклу клиента и сервера с учётом требований SDK.',
         ['Проверки и обработка их результатов включены в архитектуру'], ['Дополнительные проверки и обмен сообщениями', 'Требуется проверка платформенной совместимости'],
         ['Универсальный процент потери FPS неизвестен', 'Не выводить нагрузку из названия DRM или бизнес-модели'],
         ['Определить проверяемые события и поддерживаемые платформы SDK.', 'Реализовать жизненный цикл, сообщения и обработку ошибок.', 'Замерить запуск, CPU, память и сеть с включёнными проверками и без них.'],
         dict(implementation_cost=4, complexity=4, performance_gain=0.0)),
    ]
    result = []
    for code, name, function, source, level, summary, pros, cons, conditions, steps, scores in specs:
        result.append(M(code, name, function, source_key=source, level=level, summary=summary,
                        description=summary, problem='Выбрать реализацию технической функции с учётом ресурсов и ограничений.',
                        pros=pros, cons=cons, requires_conditions=conditions, application_steps=steps,
                        limitations=['Описание механизма не подтверждает его применение в конкретной игре из партий.',
                                     'Баллы и аппаратные коэффициенты — экспертные допущения; ускорение и трудоёмкость не измерены.'],
                        verification_method=steps[-1], verification_tools=['Профилировщик движка', 'Захват CPU/GPU и памяти'],
                        requires_features=[function], requires_prototype=True, confidence=0.5,
                        **scores))
    return result


# No multiplicative synergy is inferred from these qualitative relationships.
CONFLICTS = [
    dict(a_code='hair_strand_simulation', b_code='hair_cards_lod', conflict_type='alternative', severity=2,
         description='Альтернативные представления одного LOD волос; разные LOD могут использовать разные представления.',
         resolution='Для расчёта выбрать одно представление целевой сцены; переходы проверить отдельно.', source_key='TECH_HAIR'),
    dict(a_code='cloth_constraint_simulation', b_code='cloth_baked_animation', conflict_type='alternative', severity=2,
         description='Решатель и подготовленное движение — альтернативы для одного участка ткани.',
         resolution='Выбрать способ для целевой сцены; смешение разных участков требует отдельного бюджета.', source_key='TECH_CLOTH'),
    dict(a_code='runtime_fracture_budget', b_code='destruction_geometry_cache', conflict_type='alternative', severity=2,
         description='Симуляция и воспроизведение кэша решают одну задачу разрушения по-разному.',
         resolution='Выбрать одну реализацию события; кэш не даёт произвольной реакции на новые воздействия.', source_key='TECH_DESTRUCTION'),
    dict(a_code='runtime_fracture_budget', b_code='baked_occlusion_culling', conflict_type='risk', severity=3,
         description='Изменение геометрии может сделать предвычисленную видимость устаревшей.',
         resolution='Исключить разрушаемую геометрию из статических окклюдеров либо обновлять видимость.', source_key='TECH_DESTRUCTION'),
    dict(a_code='runtime_fracture_budget', b_code='navmesh_tiling_streaming', conflict_type='risk', severity=2,
         description='После разрушения проходимость может измениться; готовая навигация не обязательно описывает новое состояние.',
         resolution='Проверить обновление затронутых тайлов и бюджет пути при разрушениях.', source_key='TECH_DESTRUCTION'),
]

CPU_LOAD = {'portal_rendering': {'render_prep': .05}, 'hair_rendering': {'animation': .03},
            'cloth_simulation': {'physics': .06}, 'runtime_security': {}}
GPU_LOAD = {'portal_rendering': {'geometry': .08, 'shading': .08},
            'hair_rendering': {'geometry': .03, 'transparency': .06}, 'cloth_simulation': {}, 'runtime_security': {}}
EFFECTS = {
    'portal_scene_capture_budget': {'cpu': {'render_prep': -.1}, 'gpu': {'geometry': -.1, 'shading': -.1}, 'mem': {'render_targets': .1}},
    'hair_strand_simulation': {'gpu': {'compute': -.15, 'transparency': -.1}, 'mem': {'meshes': .05}},
    'hair_cards_lod': {'note': 'карточки заменяют только представление волос; без отдельного бюджета волос экономия всей геометрии не начисляется; overdraw требует замера'},
    'cloth_constraint_simulation': {'cpu': {'physics': -.15}, 'mem': {'scene': .05}},
    'cloth_baked_animation': {'note': 'заменяет только решатель ткани; без раздельного бюджета ткани экономия общей физики не начисляется'},
    'runtime_fracture_budget': {'cpu': {'physics': -.15}, 'mem': {'scene': .05}},
    'audio_convolution_reverb': {'cpu': {'audio': -.2}, 'mem': {'audio': .05}},
    'runtime_security_budget': {'note': 'накладные расходы конкретного SDK не измерены; не учтены численно, нужен отдельный замер CPU, памяти и сети'},
}
