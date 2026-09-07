"""База инженерных знаний: методы и варианты реализации каталога.

Каждая запись описывает:
  * классификацию решения (уровень, стадия, стоимость позднего внедрения);
  * влияние на подсистемы CPU / GPU / RAM / VRAM / накопитель / сеть;
  * влияние на качество и исходную концепцию;
  * применимость по формату, типу мира, движку, платформе, оборудованию;
  * способ последующей проверки.

Шкала влияния: -2 — сильное снижение нагрузки, 0 — нет влияния,
+2 — сильное увеличение нагрузки.
"""
from __future__ import annotations

from .sources import src

_DEFAULTS: dict = {
    "kind": None,               # implementation, если указана функция; иначе optimization
    "level": "algorithm",
    "recommended_stage": "prototype",
    "late_cost": "medium",
    "calc_mode": "realtime",
    "impact_cpu": 0, "impact_gpu": 0, "impact_ram": 0,
    "impact_vram": 0, "impact_disk": 0, "impact_network": 0,
    "quality_impact": 0, "concept_impact": 0,
    "performance_gain": 0.5,
    "implementation_cost": 3,
    "complexity": 3,
    "confidence": 0.7,
    "requires_prototype": False,
    "applicable_formats": None,
    "applicable_world_types": [],
    "applicable_engines": [],
    "applicable_platforms": [],
    "requires_features": [],
    "requires_hw_features": [],
    "requires_conditions": [],
    "min_scale": None,
    "pros": [], "cons": [], "limitations": [],
    "verification_method": "", "verification_tools": [],
    "application_steps": [],
    "source_key": None,
}


def M(code: str, name: str, function_code: str | None = None, **kw) -> dict:
    """Собрать описание метода с заполнением значений по умолчанию."""
    data = dict(_DEFAULTS)
    data.update(kw)
    data["code"] = code
    data["name"] = name
    data["function_code"] = function_code
    data["kind"] = data["kind"] or ("implementation" if function_code else "optimization")
    if data["applicable_formats"] is None:
        data["applicable_formats"] = ["3D"]
    return data


METHODS: list[dict] = [
    # =====================================================================
    # 1. Потоковая загрузка открытого мира
    # =====================================================================
    M("world_partition_streaming", "Разбиение мира на ячейки с потоковой загрузкой",
      "open_world_streaming",
      summary="Мир разбивается на ячейки, которые подгружаются и выгружаются по дистанции до игрока.",
      description="Вместо одного монолитного уровня мир хранится набором ячеек фиксированного размера. "
                  "Каждый кадр определяется набор ячеек в радиусе загрузки, лишние выгружаются. "
                  "Позволяет удерживать в памяти и обрабатывать только актуальную часть мира.",
      problem="Полная загрузка большого мира невозможна: она превышает бюджет RAM и времени кадра.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=1, impact_ram=1, impact_disk=1,
      performance_gain=0.75, implementation_cost=4, complexity=4, confidence=0.85,
      applicable_world_types=["open_world", "procedural", "sandbox"],
      min_scale="large",
      pros=["Снимает ограничение на размер мира", "Позволяет параллелить работу команды"],
      cons=["Требует дисциплины работы с ассетами", "Появляются задержки подгрузки"],
      limitations=["Требует строгого контроля зависимостей ассетов"],
      verification_method="Профилирование пиков времени кадра при быстром перемещении; контроль "
                          "отсутствия кадров дольше бюджета на загрузку.",
      verification_tools=["Unreal Insights", "Unity Profiler", "Профилировщик Godot"],
      source_key="UE_WORLDPARTITION"),

    M("world_origin_shifting", "Сдвиг начала координат (origin rebasing)",
      "open_world_streaming",
      summary="Перенос начала координат за игроком для исключения потери точности float на больших расстояниях.",
      description="При удалении от начала координат точность float32 падает: появляются дрожание "
                  "геометрии, артефакты физики и анимации. Решение — периодический сдвиг мира или "
                  "использование double-координат на уровне движка.",
      problem="На расстояниях свыше нескольких километров от нуля возникают видимые артефакты точности.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=1,
      performance_gain=0.3, implementation_cost=4, complexity=5, confidence=0.8,
      applicable_world_types=["open_world", "procedural", "sandbox"],
      min_scale="large",
      pros=["Устраняет артефакты точности", "Обязательно для миров больше ~5 км"],
      cons=["Сложно встроить в уже готовый проект", "Затрагивает физику, ИИ, сеть и звук"],
      limitations=["Требует пересмотра всей работы с координатами"],
      requires_prototype=True,
      verification_method="Тест на границе мира: контроль дрожания геометрии и стабильности коллизий.",
      verification_tools=["Unreal Insights"],
      source_key="UE_LWC"),

    M("hierarchical_lod", "Иерархические LOD (HLOD)",
      "open_world_streaming",
      summary="Группы удалённых объектов объединяются в один упрощённый прокси-меш и отрисовываются одним вызовом.",
      description="Дерево объектов разбивается на кластеры, для каждого кластера заранее или "
                  "автоматически строится упрощённый меш. На дистанции кластер заменяется прокси-мешем, "
                  "что радикально снижает количество вызовов отрисовки.",
      problem="В большом мире количество вызовов отрисовки становится основным ограничением CPU.",
      level="production", recommended_stage="production", late_cost="medium",
      impact_cpu=-1, impact_gpu=-2, impact_ram=1, impact_vram=1, impact_disk=1,
      quality_impact=-1,
      performance_gain=0.75, implementation_cost=3, complexity=3, confidence=0.8,
      applicable_world_types=["open_world", "procedural", "sandbox", "hub", "linear"],
      min_scale="medium",
      pros=["Существенно снижает количество вызовов отрисовки", "Хорошо масштабируется"],
      cons=["Требует пересборки при изменении мира", "Возможны « pops » при переключении"],
      limitations=["Плохо работает с полностью разрушаемым миром"],
      verification_method="Замер количества вызовов отрисовки и времени рендер-потока до и после.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_HLOD"),

    M("gpu_compute_culling", "Отсечение объектов на GPU (compute)",
      "open_world_streaming",
      summary="Отсечение по пирамиде видимости и окклюзии выполняется вычислительным шейдером по всем объектам сразу.",
      description="Список объектов переносится в буфер на GPU, где вычислительный шейдер параллельно "
                  "проверяет видимость и записывает только видимые инстансы. Снимает нагрузку с CPU "
                  "и позволяет обрабатывать сотни тысяч объектов.",
      problem="Отсечение десятков тысяч объектов на CPU занимает значительную часть кадра.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_cpu=-2, impact_gpu=1,
      performance_gain=0.65, implementation_cost=4, complexity=4, confidence=0.75,
      requires_hw_features=["Compute Shaders"],
      applicable_world_types=["open_world", "procedural", "sandbox"],
      min_scale="medium",
      pros=["Практически снимает стоимость отсечения с CPU", "Масштабируется на сотни тысяч объектов"],
      cons=["Требует перестройки рендер-конвейера", "Сложнее отлаживать"],
      limitations=["Нужен GPU с поддержкой вычислительных шейдеров"],
      requires_prototype=True,
      verification_method="Сравнение времени CPU на отсечение и полного времени кадра.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_NANITE"),

    M("baked_occlusion_culling", "Запечённое отсечение по окклюзии",
      "open_world_streaming",
      summary="Видимость ячеек рассчитывается заранее и сохраняется в данные уровня.",
      description="Для статической геометрии заранее вычисляется, какие объекты видны из каждой ячейки. "
                  "В рантайме отсечение сводится к поиску по готовой таблице.",
      problem="Рантайм-отсечение по глубине дорого и не всегда точно.",
      level="production", recommended_stage="production", late_cost="low",
      impact_cpu=-1, impact_gpu=-1, impact_ram=1, impact_disk=1,
      performance_gain=0.5, implementation_cost=2, complexity=2, confidence=0.85,
      applicable_world_types=["linear", "hub", "arena"],
      pros=["Почти нулевая стоимость в рантайме", "Просто внедрить"],
      cons=["Не учитывает динамические объекты", "Требует пересчёта при изменении геометрии"],
      limitations=["Плохо применимо к открытому миру со стримингом", "Окклюзию надо проектировать стенами и комнатами: где нечего закрыть, там нечего отсечь"],
      verification_method="Сравнение числа отрисованных объектов до и после запекания на контрольных точках.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="UNITY_OCCLUSION"),

    M("async_loading_pipeline", "Асинхронная загрузка без блокировки кадра",
      "open_world_streaming",
      summary="Загрузка ресурсов выносится в отдельный поток с ограничением времени работы на кадр.",
      description="Ресурсы читаются и создаются в фоновом потоке, а перенос в GPU происходит порциями "
                  "с контролем бюджета времени кадра, что исключает фризы.",
      problem="Синхронная загрузка вызывает заметные «фризы» при появлении новых зон.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_cpu=1, impact_disk=1,
      performance_gain=0.45, implementation_cost=3, complexity=3, confidence=0.85,
      pros=["Устраняет фризы", "Улучшает воспринимаемую плавность"],
      cons=["Требует аккуратной работы с зависимостями", "Возможна задержка появления объектов"],
      limitations=["Не снижает среднюю нагрузку, только пиковую"],
      verification_method="Замер максимального времени кадра в сценарии быстрого перемещения.",
      verification_tools=["Unreal Insights", "Unity Profiler", "Профилировщик Godot"],
      source_key="GODOT_THREADS"),

    # =====================================================================
    # 2. Крупномасштабный ландшафт
    # =====================================================================
    M("terrain_clipmap", "Клипмап / CDLOD ландшафта",
      "large_scale_terrain",
      summary="Ландшафт рендерится набором вложенных сеток с разным шагом вокруг камеры.",
      description="Вокруг камеры строится набор колец: ближние с высокой детализацией, дальние — "
                  "с низкой. Вершины смещаются по карте высот в шейдере. Позволяет отрисовывать "
                  "ландшафт любого размера за фиксированное число вызовов.",
      problem="Единая сетка ландшафта быстро превышает бюджет вершин и памяти.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_cpu=-1, impact_gpu=-1, impact_ram=-1, impact_vram=-1,
      performance_gain=0.7, implementation_cost=4, complexity=4, confidence=0.75,
      applicable_world_types=["open_world", "procedural", "sandbox"],
      min_scale="large",
      pros=["Фиксированная стоимость при любом размере мира", "Детализация сохраняется вблизи"],
      cons=["Сложная реализация", "Ограничения на нависающие формы рельефа"],
      limitations=["Пещеры и нависающие скаты требуют отдельной геометрии"],
      requires_prototype=True,
      verification_method="Замер времени рендера ландшафта при максимальной дальности обзора.",
      verification_tools=["Unreal Insights", "Профилировщик Godot"],
      source_key="WIKI_LOD"),

    M("virtual_texturing", "Виртуальное текстурирование",
      "large_scale_terrain",
      summary="Текстуры подгружаются тайлами по требованию, в VRAM хранится только видимая часть.",
      description="Все текстуры проекта рассматриваются как единое виртуальное пространство, "
                  "разбитое на тайлы. В рантайме подгружаются только тайлы, реально попадающие в кадр, "
                  "и удерживаются в кэше фиксированного размера.",
      problem="Размер текстур большого мира кратно превышает доступный объём VRAM.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_ram=1, impact_vram=-2, impact_disk=1,
      performance_gain=0.6, implementation_cost=5, complexity=5, confidence=0.7,
      applicable_world_types=["open_world", "procedural", "sandbox", "linear"],
      min_scale="medium",
      pros=["Снимает ограничение VRAM на объём текстур", "Снижает размер сборки"],
      cons=["Высокая стоимость реализации", "Появляется задержка подкачки тайлов"],
      limitations=["Требует поддержки со стороны рендер-конвейера"],
      requires_prototype=True,
      application_steps=[
          "Замерить рабочий набор текстур на типовом маршруте игрока.",
          "Выставить пул около 70% лимита VRAM, остальное — кадр и система.",
          "Ужесточить MIP-bias для далёких тайлов.",
          "Проверить подгрузку на быстром перемещении.",
          "Сверить занятую VRAM до и после.",
      ],
      verification_method="Контроль объёма VRAM и отсутствия «замыленных» текстур при движении.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_VIRTUALTEXTURING"),

    M("heightmap_compression", "Сжатие карт высот и материалов ландшафта",
      "large_scale_terrain",
      summary="Данные ландшафта хранятся в сжатом виде и распаковываются при загрузке или в шейдере.",
      description="Карты высот и масок материалов хранятся в блочно-сжатых форматах или в виде "
                  "тайлов с пониженной точностью; распаковка происходит на GPU.",
      problem="Данные ландшафта занимают значительную часть объёма игры и оперативной памяти.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=1, impact_ram=-1, impact_vram=-1, impact_disk=-2,
      quality_impact=-1,
      performance_gain=0.4, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Быстрый эффект на размер сборки", "Малый риск"],
      cons=["Возможна потеря детализации рельефа"],
      limitations=["Не снижает вычислительную нагрузку"],
      verification_method="Сравнение размера сборки и визуальное сравнение рельефа на контрольных участках.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_MIPMAP"),

    M("virtual_geometry_clusters", "Виртуализированная геометрия (кластеризованный LOD)",
      "large_scale_terrain",
      summary="Геометрия разбивается на кластеры, LOD выбирается на GPU для каждого кластера отдельно.",
      description="Меши делятся на кластеры по ~128 треугольников; для каждого кластера строится "
                  "цепочка упрощений. Выбор уровня происходит на GPU по проекции на экран, "
                  "что даёт пиксельно-точный LOD без участия CPU.",
      problem="Ручное создание LOD для тысяч уникальных ассетов не масштабируется на производстве.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=-2, impact_gpu=-1, impact_ram=-1, impact_disk=1,
      performance_gain=0.8, implementation_cost=5, complexity=5, confidence=0.65,
      applicable_platforms=["pc_windows", "ps5", "xbox_series"],
      requires_hw_features=["DirectX 12"],
      min_scale="medium",
      pros=["Снимает ручную работу по LOD", "Пиксельно-точная детализация"],
      cons=["Доступно не на всех платформах", "Требует пересборки всех ассетов"],
      limitations=["Не поддерживается на старых консолях и мобильных платформах"],
      requires_prototype=True,
      verification_method="Замер числа треугольников и времени рендера на эталонных кадрах.",
      verification_tools=["Unreal Insights"],
      source_key="UE_NANITE"),

    # =====================================================================
    # 3. Растительность и объекты окружения
    # =====================================================================
    M("gpu_instancing_vegetation", "GPU-инстансинг растительности",
      "procedural_vegetation",
      summary="Одинаковые объекты окружения отрисовываются одним вызовом с массивом трансформаций.",
      description="Вместо отдельного вызова на каждый объект в GPU передаётся меш и буфер "
                  "трансформаций; количество объектов ограничивается уже заполнением экрана, "
                  "а не числом вызовов.",
      problem="Тысячи отдельных объектов растительности перегружают CPU вызовами отрисовки.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_cpu=-2, impact_gpu=-1, impact_vram=1,
      performance_gain=0.75, implementation_cost=3, complexity=3, confidence=0.9,
      pros=["Большой эффект при умеренной стоимости", "Поддерживается всеми современными движками"],
      cons=["Усложняет выборочное взаимодействие с объектами"],
      limitations=["Требует одинаковой геометрии и материалов", "Видимость всего MultiMesh целиком: далёкие зоны резать отдельными MultiMesh"],
      verification_method="Замер количества вызовов отрисовки и времени CPU на рендер.",
      verification_tools=["Unity Profiler", "Профилировщик Godot", "Unreal Insights"],
      source_key="UNITY_INSTANCING"),

    M("gpu_procedural_placement", "Процедурное размещение на GPU",
      "procedural_vegetation",
      summary="Позиции объектов вычисляются вычислительным шейдером по правилам плотности прямо в рантайме.",
      description="Вместо хранения миллионов трансформаций на диске позиции генерируются по "
                  "маскам и правилам размещения на GPU при подгрузке ячейки. Данные о растительности "
                  "практически не занимают места.",
      problem="Хранение трансформаций для миллионов объектов перегружает память и диск.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_cpu=-2, impact_gpu=1, impact_ram=-2, impact_vram=1,
      performance_gain=0.7, implementation_cost=4, complexity=4, confidence=0.7,
      requires_hw_features=["Compute Shaders"],
      min_scale="medium",
      pros=["Радикально снижает объём данных", "Позволяет менять облик мира без пересборки"],
      cons=["Сложнее обеспечить детерминизм", "Усложняет запекание освещения"],
      limitations=["Требует вычислительных шейдеров"],
      requires_prototype=True,
      verification_method="Замер времени генерации ячейки и объёма занимаемой памяти.",
      verification_tools=["Unreal Insights"],
      source_key="UE_ISM"),

    M("impostors_billboards", "Импосторы и билборды для дальнего плана",
      "procedural_vegetation",
      summary="Удалённые объекты заменяются плоскими изображениями с предпросчитанным видом.",
      description="Для дальних дистанций используется заранее отрендеренное изображение объекта "
                  "с нескольких ракурсов вместо объёмной геометрии.",
      problem="Полноценная геометрия растительности на дальних дистанциях тратит заполнение экрана впустую.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=-2, impact_vram=-1, impact_disk=1,
      quality_impact=-1,
      performance_gain=0.6, implementation_cost=2, complexity=2, confidence=0.85,
      min_scale="medium",
      pros=["Сильно снижает нагрузку на заполнение", "Легко внедрить"],
      cons=["Заметно при близком рассмотрении", "Плохо смотрится при движении камеры"],
      limitations=["Не подходит для крупных уникальных объектов"],
      verification_method="Замер времени GPU и визуальная оценка на дистанции переключения.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_IMPOSTOR"),

    M("vegetation_atlas_lod", "Атласы и запечённые LOD растительности",
      "procedural_vegetation",
      summary="Текстуры растительности объединяются в атласы, LOD-цепочки строятся заранее.",
      description="Объединение текстур в атласы позволяет рисовать разные виды растений одним "
                  "материалом, а готовые LOD-цепочки исключают переключение материалов на дистанции.",
      problem="Разнообразие видов растительности порождает множество материалов и смен состояния GPU.",
      level="production", recommended_stage="production", late_cost="low",
      impact_gpu=-1, impact_vram=-1, impact_disk=-1,
      quality_impact=-1,
      performance_gain=0.5, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Снижает число смен состояния", "Уменьшает размер сборки"],
      cons=["Требует переработки ассетов", "Ограничивает разнообразие материалов"],
      limitations=["Требует пересборки контента"],
      verification_method="Замер числа смен состояния материалов и времени GPU.",
      verification_tools=["Unity Profiler"],
      source_key="WIKI_ATLAS"),

    # =====================================================================
    # 4. Динамическое глобальное освещение
    # =====================================================================
    M("sdf_global_illumination", "Глобальное освещение на дистанционных полях (SDF)",
      "dynamic_global_illumination",
      summary="Переотражённый свет оценивается трассировкой по заранее построенным дистанционным полям.",
      description="Для сцены строятся дистанционные поля, по которым выполняется быстрая "
                  "трассировка коротких лучей. Даёт мягкое переотражённое освещение при "
                  "умеренной стоимости и без specialised оборудования.",
      problem="Полноценная трассировка лучей слишком дорога для целевого оборудования.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_gpu=1, impact_vram=2, impact_ram=1,
      performance_gain=0.3, implementation_cost=4, complexity=4, confidence=0.7,
      requires_conditions=["Требует преимущественно статической геометрии для построения полей"],
      pros=["Динамическое ГО без аппаратного RT", "Мягкое и стабильное освещение"],
      cons=["Заметная стоимость GPU и памяти", "Ограниченная дальность переотражения"],
      limitations=["Динамическая геометрия требует пересборки полей"],
      requires_prototype=True,
      verification_method="Замер времени GPU на проход ГО и визуальная проверка стабильности.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_SDF"),

    M("irradiance_volume_probes", "Зонды освещённости (irradiance volume)",
      "dynamic_global_illumination",
      summary="Освещённость сэмплируется в узлах сетки и интерполируется для динамических объектов.",
      description="В пространстве сцены размещается сетка зондов, в каждом хранится сферическая "
                  "освещённость. Объекты получают освещение интерполяцией ближайших зондов.",
      problem="Динамические объекты не получают переотражённый свет при запечённом освещении.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_cpu=-1, impact_gpu=-1, impact_vram=1,
      quality_impact=-1,
      performance_gain=0.55, implementation_cost=3, complexity=3, confidence=0.85,
      pros=["Хорошее соотношение качества и стоимости", "Поддерживается всеми движками"],
      cons=["Низкая пространственная точность", "Утечки света через тонкие стены"],
      limitations=["Требует ручной расстановки или автогенерации зондов"],
      verification_method="Визуальная проверка на контрольных сценах и замер времени обновления зондов.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="UNITY_LIGHTPROBES"),

    M("voxel_cone_tracing", "Воксельный конусный трейсинг",
      "dynamic_global_illumination",
      summary="Сцена вокселизуется, переотражённый свет собирается конусной трассировкой по вокселям.",
      description="Геометрия сцены периодически преобразуется в разреженное воксельное "
                  "представление, по которому выполняется конусная трассировка для оценки "
                  "непрямого освещения и затенения.",
      problem="Требуется динамическое ГО с дальними переотражениями.",
      level="architecture", recommended_stage="prototype", late_cost="high",
      impact_gpu=2, impact_vram=2, impact_ram=1,
      performance_gain=0.2, implementation_cost=4, complexity=5, confidence=0.6,
      pros=["Дальние переотражения", "Полностью динамическое освещение"],
      cons=["Высокая стоимость GPU и памяти", "Артефакты утечки света"],
      limitations=["Плохо масштабируется на открытый мир"],
      requires_prototype=True,
      verification_method="Замер времени вокселизации и трассировки, визуальная оценка артефактов.",
      verification_tools=["Профилировщик Godot", "Unreal Insights"],
      source_key="WIKI_SVO"),

    M("screen_space_gi", "Экранное глобальное освещение (SSGI)",
      "dynamic_global_illumination",
      summary="Переотражённый свет оценивается только по информации, доступной в кадре.",
      description="Непрямое освещение восстанавливается трассировкой по буферу глубины и цвета "
                  "текущего кадра. Стоимость низкая, но за пределами кадра информация отсутствует.",
      problem="Нужно улучшить освещение без перехода на дорогие решения.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=1,
      quality_impact=-1,
      performance_gain=0.35, implementation_cost=2, complexity=2, confidence=0.8,
      pros=["Низкая стоимость внедрения", "Работает с любой геометрией"],
      cons=["Свет пропадает за краем экрана", "Артефакты на границах экрана"],
      limitations=["Не заменяет полноценное ГО"],
      verification_method="Визуальная оценка на краях экрана и замер времени GPU.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_AO"),

    M("temporal_radiance_cache", "Кэш излучения с временным накоплением",
      "dynamic_global_illumination",
      summary="Результат расчёта ГО переиспользуется между кадрами и обновляется частично.",
      description="Освещённость хранится в экранном или мировом кэше и обновляется небольшими "
                  "порциями каждый кадр с накоплением по истории, что снижает стоимость в разы.",
      problem="Полный пересчёт ГО каждый кадр слишком дорог.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_gpu=-1, impact_vram=1,
      performance_gain=0.5, implementation_cost=4, complexity=4, confidence=0.65,
      pros=["Кратное снижение стоимости ГО", "Хорошо сочетается с временным сглаживанием"],
      cons=["Инерция при резкой смене освещения", "Возможны «призраки»"],
      limitations=["Требует стабильной temporальной перепроекции"],
      requires_prototype=True,
      verification_method="Замер времени GPU и проверка реакции на резкую смену освещения.",
      verification_tools=["Unreal Insights"],
      source_key="UE_LUMEN"),

    M("hardware_raytraced_gi", "Глобальное освещение на аппаратной трассировке лучей",
      "dynamic_global_illumination",
      summary="Переотражённый свет рассчитывается трассировкой лучей на RT-ядрах видеокарты.",
      description="Используются аппаратные структуры ускорения (BVH) и RT-ядра. Даёт физически "
                  "корректное освещение, но стоимость остаётся высокой даже на старших GPU.",
      problem="Требуется максимальное качество освещения при наличии соответствующего оборудования.",
      level="architecture", recommended_stage="prototype", late_cost="high",
      impact_gpu=2, impact_vram=1,
      quality_impact=2,
      performance_gain=0.1, implementation_cost=4, complexity=4, confidence=0.8,
      applicable_platforms=["pc_windows", "ps5", "xbox_series"],
      requires_hw_features=["Hardware Ray Tracing"],
      pros=["Максимальная достоверность освещения", "Корректные отражения и тени"],
      cons=["Очень высокая стоимость GPU", "Ограниченная база оборудования"],
      limitations=["Требует аппаратной поддержки трассировки лучей"],
      requires_prototype=True,
      verification_method="Замер времени GPU на RT-проход и проверка на минимальной поддерживаемой видеокарте.",
      verification_tools=["Unreal Insights"],
      source_key="UE_LUMEN"),

    # =====================================================================
    # 5. Запечённое освещение
    # =====================================================================
    M("lightmap_atlas_baking", "Запекание освещения в лайтмапы",
      "baked_lighting",
      summary="Освещение статической геометрии рассчитывается заранее и сохраняется в текстуры.",
      description="Для статических объектов строятся развёртки второго набора UV и рассчитывается "
                  "освещение с учётом переотражений. Результат сохраняется в лайтмапы, "
                  "в рантайме стоимость освещения практически нулевая.",
      problem="Динамическое освещение статичных сцен неоправданно дорого.",
      level="production", recommended_stage="production", late_cost="medium",
      impact_cpu=-2, impact_gpu=-2, impact_vram=-2, impact_disk=2, impact_ram=1,
      quality_impact=-1, calc_mode="precomputed",
      performance_gain=0.8, implementation_cost=3, complexity=3, confidence=0.9,
      applicable_world_types=["linear", "hub", "arena"],
      pros=["Почти нулевая стоимость в рантайме", "Высокое качество с мягкими переотражениями"],
      cons=["Требует статической геометрии", "Долгий пересчёт при изменениях"],
      limitations=["Несовместимо с динамическим временем суток"],
      verification_method="Сравнение времени кадра рендера освещения до и после; контроль размера лайтмапов.",
      verification_tools=["Unity Profiler", "Unreal Insights", "Профилировщик Godot"],
      source_key="WIKI_LIGHTMAP"),

    M("gpu_lightmap_baking", "GPU-ускоренный пересчёт освещения",
      "baked_lighting",
      summary="Расчёт лайтмапов переносится на GPU, сокращая время производственной итерации.",
      description="Влияет не на производительность игры, а на производственный процесс: "
                  "пересчёт освещения занимает минуты вместо часов, что позволяет чаще проверять результат.",
      problem="Медленный пересчёт освещения блокирует итерации художников.",
      level="production", recommended_stage="production", late_cost="low",
      calc_mode="precomputed",
      performance_gain=0.1, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Резко ускоряет итерации", "Не влияет на рантайм"],
      cons=["Требует совместимого GPU на машинах команды"],
      limitations=["Не снижает нагрузку на игровое оборудование"],
      verification_method="Замер времени пересчёта освещения эталонного уровня.",
      verification_tools=["Unity Profiler"],
      source_key="UNITY_LIGHTMAPPER"),

    M("lightmap_compression_streaming", "Сжатие и потоковая подкачка лайтмапов",
      "baked_lighting",
      summary="Лайтмапы сжимаются и подгружаются по частям, удерживая в памяти только видимые.",
      description="Лайтмапы хранятся сжатыми и подгружаются по мере необходимости, что снижает "
                  "объём VRAM и размер сборки.",
      problem="Лайтмапы больших уровней занимают гигабайты памяти и диска.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=1, impact_vram=-2, impact_disk=-2,
      quality_impact=-1,
      performance_gain=0.4, implementation_cost=2, complexity=2, confidence=0.8,
      pros=["Существенно снижает VRAM", "Уменьшает размер сборки"],
      cons=["Возможны артефакты сжатия", "Появляется стоимость подкачки"],
      limitations=["Требует настройки качества сжатия"],
      verification_method="Замер объёма VRAM и визуальная проверка градиентов освещения.",
      verification_tools=["Unreal Insights"],
      source_key="UE_VIRTUALTEXTURING"),

    # =====================================================================
    # 6. Динамические тени
    # =====================================================================
    M("cascaded_shadow_maps", "Каскадные карты теней",
      "dynamic_shadows",
      summary="Область вокруг камеры разбивается на каскады с отдельной картой теней разного разрешения.",
      description="Ближние каскады покрывают малую площадь с высоким разрешением, дальние — "
                  "большую площадь с низким. Стандартное решение для направленного света.",
      problem="Единая карта теней не даёт одновременно покрытия и детализации.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_gpu=1, impact_vram=1,
      performance_gain=0.5, implementation_cost=3, complexity=3, confidence=0.9,
      pros=["Хорошее качество при умеренной стоимости", "Поддерживается всеми движками"],
      cons=["Видимые переходы между каскадами", "Стоимость растёт с числом каскадов"],
      limitations=["Требует настройки разделения каскадов"],
      verification_method="Замер времени рендера теней и визуальная оценка переходов каскадов.",
      verification_tools=["Unity Profiler", "Профилировщик Godot", "Unreal Insights"],
      source_key="WIKI_SHADOWMAP"),

    M("virtual_shadow_maps", "Виртуальные карты теней (VSM)",
      "dynamic_shadows",
      summary="Тени хранятся в виртуальном пространстве страниц и обновляются только там, где они нужны кадру.",
      description="Вместо одной большой карты для каждого каскада используется виртуальный набор страниц. "
                  "Движок выделяет и обновляет страницы по видимости и детализации, что позволяет "
                  "сохранять высокое разрешение теней на больших сценах без полного пересчёта всей карты.",
      problem="Большие динамические сцены требуют детальных теней, но полный набор карт теней "
              "дорог по времени рендера и видеопамяти.",
      level="algorithm", recommended_stage="preproduction", late_cost="high",
      impact_gpu=2, impact_vram=2, impact_ram=1,
      quality_impact=1,
      performance_gain=0.7, implementation_cost=4, complexity=4, confidence=0.85,
      applicable_world_types=["open_world", "procedural", "sandbox", "linear", "hub", "arena"],
      min_scale="medium",
      pros=["Высокая детализация теней на больших дистанциях", "Страницы обновляются по потребности"],
      cons=["Заметная нагрузка на GPU и VRAM", "Требует настройки размеров страниц и дальности теней"],
      limitations=["Не устраняет стоимость теней от большого числа динамических источников",
                   "Результат зависит от поддержки и настроек конкретного рендер-конвейера"],
      requires_prototype=True,
      verification_method="Замер времени shadow-прохода, пиков VRAM и количества обновляемых страниц "
                          "в сценах с разной плотностью геометрии и источников света.",
      verification_tools=["Unreal Insights", "RenderDoc"],
      source_key="UE_VSM"),

    M("distance_field_shadows", "Тени на дистанционных полях (SDF)",
      "dynamic_shadows",
      summary="Тени от дальних источников рассчитываются трассировкой по дистанционным полям сцены.",
      description="По полям расстояний выполняется мягкая трассировка теней, что даёт мягкие "
                  "тени на больших дистанциях при фиксированной стоимости.",
      problem="Каскадные карты теней плохо масштабируются на большие открытые пространства.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_cpu=-1, impact_gpu=-1, impact_vram=2, impact_ram=1,
      performance_gain=0.55, implementation_cost=4, complexity=4, confidence=0.7,
      applicable_world_types=["open_world", "procedural", "sandbox"],
      min_scale="large",
      pros=["Мягкие тени на любой дистанции", "Хорошо подходит для открытого мира"],
      cons=["Заметный расход памяти", "Требует построения полей"],
      limitations=["Динамическая геометрия требует пересборки полей"],
      requires_prototype=True,
      verification_method="Замер памяти на поля и времени трассировки теней.",
      verification_tools=["Unreal Insights"],
      source_key="UE_VSM"),

    M("screen_space_contact_shadows", "Контактные тени в экранном пространстве",
      "dynamic_shadows",
      summary="Короткие тени в местах контакта объектов дорисовываются по буферу глубины.",
      description="Дешёвый экранный проход добавляет недостающую детализацию контактов поверх "
                  "основных теней низкого разрешения.",
      problem="Тени низкого разрешения «отрывают» объекты от поверхности.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=1, quality_impact=1,
      performance_gain=0.2, implementation_cost=1, complexity=2, confidence=0.85,
      pros=["Очень низкая стоимость", "Заметно улучшает восприятие"],
      cons=["Не заменяет полноценные тени", "Артефакты на краях экрана"],
      limitations=["Работает только в пределах кадра"],
      verification_method="Визуальная оценка контактов объектов и замер времени прохода.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_AO"),

    M("static_shadow_caching", "Кэширование теней от статических объектов",
      "dynamic_shadows",
      summary="Тени от неподвижных объектов рассчитываются один раз и переиспользуются.",
      description="Тень статической геометрии рендерится в отдельную карту, которая обновляется "
                  "только при изменении освещения; в кадре перерисовываются только динамические объекты.",
      problem="Ежекадровый пересчёт теней от статики тратит время GPU впустую.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_gpu=-2, impact_vram=1, impact_disk=1,
      performance_gain=0.6, implementation_cost=3, complexity=3, confidence=0.8,
      pros=["Существенно снижает стоимость теней", "Хорошо подходит для статичных сцен"],
      cons=["Не работает с динамическим временем суток", "Требует разделения статики и динамики"],
      limitations=["Требует пересчёта при изменении освещения"],
      verification_method="Замер времени рендера теней при неподвижной камере.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_VSM"),

    # =====================================================================
    # 7. Системы частиц
    # =====================================================================
    M("gpu_particle_simulation", "Симуляция частиц на GPU",
      "particle_systems",
      summary="Позиции и состояние частиц вычисляются вычислительным шейдером, а не на CPU.",
      description="Частицы хранятся в буферах на GPU и обновляются вычислительным шейдером, "
                  "что позволяет симулировать на порядки больше частиц и снимает нагрузку с CPU.",
      problem="CPU-симуляция ограничивает число частиц и загружает главный поток.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_cpu=-2, impact_gpu=1, impact_vram=1,
      performance_gain=0.7, implementation_cost=3, complexity=3, confidence=0.85,
      requires_hw_features=["Compute Shaders"],
      pros=["На порядки больше частиц", "Снимает нагрузку с CPU"],
      cons=["Сложнее реализовать взаимодействие с игровой логикой", "Сложнее отлаживать"],
      limitations=["Нужна поддержка вычислительных шейдеров"],
      verification_method="Замер времени CPU на обновление частиц и числа активных частиц.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_NIAGARA"),

    M("particle_pooling", "Пулинг систем частиц",
      "particle_systems",
      summary="Системы частиц создаются заранее и переиспользуются вместо постоянного создания и удаления.",
      description="Пул готовых экземпляров исключает аллокации и сборку мусора во время боя, "
                  "устраняя пиковые задержки.",
      problem="Постоянное создание эффектов вызывает аллокации и сборку мусора в критичные моменты.",
      level="algorithm", recommended_stage="production", late_cost="low",
      impact_cpu=-1, impact_ram=-1,
      performance_gain=0.4, implementation_cost=2, complexity=2, confidence=0.9,
      pros=["Устраняет пики сборки мусора", "Просто внедрить"],
      cons=["Требует дисциплины при работе с эффектами"],
      limitations=["Не снижает среднюю нагрузку"],
      verification_method="Контроль отсутствия аллокаций в профилировщике во время эффектов.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_OBJECTPOOL"),

    M("flipbook_particles", "Flipbook-текстуры вместо симуляции",
      "particle_systems",
      summary="Сложный эффект заменяется анимированной последовательностью кадров плоскости.",
      description="Вместо физической симуляции частиц воспроизводится заранее отрендеренная "
                  "последовательность кадров; стоимость сводится к отрисовке нескольких плоскостей.",
      problem="Физическая симуляция сложных эффектов слишком дорога для целевого оборудования.",
      level="production", recommended_stage="production", late_cost="low",
      impact_cpu=-2, impact_gpu=-1, impact_vram=1, impact_disk=1,
      quality_impact=-1,
      performance_gain=0.55, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Очень низкая стоимость в рантайме", "Предсказуемый результат"],
      cons=["Меньше вариативности", "Худшая реакция на окружение"],
      limitations=["Плохо подходит для эффектов, зависящих от физики"],
      verification_method="Сравнение времени кадра и визуальная оценка эффекта.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_PARTICLES"),

    # =====================================================================
    # 8. Физическая симуляция
    # =====================================================================
    M("fixed_timestep_physics", "Фиксированный шаг физики с интерполяцией",
      "physics_simulation",
      summary="Физика обновляется с постоянным шагом, визуальное состояние интерполируется по времени.",
      description="Фиксированный шаг делает симуляцию воспроизводимой и стабильной при любом FPS; "
                  "визуальные трансформации интерполируются между шагами.",
      problem="Переменный шаг физики приводит к нестабильности и рассинхронизации в сети.",
      level="architecture", recommended_stage="prototype", late_cost="critical",
      performance_gain=0.35, implementation_cost=3, complexity=3, confidence=0.9,
      calc_mode="hybrid",
      pros=["Стабильность и воспроизводимость", "Обязательно для сетевой игры"],
      cons=["Сложно внедрить в готовый проект", "Добавляет задержку в один шаг"],
      limitations=["Требует интерполяции визуального состояния"],
      verification_method="Проверка воспроизводимости: одинаковая последовательность входов даёт одинаковый результат.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="GODOT_PHYSICS"),

    M("physics_lod_sleeping", "LOD физики и спящие тела",
      "physics_simulation",
      summary="Далёкие и покоящиеся тела переводятся в упрощённый режим или исключаются из симуляции.",
      description="Для удалённых объектов используются упрощённые коллайдеры и пониженная частота "
                  "обновления; покоящиеся тела засыпают и не тратят время до внешнего воздействия.",
      problem="Полная симуляция всех тел сцены тратит время CPU впустую.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=-2, quality_impact=-1,
      performance_gain=0.6, implementation_cost=2, complexity=2, confidence=0.9,
      pros=["Большой эффект при минимальной стоимости", "Практически не влияет на геймплей"],
      cons=["Возможны артефакты при выходе из спячки"],
      limitations=["Требует настройки порогов"],
      verification_method="Замер времени физики и проверка корректности пробуждения объектов.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="UE_CHAOS"),

    M("multithreaded_physics_jobs", "Многопоточная физика на системе задач",
      "physics_simulation",
      summary="Шаг физики распараллеливается на несколько потоков с контролем зависимостей.",
      description="Расчёт широкой фазы, решение контактов и интеграция распределяются по потокам; "
                  "результат собирается перед рендером.",
      problem="Однопоточная физика становится узким местом при росте числа тел.",
      level="architecture", recommended_stage="prototype", late_cost="high",
      impact_cpu=-2,
      performance_gain=0.65, implementation_cost=4, complexity=4, confidence=0.7,
      pros=["Практически линейное ускорение на многих ядрах", "Снимает узкое место CPU"],
      cons=["Требует детерминированного шага", "Сложно отлаживать состояния гонки"],
      limitations=["Эффект зависит от числа доступных ядер"],
      requires_prototype=True,
      verification_method="Замер времени шага физики при разном числе задействованных потоков.",
      verification_tools=["Unity Profiler", "Unreal Insights"],
      source_key="UNITY_JOBS"),

    M("broadphase_spatial_partitioning", "Оптимизация широкой фазы (BVH / spatial hash)",
      "physics_simulation",
      summary="Поиск потенциально сталкивающихся пар ускоряется пространственной структурой.",
      description="Вместо перебора всех пар используется иерархия ограничивающих объёмов или "
                  "пространственное хеширование, снижая сложность с квадратичной до почти линейной.",
      problem="Перебор всех пар тел квадратично растёт с ростом сцены.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_cpu=-2, impact_ram=1,
      performance_gain=0.6, implementation_cost=3, complexity=3, confidence=0.8,
      pros=["Сильно снижает стоимость широкой фазы", "Хорошо масштабируется"],
      cons=["Требует поддержки структуры при изменении сцены"],
      limitations=["Меньший эффект при малом числе тел"],
      verification_method="Замер времени широкой фазы при росте числа тел.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_BVH"),

    # =====================================================================
    # 9. Анимация персонажей
    # =====================================================================
    M("gpu_skinning_compute", "Скиннинг на GPU",
      "character_animation",
      summary="Преобразование вершин по костям выполняется на GPU вместо CPU.",
      description="Позы рассчитываются на CPU, а преобразование вершин переносится в шейдер "
                  "или вычислительный проход, снимая существенную нагрузку с CPU и памяти.",
      problem="Скиннинг на CPU ограничивает число анимированных персонажей.",
      level="architecture", recommended_stage="prototype", late_cost="high",
      impact_cpu=-2, impact_gpu=1,
      performance_gain=0.7, implementation_cost=4, complexity=4, confidence=0.75,
      pros=["Резко снижает стоимость анимации на CPU", "Позволяет много персонажей в кадре"],
      cons=["Требует переработки конвейера анимации", "Усложняет чтение позы на CPU"],
      limitations=["Поза на CPU доступна с задержкой"],
      requires_prototype=True,
      verification_method="Замер времени CPU на анимацию при максимальном числе персонажей.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_SKINNING"),

    M("animation_compression", "Сжатие анимационных данных",
      "character_animation",
      summary="Кривые анимации квантуются и упаковываются, снижая объём данных и трафика памяти.",
      description="Ключевые кадры прореживаются и квантуются, каналы с малой амплитудой "
                  "отбрасываются. Экономит память и дисковое пространство ценой точности.",
      problem="Анимации занимают значительную часть памяти и размера сборки.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=1, impact_ram=-2, impact_disk=-2,
      quality_impact=-1,
      performance_gain=0.4, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Заметно снижает память и размер сборки", "Легко внедрить"],
      cons=["Возможны артефакты при сильном сжатии"],
      limitations=["Требует подбора порогов по ассетам"],
      verification_method="Сравнение объёма памяти и визуальная проверка анимаций.",
      verification_tools=["Unity Profiler"],
      source_key="WIKI_SKINNING"),

    M("animation_lod_budget", "LOD анимации и бюджет обновлений",
      "character_animation",
      summary="Частота и детализация обновления анимации снижаются для далёких и второстепенных персонажей.",
      description="Для удалённых персонажей отключаются IK, лицевая анимация и обновление позы "
                  "происходит реже; бюджет времени распределяется между значимыми персонажами.",
      problem="Полная анимация всех персонажей тратит бюджет времени впустую.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=-2, quality_impact=-1,
      performance_gain=0.6, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Большой эффект при низкой стоимости", "Гибко настраивается"],
      cons=["Заметно на средней дистанции"],
      limitations=["Требует настройки порогов дистанции"],
      verification_method="Замер времени анимации при заполненной сцене и визуальная оценка дальних NPC.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_ANIMBUDGET"),

    M("motion_matching", "Motion matching",
      "character_animation",
      summary="Следующий фрагмент движения выбирается поиском по базе записанных анимаций.",
      description="Вместо построенного вручную графа переходов система каждую итерацию ищет в базе "
                  "движений фрагмент, лучше всего продолжающий текущее состояние и желаемую траекторию.",
      problem="Ручное построение графов переходов не масштабируется и даёт эффект скольжения.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_cpu=2, impact_ram=2, quality_impact=2,
      performance_gain=0.0, implementation_cost=5, complexity=5, confidence=0.6,
      requires_prototype=True,
      pros=["Заметно выше качество движения", "Меньше ручной работы над переходами"],
      cons=["Высокая стоимость CPU и памяти", "Требует большой базы движений"],
      limitations=["Трудно вписать в бюджет слабого оборудования"],
      verification_method="Замер времени поиска и объёма памяти базы движений.",
      verification_tools=["Unity Profiler"],
      source_key="WIKI_IK"),

    # =====================================================================
    # 10. Толпы NPC
    # =====================================================================
    M("ecs_data_oriented_crowd", "Толпа на ECS / Data-Oriented архитектуре",
      "crowd_simulation",
      summary="Данные агентов хранятся в плотных массивах, обработка ведётся системами над компонентами.",
      description="Переход от объектной модели к сущностям и компонентам с плотной упаковкой данных "
                  "даёт высокую локальность кэша и распараллеливание обновления агентов.",
      problem="Объектная модель с виртуальными вызовами и разрозненной памятью не масштабируется на тысячи NPC.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=-2, impact_ram=-1,
      performance_gain=0.8, implementation_cost=5, complexity=5, confidence=0.7,
      min_scale="medium",
      pros=["Максимальная масштабируемость", "Удобное распараллеливание"],
      cons=["Требует переработки архитектуры", "Высокая стоимость перехода на поздних стадиях"],
      limitations=["Сложно встроить в уже готовый объектный код"],
      requires_prototype=True,
      verification_method="Замер времени обновления агентов при росте их числа до целевого.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_ECS"),

    M("crowd_instancing_impostors", "Инстансинг и импосторы для толпы",
      "crowd_simulation",
      summary="Персонажи толпы рисуются инстансингом, дальние заменяются упрощёнными представлениями.",
      description="Отрисовка толпы сводится к инстансированному рендеру с LOD-цепочками, "
                  "а самые далёкие персонажи заменяются билбордами.",
      problem="Отрисовка сотен персонажей перегружает CPU вызовами и GPU геометрией.",
      level="production", recommended_stage="production", late_cost="medium",
      impact_cpu=-1, impact_gpu=-2, impact_vram=-1, quality_impact=-1,
      performance_gain=0.7, implementation_cost=3, complexity=3, confidence=0.8,
      min_scale="medium",
      pros=["Резко снижает стоимость отрисовки толпы", "Хорошо масштабируется"],
      cons=["Требует LOD-цепочек для персонажей", "Потери качества на дистанции"],
      limitations=["Заметно при быстром приближении камеры"],
      verification_method="Замер числа вызовов отрисовки и времени GPU при максимальной толпе.",
      verification_tools=["Unity Profiler", "Unreal Insights"],
      source_key="UE_MASS"),

    M("agent_update_budget", "Распределение бюджета обновлений агентов",
      "crowd_simulation",
      summary="Агенты обновляются по приоритету: значимые — каждый кадр, остальные — по очереди.",
      description="Каждый кадр обновляется ограниченное число агентов, выбранных по важности "
                  "(дистанция, видимость, сюжетная роль). Остальные обновляются реже.",
      problem="Обновление всех агентов каждый кадр не укладывается в бюджет времени.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=-2, quality_impact=-1,
      performance_gain=0.65, implementation_cost=2, complexity=2, confidence=0.85,
      min_scale="medium",
      pros=["Гибкий контроль бюджета", "Низкая стоимость внедрения"],
      cons=["Удалённые агенты реагируют с задержкой"],
      limitations=["Требует аккуратной настройки приоритетов"],
      verification_method="Замер времени обновления агентов и проверка реакции ближайших NPC.",
      verification_tools=["Unity Profiler", "Unreal Insights"],
      source_key="UE_SIGNIFICANCE"),

    # =====================================================================
    # 11. ИИ и поиск пути
    # =====================================================================
    M("navmesh_tiling_streaming", "Тайловая навмеш со стримингом",
      "ai_pathfinding",
      summary="Навигационная сетка строится и подгружается отдельными тайлами вместе с миром.",
      description="Навмеш разбивается на тайлы, которые генерируются заранее или в рантайме "
                  "и подгружаются/выгружаются вместе с ячейками мира.",
      problem="Единая навмеш на большой мир не помещается в память и долго пересобирается.",
      level="architecture", recommended_stage="prototype", late_cost="high",
      impact_cpu=-1, impact_ram=-1, impact_disk=1,
      performance_gain=0.6, implementation_cost=4, complexity=4, confidence=0.75,
      min_scale="medium",
      pros=["Масштабируется на большой мир", "Позволяет перестраивать только изменённые тайлы"],
      cons=["Требует стыковки тайлов", "Сложнее отлаживать"],
      limitations=["Требует поддержки со стороны системы навигации"],
      requires_prototype=True,
      verification_method="Замер памяти на навигационные данные и времени пересборки тайла.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_NAVMESH"),

    M("time_sliced_pathfinding", "Поиск пути с распределением по кадрам",
      "ai_pathfinding",
      summary="Запросы на поиск пути ставятся в очередь с ограничением числа запросов на кадр.",
      description="Вместо выполнения всех запросов в кадре поиск распределяется по времени "
                  "с приоритизацией; агент начинает движение по предыдущему пути.",
      problem="Пиковая нагрузка на поиск пути вызывает просадки FPS.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_cpu=-1,
      performance_gain=0.5, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Сглаживает пики нагрузки", "Просто внедрить"],
      cons=["Путь доступен не сразу", "Требует обработки задержки"],
      limitations=["Не снижает суммарную нагрузку"],
      verification_method="Замер максимального времени кадра при массовой постановке запросов.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_NAVMESH"),

    M("flow_field_pathing", "Поле направлений (flow field)",
      "ai_pathfinding",
      summary="Для группы агентов один раз строится поле направлений к цели, дальше агенты движутся по нему.",
      description="Вместо индивидуального пути для каждого агента строится векторное поле, "
                  "общее для всей группы; стоимость не зависит от числа агентов.",
      problem="Индивидуальный поиск пути для сотен агентов слишком дорог.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_cpu=-2, impact_ram=1, quality_impact=-1,
      performance_gain=0.7, implementation_cost=3, complexity=3, confidence=0.7,
      min_scale="medium",
      pros=["Стоимость не зависит от числа агентов", "Естественное поведение толпы"],
      cons=["Менее точные индивидуальные траектории", "Одно поле на общую цель"],
      limitations=["Плохо подходит для агентов с разными целями"],
      requires_prototype=True,
      verification_method="Замер времени навигации при росте числа агентов.",
      verification_tools=["Unity Profiler"],
      source_key="WIKI_NAVMESH"),

    # =====================================================================
    # 12. Водные поверхности
    # =====================================================================
    M("gerstner_fft_water", "Волны Герстнера и FFT на GPU",
      "water_simulation",
      summary="Поверхность воды строится суммой волновых функций и спектра, вычисляемых на GPU.",
      description="Геометрия и нормали воды рассчитываются в шейдере по набору волн Герстнера "
                  "или по спектру, полученному быстрым преобразованием Фурье.",
      problem="Качественная вода с реальной геометрией волн дорога для CPU.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_cpu=-1, impact_gpu=1, quality_impact=1,
      performance_gain=0.4, implementation_cost=3, complexity=4, confidence=0.75,
      requires_hw_features=["Compute Shaders"],
      pros=["Высокое качество воды", "Геометрия волн почти бесплатна для CPU"],
      cons=["Заметная стоимость GPU", "Сложная настройка спектра"],
      limitations=["Требует вычислительных шейдеров для FFT"],
      requires_prototype=True,
      verification_method="Замер времени расчёта и обновления поверхности воды.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_GERSTNER"),

    M("screen_space_water_simple", "Упрощённая вода в экранном пространстве",
      "water_simulation",
      summary="Вода реализуется плоской поверхностью с шейдерными эффектами без сложной симуляции.",
      description="Поверхность остаётся плоской, а впечатление волн создаётся нормалями, "
                  "отражениями и преломлением по буферу глубины.",
      problem="Полноценная симуляция воды не вписывается в бюджет проекта или оборудования.",
      level="algorithm", recommended_stage="prototype", late_cost="low",
      impact_gpu=-2, impact_vram=-1, quality_impact=-1, concept_impact=-1,
      performance_gain=0.7, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Очень низкая стоимость", "Предсказуемый результат"],
      cons=["Менее выразительная вода", "Ограничения на взаимодействие"],
      limitations=["Меняет визуальную концепцию водоёмов"],
      verification_method="Замер времени рендера воды и визуальная оценка.",
      verification_tools=["Профилировщик Godot", "Unity Profiler"],
      source_key="WIKI_GERSTNER"),

    # =====================================================================
    # 13. Объёмные эффекты
    # =====================================================================
    M("froxel_volumetric_fog", "Объёмный туман на froxel-сетке",
      "volumetric_effects",
      summary="Среда разбивается на объёмные ячейки (froxel), в которых оценивается рассеивание света.",
      description="Пирамида видимости разбивается на трёхмерную сетку; в каждой ячейке рассчитывается "
                  "плотность среды и освещённость, затем результат интегрируется вдоль луча.",
      problem="Плоский туман не даёт световых лучей и объёмности освещения.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_gpu=1, impact_vram=1, quality_impact=1,
      performance_gain=0.35, implementation_cost=3, complexity=4, confidence=0.75,
      pros=["Выразительное освещение среды", "Хорошо сочетается с динамическим светом"],
      cons=["Заметная стоимость GPU", "Требует настройки разрешения сетки"],
      limitations=["Трудно вписать в бюджет слабых GPU"],
      requires_prototype=True,
      verification_method="Замер времени прохода объёмов при разном разрешении сетки.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_VOLUMETRIC"),

    M("volumetric_half_resolution", "Расчёт объёмов в пониженном разрешении",
      "volumetric_effects",
      summary="Объёмные эффекты рассчитываются в половинном или четвертном разрешении и масштабируются.",
      description="Стоимость объёмов снижается пропорционально квадрату разрешения; результат "
                  "размывается временным накоплением.",
      problem="Объёмные эффекты в полном разрешении слишком дороги.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=-2, quality_impact=-1,
      performance_gain=0.6, implementation_cost=1, complexity=2, confidence=0.9,
      pros=["Очень низкая стоимость внедрения", "Заметный выигрыш"],
      cons=["Потеря детализации", "Возможны артефакты размытия"],
      limitations=["Требует качественной временной перепроекции"],
      verification_method="Замер времени GPU и сравнение качества при разном разрешении.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_VOLUMETRIC"),

    # =====================================================================
    # 14. Постобработка изображения
    # =====================================================================
    M("temporal_upscaling", "Временное масштабирование изображения",
      "post_processing",
      summary="Кадр рендерится в пониженном разрешении и восстанавливается с использованием истории кадров.",
      description="Информация предыдущих кадров перепроецируется и объединяется с текущим, "
                  "позволяя получить изображение, близкое к нативному разрешению, при существенно "
                  "меньшей стоимости рендера.",
      problem="Рендер в целевом разрешении не укладывается в бюджет GPU.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=-2, impact_vram=1, quality_impact=-1,
      performance_gain=0.75, implementation_cost=2, complexity=2, confidence=0.9,
      pros=["Один из самых выгодных методов по эффекту на единицу затрат", "Не требует переработки контента"],
      cons=["Потеря резкости и артефакты на движущихся объектах"],
      limitations=["Требует качественных векторов движения", "Тонкая геометрия и растительность дают гоустинг и мыльный эффект; трансформерные модели стабильнее CNN"],
      verification_method="Сравнение времени GPU и визуальной резкости при разных коэффициентах масштабирования.",
      verification_tools=["Unity Profiler", "Unreal Insights", "Профилировщик Godot"],
      source_key="WIKI_FSR"),

    M("dynamic_resolution_scaling", "Динамическое разрешение рендера",
      "post_processing",
      summary="Разрешение рендера автоматически меняется для удержания целевого времени кадра.",
      description="При превышении бюджета кадра разрешение снижается, при запасе — повышается. "
                  "Позволяет удерживать целевой FPS на разнообразном оборудовании.",
      problem="Фиксированное разрешение даёт либо просадки, либо неиспользуемый запас.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=-2, quality_impact=-1,
      performance_gain=0.7, implementation_cost=2, complexity=2, confidence=0.9,
      pros=["Автоматически удерживает целевой FPS", "Не требует переработки контента"],
      cons=["Заметные колебания резкости", "Требует аккуратной настройки порогов"],
      limitations=["Не решает проблему пиковой нагрузки на CPU"],
      verification_method="Проверка удержания целевого FPS на минимальной конфигурации.",
      verification_tools=["Unity Profiler", "Unreal Insights", "Профилировщик Godot"],
      source_key="UNITY_QUALITY"),

    M("deferred_forward_plus_choice", "Выбор архитектуры рендера (deferred / forward+)",
      "post_processing",
      summary="Архитектура рендера выбирается под ожидаемую сцену: отложенное затенение или forward+ с кластеризацией.",
      description="Отложенное затенение выгодно при большом числе динамических источников света, "
                  "forward+ — при прозрачности, сглаживании и ограниченном бюджете памяти.",
      problem="Неверно выбранная архитектура рендера ограничивает проект на всей его протяжённости.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_gpu=-1, impact_vram=2,
      performance_gain=0.5, implementation_cost=4, complexity=4, confidence=0.8,
      pros=["Определяет потолок производительности проекта", "Влияет на все последующие решения"],
      cons=["Смена архитектуры на поздней стадии крайне дорога"],
      limitations=["Выбор зависит от числа источников света и прозрачности"],
      requires_prototype=True,
      verification_method="Сравнительный тест двух архитектур на эталонной сцене с целевым числом источников.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_DEFERRED"),

    M("variable_rate_shading", "Переменная частота затенения (VRS)",
      "post_processing",
      summary="Частота вызова пиксельного шейдера снижается в областях с малой детализацией.",
      description="Разные области кадра затеняются с разной частотой: центр изображения — полно, "
                  "периферия и размытые зоны — с пониженной.",
      problem="Пиксельный шейдер доминирует в стоимости кадра при высокой детализации материалов.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=-2, quality_impact=-1,
      performance_gain=0.5, implementation_cost=3, complexity=3, confidence=0.65,
      requires_hw_features=["Variable Rate Shading"],
      applicable_platforms=["pc_windows", "xbox_series", "ps5"],
      pros=["Заметный выигрыш при малых усилиях", "Не требует переработки контента"],
      cons=["Ограниченная поддержка оборудования", "Требует генерации маски затенения"],
      limitations=["Не поддерживается на старых GPU и части консолей"],
      requires_prototype=True,
      verification_method="Замер времени GPU и визуальная проверка на границах зон.",
      verification_tools=["Unreal Insights"],
      source_key="WIKI_TAA"),

    # =====================================================================
    # 15. Сетевой код мультиплеера
    # =====================================================================
    M("network_relevancy_priority", "Сетевая релевантность и приоритизация",
      "multiplayer_netcode",
      summary="Клиенту передаются только значимые для него объекты, с расстановкой приоритетов.",
      description="Для каждого клиента определяется набор релевантных объектов и частота обновления "
                  "по дистанции и важности; остальное не передаётся или передаётся редко.",
      problem="Полная репликация всех объектов не укладывается в пропускную способность и бюджет CPU.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=-1, impact_network=-2,
      performance_gain=0.7, implementation_cost=4, complexity=4, confidence=0.8,
      requires_features=["multiplayer_netcode"],
      pros=["Кратное снижение сетевого трафика", "Основа масштабируемого мультиплеера"],
      cons=["Сложно внедрить в готовый проект", "Требует проектирования с самого начала"],
      limitations=["Требует чётких правил релевантности"],
      requires_prototype=True,
      verification_method="Замер трафика и времени сетевого обновления при целевом числе игроков.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_REPGRAPH"),

    M("client_prediction_reconciliation", "Предсказание на клиенте и реконсиляция",
      "multiplayer_netcode",
      summary="Клиент немедленно применяет ввод локально, затем сверяет результат с сервером.",
      description="Локальный персонаж двигается сразу по вводу игрока, сервер подтверждает состояние; "
                  "при расхождении производится пересчёт и плавная коррекция.",
      problem="Ожидание ответа сервера делает управление становится неотзывчивым при задержке сети.",
      level="architecture", recommended_stage="prototype", late_cost="critical",
      impact_cpu=1, impact_network=-1, quality_impact=1,
      performance_gain=0.3, implementation_cost=5, complexity=5, confidence=0.75,
      requires_features=["multiplayer_netcode"],
      requires_prototype=True,
      pros=["Управление остаётся отзывчивым при задержке", "Стандарт для сетевых экшен-игр"],
      cons=["Очень высокая сложность", "Требует детерминированной симуляции"],
      limitations=["Почти невозможно внедрить после релиза"],
      verification_method="Тест с искусственной задержкой и потерями пакетов; контроль корректности коррекции.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_PREDICTION"),

    M("delta_compression_state", "Дельта-компрессия сетевого состояния",
      "multiplayer_netcode",
      summary="Передаётся только разница между последним подтверждённым и текущим состоянием.",
      description="Вместо полного состояния объекта передаются изменения относительно基线, "
                  "известной получателю, что кратно снижает объём пакетов.",
      problem="Полное состояние объектов требует избыточной пропускной способности.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_cpu=1, impact_network=-2,
      performance_gain=0.55, implementation_cost=3, complexity=3, confidence=0.75,
      requires_features=["multiplayer_netcode"],
      pros=["Кратное снижение трафика", "Хорошо сочетается с релевантностью"],
      cons=["Требует надёжной схемы подтверждения", "Добавляет стоимость CPU"],
      limitations=["Эффект зависит от частоты изменений состояния"],
      verification_method="Замер объёма трафика до и после внедрения.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_DELTA"),

    M("headless_dedicated_server", "Выделенный сервер без графики",
      "multiplayer_netcode",
      summary="Серверная сборка исключает рендер, звук и ввод, оставляя только симуляцию.",
      description="Серверный исполняемый файл работает без графического контекста, что снижает "
                  "нагрузку на машину сервера и упрощает масштабирование.",
      problem="Сервер, запущенный клиентской сборкой, тратит ресурсы на рендер и звук.",
      level="production", recommended_stage="production", late_cost="high",
      impact_cpu=-2, impact_gpu=-2, impact_ram=-1,
      performance_gain=0.6, implementation_cost=3, complexity=3, confidence=0.8,
      requires_features=["multiplayer_netcode"],
      pros=["Существенно дешевле эксплуатация", "Повышает стабильность сервера"],
      cons=["Требует отдельной сборки иpipeline", "Усложняет отладку"],
      limitations=["Требует отделения серверной логики от клиентской"],
      verification_method="Замер потребления ресурсов сервером на целевом числе игроков.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UE_NETWORKING"),
]

# ---------------------------------------------------------------------------
# Расширение применимости существующих методов.
#
# Каталог изначально создавался вокруг трёхмерных проектов, однако ряд
# решений по своей сути не зависит от размерности: пулинг объектов,
# бюджет обновлений, сжатие состояния, сетевая релевантность, поиск пути.
# Ниже эти решения явно распространяются на 2D и 2.5D, а методы, работающие
# с трёхмерным рендером, — на 2.5D, где используется тот же конвейер.
# Таблица изменяется администратором без правки кода.
# ---------------------------------------------------------------------------
FORMAT_OVERRIDES: dict[str, list[str]] = {
    # Методы, не зависящие от размерности изображения.
    "particle_pooling": ["3D", "2.5D", "2D"],
    "flipbook_particles": ["3D", "2.5D", "2D"],
    "animation_compression": ["3D", "2.5D", "2D"],
    "animation_lod_budget": ["3D", "2.5D", "2D"],
    "physics_lod_sleeping": ["3D", "2.5D", "2D"],
    "broadphase_spatial_partitioning": ["3D", "2.5D", "2D"],
    "agent_update_budget": ["3D", "2.5D", "2D"],
    "time_sliced_pathfinding": ["3D", "2.5D", "2D"],
    "network_relevancy_priority": ["3D", "2.5D", "2D"],
    "delta_compression_state": ["3D", "2.5D", "2D"],
    "client_prediction_reconciliation": ["3D", "2.5D", "2D"],
    "fixed_timestep_physics": ["3D", "2.5D", "2D"],
    "headless_dedicated_server": ["3D", "2.5D", "2D"],
    "collision_layer_matrix": ["3D", "2.5D", "2D"],
    "ecs_data_oriented_crowd": ["3D", "2.5D", "2D"],
    # Методы трёхмерного рендера, применимые и к 2.5D (тот же конвейер).
    "hierarchical_lod": ["3D", "2.5D"],
    "gpu_compute_culling": ["3D", "2.5D"],
    "baked_occlusion_culling": ["3D", "2.5D"],
    "screen_space_gi": ["3D", "2.5D"],
    "temporal_radiance_cache": ["3D", "2.5D"],
    "gpu_lightmap_baking": ["3D", "2.5D"],
    "lightmap_compression_streaming": ["3D", "2.5D"],
    "screen_space_contact_shadows": ["3D", "2.5D"],
    "temporal_upscaling": ["3D", "2.5D"],
    "dynamic_resolution_scaling": ["3D", "2.5D"],
    "variable_rate_shading": ["3D", "2.5D"],
    "deferred_forward_plus_choice": ["3D", "2.5D"],
    "volumetric_half_resolution": ["3D", "2.5D"],
    "depth_prepass_early_z": ["3D", "2.5D"],
    # Альтернативные методы: рендерные — 3D/2.5D, процессные — все форматы.
    "hiz_software_occlusion": ["3D", "2.5D"],
    "bindless_uber_shaders": ["3D"],
    "destruction_geometry_cache": ["3D"],
    "ml_frame_generation": ["3D", "2.5D"],
    "splitscreen_render_budget": ["3D", "2.5D"],
    "audio_occlusion_propagation": ["3D", "2.5D", "2D"],
    "pso_precaching_warmup": ["3D", "2.5D", "2D"],
    "deterministic_lockstep": ["3D", "2.5D", "2D"],
    "tickrate_budgeting": ["3D", "2.5D", "2D"],
    "quality_tier_scalability": ["3D", "2.5D", "2D"],
    # Сейвы не зависят от размерности картинки: Plague Inc: Evolved и
    # Geometry Dash (обе 2D) используют слотовые сейвы (подтверждено FULL225).
    # Дефолт M() — ["3D"], поэтому заданы явно.
    "snapshot_slot_saves": ["3D", "2.5D", "2D"],
    "async_incremental_saves": ["3D", "2.5D", "2D"],
}

# ---------------------------------------------------------------------------
# Влияние решений на исходную концепцию игры.
#
# Часть оптимизаций не только экономит ресурсы, но и накладывает ограничения
# на геймплей и визуальный замысел: запечённые тени исключают смену времени
# суток, спящая физика противоречит полностью интерактивному миру, а единые
# атласы агентов требуют однотипности юнитов. Такие решения должны быть
# помечены заранее, пока отказ от них ещё не требует переработки проекта.
# Шкала: 0 — концепция не затрагивается, -1 — затрагивается, -2 — существенно
# меняет замысел.
# ---------------------------------------------------------------------------
CONCEPT_IMPACT_OVERRIDES: dict[str, int] = {
    "baked_occlusion_culling": -1,     # требует преимущественно статичной геометрии
    "static_shadow_caching": -1,       # исключает полностью динамическое освещение
    "impostors_billboards": -1,        # дальние объекты перестают быть объёмными
    "flipbook_particles": -1,          # ограничивает вариативность эффектов
    "fixed_timestep_physics": -1,      # накладывает требования на игровую логику
    "gpu_procedural_placement": -1,    # теряется авторская расстановка объектов
    "virtual_geometry_clusters": -1,   # ограничивает деформацию и анимацию мешей
    "crowd_instancing_impostors": -1,  # дальняя толпа теряет индивидуальность
    "agent_update_budget": -1,         # далёкие агенты реагируют с задержкой
    "time_sliced_pathfinding": -1,     # путь пересчитывается не мгновенно
    "physics_lod_sleeping": -1,        # противоречит полностью интерактивному миру
    "collision_layer_matrix": -1,      # фиксирует допустимые взаимодействия
    "lightmap_2d_baking": -1,          # статичные источники нельзя перемещать
    "skeletal_2d_deform": -1,          # меняет стиль анимации
    "crowd_2d_instancing": -1,         # требует однотипности агентов
    "deterministic_lockstep": -1,      # диктует логику, RNG и общий тик
    "splitscreen_render_budget": -1,   # делит экран и режет информацию
    "destruction_geometry_cache": -1,  # запечённое нельзя менять интерактивно
}

# ---------------------------------------------------------------------------
# Методы, специфичные для 2D и 2.5D проектов.
# ---------------------------------------------------------------------------
EXTRA_METHODS: list[dict] = [
    M("sprite_atlas_batching", "Атласы спрайтов и пакетная отрисовка",
      "character_animation",
      summary="Кадры анимации и статичные спрайты объединяются в атласы, чтобы сцена собиралась "
              "минимальным числом вызовов отрисовки.",
      description="Каждый отдельный спрайт — это потенциальный вызов отрисовки и смена текстуры. "
                  "Объединение спрайтов в атласы и сортировка по материалам позволяют собирать "
                  "весь слой одним батчем. Для скелетной 2D-анимации в атлас упаковываются части тела.",
      problem="В 2D-сцене с тысячами спрайтов основным ограничением становится количество вызовов "
              "отрисовки и переключений текстур, а не число пикселей.",
      level="production", recommended_stage="preproduction", late_cost="high",
      calc_mode="precomputed",
      impact_cpu=-2, impact_gpu=-1, impact_ram=1, impact_vram=1,
      quality_impact=0,
      performance_gain=0.7, implementation_cost=2, complexity=2, confidence=0.9,
      applicable_formats=["2D", "2.5D"],
      pros=["Радикально снижает число вызовов отрисовки", "Упрощает контроль бюджета сцены"],
      cons=["Требует дисциплины подготовки ассетов", "Ограничен размер одного атласа"],
      limitations=["Атласы большего размера, чем поддерживаемый максимум, невозможны"],
      verification_method="Замер числа вызовов отрисовки в профилировщике до и после упаковки.",
      verification_tools=["Unity Profiler", "Профилировщик Godot", "Unreal Insights"],
      source_key="WIKI_ATLAS"),

    M("sprite_sheet_compression", "Сжатие листов спрайтов и мип-уровни",
      "character_animation",
      summary="Листы анимации хранятся в сжатых форматах с отключёнными лишними мип-уровнями.",
      description="Для 2D мип-уровни часто не нужны: спрайты выводятся в масштабе, близком к "
                  "оригинальному. Отключение мип-уровней экономит память и убирает размытие, "
                  "а сжатие с альфа-каналом уменьшает размер сборки и трафик подкачки.",
      problem="Несжатые листы анимации быстро занимают весь бюджет VRAM и размер сборки.",
      level="production", recommended_stage="production", late_cost="low",
      calc_mode="precomputed",
      impact_ram=-1, impact_vram=-2, impact_disk=-2,
      performance_gain=0.4, implementation_cost=1, complexity=1, confidence=0.85,
      applicable_formats=["2D", "2.5D"],
      pros=["Просто внедряется", "Снижает размер сборки и занимаемую память"],
      cons=["Несовместимо с произвольным масштабированием спрайтов"],
      limitations=["При сильном уменьшении спрайтов без мип-уровней появляется мерцание"],
      verification_method="Контроль занимаемой текстурной памяти в профилировщике и размера сборки.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_MIPMAP"),

    M("skeletal_2d_deform", "Скелетная 2D-анимация вместо покадровой",
      "character_animation",
      summary="Персонаж собирается из частей и деформируется костями: хранится скелет, "
              "а не тысячи кадров.",
      description="Покадровая анимация требует отдельного изображения на каждый кадр. Скелетная "
                  "2D-анимация хранит наборы частей и скелет, а промежуточные состояния "
                  "вычисляются в рантайме. Экономит память и даёт плавные переходы.",
      problem="Покадровая анимация десятков персонажей требует гигабайт текстурной памяти.",
      level="production", recommended_stage="preproduction", late_cost="high",
      impact_ram=-2, impact_vram=-2, impact_disk=-2, impact_cpu=1,
      performance_gain=0.55, implementation_cost=3, complexity=3, confidence=0.8,
      applicable_formats=["2D", "2.5D"],
      pros=["Кратко снижает объём анимационных данных", "Позволяет смешивать анимации"],
      cons=["Требует перестройки конвейера анимации", "Нагрузка на CPU при большом числе костей"],
      limitations=["Стиль «ломаной» мультипликации сложнее воспроизвести"],
      requires_prototype=True,
      verification_method="Сравнение занимаемой памяти и времени анимации на эталонной сцене.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_SKINNING"),

    M("tilemap_chunk_streaming", "Чанковая подгрузка тайловой карты",
      "open_world_streaming",
      summary="Большая 2D-карта разбивается на чанки, которые подгружаются и выгружаются вокруг игрока.",
      description="Тайловая карта разрезается на прямоугольные фрагменты фиксированного размера. "
                  "В памяти удерживаются только чанки в радиусе видимости, остальные выгружаются "
                  "или догружаются в фоновом потоке.",
      problem="Большой 2D-мир не помещается в память целиком и создаёт пики при загрузке.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=1, impact_ram=1, impact_disk=1,
      performance_gain=0.7, implementation_cost=4, complexity=4, confidence=0.85,
      applicable_formats=["2D", "2.5D"],
      # Метроидвании и хабовые 2D-игры тоже грузят карту чанками/комнатами
      # (Hollow Knight, Prince of Persia: The Lost Crown — подтверждено
      # калибровкой FULL225): ограничение только open/procedural/sandbox
      # ложно исключало их реальные решения. Список приведён к sibling-методу
      # tilemap_layer_culling, у которого hub/linear уже разрешены.
      applicable_world_types=["open_world", "procedural", "sandbox", "hub", "linear"],
      min_scale="medium",
      pros=["Снимает ограничение на размер 2D-мира", "Позволяет параллелить наполнение"],
      cons=["Требует переработки уже собранных уровней", "Возможны задержки подгрузки"],
      limitations=["Требует строгого контроля зависимостей данных"],
      verification_method="Профилирование пиков времени кадра при быстром перемещении по миру.",
      verification_tools=["Unity Profiler", "Профилировщик Godot", "Unreal Insights"],
      source_key="UNITY_ADDRESSABLES"),

    M("tilemap_layer_culling", "Отсечение слоёв и чанков тайловой карты",
      "procedural_vegetation",
      summary="Скрытые слои, невидимые чанки и полностью закрытые тайлы исключаются из отрисовки.",
      description="Тайловая карта состоит из слоёв и чанков. Часть из них перекрыта другими или "
                  "находится вне камеры. Отсечение по видимости камеры и по маске перекрытия "
                  "убирает лишние вызовы отрисовки без изменения внешнего вида.",
      problem="2D-мир рисует десятки слоёв, большая часть которых не видна игроку.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_cpu=-1, impact_gpu=-2,
      performance_gain=0.6, implementation_cost=2, complexity=2, confidence=0.85,
      applicable_formats=["2D", "2.5D"],
      applicable_world_types=["open_world", "procedural", "sandbox", "linear", "hub"],
      pros=["Просто реализуется", "Не влияет на внешний вид"],
      cons=["Требует аккуратной работы с сортировкой слоёв"],
      limitations=["Эффект минимален в сценах с одним слоем"],
      verification_method="Замер числа вызовов отрисовки и времени рендер-потока.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="GODOT_PERF"),

    M("sprite_particle_atlas", "Атласные частицы со сниженной точностью",
      "particle_systems",
      summary="Частицы берутся из одного атласа, а их число и точность обновления "
              "ограничиваются бюджетом.",
      description="В 2D эффекты собираются из спрайтов. Один атлас на эффект и жёсткий лимит "
                  "одновременно живых частиц позволяют удержать число вызовов отрисовки "
                  "и время обновления в бюджете кадра.",
      problem="Массовые 2D-эффекты быстро исчерпывают бюджет вызовов отрисовки и CPU.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=-1, impact_gpu=-1,
      quality_impact=-1,
      performance_gain=0.45, implementation_cost=1, complexity=1, confidence=0.8,
      applicable_formats=["2D", "2.5D"],
      pros=["Быстро настраивается", "Даёт предсказуемый бюджет"],
      cons=["Снижает плотность и выразительность эффектов"],
      limitations=["Не подходит для эффектов, критичных к внешнему виду"],
      verification_method="Замер времени обновления частиц и числа вызовов отрисовки.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_PARTICLES"),

    M("lightmap_2d_baking", "Запекание 2D-освещения в текстуры",
      "baked_lighting",
      summary="Свет статичных источников заранее записывается в текстуры освещения вместо "
              "расчёта каждый кадр.",
      description="Для статичных источников света освещение рассчитывается заранее и сохраняется "
                  "в текстуру, которая накладывается на сцену. В рантайме остаются только "
                  "динамические источники, что убирает основную часть расчёта.",
      problem="Множество динамических 2D-источников света пересчитывает освещение каждый кадр "
              "и быстро исчерпывает бюджет GPU.",
      level="production", recommended_stage="production", late_cost="medium",
      calc_mode="precomputed",
      impact_cpu=-1, impact_gpu=-2, impact_vram=1, impact_disk=1,
      performance_gain=0.65, implementation_cost=2, complexity=2, confidence=0.85,
      applicable_formats=["2D", "2.5D"],
      applicable_world_types=["linear", "hub", "arena", "open_world"],
      pros=["Убирает стоимость статичного освещения из кадра", "Позволяет использовать больше источников"],
      cons=["Статичные источники нельзя перемещать", "Требует пересборки при изменении уровня"],
      limitations=["Динамичные источники по-прежнему рассчитываются в рантайме"],
      verification_method="Сравнение времени кадра до и после запекания на эталонном уровне.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="UNITY_LIGHTMAPPER"),

    M("shadow_caster_2d_limits", "Ограничение 2D-отбрасывателей теней",
      "dynamic_shadows",
      summary="Число отбрасывающих тени объектов и разрешение теневой карты ограничиваются "
              "по значимости.",
      description="2D-тени пересчитываются для каждого источника и каждого отбрасывателя. "
                  "Ограничение числа отбрасывателей, дальности и разрешения удерживает стоимость "
                  "теней в рамках выделенного бюджета.",
      problem="2D-тени с большим числом отбрасывателей становятся основной статьёй расхода кадра.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_cpu=-1, impact_gpu=-1,
      quality_impact=-1,
      performance_gain=0.5, implementation_cost=1, complexity=1, confidence=0.8,
      applicable_formats=["2D", "2.5D"],
      pros=["Настраивается без переработки", "Предсказуемо снижает стоимость кадра"],
      cons=["Тени дальних или мелких объектов исчезают"],
      limitations=["Заметно на объектах, попадающих под порог отсечения"],
      verification_method="Замер времени кадра при максимальном числе источников на эталонной сцене.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="GODOT_LIGHTS"),

    M("crowd_2d_instancing", "Массовая отрисовка 2D-агентов одним батчем",
      "crowd_simulation",
      summary="Однотипные 2D-агенты выводятся инстансингом с общим атласом, а их обновление "
              "распределяется по кадрам.",
      description="Сотни однотипных юнитов или персонажей выводятся одним вызовом отрисовки из "
                  "общего атласа. Обновление логики распределяется между кадрами, поэтому стоимость "
                  "в каждом кадре остаётся постоянной.",
      problem="Большое количество 2D-агентов создаёт тысячи вызовов отрисовки и пики обновления.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_cpu=-2, impact_gpu=-1,
      performance_gain=0.7, implementation_cost=3, complexity=3, confidence=0.8,
      applicable_formats=["2D", "2.5D"],
      applicable_world_types=["open_world", "arena", "sandbox", "hub"],
      pros=["Позволяет выводить тысячи агентов", "Выравнивает нагрузку по кадрам"],
      cons=["Требует однотипности агентов", "Сложнее отлаживать"],
      limitations=["Индивидуальные материалы агентов ломают батчинг"],
      requires_prototype=True,
      verification_method="Замер числа вызовов отрисовки и времени обновления на сцене с целевым числом агентов.",
      verification_tools=["Unity Profiler", "Профилировщик Godot"],
      source_key="UNITY_INSTANCING"),

    M("collision_layer_matrix", "Матрица слоёв коллизий",
      "physics_simulation",
      summary="Явная матрица взаимодействия слоёв исключает проверки пар, которые никогда не сталкиваются.",
      description="Физический движок проверяет все пары объектов, если это не запрещено. Явная "
                  "матрица слоёв убирает заведомо ненужные пары: снаряды не сталкиваются друг "
                  "с другом, декорации не участвуют в коллизиях персонажей.",
      problem="Широкая фаза проверяет огромное число пар, большинство из которых заведомо "
              "не могут столкнуться.",
      level="setting", recommended_stage="preproduction", late_cost="medium",
      impact_cpu=-2,
      performance_gain=0.6, implementation_cost=1, complexity=1, confidence=0.9,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Практически не требует кода", "Даёт быстрый и заметный эффект"],
      cons=["Ошибка в матрице приводит к «прострелам» сквозь объекты"],
      limitations=["Требует аккуратного документирования назначения слоёв"],
      verification_method="Замер времени широкой фазы и числа проверяемых пар в профилировщике.",
      verification_tools=["Unity Profiler", "Профилировщик Godot", "Unreal Insights"],
      source_key="GODOT_PHYSICS"),

    M("post_effect_selective", "Выборочное применение экранных эффектов",
      "post_processing",
      summary="Дорогие экранные эффекты применяются не ко всему кадру, а к отдельным слоям "
              "или с пониженным разрешением.",
      description="Свечение, размытие и цветокоррекция стоят proportionally площади кадра. "
                  "Ограничение области действия эффекта или расчёт в половинном разрешении "
                  "снижает стоимость в несколько раз при минимальной потере качества.",
      problem="Полноэкранная постобработка занимает значительную часть кадра даже в простых сценах.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=-2,
      quality_impact=-1,
      performance_gain=0.55, implementation_cost=2, complexity=2, confidence=0.85,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Быстро внедряется", "Эффект заметен сразу"],
      cons=["Возможны артефакты на границах области действия"],
      limitations=["Не подходит для эффектов, требующих полного кадра"],
      verification_method="Замер времени проходов постобработки в профилировщике GPU.",
      verification_tools=["Unity Profiler", "Профилировщик Godot", "Unreal Insights"],
      source_key="UNITY_QUALITY"),

    M("depth_prepass_early_z", "Предварительный проход глубины (early-Z)",
      "post_processing",
      summary="Сначала строится буфер глубины, затем основной проход отсекает перекрытые фрагменты.",
      description="Порядок отрисовки «от ближнего к дальнему» либо предварительный проход глубины "
                  "позволяют отбросить перекрытые фрагменты до выполнения дорогих шейдеров.",
      problem="При неправильном порядке отрисовки один и тот же пиксель закрашивается многократно.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_gpu=-2,
      performance_gain=0.5, implementation_cost=2, complexity=2, confidence=0.75,
      applicable_formats=["3D", "2.5D"],
      pros=["Заметно снижает перерисовку", "Не требует изменения контента"],
      cons=["Дополнительный проход геометрии стоит времени"],
      limitations=["Эффект минимален при малой перерисовке"],
      verification_method="Замер overdraw в режиме визуализации перерисовки.",
      verification_tools=["Unreal Insights", "Unity Profiler", "Профилировщик Godot"],
      source_key="WIKI_HSR"),

    # =====================================================================
    # Альтернативные методы из исследований Треков 1–2: дополняют, а не
    # дублируют каталог. У каждого — полный паспорт: проблема, паспорт влияния,
    # алгоритм применения по шагам, проверка, источник, проекты (через примеры).
    # =====================================================================
    M("hiz_software_occlusion", "Программное отсечение по Hi-Z",
      None,
      summary="Невидимая геометрия отсекается до растеризации: строится пирамида глубины "
              "(Hi-Z), AABB объектов тестируются против неё, видимые складываются "
              "в indirect-буфер отрисовки.",
      description="Альтернатива аппаратному occlusion query и GPU-culling: упрощённая сцена "
                  "растеризуется в буфер глубины (часто кадр прошлого кадра), из него строится "
                  "mip-цепочка максимумов глубины. Тест бокса объекта против цепочки дёшев и "
                  "убирает целые инстансы до вершинного шейдера. Эталон — DOOM Eternal: "
                  "в кадре десятки миллионов треугольников, рисуется малая видимая часть.",
      problem="Невидимая геометрия проходит вершинные шейдеры и создаёт overdraw впустую.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_cpu=1, impact_gpu=-2,
      performance_gain=0.6, implementation_cost=3, complexity=4, confidence=0.75,
      applicable_formats=["3D", "2.5D"],
      pros=["Снимает и вершинную нагрузку, и overdraw", "Не требует RT-ядер"],
      cons=["Построение Hi-Z стоит CPU/compute каждый кадр", "Мелкие окклюдеры бесполезны"],
      limitations=["Требует retained-сцены и indirect-отрисовки", "Динамические окклюдеры обновляют пирамиду"],
      application_steps=[
          "Отрендерить упрощённую глубину (низкополигональные прокси или кадр N-1).",
          "Построить Hi-Z mip-цепочку максимумов глубины.",
          "Протестировать AABB инстансов против цепочки на CPU или в compute.",
          "Сложить прошедшие в indirect draw buffer.",
          "Отрендерить только видимые; сверить overdraw до и после.",
      ],
      verification_method="Сравнение overdraw и числа вызовов отрисовки до и после; захват кадра.",
      verification_tools=["RenderDoc", "Unreal Insights", "PIX"],
      source_key="WIKI_HSR"),

    M("pso_precaching_warmup", "Предкомпиляция и прогрев PSO",
      None,
      summary="Шейдерные конвейеры (PSO) собираются заранее и прогреваются до геймплея, "
              "а не в первом кадре с новым материалом — исчезает shader stutter.",
      description="Главный враг PC-релиза на UE5: заезд в новую World Partition-зону собирает "
                  "сотни PSO и роняет кадры. Решение — коллекция PSO (автосбор телеметрией "
                  "или ручной прогон), сохранение кэша, загрузка при старте и смене зоны, "
                  "асинхронная компиляция с приоритетом видимых зон. Не даёт FPS, даёт гладкость.",
      problem="Первая встреча с материалом останавливает кадр на компиляцию шейдера.",
      level="production", recommended_stage="prototype", late_cost="high",
      impact_cpu=1, impact_disk=1,
      performance_gain=0.45, implementation_cost=3, complexity=3, confidence=0.85,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Убирает главный hitch PC-версий", "Дешёвая относительно рефакторинга"],
      cons=["Увеличивает время первого запуска и размер кэша", "Кэш инвалидируется драйвером"],
      limitations=["Не лечит плохую оптимизацию сцены", "Требует прогона всего контента"],
      application_steps=[
          "Включить сбор PSO-коллекции (телеметрия игроков или ручной прогон зон).",
          "Сохранить precache в поставку и проверить его размер.",
          "Грузить кэш при старте и перед стримингом новой зоны.",
          "Включить асинхронную компиляцию с приоритетом видимых зон.",
          "Замерить hitch-метрику: кадры дольше 50 мс при первом обходе контента.",
      ],
      verification_method="Hitch-детект при первом обходе мира; трассировка загрузки и компиляции.",
      verification_tools=["Unreal Insights", "PIX"],
      source_key="UNITY_SHADERLOAD"),

    M("managed_gc_alloc_budget", "Нулевой бюджет аллокаций в горячем цикле",
      None,
      summary="Горячий цикл кадра работает без аллокаций в управляемой куче: пулы, "
              "переиспользуемые буферы, обновление по событию вместо опроса.",
      description="Каждая аллокация в Update — будущая пауза GC.Collect: сборщик останавливает "
                  "код на миллисекунды. Решение — бюджет 0 байт на кадр: вынос аллокаций "
                  "из циклов, пулы и переиспользуемые буферы, отказ от строк, массивов "
                  "и замыканий в горячем пути. Контролируется колонкой GC.Alloc профилировщика.",
      problem="Управляемые движки аллоцируют в куче каждый кадр: сборка мусора даёт "
              "периодические пики времени кадра.",
      level="production", recommended_stage="prototype", late_cost="medium",
      impact_cpu=-2, impact_ram=-1,
      performance_gain=0.5, implementation_cost=2, complexity=2, confidence=0.8,
      applicable_formats=["3D", "2.5D", "2D"],
      # Только управляемые рантаймы (Unity Mono/IL2CPP, Java-подобный custom):
      # в C++-движках управляемой кучи нет, рекомендовать там нечего.
      applicable_engines=["unity", "custom"],
      pros=["Убирает периодические пики GC", "Дешевле рефакторинга рендера"],
      cons=["Требует дисциплины всего кода", "Ошибки пулов дают утечки и stale-состояния"],
      limitations=["Не лечит тяжёлую логику кадра", "Замер только на целевом железе (Editor врёт)"],
      application_steps=[
          "Записать базовый прогон: кадры GC.Alloc и пики GC.Collect.",
          "Найти аллокации каждого кадра (строки, массивы из API, замыкания).",
          "Вынести аллокации из циклов, ввести пулы и переиспользуемые буферы.",
          "Перевести опросы на события (обновление только при изменении).",
          "Повторить замер: GC.Alloc — 0 байт на кадр в горячем цикле.",
      ],
      verification_method="Колонка GC.Alloc профилировщика: 0 байт на кадр; отсутствие пиков GC.Collect.",
      verification_tools=["Unity Profiler"],
      source_key="UNITY_GC_BEST_PRACTICES"),

    M("audio_occlusion_propagation", "Аудио-окклюзия лучами и HRTF",
      None,
      summary="Слышимость считается по геометрии: луч от источника к слушателю даёт "
              "заглушение по материалу, отдельно сухая и влажная составляющие, "
              "позиционирование — HRTF.",
      description="Звук как второй глаз (Hunt: Showdown): каждый эмиттер шлёт луч, плотность "
                  "материала из таблицы поверхностей даёт obstruction 0..1, single-ray считает "
                  "только dry, multi-ray отдельно dry и wet (occlusion). Дальние источники "
                  "считаются асинхронно, ближние — синхронно. Выстрел слышно за сотни метров "
                  "с направлением и преградой.",
      problem="Без окклюзии звук проходит сквозь стены и не даёт информации о позиции.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_cpu=1,
      quality_impact=1,
      performance_gain=0.3, implementation_cost=3, complexity=3, confidence=0.8,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Звук становится геймплейной механикой", "Дешевле графических эффектов"],
      cons=["Требует разметки материалов", "HRTF усреднённой головы заходит не всем"],
      limitations=["Нужен аудио-программист и R&D микса", "Реверб легко превратить в кашу"],
      application_steps=[
          "Разметить материалы поверхностей плотностью (таблица типа SurfaceTypes).",
          "Пускать луч от каждого эмиттера к слушателю, считать obstruction 0..1.",
          "Разделить dry (прямой) и wet (отражённый) тракты.",
          "Настроить аттенюацию по мощности источника и forced-окклюзию для подземелий.",
          "Проверить слепым тестом: дистанция слышимости и направление без картинки.",
      ],
      verification_method="Отладочная отрисовка лучей и затухания; слепой тест слышимости.",
      verification_tools=["CryAudio Debug", "Wwise Profiler"],
      source_key="HUNT_AUDIO"),

    M("destruction_geometry_cache", "Запечённые кэши разрушений",
      None,
      summary="Сложная анимация разрушений и органики симулируется офлайн и воспроизводится "
              "как поток вершинных кэшей — дешевле, чем считать скининг и физику в рантайме.",
      description="Альтернатива realtime-фрактуре: симуляция в Houdini запекается в Alembic-кэш, "
                  "сжимается с lookahead, стримится чанками и декомпрессится в рантайме. "
                  "Эталон — DOOM Eternal: органика, тентакли, ткань и катсцены идут кэшами. "
                  "Цена — память и невозможность интерактивно изменить запечённое.",
      problem="Скининг и симуляция сложной органики не укладываются в бюджет кадра.",
      level="production", recommended_stage="production", late_cost="medium",
      impact_cpu=-2, impact_ram=1, impact_vram=1, impact_disk=2,
      performance_gain=0.65, implementation_cost=4, complexity=4, confidence=0.7,
      requires_prototype=True,
      requires_features=["physics_simulation"],
      applicable_formats=["3D"],
      pros=["Сложнейшая анимация за фиксированную цену", "Детерминированный результат"],
      cons=["Гигабайты кэшей", "Нет интерактивности внутри кэша"],
      limitations=["Требуется Houdini-конвейер", "Вдаль нужен LOD кэша"],
      application_steps=[
          "Симулировать разрушение офлайн и зафиксировать lookdev.",
          "Запечь Alembic-кэш и сжать с lookahead-компрессией.",
          "Нарезать кэш чанками под стриминг уровня.",
          "Настроить декомпрессию в рантайме и бюджет памяти.",
          "Сверить ms playback против ms симуляции на эталонной сцене.",
      ],
      verification_method="Сравнение времени симуляции и воспроизведения; контроль размера кэша на диске.",
      verification_tools=["Unreal Insights"],
      source_key="DOOM_ETERNAL"),

    M("deterministic_lockstep", "Детерминированный lockstep",
      None,
      summary="По сети шлются только инпуты, симулируют все клиенты идентично: fixed-point, "
              "seeded RNG, контрольные суммы десинка. Состояние не передаётся вообще.",
      description="Рецепт RTS и файтингов на тонких каналах (StarCraft, Factorio): запрет float "
                  "и wall-clock в симуляции, фиксированный порядок итераций, детерминированный "
                  "рандом, input delay с turn buckets, rolling checksum. Трафик — сотни байт в "
                  "секунду вместо состояния сотен юнитов. Альтернатива снапшотам и предикту. "
                  "Цена — тотальная дисциплина кода и общий тик.",
      problem="Синхронизация состояния сотен сущностей не влезает в канал и CPU.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=1, impact_network=-2,
      performance_gain=0.7, implementation_cost=4, complexity=5, confidence=0.85,
      requires_prototype=True,
      requires_features=["multiplayer_netcode"],
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Минимальный трафик", "Реплей — килобайты сида и команд", "Кроссплей проще"],
      cons=["Самый медленный ПК тормозит всех", "Нет rejoin без снапшота", "Любой десинк — вылет"],
      limitations=["P2P светит всю карту (maphack)", "Мультитред только read-only"],
      application_steps=[
          "Запретить float и wall-clock в симуляции, перейти на fixed-point.",
          "Зафиксировать порядок итераций и seeded RNG.",
          "Ввести input delay и turn buckets под пинг.",
          "Добавить rolling checksum каждого тика и детект десинка.",
          "Прогнать demo дважды и сравнить checksum побайтово.",
      ],
      verification_method="Двойной прогон реплея с побайтовым сравнением; CRC каждого тика.",
      verification_tools=["Unreal Insights"],
      source_key="GAFFER_TIMESTEP"),

    M("quality_tier_scalability", "Тиры качества и scalability-группы",
      None,
      summary="Графика нарезается тирами (Low..Ultra) с per-platform overrides и адаптивным "
              "переключением по FPS и температуре — один билд покрывает бюджетник и флагман.",
      description="Процесс, а не эффект: замер min-spec, нарезка тиров (разрешение, тени, MSAA, "
                  "LOD bias, async upload, качество текстур), переопределения под платформы, "
                  "adaptive cap при росте variance (рваные 35-55 лучше зафиксировать на 30). "
                  "Проектировать под sustained 55-70% пика: троттлинг приходит через 2-5 минут, "
                  "а не на замере первой минуты.",
      problem="Один конфиг графики либо тормозит на слабом, либо не использует сильное железо.",
      level="setting", recommended_stage="prototype", late_cost="medium",
      performance_gain=0.5, implementation_cost=2, complexity=2, confidence=0.9,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Один билд на весь рынок", "Дешёвое внедрение", "Лечит троттлинг"],
      cons=["Требует device farm", "Комбинаторика тиров и платформ"],
      limitations=["Не заменяет оптимизацию сцены", "Арт-дирекшн должен заложить запас"],
      application_steps=[
          "Замерить min-spec и sustained-перф (не пик первой минуты).",
          "Нарезать тиры: разрешение, тени, MSAA, дистанции, LOD bias, текстуры.",
          "Задать per-platform overrides и adaptive cap по variance.",
          "Прогнать 3 тира устройств по 15+ минут с термозамером.",
          "Зафиксировать дефолтный тир под каждую платформу.",
      ],
      verification_method="Прогон на трёх тирах устройств от 15 минут; frametime-гистограммы.",
      verification_tools=["Unity Profiler", "Snapdragon Profiler"],
      source_key="UNITY_QUALITY"),

    M("ml_frame_generation", "ML-генерация кадров",
      None,
      summary="Синтез промежуточных кадров между реальными: воспринимаемый FPS растёт, "
              "реальный инпут-лаг — тоже. Допустима только от стабильных 60+ базовых.",
      description="Пара к апскейлу, не замена оптимизации: генератор дорисовывает кадры, "
                  "Reflex/XeLL обязателен, motion blur режется вдвое, в меню, кат-переходах "
                  "и competitive — выключена. Без Quality/Performance-режимов апскейла 4K Ultra "
                  "неиграбельна даже на топ-картах. Артефакты — shimmer на заборах и госты частиц.",
      problem="Апскейла не хватает до целевого FPS, а снижать настройки уже некуда.",
      level="setting", recommended_stage="production", late_cost="low",
      impact_gpu=1, impact_vram=1,
      quality_impact=-1,
      performance_gain=0.6, implementation_cost=2, complexity=2, confidence=0.75,
      requires_conditions=["Базовый FPS не ниже 60", "Не для competitive и меню"],
      applicable_formats=["3D", "2.5D"],
      pros=["Удвоение воспринимаемого FPS", "Спасает RT-режимы"],
      cons=["+лаг ввода", "Артефакты на тонкой динамике", "VRAM под буферы истории"],
      limitations=["Требует vendor-железо", "Не спасает неиграбельный base"],
      application_steps=[
          "Добиться стабильных 60+ базовых без генерации.",
          "Включить генерацию только в геймплее, выключить в меню и катсценах.",
          "Включить Reflex/XeLL и уполовинить motion blur.",
          "Проверить ICAT на статике и pan-through-fence.",
          "Замерить FrameView latency до и после.",
      ],
      verification_method="ICAT-сравнение и FrameView-замер задержки; slowed-video на shimmer.",
      verification_tools=["RenderDoc", "Nsight Graphics"],
      source_key="WIKI_DLSS"),

    M("splitscreen_render_budget", "Бюджетирование split-screen",
      None,
      summary="Два вьюпорта — двойные draw calls, тени и render targets: отдельные пресеты "
              "на 2p/3p, общие пост-эффекты, кастомный culling на две камеры.",
      description="Кооп на одном экране умножает нагрузку: 2x shadow cascades, 2x targets в VRAM. "
                  "Эталон — It Takes Two: агрессивные LOD и HLOD, половина пост-эффектов общая, "
                  "на 3p — один каскад, без vegetation и motion blur, скрытие detail-объектов. "
                  "Просесть нельзя ни в одной половине.",
      problem="Split-screen удваивает нагрузку, а бюджеты посчитаны на один вьюпорт.",
      level="production", recommended_stage="prototype", late_cost="high",
      impact_gpu=2, impact_ram=1, impact_vram=1,
      concept_impact=-1,
      performance_gain=0.5, implementation_cost=3, complexity=3, confidence=0.8,
      requires_features=["multiplayer_netcode"],
      applicable_formats=["3D", "2.5D"],
      pros=["Кооп-фишка без онлайна", "Дисциплинирует бюджеты всей игры"],
      cons=["2x нагрузка на слабом железе", "Половина экрана — половина информации"],
      limitations=["На base-консолях только 30fps", "Требует отдельных пресетов"],
      application_steps=[
          "Посчитать 2x/3x нагрузку: draws, тени, targets.",
          "Завести отдельные пресеты на 2p и 3p (каскады, vegetation, blur).",
          "Сделать пост-эффекты общими, culling — на две камеры.",
          "Спрятать detail-объекты и refraction на дополнительных вью.",
          "Прогнать stat unit отдельно по каждому вьюпорту.",
      ],
      verification_method="Замер thread-bound и времени кадра на каждый вьюпорт отдельно.",
      verification_tools=["Unreal Insights", "RenderDoc"],
      source_key="DF_ITTakesTWO"),

    M("tickrate_budgeting", "Бюджетирование серверного тикрейта",
      None,
      summary="Тикрейт как деньги: 20/30/64/128 Гц напрямую конвертируются в CPU, bandwidth "
              "и отзывчивость. Выбирается по жанру, а не по максимуму.",
      description="Математика: 128 Гц требует ~125 КБ/с upload и в разы больше CPU, чем 64; "
                  "20 Гц full-state при 50 мс пинга даёт лишь на 2 кадра больше, чем 60 Гц, "
                  "ценой x3 bandwidth. Правило: 30 Гц — кооп и MMO, 64 — матчмейкинг, "
                  "128 — только tournament. Сначала профайлить NetBroadcastTickTime, потом "
                  "поднимать тик.",
      problem="Высокий тикрейт поднимают вслепую и получают счёт за CPU и трафик.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=2, impact_network=2,
      performance_gain=0.6, implementation_cost=3, complexity=3, confidence=0.85,
      requires_features=["multiplayer_netcode"],
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Предсказуемая цена онлайна", "Отзывчивость там, где нужна"],
      cons=["Высокий тик виден в счетах за флот", "Два баланса под два тикрейта"],
      limitations=["Плохой канал высокий тик только ухудшает", "Rollback требует детерминизма"],
      application_steps=[
          "Замерить bandwidth тика и CPU симуляции на целевом онлайне.",
          "Выбрать тик по жанру: 30 кооп, 64 матчмейкинг, 128 tournament.",
          "Проверить upload клиентов под выбранный тик.",
          "Прогнать tick stability p50/p99 и desync-кейсы на матч.",
          "Зафиксировать тик до прототипа сети.",
      ],
      verification_method="Стабильность тика p50/p99, gunfire delay, packet loss по регионам.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="RIOT_TICK"),

    M("bindless_uber_shaders", "Bindless-ресурсы и uber-шейдеры",
      None,
      summary="Весь список текстур биндится один раз с доступом по индексу, сотни пермутаций "
              "схлопываются в few massive uber-shaders, draw calls мержатся compute-шейдером "
              "в indirect-буфер.",
      description="Альтернатива взрыву PSO: ~500 PSO вместо тысяч, десяток descriptor layouts, "
                  "динамический мерж draw calls в indirect index buffer, переиспользуемый для "
                  "depth prepass и lighting pass. Z-draw calls почти исчезают, нет wasted VS. "
                  "Эталон — DOOM Eternal: уровни вдвое больше, ассетов на порядок больше, 60fps "
                  "даже на base-консолях. Цена — сложность шейдерной инженерии.",
      problem="Смены состояния и тысячи пермутаций шейдеров съедают CPU и память.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_cpu=-2, impact_gpu=-1,
      performance_gain=0.7, implementation_cost=4, complexity=5, confidence=0.7,
      requires_hw_features=["Bindless Textures"],
      applicable_formats=["3D"],
      pros=["Исчезают function bottlenecks", "Агрессивный мерж геометрии возможен"],
      cons=["Требует современного API и железа", "Отладка мега-шейдеров тяжела"],
      limitations=["Мелкие indie-команды не потянут", "Инструменты захвата обязательны"],
      application_steps=[
          "Перевести материалы на bindless-дескрипторы с индексом.",
          "Схлопнуть пермутации в uber-шейдеры, зафиксировать ~500 PSO.",
          "Написать compute-мерж draw calls в indirect buffer.",
          "Переиспользовать буфер для depth prepass и lighting pass.",
          "Сверить число draws в захвате кадра до и после.",
      ],
      verification_method="Подсчёт draws и state changes в захвате кадра; дескрипторная статистика.",
      verification_tools=["RenderDoc", "PIX"],
      source_key="COENEN_DOOM"),

    # --- Пополнение по разборам субтитров и документации (2026) -------------
    M("mesh_index_optimization", "Оптимизация индексов меша (vertex cache / overdraw)",
      None,
      summary="Индексы переупорядочиваются под кэш вершин и овердроу, вершины квантуются: "
              "меньше вызовов вершинного шейдера и видеопамяти без потери качества.",
      description="Конвейер meshoptimizer, порядок важен: indexing → vertex cache → overdraw "
                  "(порог 1.05) → vertex fetch → quantization. Overdraw-оптимизацию пропускать "
                  "на мобильных tiled-GPU. Godot 4 генерирует LOD этой же библиотекой.",
      problem="Неупорядоченные индексы перегружают вершинный шейдер и раздувают видеопамять.",
      level="production", recommended_stage="prototype", late_cost="medium",
      impact_gpu=-1, impact_disk=-1,
      performance_gain=0.55, implementation_cost=2, complexity=3, confidence=0.8,
      applicable_formats=["3D", "2.5D"],
      pros=["Дешевле вершинный шейдер", "Меньше видеопамять"],
      cons=["Встраивается в ассет-пайплайн", "Нужен замер ACMR/ATVR"],
      limitations=["На tiled-GPU overdraw-проход не выгоден"],
      application_steps=[
          "Прогнать индексы через vertex cache optimization.",
          "Добавить overdraw-проход с порогом 1.05 (кроме мобильных).",
          "Включить квантование вершин и фильтрацию индексов.",
          "Сверить ACMR/ATVR и время кадра до и после.",
      ],
      verification_method="Метрики ACMR/ATVR через meshopt_analyze и замер времени кадра.",
      verification_tools=["Unreal Insights", "Unity Profiler", "RenderDoc"],
      source_key="MESHOPT"),

    M("neural_texture_compression", "Нейросжатие текстур",
      "large_scale_terrain",
      summary="Текстуры хранятся в нейронном виде: до 7 раз меньше видеопамяти при "
              "сохранении деталей; распаковка стоит производительности GPU.",
      description="Поверхности анализируются на схожие фрагменты и пересоздаются нейросетью "
                  "(RTX Neural Texture Compression). Дополняет виртуальное текстурирование, "
                  "а не заменяет его. Полная выгода только на GPU с нейроускорением.",
      problem="4K-наборы текстур не помещаются в бюджет видеопамяти.",
      level="production", recommended_stage="prototype", late_cost="medium",
      calc_mode="hybrid",
      impact_gpu=1, impact_vram=-2, impact_ram=-1, impact_disk=-1,
      performance_gain=0.55, implementation_cost=2, complexity=3, confidence=0.6,
      requires_prototype=True,
      pros=["Радикально меньше видеопамять", "Детали лучше классического сжатия"],
      cons=["Стоит GPU на распаковке", "Только новые видеокарты"],
      limitations=["Без нейроускорения выгода частичная", "Требует пережатия всех наборов"],
      application_steps=[
          "Выделить наборы, превышающие бюджет видеопамяти.",
          "Пережать пилотный набор и сверить артефакты.",
          "Включить в пайплайн виртуального текстурирования.",
          "Проверить на min-spec видеокарте из каталога.",
      ],
      verification_method="Замер занятой видеопамяти и времени кадра на пилотном наборе.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_DLSS"),

    M("planar_reflection_budget", "Бюджет плоских отражений",
      "water_simulation",
      summary="Зеркальные отражения рендерятся отдельным проходом: красиво, но сцена "
              "рисуется дважды. Бюджет и дистанция ограничивают цену.",
      description="Planar reflection даёт точное зеркало в отличие от экранного (SSR видит "
                  "только кадр), но требует повторного рендера. Правило: один planar-источник "
                  "на сцену, половинное разрешение, жёсткая дистанция отсечения.",
      problem="Зеркала и вода без бюджета удваивают нагрузку на GPU.",
      level="algorithm", recommended_stage="prototype", late_cost="high",
      impact_gpu=2, impact_cpu=1,
      performance_gain=0.35, implementation_cost=3, complexity=3, confidence=0.8,
      quality_impact=1,
      pros=["Точные отражения", "Предсказуемая цена при бюджете"],
      cons=["Двойной рендер сцены", "Поздняя замена затрагивает уровни"],
      limitations=["Больше одного источника — только по веской причине"],
      application_steps=[
          "Оставить один planar-источник на сцену.",
          "Поставить половинное разрешение и дистанцию отсечения.",
          "Сравнить с SSR-вариантом по кадру и качеству.",
          "Зафиксировать бюджет до наполнения уровней.",
      ],
      verification_method="Замер времени кадра с отражениями и без на контрольной точке.",
      verification_tools=["Unreal Insights", "Unity Profiler", "RenderDoc"],
      source_key="UE_LUMEN"),

    M("normal_bake_retopology_pipeline", "Запекание нормалей и ретопология",
      None,
      summary="Детали высокополигональной модели запекаются в normal map низкополигональной: "
              "затенения сохраняются, полигоны — нет.",
      description="Скульпт с миллионами полигонов переносится на игровую модель картой нормалей, "
                  "сетка чистится ретопологией. Классика для персонажей и пропсов: арт Souls-серии "
                  "держится на этом приёме.",
      problem="Высокополигональные модели напрямую не тянут целевой FPS.",
      level="production", recommended_stage="preproduction", late_cost="medium",
      calc_mode="precomputed",
      impact_gpu=-1, impact_vram=-1, impact_disk=-1,
      performance_gain=0.6, implementation_cost=2, complexity=2, confidence=0.85,
      applicable_formats=["3D", "2.5D"],
      pros=["Детали без полигонов", "Дешёвый и проверяемый пайплайн"],
      cons=["Требует DCC-навыков", "Артефакты швов при плохом UV"],
      limitations=["Не спасает плохую топологию анимаций"],
      application_steps=[
          "Довести скульпт до нужной детализации.",
          "Сделать ретопологию и развёртку.",
          "Запечь normal map и сверить швы.",
          "Проверить силуэт на дистанции LOD-переключений.",
      ],
      verification_method="Сравнение числа треугольников и времени кадра до и после.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="UNITY_GFX_PERF"),

    M("build_size_startup_budgets", "Бюджеты размера сборки и старта",
      None,
      summary="Вес сборки и время старта ограничиваются бюджетами: subset шрифтов, группы "
              "Addressables, выгрузка лишнего. Тяжёлая игра теряет игроков до геймплея.",
      description="Чем больше весит игра и дольше запускается, тем меньше людей доходит до "
                  "геймплея. Бюджеты: шрифты только нужными глифами, ассеты — группами с "
                  "приоритетами загрузки/выгрузки, старт — с экраном-заглушкой и порогом времени.",
      problem="Раздутая сборка и долгий старт срезают аудиторию на входе.",
      level="production", recommended_stage="prototype", late_cost="high",
      calc_mode="precomputed",
      impact_ram=-1, impact_disk=-2,
      performance_gain=0.5, implementation_cost=2, complexity=2, confidence=0.8,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Больше дошедших до геймплея", "Дешевле дистрибуция и патчи"],
      cons=["Требует дисциплины ассетов", "Поздняя чистка болезненна"],
      limitations=["Не ускоряет сам кадр, только вход в игру"],
      application_steps=[
          "Замерить вес по категориям и время холодного старта.",
          "Урезать шрифты до используемых глифов.",
          "Разложить ассеты по группам загрузки/выгрузки.",
          "Поставить порог старта и проверять на каждый релиз.",
      ],
      verification_method="Вес сборки по категориям и время холодного старта на min-spec.",
      verification_tools=["Unity Profiler", "Unreal Insights"],
      source_key="UNITY_ADDRESSABLES"),

    M("differential_patch_pipeline", "Дифференциальные патчи",
      None,
      summary="Обновления доставляются разницей, а не полными файлами: патч 1 ГБ "
              "превращается в 10–100 МБ.",
      description="Контент режется на чанки с версиями, клиент докачивает изменившиеся куски. "
                  "Критично для мобильных сетей, где трафик дорог, и для live-игры с частыми "
                  "религами: маленький патч качают, большой — откладывают.",
      problem="Полные пересборки при каждом хотфиксе убивают обновление на слабом канале.",
      level="production", recommended_stage="production", late_cost="low",
      calc_mode="precomputed",
      impact_disk=-1, impact_network=-2,
      performance_gain=0.4, implementation_cost=2, complexity=3, confidence=0.75,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Патчи качают, а не откладывают", "Дешевле CDN и трафик игроков"],
      cons=["Требует версионирования чанков", "Сложнее откат"],
      limitations=["Не чинит архитектуру, только доставку"],
      application_steps=[
          "Нарезать контент на версионируемые чанки.",
          "Настроить дифф-сборку обновлений.",
          "Проверить размер патча на типовом хотфиксе.",
          "Протестировать откат на предыдущий чанк.",
      ],
      verification_method="Размер патча типового хотфикса и время обновления на медленном канале.",
      verification_tools=["Unity Profiler"],
      source_key="UNITY_ADDRESSABLES"),

    M("audio_streaming_compression", "Потоковое сжатие аудио",
      None,
      summary="Озвучка и музыка идут потоком в сжатом виде: минус гигабайты сборки "
              "и оперативной памяти ценой небольшой потери качества.",
      description="Полные записи (кейс Baldur's Gate 3 — порядка 20 ГБ звука) не держатся "
                  "в памяти: стриминг с диска + Ogg/Opus-сжатие. Баланс: битрейт диалогов выше, "
                  "фоновых слоёв ниже.",
      problem="Несжатое аудио раздувает сборку и оперативную память.",
      level="production", recommended_stage="production", late_cost="low",
      calc_mode="precomputed",
      impact_ram=-1, impact_disk=-2,
      performance_gain=0.4, implementation_cost=1, complexity=2, confidence=0.8,
      quality_impact=-1,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Минус гигабайты сборки", "Внедряется поздно без боли"],
      cons=["Слышимые артефакты на низком битрейте", "Нагрузка на диск при стриминге"],
      limitations=["Диалоги требуют высокого битрейта"],
      application_steps=[
          "Разделить аудио на диалоги, музыку и фоны.",
          "Выставить битрейты по категориям.",
          "Включить стриминг длинных записей.",
          "Прослушать на типовых устройствах игроков.",
      ],
      verification_method="Вес аудиобанков и пики памяти на сценах с озвучкой.",
      verification_tools=["Unity Profiler", "Unreal Insights"],
      source_key="HUNT_AUDIO"),

    M("composition_bootstrap_architecture", "Композиционный каркас проекта",
      None,
      summary="Проект строится композицией, а не наследованием: данные отдельно от механик, "
              "сервисы (ассеты, сцены, звук, сейвы) и DI-контейнер заводятся в бутстрапе.",
      description="Наследование ломается, когда скорость одновременно хотят менять движение, "
                  "гравитация и ветер: приходится переписывать половину проекта. Композиция "
                  "(компоненты + системы, ECS/DOTS/Mass) отделяет данные от механик, и новые "
                  "механики добавляются без переделки старых. Для прототипа из 20 классов "
                  "избыточно — раскрывается на росте.",
      problem="Добавление каждой механики превращается в переписывание половины проекта.",
      level="architecture", recommended_stage="preproduction", late_cost="critical",
      impact_cpu=-1,
      performance_gain=0.6, implementation_cost=4, complexity=4, confidence=0.7,
      requires_prototype=True,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Механики добавляются без переделки", "Масштабируется на контентную команду"],
      cons=["Инфраструктура окупается не сразу", "Порог входа выше"],
      limitations=["Для мини-прототипа избыточно", "Требует дисциплины данных"],
      application_steps=[
          "Выделить данные механик из классов поведения.",
          "Завести бутстрап, пайплайн запуска и DI-контейнер.",
          "Подключить сервисы ассетов, сцен, звука и сейвов.",
          "Добавить две механики подряд и проверить, что ничего не переписывалось.",
      ],
      verification_method="Время добавления контрольной механики и связность графа зависимостей.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="WIKI_ECS"),

    M("art_direction_stylization", "Стилизация вместо фотореализма",
      None,
      summary="Художественный стиль снижает требования к fidelity: low-poly, плоское "
              "освещение и читаемые силуэты дают 60 FPS там, где реализм требует "
              "трассировки и 4K-текстур.",
      description="Архитектурное решение уровня концепции: вместо гонки за реализмом "
                  "игра выбирает стилизацию (как Limbo, Torna Way и clean low-poly), "
                  "и тогда не нужны ни тяжёлое освещение, ни плотная геометрия. "
                  "Цена — сама концепция: решение определяет весь арт-пайплайн "
                  "и не откатывается без пересоздания ассетов.",
      problem="Фотореализм требует железа, которого нет у целевой аудитории.",
      level="architecture", recommended_stage="concept", late_cost="critical",
      performance_gain=0.7, implementation_cost=2, complexity=2, confidence=0.7,
      concept_impact=-2,
      applicable_formats=["3D", "2.5D", "2D"],
      pros=["Дешёвый рендер при выразительной картинке", "Стабильный FPS на слабом железе"],
      cons=["Определяет всю игру", "Поздняя смена — пересоздание ассетов"],
      limitations=["Не подходит проектам, где реализм — требование"],
      application_steps=[
          "Зафиксировать стиль в арт-библии до производства контента.",
          "Проверить читаемость силуэтов на серых болванках.",
          "Подобрать освещение под стиль, а не наоборот.",
      ],
      verification_method="Сравнение бюджета кадра стилизованной и реалистичной вертикали.",
      verification_tools=["Unity Profiler", "Unreal Insights"],
      source_key="WIKI_IMPOSTOR"),

    M("srp_batcher_discipline", "SRP Batcher и дисциплина материалов (URP/HDRP)",
      None,
      summary="SRP Batcher режет смены состояний между вызовами: мало вариантов шейдеров, "
              "много материалов, запрет MaterialPropertyBlock.",
      description="В URP/HDRP узкое место — не число вызовов, а смены состояний. SRP Batcher "
                  "объединяет bind+draw в батчи при условии: мало вариантов шейдеров, материалы "
                  "различаются только свойствами, без MaterialPropertyBlock. Со статическим "
                  "батчингом и BRG/GPU Resident Drawer не комбинируется — выбирается что-то одно.",
      problem="Смены состояний между вызовами съедают CPU в SRP-проектах.",
      level="setting", recommended_stage="prototype", late_cost="low",
      impact_cpu=-2,
      performance_gain=0.6, implementation_cost=1, complexity=2, confidence=0.85,
      applicable_engines=["unity"],
      applicable_formats=["3D", "2.5D"],
      pros=["Включается флагом", "Масштабируется на весь проект"],
      cons=["Требует чистки вариантов шейдеров", "PropertyBlock ломает батчинг"],
      limitations=["Не комбинируется со static batching и BRG одновременно"],
      application_steps=[
          "Включить SRP Batcher и замерить SetPass calls.",
          "Сократить варианты шейдеров, материалы различать свойствами.",
          "Убрать MaterialPropertyBlock из горячих путей.",
          "Выбрать один механизм: SRP Batcher, static batching или BRG.",
      ],
      verification_method="Счётчик SetPass calls и время рендер-потока до и после.",
      verification_tools=["Unity Profiler", "Frame Debugger"],
      source_key="UNITY_SRP_BATCHER"),

    M("tiled_clustered_light_culling", "Тайловое и кластерное отсечение источников света",
      None,
      summary="Источники назначаются тайлам и кластерам экрана вместо перебора всех "
              "источников в каждом пикселе: сотни источников без deferred.",
      description="Экран бьётся на тайлы (2D) или кластеры (3D с глубиной), каждому назначается "
                  "только влияющий на него свет. Forward-вариант требует depth pre-pass для "
                  "min-max отсечения и естественно держит прозрачность и MSAA, где deferred "
                  "требует сотни мегабайт G-буферов. Кластеры устойчивее тайлов к разрывам "
                  "глубины; пересечение выгоды — порядка тысяч источников.",
      problem="Десятки динамических источников в forward-рендере умножают стоимость шейдинга.",
      level="algorithm", recommended_stage="prototype", late_cost="medium",
      impact_gpu=-1, impact_vram=-1,
      performance_gain=0.6, implementation_cost=3, complexity=3, confidence=0.8,
      requires_prototype=True,
      requires_conditions=["Окупается при десятках источников света; при единицах — оверхед"],
      applicable_formats=["3D", "2.5D"],
      pros=["Сотни источников без deferred", "Прозрачность и MSAA из коробки"],
      cons=["Нужен depth pre-pass", "Сложность сетки источников"],
      limitations=["При единицах источников оверхед превышает выигрыш", "Прозрачные слои требуют отдельной обработки сетки"],
      application_steps=[
          "Посчитать динамические источники в тяжёлых сценах.",
          "Выбрать tiled или clustered по их числу и прозрачности.",
          "Включить depth pre-pass для forward-варианта.",
          "Замерить время lighting pass до и после.",
      ],
      verification_method="Время прохода освещения при целевом числе источников.",
      verification_tools=["RenderDoc", "Unreal Insights", "Unity Profiler"],
      source_key="CLUSTERED_SHADING"),

    M("snapshot_slot_saves", "Слотовые снапшоты мира (синхронная запись)",
      "save_system",
      summary="Полный снимок мира сериализуется в слот синхронно: просто и целостно "
              "для маленьких данных.",
      description="Состояние систем собирается в объект сохранения и пишется в слот целиком "
                  "(синхронный SaveGameToSlot; бинарь + GZip режут размер). Запись блокирует "
                  "поток: для меню и паузы незаметно, для автосейва в геймплее — фриз.",
      problem="Прогресс должен пережить выключение; частичная запись хуже потери часа.",
      level="production", recommended_stage="preproduction", late_cost="high",
      impact_cpu=1, impact_disk=2,
      performance_gain=0.3, implementation_cost=2, complexity=2, confidence=0.85,
      pros=["Простота и предсказуемость", "Целостный файл легко проверять"],
      cons=["Фриз на записи больших данных", "Размер растёт с прогрессом"],
      limitations=["Без версионирования патч ломает сейвы", "Синхронная запись — только для меню и паузы"],
      application_steps=[
          "Отделить модель сохранения от рантайма (плоские данные, стабильные ID).",
          "Завести слоты и поле версии формата.",
          "Сериализовать в бинарь + сжатие, писать атомарно (temp + rename + checksum).",
          "Проверить загрузку сейва прошлой версии миграциями.",
          "Замерить фриз записи и размер файла на позднем прогрессе.",
      ],
      verification_method="Замер фриза записи и размера файла; загрузка сейва прошлой версии.",
      verification_tools=["Unreal Insights"],
      source_key="UE_SAVEGAME"),

    M("async_incremental_saves", "Асинхронные инкрементальные автосейвы",
      "save_system",
      summary="Грязные данные снимаются в immutable-снапшот на игровом потоке, сериализация "
              "и запись — на воркере; пишется только изменившееся.",
      description="Разделение capture/encode/write: быстрый снимок на игровом потоке, тяжёлая "
                  "работа на воркере (рекомендованный путь от фризов). Dirty-флаги пишут только "
                  "изменения; ротация слотов и атомарная запись страхуют от битого файла.",
      problem="Автосейв в геймплее не должен останавливать кадр.",
      level="production", recommended_stage="preproduction", late_cost="high",
      impact_cpu=1, impact_ram=1, impact_disk=1,
      performance_gain=0.6, implementation_cost=3, complexity=3, confidence=0.8,
      pros=["Нет фриза в геймплее", "Малый размер инкремента"],
      cons=["Синхронизация потоков и снапшотов", "Миграции версий сложнее"],
      limitations=["Сериализация живого мира с воркера — гонка и битые сейвы",
                   "Один слот без ротации уязвим к обрыву записи"],
      application_steps=[
          "Разделить capture (игровой поток, immutable) и encode/write (воркер).",
          "Ввести dirty-флаги систем и ротацию слотов.",
          "Писать атомарно с checksum и fallback на предыдущий слот.",
          "Прогнать миграции версий на старых сейвах.",
          "Замерить отсутствие фриза при автосейве в геймплее.",
      ],
      verification_method="Профайлинг кадра в момент автосейва; краш-тест записи и восстановление.",
      verification_tools=["Unreal Insights", "Unity Profiler"],
      source_key="SAVE_PATTERNS"),

    M("screenspace_light_shafts", "Экранные световые валы (пост-процесс)",
      "post_processing",
      summary="Световые валы как экранный пост-процесс: радиальный блур от ярких источников "
              "без предрасчёта сцены.",
      description="Пост-процесс суммирует сэмплы вдоль луча к экранной позиции источника "
                  "с затуханием (вес, плотность, экспозиция). Не требует настройки сцены, "
                  "работает на любом анимированном кадре; оценка окклюзии приблизительная "
                  "и любит контраст.",
      problem="Настоящее рассеивание в объёме дорого; валам нужен дешёвый аналог.",
      level="algorithm", recommended_stage="production", late_cost="low",
      impact_gpu=1,
      performance_gain=0.4, implementation_cost=2, complexity=2, confidence=0.8,
      applicable_formats=["3D", "2.5D"],
      pros=["Дешёвые валы без предрасчёта сцены", "Работает на любом анимированном кадре"],
      cons=["Врёт при слабом контрасте источник/окклюдер", "Нет настоящего рассеивания в объёме"],
      limitations=["Источник должен быть в кадре", "Оценка окклюзии приблизительная"],
      application_steps=[
          "Выделить яркие источники в отдельный проход.",
          "Настроить сэмплирование к экранной позиции источника (вес, плотность, затухание).",
          "Сравнить с объёмным туманом: выбрать что-то одно на сцену.",
          "Замерить стоимость прохода на целевом разрешении.",
      ],
      verification_method="Скриншот-тест и замер времени прохода до и после.",
      verification_tools=["RenderDoc"],
      source_key="GPU_GEMS_SHAFTS"),

    M("rvo_local_avoidance", "Локальное избегание агентов (RVO/ORCA)",
      "ai_pathfinding",
      summary="Локальное расхождение агентов по взаимным скоростям: half-plane на агента, "
              "линейное программирование, параллелится.",
      description="Каждый агент берёт половину ответственности за расхождение: из скоростей "
                  "соседей строится полуплоскость допустимых скоростей, оптимум выбирается "
                  "линейным программированием. Гладко, без осцилляций; горизонт локальный — "
                  "ловушки и строй не решаются.",
      problem="Десятки агентов толкаются и дрожат без локального избегания.",
      level="algorithm", recommended_stage="production", late_cost="medium",
      impact_cpu=1,
      performance_gain=0.6, implementation_cost=2, complexity=3, confidence=0.85,
      pros=["Гладкие траектории без осцилляций", "Параллелится по агентам",
            "Доказанная бесконфликтность при общем протоколе"],
      cons=["Только локальный горизонт — ловушки не решает", "Клинические лобовые сценарии проваливаются"],
      limitations=["Не заменяет глобальный поиск пути", "Требует настройки горизонтов и соседей"],
      application_steps=[
          "Зарегистрировать агентов с радиусом и дистанцией соседей.",
          "Каждый физический кадр подавать скорость и применять safe velocity.",
          "Настроить горизонты времени, соседей и приоритеты.",
          "Прогнать стресс-сцену: CPU избегания и отсутствие застреваний.",
      ],
      verification_method="Стресс-сцена: время избегания на агента и отсутствие застреваний.",
      verification_tools=["Unity Profiler", "Unreal Insights"],
      source_key="ORCA_RVO"),
]

EXTRA_LINKS: dict[str, dict[str, tuple[str, str, str]]] = {
    "sprite_atlas_batching": {
        "unreal": ("ue_ism", "partial", "Paper2D и инстансинг спрайтов дают частичный аналог упаковки."),
        "unity": ("u_srp_batcher", "direct", "SRP Batcher и Sprite Atlas собирают слои в батчи."),
        "godot": ("g_multimesh", "partial", "Готового атласного батчинга нет, частично через MultiMesh."),
        "custom": ("c_render_graph", "alternative", "Реализуется как проход собственного графа рендера."),
    },
    "sprite_sheet_compression": {
        "unreal": ("ue_lod", "missing", "Требуется ручная настройка форматов текстур."),
        "unity": ("u_texture_streaming", "direct", "Настройки импорта текстур и форматы сжатия."),
        "godot": ("g_mesh_lod", "missing", "Настраивается вручную через параметры импорта."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "skeletal_2d_deform": {
        "unreal": ("ue_lod", "missing", "Встроенного 2D-скелетного решения нет."),
        "unity": ("u_lod_group", "partial", "2D Animation пакет, интеграция со скинингом."),
        "godot": ("g_mesh_lod", "partial", "Skeleton2D и Polygon2D, без полноценного скелетного пакета."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "tilemap_chunk_streaming": {
        "unreal": ("ue_world_partition", "partial", "World Partition рассчитан на 3D, для 2D требуется адаптация."),
        "unity": ("u_addressables", "direct", "Addressables и сцены с чанками карты."),
        "godot": ("g_bg_loading", "direct", "ResourceLoader.load_threaded для фоновой подгрузки чанков."),
        "custom": ("c_streaming", "missing", "Требуется собственный конвейер загрузки."),
    },
    "tilemap_layer_culling": {
        "unreal": ("ue_ism", "partial", "Частично решается инстансингом и ручным управлением слоями."),
        "unity": ("u_occlusion", "limited", "Окклюзия рассчитана на 3D, для 2D применяется ограниченно."),
        "godot": ("g_visibility", "direct", "Ручное управление видимостью слоёв и нод."),
        "custom": ("c_render_graph", "alternative", "Отсечение реализуется в графе рендера."),
    },
    "sprite_particle_atlas": {
        "unreal": ("ue_niagara", "partial", "Niagara рассчитан на 3D, для 2D требуется адаптация."),
        "unity": ("u_vfxgraph", "limited", "VFX Graph ориентирован на 3D; для 2D применяется ограниченно."),
        "godot": ("g_gpu_particles", "partial", "GPUParticles2D с текстурой из атласа."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "lightmap_2d_baking": {
        "unreal": ("ue_lumen", "missing", "Для 2D-освещения встроенного запекания нет."),
        "unity": ("u_lightmapper", "direct", "Progressive Lightmapper поддерживает 2D-сцены."),
        "godot": ("g_gi", "partial", "LightmapGI применим к 2D с ручной настройкой."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "shadow_caster_2d_limits": {
        "unreal": ("ue_vsm", "missing", "Встроенного 2D-теневого решения нет."),
        "unity": ("u_quality", "direct", "Настройки качества 2D-теней и лимиты источников."),
        "godot": ("g_shadows", "direct", "Настройки 2D-освещения и теней в проекте."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "crowd_2d_instancing": {
        "unreal": ("ue_ism", "partial", "Инстансинг применим к 2D-спрайтам с ограничениями."),
        "unity": ("u_instancing", "direct", "GPU Instancing и BatchRendererGroup для 2D."),
        "godot": ("g_multimesh", "direct", "MultiMeshInstance2D для массовой отрисовки."),
        "custom": ("c_render_graph", "alternative", "Реализуется в собственном графе рендера."),
    },
    "collision_layer_matrix": {
        "unreal": ("ue_chaos", "direct", "Настройка профилей коллизий Chaos."),
        "unity": ("u_quality", "direct", "Матрица столкновений слоёв в настройках физики."),
        "godot": ("g_physics_server", "direct", "Слои и маски коллизий PhysicsServer."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "post_effect_selective": {
        "unreal": ("ue_niagara", "missing", "Требуется собственная настройка области эффекта."),
        "unity": ("u_srp", "direct", "Настраиваемые проходы URP и HDRP."),
        "godot": ("g_visibility", "partial", "Частично через слои и области видимости."),
        "custom": ("c_render_graph", "alternative", "Проходы эффектов в собственном графе рендера."),
    },
    "depth_prepass_early_z": {
        "unreal": ("ue_nanite", "automation", "Nanite автоматически формирует проход глубины."),
        "unity": ("u_srp", "direct", "Настраивается в URP и HDRP как depth prepass."),
        "godot": ("g_occluder", "partial", "Прямого управления порядком меньше, чем в коммерческих движках."),
        "custom": ("c_render_graph", "direct", "Проход глубины в собственном графе рендера."),
    },
    "mesh_index_optimization": {
        "unreal": ("ue_lod", "partial", "LOD-цепочки строятся поверх оптимизированных индексов."),
        "unity": ("u_lod_group", "partial", "LOD Group плюс прогон meshoptimizer в пайплайне."),
        "godot": ("g_mesh_lod", "direct", "Автогенерация LOD в Godot 4 построена на meshoptimizer."),
        "custom": ("c_memory", "partial", "meshoptimizer подключается как библиотека ассет-пайплайна."),
    },
    "neural_texture_compression": {
        "unreal": ("ue_virtual_texturing", "complement", "Нейросжатие тайлов дополняет виртуальное текстурирование."),
        "unity": ("u_texture_streaming", "partial", "Стриминг мипов из коробки, NTC — внешним плагином."),
        "godot": ("g_visibility", "missing", "Нейросжатия текстур нет."),
        "custom": ("c_manual", "partial", "Подключается через нейроускорение самостоятельно."),
    },
    "planar_reflection_budget": {
        "unreal": ("ue_lumen", "partial", "Lumen-отражения вместо плоских; planar — отдельной настройкой."),
        "unity": ("u_srp", "direct", "Planar Reflection Probe в URP и HDRP."),
        "godot": ("g_visibility", "partial", "ReflectionProbe вручную, бюджет planar — настройкой."),
        "custom": ("c_manual", "partial", "Проход отражения пишется в графе рендера."),
    },
    "normal_bake_retopology_pipeline": {
        "unreal": ("ue_lod", "partial", "Запечённые нормали живут на LOD-цепочках."),
        "unity": ("u_lod_group", "partial", "Бейк во внешнем DCC, раскладка — группой LOD."),
        "godot": ("g_mesh_lod", "partial", "Бейк во внешнем DCC, LOD автоматический."),
        "custom": ("c_manual", "partial", "Ретопология и бейк во внешнем DCC."),
    },
    "build_size_startup_budgets": {
        "unreal": ("ue_insights", "diagnostic", "Аудит размера и времени старта через Insights."),
        "unity": ("u_addressables", "direct", "Группы Addressables и бюджеты размера."),
        "godot": ("g_bg_loading", "partial", "Фоновая загрузка смягчает старт, бюджеты — вручную."),
        "custom": ("c_streaming", "partial", "Бюджеты размера в собственном стриминге."),
    },
    "differential_patch_pipeline": {
        "unreal": ("ue_insights", "diagnostic", "Контроль размера чанков пакетов."),
        "unity": ("u_addressables", "direct", "Content Update: дифференциальные бандлы."),
        "godot": ("g_bg_loading", "partial", "Докачка ресурсов фоновым загрузчиком."),
        "custom": ("c_streaming", "partial", "Дифф-патчи поверх собственного стриминга."),
    },
    "audio_streaming_compression": {
        "unreal": ("ue_insights", "diagnostic", "Контроль памяти аудиобанков через Insights."),
        "unity": ("u_addressables", "partial", "Аудиобанки в Addressables со стримингом."),
        "godot": ("g_bg_loading", "partial", "Аудиопотоки через фоновый загрузчик."),
        "custom": ("c_manual", "partial", "Ogg/Opus-стриминг пишется самостоятельно."),
    },
    "composition_bootstrap_architecture": {
        "unreal": ("ue_mass", "partial", "MassEntity задаёт ECS-каркас, сервисы и DI — кодом."),
        "unity": ("u_dots", "partial", "Entities и субсцены как каркас, сервисы — кодом."),
        "godot": ("g_threads", "partial", "Сервисы на автозагрузке и пуле потоков."),
        "custom": ("c_ecs", "direct", "Собственный ECS и DI-контейнер."),
    },
    "art_direction_stylization": {
        "unreal": ("ue_lumen", "missing", "Стиль задаётся артом, а не движком; Lumen подстраивается под него."),
        "unity": ("u_srp", "partial", "Стиль собирается настройками URP/HDRP и шейдерами."),
        "godot": ("g_visibility", "partial", "Стиль держится дистанциями и ручным светом."),
        "custom": ("c_manual", "partial", "Стиль полностью в руках команды."),
    },
    "srp_batcher_discipline": {
        "unreal": ("ue_nanite", "missing", "SRP Batcher — механизм Unity, аналога нет."),
        "unity": ("u_srp_batcher", "direct", "SRP Batcher включается в настройках конвейера."),
        "godot": ("g_multimesh", "missing", "Батчера состояний нет, только MultiMesh."),
        "custom": ("c_render_graph", "alternative", "Персистентные буферы в собственном графе."),
    },
    "tiled_clustered_light_culling": {
        "unreal": ("ue_lumen", "missing", "Отдельного tiled-culling нет; много источников — через Lumen/Deferred."),
        "unity": ("u_srp", "direct", "Forward+ в URP: кластеризованное назначение источников."),
        "godot": ("g_visibility", "partial", "Кластеризация уже внутри Forward+, настраивать нечего."),
        "custom": ("c_render_graph", "direct", "Тайловая классификация и сетка источников в собственном графе."),
    },
    "managed_gc_alloc_budget": {
        "unity": ("u_profiler", "diagnostic", "GC.Alloc-колонка CPU Usage Profiler и руководство по best practices."),
        "custom": ("c_profiler", "diagnostic", "Маркеры аллокаций горячего цикла в Tracy."),
    },
    "snapshot_slot_saves": {
        "unity": ("u_addressables", "missing", "Готового сейв-слоя нет; слоты и сериализация — кодом поверх JsonUtility."),
        "godot": ("g_bg_loading", "missing", "Слотов нет; запись через ResourceSaver/FileAccess своими слотами."),
        "custom": ("c_manual", "direct", "Сериализация, слоты и миграции пишутся под проект."),
    },
    "async_incremental_saves": {
        "unreal": ("ue_insights", "diagnostic", "Замер фриза автосейва в Insights."),
        "unity": ("u_profiler", "diagnostic", "Замер фриза автосейва в Profiler."),
        "godot": ("g_profiler", "diagnostic", "Замер фриза автосейва в профилировщике."),
        "custom": ("c_profiler", "diagnostic", "Замер фриза автосейва через Tracy."),
    },
    "screenspace_light_shafts": {
        "unreal": ("ue_lumen", "missing", "Отдельного screen-space пасса валов нет."),
        "unity": ("u_srp", "partial", "Кастомный fullscreen-проход в URP."),
        "godot": ("g_visibility", "missing", "Встроенных крепускулярных лучей нет."),
        "custom": ("c_render_graph", "direct", "Радиальный блур-проход в собственном графе рендера."),
    },
    "rvo_local_avoidance": {
        "unreal": ("ue_navmesh", "partial", "Крауд-избегание детура поверх навмеша."),
        "unity": ("u_navmesh", "partial", "RVO-стиринг агента: качество и приоритет избегания."),
        "godot": ("g_navigation", "direct", "RVO-библиотека внутри NavigationServer."),
        "custom": ("c_manual", "partial", "Открытая RVO2/ORCA-библиотека подключается кодом."),
    },
}

EXTRA_CONFLICTS: list[dict] = [
    {
        "a_code": "skeletal_2d_deform", "b_code": "sprite_atlas_batching",
        "conflict_type": "dependency", "severity": 2,
        "description": "Скелетная 2D-анимация требует упаковки частей тела в общий атлас, "
                       "иначе каждый вызов отрисовки останется отдельным.",
        "resolution": "Планировать атласы одновременно с переходом на скелетную анимацию.",
        "source_key": "WIKI_ATLAS",
    },
    {
        "a_code": "lightmap_2d_baking", "b_code": "post_effect_selective",
        "conflict_type": "synergy", "severity": 1,
        "description": "Запечённое 2D-освещение снижает стоимость кадра, а выборочная "
                       "постобработка убирает остаточную нагрузку на GPU.",
        "resolution": "Применять совместно для 2D-проектов с большим числом источников света.",
        "source_key": "UNITY_LIGHTMAPPER",
    },
    {
        "a_code": "skeletal_2d_deform", "b_code": "sprite_sheet_compression",
        "conflict_type": "conflict", "severity": 1,
        "description": "Сжатие с потерей качества заметнее на деформируемых частях тела, "
                       "чем на готовых кадрах покадровой анимации.",
        "resolution": "Для скелетной анимации использовать менее агрессивное сжатие.",
        "source_key": "WIKI_MIPMAP",
    },
    {
        "a_code": "crowd_2d_instancing", "b_code": "agent_update_budget",
        "conflict_type": "synergy", "severity": 1,
        "description": "Распределение обновлений по кадрам незаметно при массовой отрисовке "
                       "агентов одним батчем.",
        "resolution": "Применять совместно для сцен с большим числом 2D-агентов.",
        "source_key": "UE_SIGNIFICANCE",
    },
    # --- Альтернативные методы: баланс набора --------------------------------
    {
        "a_code": "deterministic_lockstep", "b_code": "multithreaded_physics_jobs",
        "conflict_type": "conflict", "severity": 3,
        "description": "Параллельные потоки ломают порядок симуляции: результат зависит от "
                       "планировщика, lockstep расходится и даёт десинк.",
        "resolution": "Параллелить только read-only чтения либо детерминированный планировщик.",
        "source_key": "GAFFER_TIMESTEP",
    },
    {
        "a_code": "ml_frame_generation", "b_code": "client_prediction_reconciliation",
        "conflict_type": "conflict", "severity": 2,
        "description": "Генерация добавляет лаг ввода, а предсказание требует мгновенной реакции: "
                       "в competitive с FG играть нельзя.",
        "resolution": "Не включать генерацию в competitive-режимах; Reflex обязателен.",
        "source_key": "WIKI_DLSS",
    },
    {
        "a_code": "pso_precaching_warmup", "b_code": "async_loading_pipeline",
        "conflict_type": "synergy", "severity": 1,
        "description": "Прогретые PSO убирают hitch, асинхронная загрузка убирает фризы: вместе "
                       "дают гладкий стриминг без остановок кадра.",
        "resolution": "Применять совместно для миров со стримингом.",
        "source_key": "UNITY_SHADERLOAD",
    },
    {
        "a_code": "quality_tier_scalability", "b_code": "hardware_raytraced_gi",
        "conflict_type": "synergy", "severity": 1,
        "description": "Тиры позволяют включать трассировку только там, где железо тянет, "
                       "а не резать её для всех.",
        "resolution": "Привязать RT-пресеты к верхним тирам и проверять на min-spec тира.",
        "source_key": "UNITY_QUALITY",
    },
    {
        "a_code": "planar_reflection_budget", "b_code": "screen_space_gi",
        "conflict_type": "conflict", "severity": 2,
        "description": "Плоские отражения рендерят сцену дважды, а экранное освещение уже "
                       "считает отражения по кадру: держать оба — платить дважды.",
        "resolution": "Выбрать одну систему отражений как основную.",
        "source_key": "UE_LUMEN",
    },
    {
        "a_code": "temporal_upscaling", "b_code": "hardware_raytraced_gi",
        "conflict_type": "synergy", "severity": 2,
        "description": "Трассировка даёт шумное изображение, которое временной апскейлер "
                       "сглаживает и одновременно возвращает FPS: связка DLSS + RT.",
        "resolution": "Проектировать RT-пресеты только в паре с апскейлером.",
        "source_key": "WIKI_DLSS",
    },
    {
        "a_code": "tiled_clustered_light_culling", "b_code": "depth_prepass_early_z",
        "conflict_type": "synergy", "severity": 2,
        "description": "Forward-вариант кластеризации строится на min-max отсечении по глубине: "
                       "без прохода глубины сетка источников нечем инициализировать.",
        "resolution": "Включать парой: сначала depth pre-pass, затем классификацию источников.",
        "source_key": "CLUSTERED_SHADING",
    },
]

# ---------------------------------------------------------------------------
# Связи методов с инструментами движков.
# Формат: метод -> { движок: (инструмент, тип связи, пояснение) }
# ---------------------------------------------------------------------------
METHOD_ENGINE_LINKS: dict[str, dict[str, tuple[str, str, str]]] = {
    "world_partition_streaming": {
        "unreal": ("ue_world_partition", "direct", "World Partition автоматически стримит ячейки мира."),
        "unity": ("u_addressables", "direct", "Addressables обеспечивает адресную загрузку сцен и ассетов."),
        "godot": ("g_bg_loading", "partial", "Требуется самостоятельная организация плиток и приоритетов загрузки."),
        "custom": ("c_streaming", "missing", "Подсистему стриминга необходимо реализовать самостоятельно."),
    },
    "world_origin_shifting": {
        "unreal": ("ue_lwc", "direct", "Large World Coordinates решает проблему точности на уровне движка."),
        "unity": ("u_quality", "missing", "Встроенного решения нет, требуется собственный origin rebasing."),
        "godot": ("g_visibility", "missing", "Встроенного решения нет, требуется ручной сдвиг."),
        "custom": ("c_streaming", "alternative", "Реализуется вместе с подсистемой стриминга."),
    },
    "hierarchical_lod": {
        "unreal": ("ue_hlod", "direct", "HLOD генерируется и собирается средствами редактора."),
        "unity": ("u_lod_group", "partial", "Готового HLOD нет, требуется ручная сборка или сторонний пакет."),
        "godot": ("g_mesh_lod", "partial", "Есть автоматический LOD мешей, но не объединение кластеров."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "gpu_compute_culling": {
        "unreal": ("ue_nanite", "direct", "Nanite выполняет кластеризованное отсечение на GPU."),
        "unity": ("u_instancing", "partial", "Требуется собственная реализация через compute-шейдеры."),
        "godot": ("g_multimesh", "partial", "Частично решается MultiMesh, без compute-отсечения."),
        "custom": ("c_render_graph", "alternative", "Реализуется как проход собственного графа рендера."),
    },
    "baked_occlusion_culling": {
        "unreal": ("ue_hlod", "partial", "Используется предпросчитанная видимость и HLOD."),
        "unity": ("u_occlusion", "direct", "Встроенная система запечённой окклюзии с порталами."),
        "godot": ("g_occluder", "direct", "Окклюдеры расставляются вручную в редакторе."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "async_loading_pipeline": {
        "unreal": ("ue_world_partition", "automation", "Стриминг ячеек из коробки."),
        "unity": ("u_addressables", "direct", "Асинхронная загрузка через Addressables."),
        "godot": ("g_bg_loading", "direct", "ResourceLoader.load_threaded в отдельном потоке."),
        "custom": ("c_streaming", "missing", "Требуется собственный конвейер загрузки."),
    },
    "terrain_clipmap": {
        "unreal": ("ue_nanite", "alternative", "Nanite частично заменяет клипмап для статичной геометрии."),
        "unity": ("u_lod_group", "partial", "Требуется собственная реализация или сторонний ассет."),
        "godot": ("g_mesh_lod", "partial", "Базовый LOD мешей, клипмап реализуется вручную."),
        "custom": ("c_render_graph", "alternative", "Собственный проход ландшафта в графе рендера."),
    },
    "virtual_texturing": {
        "unreal": ("ue_virtual_texturing", "direct", "Встроенное виртуальное текстурирование."),
        "unity": ("u_texture_streaming", "partial", "Стриминг мип-уровней, но не полноценное виртуальное текстурирование."),
        "godot": ("g_visibility", "missing", "Встроенного аналога нет."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "heightmap_compression": {
        "unreal": ("ue_virtual_texturing", "complement", "Хорошо сочетается с виртуальным текстурированием."),
        "unity": ("u_texture_streaming", "complement", "Дополняет стриминг мип-уровней."),
        "godot": ("g_mesh_lod", "partial", "Требуется ручная настройка форматов."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "virtual_geometry_clusters": {
        "unreal": ("ue_nanite", "direct", "Прямая реализация виртуализированной геометрии."),
        "unity": ("u_lod_group", "missing", "Встроенного аналога нет."),
        "godot": ("g_mesh_lod", "missing", "Встроенного аналога нет."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "gpu_instancing_vegetation": {
        "unreal": ("ue_ism", "direct", "Instanced и Hierarchical Static Mesh компоненты."),
        "unity": ("u_instancing", "direct", "GPU Instancing и BatchRendererGroup."),
        "godot": ("g_multimesh", "direct", "MultiMeshInstance3D с массивом трансформаций."),
        "custom": ("c_render_graph", "alternative", "Инстансинг реализуется в собственном графе рендера."),
    },
    "gpu_procedural_placement": {
        "unreal": ("ue_ism", "partial", "Через procedural foliage и HISM, но генерация в основном на CPU."),
        "unity": ("u_dots", "alternative", "Удобно совмещать с ECS и Burst."),
        "godot": ("g_threads", "partial", "Возможна генерация в потоке, без GPU-размещения."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "impostors_billboards": {
        "unreal": ("ue_ism", "complement", "Дополняет инстансинг растительности."),
        "unity": ("u_lod_group", "partial", "Реализуется как последний уровень LOD."),
        "godot": ("g_multimesh", "partial", "Реализуется вручную через билборды."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "vegetation_atlas_lod": {
        "unreal": ("ue_lod", "direct", "LOD-цепочки и атласы собираются редактором."),
        "unity": ("u_lod_group", "direct", "LOD Group и настройка атласов."),
        "godot": ("g_mesh_lod", "direct", "Автоматическая генерация LOD."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "sdf_global_illumination": {
        "unreal": ("ue_lumen", "direct", "Lumen использует дистанционные поля для ГО."),
        "unity": ("u_srp", "limited", "Требует HDRP и собственной настройки."),
        "godot": ("g_gi", "partial", "VoxelGI и SDFGI дают упрощённый аналог."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "irradiance_volume_probes": {
        "unreal": ("ue_lumen", "partial", "Работает вместе с зондами освещённости."),
        "unity": ("u_light_probes", "direct", "Light Probes и Adaptive Probe Volumes."),
        "godot": ("g_gi", "direct", "VoxelGI и LightmapGI с зондами."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "voxel_cone_tracing": {
        "unreal": ("ue_lumen", "alternative", "Lumen решает ту же задачу другими средствами."),
        "unity": ("u_srp", "limited", "Требует собственной реализации в HDRP."),
        "godot": ("g_gi", "direct", "VoxelGI — прямая реализация подхода."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "screen_space_gi": {
        "unreal": ("ue_lumen", "complement", "Используется как дополнение к основному ГО."),
        "unity": ("u_srp", "partial", "Экранное затенение и отражения доступны в URP/HDRP."),
        "godot": ("g_shadows", "partial", "Ограниченная поддержка экранных эффектов."),
        "custom": ("c_render_graph", "alternative", "Проход в собственном графе рендера."),
    },
    "temporal_radiance_cache": {
        "unreal": ("ue_lumen", "direct", "Кэш освещённости Lumen с временным накоплением."),
        "unity": ("u_srp", "partial", "Требует собственной реализации."),
        "godot": ("g_gi", "partial", "Частично решается SDFGI."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "hardware_raytraced_gi": {
        "unreal": ("ue_lumen", "direct", "Lumen использует аппаратную трассировку при включённом режиме."),
        "unity": ("u_srp", "limited", "Ограниченная поддержка в HDRP."),
        "godot": ("g_shadows", "missing", "Встроенного аппаратного RT нет."),
        "custom": ("c_render_graph", "alternative", "Требуется собственная интеграция RT API."),
    },
    "lightmap_atlas_baking": {
        "unreal": ("ue_lumen", "alternative", "Альтернатива динамическому ГО Lumen."),
        "unity": ("u_lightmapper", "direct", "Progressive Lightmapper с CPU и GPU бэкендом."),
        "godot": ("g_gi", "direct", "LightmapGI с запеканием в редакторе."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "gpu_lightmap_baking": {
        "unreal": ("ue_lumen", "partial", "GPU Lightmass используется как внешний инструмент."),
        "unity": ("u_lightmapper", "direct", "GPU-бэкенд Progressive Lightmapper."),
        "godot": ("g_gi", "partial", "Запекание выполняется на CPU."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "lightmap_compression_streaming": {
        "unreal": ("ue_virtual_texturing", "direct", "Лайтмапы подгружаются через виртуальное текстурирование."),
        "unity": ("u_texture_streaming", "partial", "Стриминг текстур, лайтмапы требуют настройки."),
        "godot": ("g_gi", "partial", "Требуется ручная настройка форматов."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "cascaded_shadow_maps": {
        "unreal": ("ue_vsm", "alternative", "Virtual Shadow Maps заменяют каскады."),
        "unity": ("u_quality", "direct", "Настройка каскадов в Quality Settings."),
        "godot": ("g_shadows", "direct", "PSSM-каскады в настройках DirectionalLight3D."),
        "custom": ("c_render_graph", "alternative", "Проход теней в собственном графе рендера."),
    },
    "virtual_shadow_maps": {
        "unreal": ("ue_vsm", "direct", "Virtual Shadow Maps — встроенный конвейер виртуальных карт теней Unreal Engine."),
        "unity": ("u_srp", "missing", "Полного встроенного аналога VSM нет; требуется другой теневой конвейер или пакет."),
        "godot": ("g_shadows", "missing", "Полного встроенного аналога VSM нет; требуется собственная реализация."),
        "custom": ("c_render_graph", "alternative", "Реализуется как виртуализированный конвейер страниц теней в графе рендера."),
    },
    "distance_field_shadows": {
        "unreal": ("ue_vsm", "direct", "Virtual Shadow Maps и дистанционные поля."),
        "unity": ("u_srp", "limited", "Ограниченная поддержка в HDRP."),
        "godot": ("g_shadows", "partial", "Частично реализуется через SDFGI."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "screen_space_contact_shadows": {
        "unreal": ("ue_vsm", "complement", "Дополняет основные тени."),
        "unity": ("u_srp", "direct", "Contact Shadows в HDRP."),
        "godot": ("g_shadows", "partial", "Частично через экранное затенение."),
        "custom": ("c_render_graph", "alternative", "Проход в собственном графе рендера."),
    },
    "static_shadow_caching": {
        "unreal": ("ue_vsm", "direct", "Кэширование страниц виртуальных карт теней."),
        "unity": ("u_quality", "partial", "Режим статических теней с кэшированием."),
        "godot": ("g_shadows", "partial", "Требуется ручная настройка статики."),
        "custom": ("c_render_graph", "alternative", "Реализуется в графе рендера."),
    },
    "gpu_particle_simulation": {
        "unreal": ("ue_niagara", "direct", "Niagara с GPU-симуляцией."),
        "unity": ("u_vfxgraph", "direct", "Visual Effect Graph с GPU-симуляцией."),
        "godot": ("g_gpu_particles", "direct", "GPUParticles3D."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "particle_pooling": {
        "unreal": ("ue_niagara", "complement", "Пул компонентов Niagara."),
        "unity": ("u_dots", "partial", "Удобно совмещать с ECS без сборки мусора."),
        "godot": ("g_visibility", "partial", "Ручное управление пулом узлов."),
        "custom": ("c_memory", "alternative", "Собственные пулы объектов."),
    },
    "flipbook_particles": {
        "unreal": ("ue_niagara", "direct", "Поддерживается материалами с flipbook."),
        "unity": ("u_vfxgraph", "direct", "Поддерживается Visual Effect Graph."),
        "godot": ("g_gpu_particles", "partial", "Реализуется через анимацию текстуры."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "fixed_timestep_physics": {
        "unreal": ("ue_chaos", "direct", "Chaos работает с фиксированным шагом и интерполяцией."),
        "unity": ("u_dots", "direct", "Fixed Step в настройках физики и DOTS."),
        "godot": ("g_physics_server", "direct", "PhysicsServer3D с фиксированным шагом."),
        "custom": ("c_job_system", "alternative", "Собственный планировщик с фиксированным шагом."),
    },
    "physics_lod_sleeping": {
        "unreal": ("ue_chaos", "direct", "Chaos поддерживает спящие тела и LOD."),
        "unity": ("u_quality", "direct", "Пороги сна в настройках физики."),
        "godot": ("g_physics_server", "direct", "Настройки областей и сна."),
        "custom": ("c_job_system", "alternative", "Собственная логика LOD."),
    },
    "multithreaded_physics_jobs": {
        "unreal": ("ue_chaos", "direct", "Chaos использует систему задач движка."),
        "unity": ("u_jobs", "direct", "C# Job System и Unity Physics."),
        "godot": ("g_threads", "partial", "WorkerThreadPool, физика ограничена."),
        "custom": ("c_job_system", "alternative", "Собственная система задач."),
    },
    "broadphase_spatial_partitioning": {
        "unreal": ("ue_chaos", "automation", "Реализовано внутри Chaos."),
        "unity": ("u_dots", "automation", "Реализовано внутри Unity Physics."),
        "godot": ("g_physics_server", "automation", "Реализовано внутри PhysicsServer3D."),
        "custom": ("c_ecs", "alternative", "Собственная структура в ECS."),
    },
    "gpu_skinning_compute": {
        "unreal": ("ue_anim_budget", "partial", "Частично автоматизировано, требуется настройка."),
        "unity": ("u_dots", "partial", "Требует собственной реализации через compute."),
        "godot": ("g_gpu_particles", "missing", "Встроенного GPU-скиннинга нет."),
        "custom": ("c_render_graph", "alternative", "Проход скиннинга в графе рендера."),
    },
    "animation_compression": {
        "unreal": ("ue_lod", "direct", "Настройки сжатия анимаций в редакторе."),
        "unity": ("u_quality", "direct", "Настройки сжатия в импортере анимаций."),
        "godot": ("g_mesh_lod", "partial", "Ограниченные настройки."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "animation_lod_budget": {
        "unreal": ("ue_anim_budget", "direct", "Animation Budget Allocator."),
        "unity": ("u_quality", "partial", "Требуется собственная реализация."),
        "godot": ("g_visibility", "partial", "Ручное управление через слои и видимость."),
        "custom": ("c_job_system", "alternative", "Собственное распределение бюджета."),
    },
    "motion_matching": {
        "unreal": ("ue_anim_budget", "missing", "Встроенного решения нет, требуется плагин или своя реализация."),
        "unity": ("u_dots", "alternative", "Удобно реализовывать на ECS с Burst."),
        "godot": ("g_threads", "missing", "Встроенного решения нет."),
        "custom": ("c_ecs", "missing", "Реализуется полностью самостоятельно."),
    },
    "ecs_data_oriented_crowd": {
        "unreal": ("ue_mass", "direct", "Mass Entity — ECS-фреймворк для толпы."),
        "unity": ("u_dots", "direct", "Entities и Unity Physics."),
        "godot": ("g_threads", "partial", "Можно распараллелить через WorkerThreadPool."),
        "custom": ("c_ecs", "alternative", "Собственный ECS."),
    },
    "crowd_instancing_impostors": {
        "unreal": ("ue_mass", "complement", "Используется вместе с Mass Entity."),
        "unity": ("u_instancing", "direct", "GPU Instancing персонажей толпы."),
        "godot": ("g_multimesh", "direct", "MultiMeshInstance3D для толпы."),
        "custom": ("c_render_graph", "alternative", "Инстансинг в собственном графе рендера."),
    },
    "agent_update_budget": {
        "unreal": ("ue_significance", "direct", "Significance Manager распределяет бюджет."),
        "unity": ("u_quality", "partial", "Требуется собственная реализация приоритизации."),
        "godot": ("g_visibility", "partial", "Ручное управление обновлением."),
        "custom": ("c_job_system", "alternative", "Собственный планировщик приоритетов."),
    },
    "navmesh_tiling_streaming": {
        "unreal": ("ue_navmesh", "direct", "Навмеш со стримингом ячеек мира."),
        "unity": ("u_navmesh", "partial", "NavMesh Components с рантайм-сборкой."),
        "godot": ("g_navigation", "partial", "NavigationServer3D, стриминг вручную."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "time_sliced_pathfinding": {
        "unreal": ("ue_navmesh", "partial", "Ограничение запросов настраивается."),
        "unity": ("u_jobs", "direct", "Поиск пути в C# Job System."),
        "godot": ("g_navigation", "partial", "Ограничение числа запросов вручную."),
        "custom": ("c_job_system", "alternative", "Собственная очередь запросов."),
    },
    "flow_field_pathing": {
        "unreal": ("ue_mass", "partial", "Возможна реализация на Mass Entity."),
        "unity": ("u_dots", "direct", "Удобно реализовывать на ECS с Burst."),
        "godot": ("g_navigation", "partial", "Требуется собственная реализация."),
        "custom": ("c_ecs", "alternative", "Собственная реализация в ECS."),
    },
    "gerstner_fft_water": {
        "unreal": ("ue_niagara", "partial", "Реализуется шейдером воды, Niagara для пены."),
        "unity": ("u_srp", "partial", "Шейдер воды в URP/HDRP."),
        "godot": ("g_gpu_particles", "partial", "Шейдер воды, GPU-частицы для брызг."),
        "custom": ("c_render_graph", "alternative", "Проход воды в графе рендера."),
    },
    "screen_space_water_simple": {
        "unreal": ("ue_niagara", "partial", "Материал воды с экранными эффектами."),
        "unity": ("u_srp", "direct", "Готовый шейдер воды в URP."),
        "godot": ("g_visibility", "partial", "Простой материал воды."),
        "custom": ("c_render_graph", "alternative", "Проход воды в графе рендера."),
    },
    "froxel_volumetric_fog": {
        "unreal": ("ue_lumen", "direct", "Объёмный туман интегрирован в конвейер."),
        "unity": ("u_srp", "direct", "Volumetric Fog в HDRP."),
        "godot": ("g_shadows", "partial", "Ограниченная поддержка объёмов."),
        "custom": ("c_render_graph", "alternative", "Проход объёмов в графе рендера."),
    },
    "volumetric_half_resolution": {
        "unreal": ("ue_lumen", "complement", "Настройка разрешения объёмов."),
        "unity": ("u_quality", "direct", "Настройка разрешения объёмного тумана в HDRP."),
        "godot": ("g_shadows", "partial", "Требуется собственная реализация."),
        "custom": ("c_render_graph", "alternative", "Проход в пониженном разрешении."),
    },
    "temporal_upscaling": {
        "unreal": ("ue_lumen", "complement", "Работает совместно с временным накоплением."),
        "unity": ("u_srp", "direct", "Встроенные апскейлеры в URP/HDRP."),
        "godot": ("g_visibility", "partial", "Ограниченная поддержка, требуется настройка."),
        "custom": ("c_render_graph", "missing", "Реализуется полностью самостоятельно."),
    },
    "dynamic_resolution_scaling": {
        "unreal": ("ue_insights", "diagnostic", "Unreal Insights помогает подобрать пороги."),
        "unity": ("u_quality", "direct", "Dynamic Resolution в URP/HDRP."),
        "godot": ("g_profiler", "direct", "Масштабирование viewport с контролем через профилировщик."),
        "custom": ("c_render_graph", "alternative", "Собственное управление разрешением."),
    },
    "deferred_forward_plus_choice": {
        "unreal": ("ue_lumen", "direct", "Отложенное затенение используется по умолчанию."),
        "unity": ("u_srp", "direct", "Выбор между URP (forward+) и HDRP (deferred)."),
        "godot": ("g_gi", "direct", "Конвейер Godot 4 — forward+, выбирается настройками."),
        "custom": ("c_render_graph", "direct", "Архитектура определяется графом рендера."),
    },
    "variable_rate_shading": {
        "unreal": ("ue_insights", "diagnostic", "Unreal Insights для оценки выигрыша."),
        "unity": ("u_srp", "limited", "Ограниченная поддержка в HDRP."),
        "godot": ("g_profiler", "missing", "Встроенной поддержки нет."),
        "custom": ("c_render_graph", "missing", "Реализуется полностью самостоятельно."),
    },
    "network_relevancy_priority": {
        "unreal": ("ue_replication_graph", "direct", "Replication Graph для массовой репликации."),
        "unity": ("u_netcode", "direct", "Netcode for Entities с приоритизацией."),
        "godot": ("g_multiplayer", "partial", "MultiplayerAPI, релевантность вручную."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "client_prediction_reconciliation": {
        "unreal": ("ue_networking", "direct", "CharacterMovementComponent с предсказанием и реконсиляцией."),
        "unity": ("u_netcode", "direct", "Предсказание в Netcode for Entities."),
        "godot": ("g_multiplayer", "partial", "Базовый API, предсказание реализуется вручную."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "delta_compression_state": {
        "unreal": ("ue_replication_graph", "complement", "Дополняет граф репликации."),
        "unity": ("u_netcode", "direct", "Встроенная дельта-компрессия."),
        "godot": ("g_multiplayer", "partial", "Требуется собственная реализация."),
        "custom": ("c_manual", "missing", "Реализуется полностью самостоятельно."),
    },
    "headless_dedicated_server": {
        "unreal": ("ue_networking", "direct", "Сборка Dedicated Server."),
        "unity": ("u_netcode", "direct", "Сборка Dedicated Server Build."),
        "godot": ("g_multiplayer", "direct", "Экспорт без графики с MultiplayerAPI."),
        "custom": ("c_manual", "direct", "Собственная серверная сборка."),
    },
}

# ---------------------------------------------------------------------------
# Конфликты, зависимости и усиления (MVP: не менее 10 записей)
#
# Удалённые связи (калибровка FULL225, см. CALIBRATION_FULL225.md):
# связь признаётся ложной, только если реальные shipped-игры доказывают
# обратное. Удаление здесь НЕ чистит старые БД (сидер делает upsert):
# удаление выполняет миграция alembic (см. versions/*_drop_false_conflicts.py).
#  - baked_occlusion_culling × world_partition_streaming (conflict):
#    Fallout 4 previs — по-ячеечная запечённая видимость в стримимом Бостоне.
#  - dynamic_resolution_scaling × temporal_upscaling (conflict):
#    штатная связка DRS+TSR/DLSS (Forza, Remnant II, Jedi Survivor, SH2).
#  - fixed_timestep_physics → multithreaded_physics_jobs (dependency):
#    направление перепутано; однонитевый фикс-степ — норма
#    (Undertale, Geometry Dash, файтинги). Обратное направление тоже ложно
#    как универсальное (Fortnite/Chaos), поэтому строка удалена, а не развёрнута.
#  - client_prediction_reconciliation → fixed_timestep_physics (dependency):
#    UE4-предикт работает на переменном шаге через timestamped replay
#    (DBD, Sea of Thieves, PAYDAY 3). Для rollback — см. cons метода.
#  - ecs_data_oriented_crowd → gpu_skinning_compute (dependency):
#    сотни агентов штатно анимируются на CPU (BG3, Overwatch — 12 героев).
#  - headless_dedicated_server → client_prediction_reconciliation (dependency):
#    авторитетные серверы без предикта — норма (WoW, Terraria, Factorio).
#  - destruction_geometry_cache → async_loading_pipeline (dependency,
#    в EXTRA_CONFLICTS ниже): линейные игры предзагружают кэши на загрузке
#    уровня (MGR:R, Teardown) без асинхронного стриминга.
# ---------------------------------------------------------------------------
CONFLICTS: list[dict] = [
    {
        "a_code": "lightmap_atlas_baking", "b_code": "hardware_raytraced_gi", "conflict_type": "conflict",
        "severity": 3,
        "description": "Запечённое и полностью динамическое освещение дублируют друг друга: результат "
                       "освещения суммируется, а стоимость разработки удваивается.",
        "resolution": "Выбрать одну схему освещения до начала производства контента.",
        "source_key": "WIKI_LIGHTMAP",
    },
    {
        "a_code": "gpu_procedural_placement", "b_code": "lightmap_atlas_baking", "conflict_type": "conflict",
        "severity": 3,
        "description": "Объекты, размещаемые в рантайме, не могут получить запечённое освещение: "
                       "лайтмап существует только для заранее известной геометрии.",
        "resolution": "Использовать зонды освещённости для процедурных объектов или отказаться от запекания.",
        "source_key": "UNITY_LIGHTPROBES",
    },
    {
        "a_code": "cascaded_shadow_maps", "b_code": "distance_field_shadows", "conflict_type": "conflict",
        "severity": 1,
        "description": "Два механизма теней для направленного света дублируют стоимость и дают "
                       "непредсказуемое наложение результатов.",
        "resolution": "Выбрать одну систему теней как основную.",
        "source_key": "WIKI_SHADOWMAP",
    },
    {
        "a_code": "motion_matching", "b_code": "animation_compression", "conflict_type": "conflict",
        "severity": 2,
        "description": "Сильное сжатие анимаций искажает позы, что ухудшает точность подбора "
                       "движений в motion matching.",
        "resolution": "Исключить из сжатия движения, участвующие в базе motion matching.",
        "source_key": "WIKI_SKINNING",
    },
    {
        "a_code": "static_shadow_caching", "b_code": "hardware_raytraced_gi", "conflict_type": "conflict",
        "severity": 2,
        "description": "Кэширование теней предполагает неизменное освещение, тогда как аппаратная "
                       "трассировка строится на полностью динамическом освещении.",
        "resolution": "Кэшировать только тени статических источников света.",
        "source_key": "UE_VSM",
    },
    {
        "a_code": "virtual_texturing", "b_code": "heightmap_compression", "conflict_type": "synergy",
        "severity": 1,
        "description": "Сжатие тайлов повышает эффективность кэша виртуального текстурирования "
                       "и снижает трафик подкачки.",
        "resolution": "Применять совместно.",
        "source_key": "UE_VIRTUALTEXTURING",
    },
    {
        "a_code": "gpu_particle_simulation", "b_code": "particle_pooling", "conflict_type": "synergy",
        "severity": 1,
        "description": "Пулинг устраняет аллокации при создании GPU-систем частиц, сохраняя "
                       "стабильность времени кадра.",
        "resolution": "Применять совместно.",
        "source_key": "WIKI_OBJECTPOOL",
    },
    {
        "a_code": "agent_update_budget", "b_code": "crowd_instancing_impostors", "conflict_type": "synergy",
        "severity": 1,
        "description": "Снижение частоты обновления дальних агентов незаметно при их отрисовке "
                       "упрощёнными представлениями.",
        "resolution": "Применять совместно для массовых сцен.",
        "source_key": "UE_SIGNIFICANCE",
    },
    {
        "a_code": "network_relevancy_priority", "b_code": "delta_compression_state", "conflict_type": "synergy",
        "severity": 1,
        "description": "Дельта-компрессия максимально эффективна при ограниченном и стабильном "
                       "наборе релевантных объектов.",
        "resolution": "Применять совместно.",
        "source_key": "WIKI_DELTA",
    },
]


# Методы, классифицируемые как общие методы оптимизации (остальные — варианты
# реализации игровой функции). Разделение используется в интерфейсе и фильтрах.
OPTIMIZATION_CODES = {
    "hierarchical_lod", "gpu_compute_culling", "baked_occlusion_culling", "async_loading_pipeline",
    "heightmap_compression", "impostors_billboards", "vegetation_atlas_lod", "screen_space_gi",
    "temporal_radiance_cache", "gpu_lightmap_baking", "lightmap_compression_streaming",
    "screen_space_contact_shadows", "static_shadow_caching", "particle_pooling", "flipbook_particles",
    "physics_lod_sleeping", "multithreaded_physics_jobs", "broadphase_spatial_partitioning",
    "animation_compression", "animation_lod_budget", "crowd_instancing_impostors",
    "agent_update_budget", "time_sliced_pathfinding", "volumetric_half_resolution",
    "temporal_upscaling", "dynamic_resolution_scaling", "variable_rate_shading",
    "delta_compression_state",
    # 2D / 2.5D: общие методы оптимизации
    "sprite_sheet_compression", "tilemap_layer_culling", "sprite_particle_atlas",
    "shadow_caster_2d_limits", "collision_layer_matrix", "post_effect_selective",
    "depth_prepass_early_z",
    # Альтернативные методы Треков 1–2
    "hiz_software_occlusion", "pso_precaching_warmup", "audio_occlusion_propagation",
    "destruction_geometry_cache", "deterministic_lockstep", "quality_tier_scalability",
    "ml_frame_generation", "splitscreen_render_budget", "tickrate_budgeting",
    "bindless_uber_shaders",
    # Пополнение по разборам субтитров и документации (2026)
    "mesh_index_optimization", "neural_texture_compression", "planar_reflection_budget",
    "normal_bake_retopology_pipeline", "build_size_startup_budgets",
    "differential_patch_pipeline", "audio_streaming_compression",
    "composition_bootstrap_architecture",
    "art_direction_stylization", "srp_batcher_discipline",
    "tiled_clustered_light_culling", "managed_gc_alloc_budget",
}

# Полезная классификация не должна зависеть от того, был ли метод изначально
# добавлен как «общий». Карточки реальных игр используют эти решения внутри
# конкретных подсистем, поэтому отсутствие function_code скрывает их от
# фильтрации, объяснений и расчёта профиля.
FUNCTION_ASSIGNMENTS: dict[str, str] = {
    "art_direction_stylization": "art_pipeline",
    "audio_occlusion_propagation": "audio_system",
    "audio_streaming_compression": "audio_system",
    "bindless_uber_shaders": "rendering_architecture",
    "build_size_startup_budgets": "build_delivery",
    "composition_bootstrap_architecture": "project_architecture",
    "destruction_geometry_cache": "destruction_simulation",
    "deterministic_lockstep": "multiplayer_netcode",
    "differential_patch_pipeline": "build_delivery",
    "hiz_software_occlusion": "rendering_architecture",
    "managed_gc_alloc_budget": "runtime_memory",
    "mesh_index_optimization": "geometry_pipeline",
    "ml_frame_generation": "upscaling_frame_generation",
    "normal_bake_retopology_pipeline": "art_pipeline",
    "pso_precaching_warmup": "rendering_architecture",
    "quality_tier_scalability": "render_scalability",
    "splitscreen_render_budget": "split_screen_rendering",
    "srp_batcher_discipline": "rendering_architecture",
    "tickrate_budgeting": "multiplayer_netcode",
    "tiled_clustered_light_culling": "rendering_architecture",
}


# Короткий, проверяемый план внедрения для штатных методов каталога. Пустой
# application_steps превращает запись в декларацию без практического способа
# проверки, поэтому для опубликованных методов он не должен оставаться
# значением по умолчанию.
APPLICATION_STEPS: dict[str, list[str]] = {
    "agent_update_budget": [
        "Разделить обновление агентов на группы по расстоянию и важности.",
        "Задать бюджет времени кадра и максимальное число обновлений за тик.",
        "Проверить задержку реакции агентов на типичных сценах.",
    ],
    "animation_lod_budget": [
        "Определить уровни детализации скелета и допустимые дистанции.",
        "Ограничить число одновременно обновляемых персонажей.",
        "Проверить popping, CPU-время и качество переходов.",
    ],
    "async_loading_pipeline": [
        "Разделить ресурсы на независимые пакеты загрузки.",
        "Вынести чтение и распаковку в фоновые очереди.",
        "Проверить пики IO, время кадра и отсутствие блокирующих переходов.",
    ],
    "baked_occlusion_culling": [
        "Разбить уровни на ячейки и подготовить наборы видимости.",
        "Запечь окклюзию для типовых камер и маршрутов.",
        "Сверить количество отрисованных объектов до и после запекания.",
    ],
    "crowd_instancing_impostors": [
        "Сгруппировать повторяющиеся модели и подготовить варианты impostor.",
        "Перевести массовые экземпляры на instancing с дистанционными LOD.",
        "Проверить draw calls, CPU-обновления и визуальные артефакты.",
    ],
    "deferred_forward_plus_choice": [
        "Составить матрицу материалов, прозрачности и числа источников света.",
        "Сравнить deferred и Forward+ на representative-сценах.",
        "Зафиксировать режим по GPU-времени, памяти и качеству освещения.",
    ],
    "dynamic_resolution_scaling": [
        "Задать целевое время кадра и допустимый диапазон разрешения.",
        "Подключить обратную связь по GPU frame time с ограничением шага.",
        "Проверить стабильность масштаба и читаемость интерфейса.",
    ],
    "fixed_timestep_physics": [
        "Выбрать фиксированный physics tick и правила накопления времени.",
        "Разделить физический шаг и визуальную интерполяцию.",
        "Проверить стабильность столкновений при разном FPS.",
    ],
    "flow_field_pathing": [
        "Разбить навигацию на сектора и построить поля направлений.",
        "Кэшировать поля для общих целей и обновлять их по событию.",
        "Проверить стоимость перестроения и обход динамических препятствий.",
    ],
    "gpu_instancing_vegetation": [
        "Сгруппировать растительность по материалам и диапазонам дистанций.",
        "Подготовить GPU-данные экземпляров и варианты LOD.",
        "Проверить плотность, overdraw и стабильность GPU frame time.",
    ],
    "gpu_particle_simulation": [
        "Определить частицы, которым нужна параллельная обработка на GPU.",
        "Задать лимиты буферов, эмиттеров и стоимость сортировки.",
        "Сравнить GPU-время и поведение при заполнении буфера.",
    ],
    "gpu_procedural_placement": [
        "Определить seed, области генерации и детерминированные правила.",
        "Выполнить размещение в compute-проходе с ограниченным бюджетом.",
        "Проверить повторяемость, коллизии и время генерации при стриминге.",
    ],
    "hardware_raytraced_gi": [
        "Ограничить лучи, bounce и радиус трассировки по целевому GPU.",
        "Добавить fallback для оборудования без аппаратного RT.",
        "Проверить latency, шум, память и качество в динамических сценах.",
    ],
    "headless_dedicated_server": [
        "Выделить серверную сборку без рендера и клиентских ассетов.",
        "Задать лимиты тиков, соединений и логирования.",
        "Проверить запуск, повторное подключение и нагрузку без GPU.",
    ],
    "hierarchical_lod": [
        "Разделить сцену на группы и определить уровни детализации.",
        "Настроить дистанции, hysteresis и правила переходов.",
        "Проверить popping, draw calls и время построения LOD.",
    ],
    "multithreaded_physics_jobs": [
        "Разбить физический шаг на независимые jobs без гонок данных.",
        "Настроить worker pool и барьеры синхронизации.",
        "Проверить масштабирование по ядрам и детерминизм результатов.",
    ],
    "navmesh_tiling_streaming": [
        "Разделить navmesh на тайлы, совпадающие с зонами стриминга.",
        "Строить и выгружать тайлы асинхронно по радиусу активности.",
        "Проверить связность маршрутов на границах тайлов.",
    ],
    "particle_pooling": [
        "Задать верхние лимиты эмиттеров и частиц по сценам.",
        "Переиспользовать объекты вместо частого выделения и освобождения.",
        "Проверить пики CPU, память пула и корректное восстановление состояния.",
    ],
    "physics_lod_sleeping": [
        "Разделить физические тела по расстоянию и важности.",
        "Усыплять удалённые тела и снижать частоту их обновления.",
        "Проверить пробуждение, столкновения и отсутствие пропуска событий.",
    ],
    "post_effect_selective": [
        "Составить список эффектов по сценам и уровням качества.",
        "Отключать дорогие проходы вне нужных условий и разрешения.",
        "Проверить GPU-время, порядок композитинга и визуальные артефакты.",
    ],
    "screen_space_gi": [
        "Задать радиус, число шагов и временное накопление GI.",
        "Добавить fallback при выходе отражения за экран.",
        "Проверить ghosting, шум и стоимость на целевых разрешениях.",
    ],
    "temporal_upscaling": [
        "Выбрать внутреннее разрешение и диапазон динамического масштаба.",
        "Подать корректные motion vectors и историю кадров.",
        "Проверить ghosting, резкость и GPU-время на движении камеры.",
    ],
    "time_sliced_pathfinding": [
        "Разбить поиск пути на небольшие квоты работы по кадрам.",
        "Задать приоритеты запросов и очередь отмены устаревших задач.",
        "Проверить latency получения пути и равномерность CPU-нагрузки.",
    ],
    "virtual_shadow_maps": [
        "Задать размер страниц и лимит кэша виртуальных теней.",
        "Настроить обновление страниц по движению источников и камеры.",
        "Проверить page faults, память и качество дальних теней.",
    ],
    "volumetric_half_resolution": [
        "Выполнять объёмный проход в половинном разрешении с апсемплингом.",
        "Ограничить число шагов и дальность интегрирования.",
        "Проверить banding, ghosting и выигрыш GPU-времени.",
    ],
    "world_partition_streaming": [
        "Определить размер ячеек и радиусы загрузки/выгрузки.",
        "Разнести IO, распаковку и активацию ресурсов по очередям.",
        "Проверить hitching, память и переходы между соседними ячейками.",
    ],
    "animation_compression": [
        "Выбрать допустимую ошибку позиции, вращения и масштаба.",
        "Сжать клипы и исключить движения, чувствительные к потере точности.",
        "Проверить CPU-время декодирования и качество поз на крайних кадрах.",
    ],
    "broadphase_spatial_partitioning": [
        "Выбрать структуру broadphase и размер пространственных ячеек.",
        "Обновлять только переместившиеся объекты и фильтровать пары слоями.",
        "Проверить число кандидатов и стоимость перестроения при массовом движении.",
    ],
    "cascaded_shadow_maps": [
        "Разбить дальность камеры на каскады с отдельными матрицами света.",
        "Настроить bias, размер карт и стабилизацию границ.",
        "Проверить shimmering, peter-panning и GPU-время на дальних сценах.",
    ],
    "client_prediction_reconciliation": [
        "Буферизовать ввод клиента с последовательными номерами команд.",
        "Повторно применять неподтверждённые команды после серверного снапшота.",
        "Проверить расхождение позиций при задержке, потере и reorder пакетов.",
    ],
    "collision_layer_matrix": [
        "Описать слои объектов и разрешённые пары столкновений.",
        "Применить маски до narrowphase и запретить лишние проверки.",
        "Проверить контакты, триггеры и обратную совместимость уровней.",
    ],
    "crowd_2d_instancing": [
        "Сгруппировать повторяющиеся 2D-спрайты по атласам и материалам.",
        "Добавить instancing и дистанционное снижение детализации.",
        "Проверить draw calls, overdraw и читаемость толпы.",
    ],
    "delta_compression_state": [
        "Выбрать baseline-снапшот и список полей, передаваемых по изменению.",
        "Квантизовать значения без нарушения игровой логики.",
        "Измерить bandwidth, задержку восстановления и ошибки состояния.",
    ],
    "depth_prepass_early_z": [
        "Выделить непрозрачные материалы с высоким overdraw.",
        "Добавить depth prepass только там, где он окупает дополнительный проход.",
        "Сравнить overdraw, пропуски фрагментов и GPU-время.",
    ],
    "distance_field_shadows": [
        "Подготовить distance fields для статической геометрии.",
        "Задать радиус, качество и fallback для объектов без поля.",
        "Проверить контактные тени, память и артефакты на тонкой геометрии.",
    ],
    "ecs_data_oriented_crowd": [
        "Разложить состояние агентов на компоненты с плотным хранением.",
        "Обрабатывать одинаковые системы пакетно и без виртуальных вызовов.",
        "Проверить cache misses, время систем и масштабирование числа агентов.",
    ],
    "flipbook_particles": [
        "Подготовить атлас кадров эффекта с одинаковой сеткой.",
        "Перенести выбор кадра в GPU и ограничить частоту обновления.",
        "Проверить память атласа, alpha overdraw и переходы кадров.",
    ],
    "froxel_volumetric_fog": [
        "Задать трёхмерную froxel-сетку и диапазон глубины.",
        "Интегрировать свет в ограниченном числе шагов с temporal reuse.",
        "Проверить шум, banding, память и GPU-время на целевых разрешениях.",
    ],
    "gerstner_fft_water": [
        "Выбрать спектр волн и параметры Gerstner/FFT для водоёма.",
        "Обновлять поверхность на GPU и ограничить число гармоник.",
        "Проверить береговую линию, отражения и стоимость при шторме.",
    ],
    "gpu_compute_culling": [
        "Собрать буфер экземпляров с bounds и уровнями детализации.",
        "Выполнить frustum/occlusion culling в compute и indirect draw.",
        "Проверить синхронизацию буферов, overdraw и выигрыш CPU.",
    ],
    "gpu_lightmap_baking": [
        "Подготовить UV-каналы и разделить статическую геометрию по сценам.",
        "Запустить GPU bake с ограничением памяти и размера атласов.",
        "Проверить швы, шум, время сборки и расход видеопамяти.",
    ],
    "gpu_skinning_compute": [
        "Перенести матрицы костей и вершины в GPU-буферы.",
        "Выполнять skinning compute-проходом перед отрисовкой.",
        "Проверить sync points, деформации и выигрыш CPU на толпе.",
    ],
    "heightmap_compression": [
        "Выбрать формат сжатия высот с допустимой ошибкой рельефа.",
        "Хранить тайлы и распаковывать их при загрузке нужной области.",
        "Проверить память, время распаковки и артефакты силуэта.",
    ],
    "impostors_billboards": [
        "Снять набор представлений объекта и подготовить atlas.",
        "Задать дистанции перехода и hysteresis для billboard.",
        "Проверить силуэт, освещение и popping при вращении камеры.",
    ],
    "irradiance_volume_probes": [
        "Разместить probes по объёму с учётом размеров комнат и улиц.",
        "Запечь или обновлять irradiance в заданном бюджете.",
        "Проверить утечки света, память и поведение при смене освещения.",
    ],
    "lightmap_2d_baking": [
        "Разметить неподвижные 2D-светильники и их области влияния.",
        "Запечь освещение в атлас с отдельным слоем для динамики.",
        "Проверить масштабирование камеры, память и резкость спрайтов.",
    ],
    "lightmap_atlas_baking": [
        "Подготовить вторичные UV и задать плотность texel для объектов.",
        "Собрать lightmap-атласы с контролем padding и швов.",
        "Проверить качество теней, память и время пересборки уровня.",
    ],
    "lightmap_compression_streaming": [
        "Выбрать формат lightmap с учётом HDR и целевого GPU.",
        "Разделить атласы по зонам и загружать их вместе с уровнем.",
        "Проверить размер сборки, hitching и качество декомпрессии.",
    ],
    "motion_matching": [
        "Собрать размеченную базу движений и признаки позы.",
        "Настроить поиск ближайшего клипа и плавное blending.",
        "Проверить latency поиска, память базы и ошибки переходов.",
    ],
    "network_relevancy_priority": [
        "Разделить мир на зоны видимости и задать приоритеты сущностей.",
        "Отправлять редкие обновления для дальних или неважных объектов.",
        "Проверить bandwidth, пропуски событий и восстановление при смене зоны.",
    ],
    "screen_space_contact_shadows": [
        "Ограничить длину screen-space луча и число шагов.",
        "Добавить fallback для объектов вне глубинного буфера.",
        "Проверить ghosting, шум и стоимость эффекта на разных разрешениях.",
    ],
    "screen_space_water_simple": [
        "Выделить поверхность воды и подготовить depth/refraction данные.",
        "Считать отражение и искажение только в экранной области.",
        "Проверить исчезновение объектов за экраном и стоимость прохода.",
    ],
    "sdf_global_illumination": [
        "Построить SDF для статической геометрии и задать размер вокселя.",
        "Трассировать ограниченное число конусов с temporal accumulation.",
        "Сравнить утечки света, шум, память и GPU-время с fallback.",
    ],
    "shadow_caster_2d_limits": [
        "Ограничить число shadow caster-полигонов на камеру.",
        "Объединять простые контуры и отключать дальние источники.",
        "Проверить тени на перекрытиях и стоимость в сценах с толпой.",
    ],
    "skeletal_2d_deform": [
        "Задать кости, веса вершин и допустимую глубину иерархии.",
        "Выполнять деформацию пакетно для видимых персонажей.",
        "Проверить CPU/GPU-время, артефакты весов и память поз.",
    ],
    "sprite_atlas_batching": [
        "Собрать спрайты в атласы по материалам и форматам альфа.",
        "Сохранить единый материал и сортировку внутри batch.",
        "Проверить draw calls, bleed по краям и размер атласов.",
    ],
    "sprite_particle_atlas": [
        "Разместить варианты частиц в атласе с padding и mip-правилами.",
        "Выбирать tile через UV-индекс без смены материала.",
        "Проверить overdraw, память и корректность альфа-канала.",
    ],
    "sprite_sheet_compression": [
        "Выбрать формат сжатия, сохраняющий резкие границы альфа.",
        "Настроить mipmaps и padding для соседних кадров.",
        "Проверить размер сборки, мерцание и качество на разных масштабах.",
    ],
    "static_shadow_caching": [
        "Пометить источники и геометрию, которые не меняются в рантайме.",
        "Кэшировать их вклад и инвалидировать только при изменении сцены.",
        "Проверить корректность после перемещения динамических объектов.",
    ],
    "temporal_radiance_cache": [
        "Определить history buffer и правила reprojection для освещения.",
        "Отбрасывать устаревшую историю по движению камеры и объектов.",
        "Проверить ghosting, flicker и выигрыш GPU на динамических сценах.",
    ],
    "terrain_clipmap": [
        "Разбить terrain на кольца clipmap с разной детализацией.",
        "Обновлять только пересекаемые камерой полосы высот.",
        "Проверить швы колец, память и стоимость перемещения на большой скорости.",
    ],
    "tilemap_chunk_streaming": [
        "Выбрать размер чанка и границы, совпадающие с маршрутом камеры.",
        "Загружать соседние чанки заранее и выгружать дальние.",
        "Проверить hitching, коллизии и стыки тайлов при переходе.",
    ],
    "tilemap_layer_culling": [
        "Разделить слои тайлмапа по дистанции и важности.",
        "Отсекать невидимые слои до формирования draw calls.",
        "Проверить порядок слоёв, overdraw и CPU-время.",
    ],
    "variable_rate_shading": [
        "Создать карту shading rate по движению, периферии и важности.",
        "Задать fallback для GPU без VRS и ограничить резкие границы.",
        "Проверить качество мелких деталей и фактический выигрыш GPU.",
    ],
    "vegetation_atlas_lod": [
        "Собрать atlas растительности с несколькими уровнями детализации.",
        "Настроить переходы, alpha-test и дистанционный billboard.",
        "Проверить overdraw, popping и память текстур.",
    ],
    "virtual_geometry_clusters": [
        "Разбить меши на кластеры с bounds и иерархией детализации.",
        "Настроить streaming и culling кластеров по экранному размеру.",
        "Проверить память, page faults и стабильность GPU-времени.",
    ],
    "voxel_cone_tracing": [
        "Вокселизировать статическую сцену с выбранным разрешением.",
        "Трассировать конусы с ограничением числа mip-уровней и bounce.",
        "Проверить утечки света, шум и стоимость против более простого fallback.",
    ],
    "world_origin_shifting": [
        "Определить радиус, после которого центр мира переносится к игроку.",
        "Синхронно сдвигать трансформы, физику, аудио и сетевые координаты.",
        "Проверить точность дальних объектов и корректность сохранений.",
    ],
}


def all_methods() -> list[dict]:
    """Полный список методов с учётом расширений применимости."""
    merged = list(METHODS) + list(EXTRA_METHODS)
    out = []
    for m in merged:
        data = dict(m)
        if data["code"] in FORMAT_OVERRIDES:
            data["applicable_formats"] = list(FORMAT_OVERRIDES[data["code"]])
        if data["code"] in CONCEPT_IMPACT_OVERRIDES:
            data["concept_impact"] = CONCEPT_IMPACT_OVERRIDES[data["code"]]
        if not data.get("function_code"):
            data["function_code"] = FUNCTION_ASSIGNMENTS.get(data["code"])
        if not data.get("application_steps"):
            data["application_steps"] = list(APPLICATION_STEPS.get(data["code"], []))
        out.append(data)
    return out


# ---------------------------------------------------------------------------
# Связи Трека 1 для новых движков (CryEngine / Source / HeroEngine).
# Только новые движки: слияние идёт по методам, поэтому существующие связи
# unreal / unity / godot / custom не затираются (GRASP: информация — у метода).
# Тип связи честный: direct — есть из коробки, partial/alternative — с работой
# руками, missing — нет аналога (встроенное не абсолют).
# ---------------------------------------------------------------------------
TRACK1_ENGINE_LINKS: dict[str, dict[str, tuple[str, str, str]]] = {
    "hierarchical_lod": {
        "cryengine": ("ce_merged", "direct", "Merged Meshes и LOD-цепочки для открытого мира."),
    },
    "gpu_instancing_vegetation": {
        "cryengine": ("ce_vegetation", "direct", "Инстансинг и покраска вегетации по маскам."),
    },
    "sdf_global_illumination": {
        "cryengine": ("ce_svogi", "direct", "SVOGI/SVOTI: конусная трассировка по вокселям."),
    },
    "volumetric_half_resolution": {
        "cryengine": ("ce_fog", "direct", "Объёмный туман и облака с половинным разрешением."),
    },
    "async_loading_pipeline": {
        "cryengine": ("ce_merged", "partial", "Стриминг через merged-группы и LOD-дистанции."),
        "source": ("s_vphysics", "missing", "Конвейера стриминга нет: BSP-хабы грузятся целиком."),
        "heroengine": ("h_instancing", "alternative", "Вместо бесшовного стриминга — инстансинг планет."),
    },
    "gpu_compute_culling": {
        "cryengine": ("ce_merged", "missing", "GPU-driven culling нет, только merged-батчи и дистанции."),
    },
    "cascaded_shadow_maps": {
        "cryengine": ("ce_svogi", "partial", "Каскады есть, дальний план закрывает воксельное затенение."),
    },
    "fixed_timestep_physics": {
        "source": ("s_vphysics", "direct", "Фиксированный шаг VPhysics/Rubikon с интерполяцией."),
        "heroengine": ("h_hsl", "missing", "Фикс-тик задаётся скриптами, не движком."),
    },
    "physics_lod_sleeping": {
        "source": ("s_vphysics", "direct", "Сон и пробуждение тел — базовый механизм VPhysics."),
    },
    "broadphase_spatial_partitioning": {
        "source": ("s_vphysics", "partial", "Широкая фаза внутри VPhysics, без отдельного API."),
    },
    "network_relevancy_priority": {
        "source": ("s_netcode", "partial", "Релевантность через PVS и дистанции, без графа зон."),
        "heroengine": ("h_instancing", "partial", "Релевантность через инстансы и фазы вместо бесшовки."),
        "cryengine": ("ce_audio", "missing", "Графа релевантности нет, только дистанции и LOD."),
    },
    "client_prediction_reconciliation": {
        "source": ("s_netcode", "direct", "Предикт, интерполяция и компенсация задержек; в CS2 — sub-tick."),
        "heroengine": ("h_cloud", "partial", "Предикт поверх авторитетного HeroCloud-сервера."),
    },
    "delta_compression_state": {
        "source": ("s_netcode", "partial", "Дельта-снапшоты и сжатие состояния в тиках."),
    },
    "headless_dedicated_server": {
        "source": ("s_netcode", "direct", "Выделенные серверы без графики — стандарт Source."),
        "heroengine": ("h_cloud", "direct", "HeroCloud: симуляционные серверы как сервис."),
    },
    "world_partition_streaming": {
        "heroengine": ("h_instancing", "alternative", "Бесшовной партиции нет: мир режется на инстансы планет."),
    },
    "temporal_upscaling": {
        "source": ("s_vulkan", "missing", "Временного апскейлера нет, только MSAA и downscale."),
        "heroengine": ("h_hsl", "missing", "Апскейлеров нет, только снижение разрешения."),
    },
    # --- Альтернативные методы: честные связки по движкам ------------------
    "hiz_software_occlusion": {
        "unreal": ("ue_nanite", "partial", "Nanite делает двухпроходное отсечение внутри, отдельного Hi-Z нет."),
        "unity": ("u_occlusion", "partial", "Запечённая окклюзия покрывает статику, динамики — нет."),
        "godot": ("g_occluder", "partial", "Окклюдеры расставляются вручную."),
        "custom": ("c_render_graph", "direct", "Hi-Z проход в собственном графе рендера."),
        "cryengine": ("ce_merged", "missing", "Отдельного Hi-Z нет, только merged-батчи и дистанции."),
        "source": ("s_vulkan", "missing", "Программного Hi-Z нет, только areaportals."),
        "heroengine": ("h_hsl", "missing", "Отсечение не строится, только дистанции."),
    },
    "pso_precaching_warmup": {
        "unreal": ("ue_insights", "diagnostic", "Hitch-детект и контроль прогрева по Insights."),
        "unity": ("u_profiler", "diagnostic", "Замер shader load time в Profiler."),
        "godot": ("g_profiler", "diagnostic", "Контроль компиляции конвейеров."),
        "custom": ("c_profiler", "direct", "Tracy-маркеры прогревов и CLI-захват."),
        "source": ("s_vprof", "diagnostic", "Замер hitch при загрузке карт."),
    },
    "audio_occlusion_propagation": {
        "cryengine": ("ce_audio", "direct", "Трассировка слышимости по геометрии и HRTF."),
        "unreal": ("ue_chaos", "missing", "Аудио-окклюзии нет — Chaos только физика."),
        "custom": ("c_manual", "missing", "Аудио-трассировка пишется самостоятельно."),
        "godot": ("g_physics_server", "missing", "Лучи только для физики, не для звука."),
        "source": ("s_vphysics", "missing", "Звуковой окклюзии нет."),
        "heroengine": ("h_hsl", "missing", "Считается скриптами, не движком."),
    },
    "destruction_geometry_cache": {
        "unreal": ("ue_chaos", "alternative", "Chaos — realtime-фрактура вместо запечённого playback."),
        "unity": ("u_addressables", "partial", "Кэши стримятся бандлами."),
        "godot": ("g_bg_loading", "partial", "Кэши подгружаются фоновым загрузчиком."),
        "custom": ("c_streaming", "partial", "Кэши идут общим конвейером стриминга."),
    },
    "deterministic_lockstep": {
        "source": ("s_netcode", "alternative", "Valve-модель — снапшоты и предикт, а не lockstep."),
        "unity": ("u_netcode", "partial", "Netcode for Entities ближе к детерминизму."),
        "godot": ("g_multiplayer", "partial", "Детерминизм собирается вручную поверх API."),
        "custom": ("c_manual", "missing", "Фикс-точка и RNG пишутся самостоятельно."),
        "heroengine": ("h_cloud", "alternative", "Авторитетный сим вместо lockstep."),
    },
    "quality_tier_scalability": {
        "unity": ("u_quality", "direct", "Тиры качества и per-platform overrides."),
        "unreal": ("ue_insights", "missing", "Scalability Groups настраиваются вручную."),
        "godot": ("g_visibility", "missing", "Тиров нет, только ручные дистанции."),
        "custom": ("c_manual", "missing", "Тиры и адаптивный cap пишутся самостоятельно."),
    },
    "ml_frame_generation": {
        "unreal": ("ue_insights", "diagnostic", "Замер latency генерации."),
        "unity": ("u_profiler", "diagnostic", "Замер latency генерации."),
        "godot": ("g_profiler", "diagnostic", "Замер latency генерации."),
        "custom": ("c_profiler", "diagnostic", "Замер latency через Tracy."),
        "source": ("s_vprof", "diagnostic", "Замер pacing."),
    },
    "splitscreen_render_budget": {
        "unreal": ("ue_hlod", "partial", "HLOD и proxy-LOD режут двойные draw calls."),
        "unity": ("u_occlusion", "partial", "Окклюзия на две камеры."),
        "godot": ("g_visibility", "partial", "Ручное управление видимостью на вью."),
        "custom": ("c_render_graph", "alternative", "Два вью в собственном графе."),
    },
    "tickrate_budgeting": {
        "source": ("s_netcode", "direct", "Тикрейт, interp и lagcomp — ядро netcode."),
        "unity": ("u_netcode", "direct", "Тикрейт Netcode-пакетов."),
        "godot": ("g_multiplayer", "partial", "Тик настраивается поверх API."),
        "custom": ("c_manual", "missing", "Тик и bandwidth считаются самостоятельно."),
        "heroengine": ("h_cloud", "partial", "Тик серверов HeroCloud."),
    },
    "bindless_uber_shaders": {
        "custom": ("c_render_graph", "direct", "Bindless-дескрипторы в собственном графе."),
        "unreal": ("ue_nanite", "alternative", "Nanite решает мерж иначе — кластерами."),
        "unity": ("u_srp_batcher", "partial", "SRP Batcher режет смены состояний."),
        "godot": ("g_multimesh", "missing", "Bindless нет, только MultiMesh."),
        "source": ("s_vulkan", "partial", "Vulkan-бэкенд с дескрипторами."),
    },
}


def all_links() -> dict[str, dict[str, tuple[str, str, str]]]:
    """Полный набор связей методов с инструментами движков."""
    merged: dict[str, dict[str, tuple[str, str, str]]] = {k: dict(v) for k, v in METHOD_ENGINE_LINKS.items()}
    # Глубокое слияние по методам: новый словарь не должен затирать связи
    # других движков целиком (раньше update заменял весь метод).
    for source in (EXTRA_LINKS, TRACK1_ENGINE_LINKS):
        for method_code, per_engine in source.items():
            merged.setdefault(method_code, {}).update(per_engine)
    return merged


def all_conflicts() -> list[dict]:
    return list(CONFLICTS) + list(EXTRA_CONFLICTS)


def with_sources() -> tuple[list[dict], list[dict]]:
    """Подставить источники в методы и конфликты."""
    methods = []
    for m in all_methods():
        data = dict(m)
        s = src(data.pop("source_key", None))
        data["kind"] = "optimization" if data["code"] in OPTIMIZATION_CODES else "implementation"
        data["source_title"] = s["title"]
        data["source_url"] = s["url"]
        data["source_date"] = s["date"]
        methods.append(data)
    conflicts = []
    for c in all_conflicts():
        data = dict(c)
        s = src(data.pop("source_key", None))
        data["source_title"] = s["title"]
        data["source_url"] = s["url"]
        conflicts.append(data)
    return methods, conflicts
