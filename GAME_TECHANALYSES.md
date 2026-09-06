# Теханализы игр: релиз ПК, версии, репутация, решения

Глубокий разбор по каждой игре из списка: движок и ключевые техники, состояние
ПК-релиза на старте, поздние версии и что в них менялось, причина репутации
(функционал или реализация), взвешенные плюсы/минусы решений, влияние на
оптимизацию, графику и прочее. В конце каждой карточки — привязка к методам
каталога DSS для отчёта.

Легенда оценок решений: `+` — подтверждённый плюс, `−` — подтверждённый минус,
`±` — компромисс. Источники указаны в каждой карточке.

---

## Партия 1

### 1. Doom (1993, id Software)

- **Движок/рендер/сеть:** id Tech 1. Псевдо-3D на 2D-плане: BSP-дерево для порядка отрисовки (front-to-back, без runtime-сортировки), стены — вертикальные колонки, пол/потолок — visplanes (flood fill), спрайты вместо полигонов, фиксированная точка 16.16, без z-буфера. Сеть: ранний мультиплеер (deathmatch — термин родился здесь), позже моддинг и source-ports.
- **Релиз ПК:** shareware (первый эпизод бесплатно). Минимум 386/4 МБ, реально играбельно на 486DX-33. Главный лимит — 128 одновременных visplanes: превышение = вылет в DOS («No more visplanes»). Комнат друг над другом нет в принципе.
- **Версии:** Doom II, Heretic/Hexen/Strife на том же движке; исходники открыты (1997) → сотни source-ports, снявших лимиты.
- **Причина репутации:** реализация (инженерия), не контент. Кармак не стал «дожимать железо», а переформулировал задачу: предвычисление (BSP строится node builder'ом при компиляции) вместо runtime-проверок. Fun fact: BSP взяли из статьи Fuchs–Kedem–Naylor 1988, до этого альфы упирались в концентрические круги E1M2.
- **Решения:**
  - `+` BSP-предвычисление: ноль сортировки в кадре, карты любого размера без падения скорости.
  - `+` Колонки + visplanes: простая математика на пиксел.
  - `−` Плоский мир: нельзя мосты/этажи (обходили дамми-секторами), камера всегда горизонтальна.
  - `−` Жёсткие лимиты (128 visplanes, 256 сегов): ошибка дизайна уровней = вылет.
- **Влияние:** оптимизация — предвычисление вместо runtime (урок на десятилетия, BSP жил до 2000-х); графика — «2.5D» как осознанный tradedоспособ; сеть — deathmatch как жанр.
- **DSS:** `baked_occlusion_culling`, `hierarchical_lod` (идея предвычисления), `fixed_timestep_physics`.
- **Источники:** DoomWiki «Doom rendering engine» (http://doomwiki.org/wiki/Doom_rendering_engine), Wikipedia «Doom engine» (https://en.wikipedia.org/wiki/Doom_engine), Harlepengren «Doom Ran on a 486» (https://harlepengren.com/how-doom-engine-worked/).

### 2. Grand Theft Auto III (2001, DMA Design / Rockstar)

- **Движок/рендер:** RenderWare (Criterion). Первый плотный 3D-город со стримингом: город нарезан на тысячи секторов, вокруг игрока — невидимый квадрат загрузки, модели/текстуры грузятся с DVD по мере движения и выгружаются сзади. Вдали — low-poly импостеры с мутными текстурами (позже — стандарт LOD).
- **Релиз ПК (2002):** в целом удачный порт эпохи; главная боль — стриминг с HDD вместо DVD-оптимизированной раскладки. Технический потолок — DVD-привод 2–4 МБ/с и время позиционирования головки, а не GPU.
- **Версии:** Vice City и San Andreas на том же ядре с эволюцией стриминга (см. ниже).
- **Причина репутации:** реализация (стриминг 130 МБ города в 32 МБ PS2-памяти) + функционал (свобода: 360 градусов без дверей-лифтов как ширм).
- **Решения:**
  - `+` Скользящее окно загрузки: город любого размера при фиксированной памяти.
  - `+` LOD-импостеры горизонта: силуэт города бесплатно.
  - `+` Кастомный менеджер памяти + ассеты фиксированных размеров (500+ файлов ровно по 2 КБ): нет фрагментации.
  - `+` Раскладка файлов на DVD по близости в мире: меньше seeks головки.
  - `−` Игрок быстрее диска: ограничение скорости машин и скрытое сопротивление воздуха +5%, перепланировка улиц Портленда (здание посреди магистрали!), запрет полётов.
  - `−` Пул всего на 8 типов машин: клоны в трафике.
- **Влияние:** оптимизация — стриминг как базовый паттерн открытых миров до сих пор; графика — pop-in как врождённый налог; дизайн — планировка города под скорость чтения диска.
- **DSS:** `world_partition_streaming`, `hierarchical_lod`, `async_loading_pipeline`, `particle_pooling`.
- **Источники:** GMTK «How Rockstar fit an entire city into PS2 memory» (https://gmtk.substack.com/p/how-rockstar-fit-an-entire-city-into), GamesRadar + твиты Obbe Vermeij (https://www.gamesradar.com/games/grand-theft-auto/gta-3-dev-says-that-the-open-world-games-hardest-technical-challenge-was-partially-solved-with-careful-city-planning-and-some-extra-windy-weather/).

### 3. Grand Theft Auto: Vice City (2002)

- **Движок:** то же ядро RenderWare+GTA3, но вертолёты заставили решить вид сверху: выше определённой высоты показываются только low-poly модели — памяти хватает на дальние скайлайны.
- **Релиз ПК (2003):** спокойный порт; системных скандалов не было — техника уже обкатана на GTA3.
- **Причина репутации:** функционал (атмосфера 80-х, радио, вертолёты) при той же технической базе. Доказательство, что контентный скачок возможен без смены движка.
- **Решения:**
  - `+` Высотный LOD-режим: полёты без переписывания стриминга.
  - `±` Та же память и те же пулы: клоны машин, pop-in на скорости.
- **Влияние:** оптимизация — LOD по высоте как отдельный режим; графика — неон и вода как дешёвые маркеры эпохи.
- **DSS:** те же методы, что у GTA3.
- **Источники:** см. разбор GMTK выше (эволюция Vice City → San Andreas внутри).

### 4. Grand Theft Auto: San Andreas (2004)

- **Движок:** то же ядро. Прорыв — отказ от островов и экранов загрузки: пустая сельская местность между городами работает буфером (пока едешь, предыдущий город выгружается из памяти). Файл `stream.ini`: всего 13.5 МБ памяти под стриминг города.
- **Релиз ПК (2005):** хороший порт; позже — скандал с Hot Coffee (вырезанный контент в файлах, не техника) и удаление музыки из Steam-версий (лицензии).
- **Причина репутации:** функционал (штат вместо города: прокачка, банды, самолёты) на технике, выжатой до предела.
- **Решения:**
  - `+` География как буфер памяти: дизайн мира = менеджмент памяти.
  - `−` Предел достигнут: дальше так масштабироваться было некуда (ответом стал RAGE в GTA4).
- **Влияние:** оптимизация — левел-дизайн как инструмент производительности, буквально.
- **DSS:** `world_partition_streaming`, `crowd_instancing_impostors`, `time_sliced_pathfinding`.
- **Источники:** GMTK-разбор (там же), твиты Obbe Vermeij о stream.ini.

### 5. Grand Theft Auto IV (2008, Rockstar North)

- **Движок:** RAGE + Euphoria. Первый HD-город Rockstar: отложенный рендер, плотный трафик/педы, физика.
- **Релиз ПК (декабрь 2008) — провальный старт:** тормоза на заведомо достаточном железе, недогруженные текстуры, вылеты при запуске, ошибки RESC10, капризы к энергосбережению CPU; поверх — DRM-удавка (GFWL + Rockstar Social Club + SecuROM) и патчи, проходящие сертификацию Microsoft. Rockstar публично признала проблемы (IGN, декабрь 2008). Патчи 1.0.x–1.0.7 чинили краши и физику, но архитектурно игра осталась CPU-bound с однопоточными лимитами: даже годы спустя прирост даёт только грубая CPU-мощь (i5-2500K: +250%, Ryzen 9800X3D «лечит» фреймтайм).
- **Поздние версии:** патч 2016 (поддержка Win 8/10); Complete Edition 2020 — вырезаны GFWL **вместе с мультиплеером** и лидербордами; фанаты чинят сами (drawlist overflow, миссия «Out of Commission» ломалась при FPS выше 60!). Свежее: RTX Remix-мод от xoxor4d (реверс-инжиниринг DX9-кода под RTGI) — Digital Foundry, ноябрь 2025: даже RTX 5090 упирается в CPU-бутылочное горлышко, 40 fps без настройки дальности.
- **Причина репутации:** реализация (порт), не игра. Урок: однопоточный CPU-дизайн не чинится ни патчами, ни десятилетиями железа.
- **Решения:**
  - `+` Плотность и физика города как планка avem.
  - `−` GFWL как точка отказа: мертвые серверы = мёртвая игра (лечили удалением вместе с мультиплеером).
  - `−` CPU-bound без запаса: масштабирование только вверх по одному ядру.
  - `±` Сообщество как служба поддержки: моды доделывают то, что не доделал издатель.
- **Влияние:** оптимизация — антипример: reservas CPU-бюджета и отказ от DRM-цепочек; графика — RT-мод возможен даже на DX9-коде, но упирается в ту же стену.
- **DSS:** `fixed_timestep_physics`, `time_sliced_pathfinding`; риски late_streaming/deadline_pressure, `crowd_instancing_impostors`.
- **Источники:** IGN «Rockstar Talks GTA IV Technical Problems» (https://www.ign.com/articles/2008/12/06/rockstar-talks-gta-iv-technical-problems), Digital Foundry «From Disaster Port To Path Traced Mod Showcase» (https://www.digitalfoundry.net/features/grand-theft-auto-4-pc-from-disaster-port-to-path-traced-mod-showcase), GTA Wiki патчи 1.0.7.0 / 2016 / 2020 (https://gta.wiki/w/Grand_Theft_Auto_IV/Title_Update_Notes/Update_2020-03-19).

### 6. Grand Theft Auto V (2013/2015/2025, Rockstar North)

- **Движок:** RAGE + Euphoria. Стриминг мира, LOD, плотность трафика/педов слайдерами, смена дня/ночи, расширенные настройки ПК (дальность, длинные тени, трава Ultra, MSAA/TXAA). 64-битный стриминг кольцами внимания: коллизии ~150 м, меши ~300 м, горизонт — HLOD-импостеры; на PS3/X360 — обязательная установка части данных на HDD с параллельным чтением с двух приводов.
- **Релиз ПК (2015) — образцовый:** 60 fps, расширенная графика, бенчмарк. Ложка дёгтя: баг нелатинских имён пользователей Windows (игра не запускалась) и привязка к Social Club.
- **Версии:** PS5/XSX (2022): 60 fps режимы; Enhanced ПК (2025): RT-отражения/тени/AO/GI, DLSS/FSR, DualSense. Legacy остался для слабого железа — редкий пример честной вилки.
- **Причина репутации:** функционал (три героя, ограбления, Online как платформа на десятилетие) + реализация (масштабируемость настроек от слабого ПК до RT).
- **Решения:**
  - `+` Слайдеры плотности/дальности: каждая подсистема крутится отдельно.
  - `+` Две ветки (Legacy/Enhanced): старое железо не брошено.
  - `−` Онлайн-зависимость и читеры как вечный налог.
- **Влияние:** оптимизация — эталон зернистых настроек; графика — RT как опция, а не требование.
- **DSS:** профиль GTA-like даёт класс 2 с корзиной (Arc A750 ≈ RTX 3060 — официальная рекомендация Enhanced); `temporal_upscaling`, `hierarchical_lod`, `crowd_instancing_impostors`.
- **Источники:** Rockstar Support «Grand Theft Auto V PC system requirements» (https://support.rockstargames.com/articles/lMQXeP2Z1mN3g9oZiBZFR/grand-theft-auto-v-pc-system-requirements), technical.city GTA V (требовательность 1.2/10, RTX 3060 в 4.2 раза быстрее GTX 660).

### 7. Metal Gear Solid V: The Phantom Pain (2015, Kojima Productions)

- **Движок:** Fox Engine. Отложенный рендер + PBR + подповерхностное рассеяние. GI — локальные irradiance-карты через сферические гармоники (9 коэффициентов вместо кубемап: память и bandwidth), диффуз считается в half-res HDR с билатеральным апскейлом по глубине, затем динамический свет в полном разрешении (сложность света O(N+M) вместо O(N×M) прямого рендера). Плотность источников на ПК не режется (на консолях — да).
- **Релиз ПК — отличный:** лучший вид среди платформ, 60 fps, 4K/DSR, G-Sync. Самый дорогой пресет — Effects Extra High (падение на треть даже на GTX 980 Ti в 1440p). Ground Zeroes (пролог) вышел на ПК на 9 месяцев позже.
- **Причина репутации:** реализация (эталонный порт и масштабируемость) + функционал (стелс-песочница); тень — раскол Kojima/Konami и ощущение незавершённости второй главы (сюжет, не техника).
- **Решения:**
  - `+` SH вместо кубемап: GI почти бесплатно по памяти.
  - `+` Half-res + билатеральный апскейл: качество полного разрешения за полцены.
  - `+` Зернистые пресеты с измеренной ценой каждого (гайд NVIDIA).
  - `−` Effects Extra High: ловушка для перфекционистов.
- **Влияние:** оптимизация — «считай в половинном, поднимай умно»; графика — фотореализм 2015 без RT.
- **DSS:** `deferred_forward_plus_choice`, `screen_space_gi`, `volumetric_half_resolution`, `post_effect_selective`.
- **Источники:** Adrian Courrèges «MGS V Graphics Study» (https://www.adriancourreges.com/blog/2017/12/15/mgs-v-graphics-study/), NVIDIA Performance Guide (https://www.nvidia.com/en-us/geforce/news/metal-gear-solid-v-the-phantom-pain-graphics-and-performance-guide/), Digital Foundry «Tech Analysis: MGS5 FOX Engine» (https://www.eurogamer.net/digitalfoundry-tech-analysis-mgs5-fox-engine).

### 8. Half-Life 2 (2004, Valve)

- **Движок:** Source. Havok в основе + переписанный игровой слой физики («Physics AI», substance system: задал материал — поведение посчиталось), Faceposer поверх 40 лицевых action units Экмана (мимика, жесты, мизансцены через ИИ, библиотека переиспользуемых жестов), фиксированный шаг физики 66 Гц (15 мс), BSP v19 + displacements, DX6–9 лесенка (шейдеры 2.0/2.0+, 8 МБ VRAM минимум).
- **Релиз ПК:** шедевр, омрачённый кражей исходников (2003) и годом задержки + принудительный Steam (ненависть эпохи, позже — платформа десятилетия). Моды и SDK (Softimage XSI EXP в комплекте подхода) продлили жизнь на десятилетия.
- **Причина репутации:** реализация (физика как геймплей, лица как нарратив) + функционал (бесшовное повествование без катсцен).
- **Решения:**
  - `+` Substance system: физика из материала, а не из скриптов.
  - `+` Экман-юниты: лицо не умеет «сломаться» — грамматика запрещает невозможное.
  - `+` Лесенка DX: одна игра на 5 лет железа.
  - `−` BSP-наследие Quake: статичность мира (стены не двигаются вбок).
- **Влияние:** оптимизация — физика по требованию геймдизайна; графика — мимика как контент; экосистема — SDK как стратегия.
- **DSS:** `fixed_timestep_physics`, `physics_lod_sleeping`, `baked_occlusion_culling`, `animation_lod_budget`.
- **Источники:** IGN «GDC 2004: Half-Life 2 Source Engine Demo» (https://www.ign.com/articles/2004/03/25/gdc-2004-half-life-2-source-engine-demo), 4Gamer-интервью (https://www.4gamer.net/specials/hl2int/hl2int_e2.html), Faceposer PDF (https://valvearchive.com/Publications/Half-Life%202%20-%20Raising%20the%20Bar/01%20Eckman%2BPoser.pdf), BSP-формат (http://www.bagthorpe.org/bob/cofrdrbob/bspformat.html).

### 9. No Man’s Sky (2016, Hello Games)

- **Движок:** собственный, процедурный. Формулы вместо контента: планеты, флора, фауна, экономика из сидов; 18 квинтиллионов планет как следствие, а не цель.
- **Релиз ПК — двойной провал:** (а) маркетинговый: мультиплеера «встретиться нельзя» не оказалось, ASA-расследование, рефанды; (б) технический: статтеры, невозможность запуска, рестарты ПК, звук (IGN, август 2016). Дей-ван патч 1.03 уже переписывал генерацию, торговлю, бой и тени — игра рецензентов и релизная разошлись.
- **Версии:** Foundation → Next (2018: настоящий мультиплеер, визуальный оверхол, миллионы новых продаж) → Beyond (2019: VR с переделкой 20 механик под контроллеры, Nexus на 32 игроков, Vulkan) → дальше десятки бесплатных апдейтов. Хрестоматийное искупление.
- **Причина репутации:** сначала реализация (обещания vs билд), потом — процесс (бесплатные апдейты годами). Функционал (процедуры) был с первого дня.
- **Решения:**
  - `+` Формулы вместо ассетов: бесконечный контент маленькой командой.
  - `+` Бесплатные крупные патчи как стратегия доверия (Next окупился миллионами продаж).
  - `−` Процедуры без якоря: широта без глубины на старте.
  - `−` VR/мультиплеер поверх готового: переделка, а не надстройка (урок для планирования).
- **Влияние:** оптимизация — генерация быстрее загрузки (скорость генерации x2 уже в 1.03); графика — pop-in и тени как вечная боль процедурок; менеджмент — не анонсируй мультиплеер без серверов.
- **DSS:** `gpu_procedural_placement`, `hierarchical_lod`, `async_loading_pipeline`; риски deadline_pressure/prototype_needed.
- **Источники:** Ars Technica day-one patch (https://arstechnica.com/gaming/2016/08/mans-sky-day-one-patch-details-release-date/), Kotaku (https://kotaku.com/no-mans-skys-day-one-patch-will-make-some-huge-changes-1784940149), Ars Beyond (https://arstechnica.com/gaming/2019/08/sean-murray-tells-us-nearly-everything-to-expect-in-no-mans-sky-beyond/), Independent Next (https://www.the-independent.com/games/no-mans-sky-update-download-next-features-release-date-multiplayer-a8452461.html), IGN PC-проблемы (https://www.ign.com/articles/2016/08/12/no-mans-sky-users-reporting-pc-launch-day-problems).

### 10. Left 4 Dead (2008, Valve/Turtle Rock)

- **Движок:** Source. Главная система — AI Director: navmesh + flow distance (расстояние по маршруту, не по прямой) + Active Area Set (население только вокруг команды, сотни врагов из пула переиспользуемых сущностей) + structured unpredictability (бродяги/мобы/спецзаражённые/боссы/кеши с разными частотами) + adaptive dramatic pacing (интенсивность каждого выжившего: ранения +, затухание к нулю; фазы Build Up → Sustain → Peak Fade → Relax 30–45 сек). Важно: регулируется частота (pacing), а не амплитуда (сложность).
- **Релиз ПК:** ровно, без скандалов; Versus-режим и DLC дожили до L4D2 (2009), вызвавшей «предательство» фанатов скоростью сиквела.
- **Причина репутации:** реализация (процедурный нарратив вместо скриптов — цитата Ньюэлла) + функционал (кооп-формула). Реверс-инжиниринг 2026 года подтвердил архитектуру вплоть до коэффициентов.
- **Решения:**
  - `+` AAS: сотни врагов из десятков сущностей.
  - `+` Пейсинг вместо сложности: честность + реиграбельность.
  - `+` Наивные метрики работают: грубая интенсивность даёт точную драму.
  - `−` Сложность внедрения: 5 лет спустя отрасль так и не скопировала ( barrier — комплексность, не железо).
- **Влияние:** оптимизация — не рендерить/не симулировать вне AAS; ИИ — темп как управляемая величина; дизайн — процедурная история.
- **DSS:** `agent_update_budget`, `flow_field_pathing`, `navmesh_tiling_streaming`, `time_sliced_pathfinding`, `crowd_instancing_impostors`, `particle_pooling`.
- **Источники:** Valve «The AI Systems of Left 4 Dead» (https://cdn.akamai.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf), GameDeveloper «The Discomfort Zone» (https://www.gamedeveloper.com/design/the-discomfort-zone-the-hidden-potential-of-valve-s-ai-director), реверс L4D2 Director (https://github.com/zeljkovranjes/l4d2-director-system-research).

---
*Партия 1 из 6. Продолжение ниже.*

---

## Партия 2

### 11. Crash Bandicoot (1996, Naughty Dog)

- **Движок/рендер:** собственный. Три хака PlayStation: (1) виртуальная память — уровни 8–16 МБ в 2 МБ RAM чанками по 64 КБ с CD (300 КБ/с, Sony боялась за приводы); (2) предвычисленная видимость и сортировка на SGI-ферме (у PS1 нет z-буфера) + рельсовая камера, прячущая геометрию за поворотами; (3) вершинная анимация вместо скелетной + кастомное сжатие 50–80:1, персонажи без текстур (шейдинг вместо текстур — обход отсутствия перспективной коррекции PS1).
- **Релиз ПК:** оригинала на ПК не было (эксклюзив PS1); N. Sane Trilogy (2017, Vicarious Visions) — достойный ремейк, позже ПК-версия стабильна.
- **Причина репутации:** реализация (инженерия сжатия и памяти) + функционал (маскот Sony). Язык GOOL (Lisp-диалект для объектов: стейт-машины, лёгкие треды, прототип существа за 10 минут) — инструмент как force multiplier.
- **Решения:**
  - `+` CD как виртуальная память + NPT-раскладчик (экспертная система укладки 500–1000 ресурсов в 1.2 МБ).
  - `+` Предвычисление видимости: ноль runtime-цены, лимит 800 полигонов в кадре.
  - `+` Вершины вместо костей: мультяшность без артефактов.
  - `−` Рельсы камеры как клетка дизайна; 8-часовые прогоны фермы на уровень.
- **Влияние:** оптимизация — стриминг чанками (предок всех open-world стримингов), предвычисление; графика — шейдинг вместо текстур как осознанный traded; процесс — свой язык под задачу.
- **DSS:** `async_loading_pipeline`, `baked_occlusion_culling`, `animation_compression`, `mesh_index_optimization`.
- **Источники:** Andy Gavin «Making Crash Bandicoot» GOOL ч.9 (https://all-things-andy-gavin.com/2011/03/12/making-crash-bandicoot-gool-part-9/), ч.3 (https://all-things-andy-gavin.com/2011/02/04/making-crash-bandicoot-part-3/), GameDeveloper «How Naughty Dog broke Sony hardware rules» (https://www.gamedeveloper.com/design/how-naughty-dog-broke-sony-s-hardware-rules-to-create-i-crash-bandicoot-i-), Ars War Stories (https://arstechnica.com/gaming/2021/09/war-stories-how-crash-bandicoot-hacked-the-original-playstation/).

### 12. Street Fighter V (2016, Capcom)

- **Движок:** Unreal Engine 4. Сеть — собственный rollback (не GGPO).
- **Релиз ПК — провал доступа, не графики:** сервера легли в первые часы (ошибки 21400/10007, матчмейкинг, вылеты из Survival), извинения Оно; игра вышлаурезанной: нет Arcade, лоби на 2 вместо 8, нет костюмов и наказаний за rage-quit, баги отдельных арен (лаг на сцене Байсона), старые файтстики через костыли. Steam — 54% негативных.
- **Версии:** годами добирали контент сезонами; позже — улучшение ролбэка, Arcade Edition (2018), Champion Edition (2020). Плюс известный технический долг: ~8 кадров инпут-лага на старте (снижали патчами) и rootkit-античит (скандал с драйвером capcom.sys).
- **Причина репутации:** реализация (серверы + сырой релиз ради про-сцены), не файтинг-механика. Антипример «выпустить платформу без платформы».
- **Решения:**
  - `+` Ранний собственный rollback: приличный онлайн после починки.
  - `−` Релиз без сингла при мёртвых серверах: не во что играть вообще.
  - `−` Инпут-лаг и rootkit: технический долг, отравивший репутацию на годы.
- **Влияние:** сеть — беты ≠ нагрузочное тестирование релиза; менеджмент — контентный минимум + неработающий онлайн = худшая комбинация.
- **DSS:** `headless_dedicated_server`, `tickrate_budgeting`, `client_prediction_reconciliation`, `deterministic_lockstep`; риск deadline_pressure.
- **Источники:** GameInformer (https://gameinformer.com/b/news/archive/2016/02/16/capcom%E2%80%99s-ono-is-sorry-that-street-fighter-v-is-a-launch-day-mess.aspx), Kotaku (https://kotaku.com/street-fighter-vs-launch-sure-has-been-a-bummer-1760146427), VG247 (https://www.vg247.com/street-fighter-5-launch-day-server-issues), PC Gamer (https://www.pcgamer.com/capcoms-yoshinori-ono-apologises-for-sfv-server-issues/).

### 13. Guilty Gear Strive (2021, Arc System Works)

- **Движок:** Unreal Engine 4. Cel-shading нового поколения (тун-шейдинг + градации, ручной контроль света по частям тела, limited animation), rollback-неткод, спроектированный с первого дня (разделение объектов на откатываемые/нет ради памяти, правки движка под просадки частиц и скелета на PS4 CPU (трансформации костей переписаны под векторные регистры SIMD)).
- **Релиз ПК — спокойный:** публичные беты заранее, внятная задержка ради netcode. Минусы на старте: серверные работы, нет кроссплея ПК/PS, упрощение глубины vs Xrd (споры), UI-читаемость.
- **Причина репутации:** реализация (лучший rollback в жанре + картинка) + функционал (доступность без потери глубины, wall-break).
- **Решения:**
  - `+` Rollback с первого дня дизайна, а не прикрученный: на 124 мс пинга ≤3 кадров отката.
  - `+` Ручной свет по частям: аниме-стиль, невозможный честным рендером.
  - `−` CPU PS4 давился откатом частиц/скелета — правили движок.
  - `±` Упрощение входов: шире аудитория, уже потолок для ветеранов.
- **Влияние:** сеть — rollback как стандарт жанра (контраст с SFV); графика — «неправильный» свет как фича; процесс — Material Editor для быстрых итераций с художниками.
- **DSS:** `deterministic_lockstep`, `client_prediction_reconciliation`, `animation_compression`, `post_effect_selective`.
- **Источники:** UnrealEngine-интервью (https://www.unrealengine.com/developer-interviews/how-guilty-gear--strive--hits-an-ultra-combo-with-groundbreaking-visuals-and-gameplay), Ars про rollback (https://arstechnica.com/gaming/2021/02/how-guilty-gear-saved-its-online-play-in-a-post-offline-world/), Windows Central (https://www.windowscentral.com/guilty-gear-strive-pc-review), TheGamer Q&A (https://www.thegamer.com/arc-system-works-qa-interview-guilty-gear-strive-rollback-netcode-fgc-esports/).

### 14. Baldur’s Gate 3 (2023, Larian)

- **Движок:** Divinity Engine 4.0. Кинематографичность (MoCap, катсцены), симуляция толпы и ИИ.
- **Релиз ПК — триумф с оговоркой:** Акт 3 (город Врата Балдура) роняет CPU: плотность NPC, землетрясения, переходы в катсцены; движение кругами −20% fps при том же виде; Ryzen 5 3600 — до −50% и рваный фреймтайм, Vulkan на ~10% хуже DX11 в толпе; призраки саммонов −10%. Масштабирование по ядрам пыхтит: 8 ядер без HT лучше всех, полный 12900K почти не быстрее 6 ядер.
- **Патчи:** №2 (CPU, декали/текстуры в worker threads, сейвы), №3 (отключение дальних NPC с диалогами, толпы, Нижний город), №5 (утечки памяти, виртуальные текстуры, HLOD с пониженным числом треугольников, вода). Лечили отключением симуляции вдали — честная цена.
- **Причина репутации:** функционал (свобода, сценарий, кооператив) перекрыл технику; репутация «игры, которую чинили в прямом эфире».
- **Решения:**
  - `+` Патчи по делу: потоки, LOD, память вместо обещаний.
  - `−` Плотность без CPU-бюджета: средний ПК 2023 года не тянет главный город игры.
  - `±` DX11 стабильнее Vulkan там, где важно.
- **Влияние:** оптимизация — толпа = CPU, а не GPU (урок для планирования); графика — HLOD и виртуалки как заплатки постфактум.
- **DSS:** `crowd_instancing_impostors`, `agent_update_budget`, `ecs_data_oriented_crowd`, `hierarchical_lod`, `multithreaded_physics_jobs`; риск crowd_budget.
- **Источники:** Digital Foundry Act 3 (https://www.digitalfoundry.net/articles/digitalfoundry-2023-baldurs-gate-3-act-three-massively-hits-cpu-performance-but-why), Larian Patch 5 (https://baldursgate3.game/news/patch-5-now-live%5F99), Patch 2 (https://baldursgate3.game/news/patch-2-now-live_89), Community Update 24 (https://www.baldursgate3.game/news/community-update-24-looking-to-the-future_88), DSOG Patch 3 (https://www.dsogaming.com/patches/baldurs-gate-3-patch-3-is-4-9gb-in-size-brings-cpu-performance-improvements-full-changelog).

### 15. The Witcher 3: Wild Hunt (2015/2022, CDPR)

- **Движок:** REDengine 3, затем next-gen апгрейд (RTXGI, RT-отражения/тени/AO, DLSS/FSR2, DX12-ветка рядом с DX11).
- **Релиз ПК (2015) — достойно** для открытого мира; настоящий скандал — downgrade-дебаты (трейлеры vs релиз) и позже next-gen патч 2022: DX12-ветка медленнее DX11 на 45% в Новиграде без RT, шейдерные статтеры, краши, FSR-краши; хотфикс вернул DX11-паритет частично. RT-режим: только DLSS3 Frame Generation объезжает CPU-стену.
- **Причина репутации:** функционал (квесты, Гвинт, DLC как эталон) + техника (стриминг, погода, толпы Новиграда). Downgrade-спор — про маркетинг, не движок.
- **Решения:**
  - `+` Две ветки API (DX11 без RT как запасной аэродром) — спасли релиз апгрейда.
  - `+` RTXGI вместо кубемап художников: ночь и день буквально.
  - `−` DX12-враппер поверх DX11-кода: CPU-стена даже на 12900K+DDR5-6400.
  - `−` Шейдерный статтер без предкомпиляции.
- **Влияние:** оптимизация — новая API-ветка ≠ бесплатный прирост; графика — RT как опция с честной ценой; процесс — хотфиксы чинят симптомы, архитектуру — нет.
- **DSS:** `hardware_raytraced_gi`, `temporal_upscaling`, `ml_frame_generation`, `hierarchical_lod`, `crowd_instancing_impostors`, `pso_precaching_warmup`.
- **Источники:** Digital Foundry next-gen (https://www.digitalfoundry.net/articles/digitalfoundry-2022-the-witcher-3s-next-gen-upgrade-is-beautiful-on-pc-but-performance-is-not-good-enough), PC Gamer hotfix (https://www.pcgamer.com/the-witcher-3-next-gen-update-hotfix/), RPS (https://www.rockpapershotgun.com/the-witcher-3-next-gen-update-tested-worse-performance-even-without-ray-tracing), VGC 4 issues (https://www.videogameschronicle.com/news/cd-projekt-is-investigating-four-main-issues-with-witcher-3s-next-gen-update/), IGN (https://www.ign.com/articles/the-witcher-3-wild-hunts-next-gen-update-causing-major-performance-issues-for-some-pc-players).

### 16. The Elder Scrolls V: Skyrim (2011, Bethesda)

- **Движок:** Creation Engine (форк Gamebryo). Мир как база данных: каждый сдвинутый карандаш пишется в сейв. Таймер Havok жёстко привязан к 60 FPS: разблокировка до 120–144 ломает интегратор Верле (неверная Δt — посуда разлетается со сверхзвуковой скоростью).
- **Релиз ПК — терпимо, PS3 — катастрофа:** сейвы 5.5+ МБ → статтеры до нуля fps; причина — 256+256 МБ split-памяти PS3 против unified 512 МБ Xbox 360 + растущая БД мира + сборщик мусора, не отдающий память (лаги переползали даже на новый сейв). Патч 2.01 поднял базовые 20→25 fps, корень не вылечил. На ПК та же болезнь мягче: вылеты за адресное пространство, цветные текстуры.
- **Версии:** Legendary, Special Edition (64-bit — главное лекарство), Anniversary, VR. Жива модами и переизданиями.
- **Причина репутации:** функционал (свобода, моды, драконы) поверх хрупкой реализации. Урок: неограниченный мир на ограниченной памяти.
- **Решения:**
  - `+` Моды и Creation Kit как вторая жизнь (десятилетие+).
  - `+` 64-bit переиздание вылечило класс проблем целиком.
  - `−` Сейв как растущая БД без GC-стратегии под split-память.
  - `−` Скриптовый слой поверх движка: удобство модов ценой памяти.
- **Влияние:** оптимизация — бюджет памяти под сейв, а не только под кадр; графика — LOD и стриминг как данность; платформы — unified vs split как архитектурный риск.
- **DSS:** `async_loading_pipeline`, `hierarchical_lod`, `navmesh_tiling_streaming`; риск memory_budget.
- **Источники:** GameDeveloper «Out-of-memory: Skyrim PS3 woes» (https://www.gamedeveloper.com/programming/out-of-memory-skyrim-s-ps3-woes-examined), Digital Foundry PS3 lag (https://www.digitalfoundry.net/articles/digitalfoundry-vs-ps3-skyrim-lag), GameInformer + Sawyer про split-память (https://gameinformer.com/b/news/archive/2011/12/05/why-skyrim-may-not-be-working-right-on-ps3.aspx), GamesIndustry Tech Focus (https://www.gamesindustry.biz/digitalfoundry-tech-focus-skyrim).

### 17. The Elder Scrolls IV: Oblivion (2006, Bethesda)

- **Движок:** Gamebryo + Havok + SpeedTree + FaceGen. Фишка — Radiant AI: потребности NPC, пакеты ИИ 4 уровней обработки (high в загруженной ячейке → грубая симуляция вне её), диалоги как скриптовый язык. Тот же Havok-таймер, что в Skyrim: физика живёт только на 60 FPS.
- **Релиз ПК:** без катастроф уровня Skyrim-PS3, но с феноменом «лошадиная броня» (первый микротранзакционный скандал) и упрёками в уровневой прокачке мира под игрока.
- **Причина репутации:** функционал (живой мир с расписаниями) + реализация (урезанный, но работающий Radiant). Доказательство, что симуляция вне экрана должна быть дешёвой.
- **Решения:**
  - `+` 4-уровневая обработка ИИ: полный фарш только рядом, вдали — грубая симуляция без боя и еды.
  - `−` Обещанного «думающего» мира не случилось: потребности свелись к расписаниям.
- **Влияние:** ИИ — LOD не только у геометрии, но и у симуляции; экономика — horse armor как прецедент монетизации.
- **DSS:** `agent_update_budget`, `time_sliced_pathfinding`, `physics_lod_sleeping`.
- **Источники:** paavohtl «What was Radiant AI, anyway?» (https://blog.paavo.me/radiant-ai/).

### 18. The Legend of Zelda: Breath of the Wild (2017, Nintendo)

- **Движок:** собственный + Havok. Химический движок поверх физического: огонь/вода/лёд/электричество/ветер как элементы с тремя правилами (элемент меняет материал, элементы меняют друг друга, материалы друг друга — нет). Плюс «ложь во благо» (game physics вместо textbook).
- **Релиз:** Wii U (720p, просадки до ~20 в Какарико) и Switch (900p док, плавнее в портативе). Double-buffered vsync: несмог 30 → жёсткие 20. Визуально версии почти идентичны (разрешение + фильтрация).
- **Причина репутации:** функционал (мультипликативный геймплей, прототип в 8-бит) + реализация (Havok + химия на слабом железе).
- **Решения:**
  - `+` Правила вместо контента: объекты комбинируются сами.
  - `+` Стилизация: цел-шейдинг стареет медленнее фотореализма.
  - `−` CPU Wii U: физика роняет кадры именно там, где весело.
  - `−` Double-buffer: ступенька 30→20 без промежуточного.
- **Влияние:** оптимизация — half-res альфа-эффекты, билинейка как данность слабого GPU; дизайн — прототип в 8 битах дешевле месяца продакшна.
- **DSS:** `gpu_particle_simulation`, `flow_field_pathing`, `physics_lod_sleeping`, `art_direction_stylization`.
- **Источники:** DF Wii U tech (https://www.digitalfoundry.net/articles/digitalfoundry-2016-the-legend-of-zelda-breath-of-the-wild-pushes-wii-u-hardware-to-the-limit), DF Switch vs Wii U (https://www.digitalfoundry.net/articles/digitalfoundry-2017-the-legend-of-zelda-breath-of-the-wild-switch-vs-wii-u-face-off), GDC/Thumbsticks (https://www.thumbsticks.com/gdc-17-breath-of-the-wild-science-lies/), GameDeveloper (https://www.gamedeveloper.com/design/forging-i-zelda-i-s-future-by-revisiting-its-past), DF extended (https://www.youtube.com/watch?v=uiEYTN-nDso).

### 19. Super Mario 64 (1996, Nintendo)

- **Движок/железо:** N64 + SGI-станции. Z-буфер как свобода дизайна (никакого предвычисленного порядка!), аналоговая камера как изобретение: тысячи итераций систем, оператор-Лакиту как объяснение игроку, C-кнопки вместо второго стика.
- **Релиз:** эталон 3D-платформера; критика камеры была, но дизайн компенсировал (безопасные падения, предсказуемые прыжки). Разрабатывался параллельно с железом на эмуляторных платах, контроллера не было полгода (модифицированные сеговские пады!).
- **Причина репутации:** реализация (камера + аналог как новый язык) + функционал (звёзды, хаб-замок). Использовано ~40–60% возможностей N64 по словам команды.
- **Решения:**
  - `+` Z-буфер вместо BSP-порядка: диорамные уровни без ограничений.
  - `+` Камера как персонаж: объяснение механики внутри мира.
  - `−` C-кнопки: поворота на 90° не хватает для точности.
  - `±` Половина времени — на базовую систему, уровни «набросаны» в конце (и это сработало).
- **Влияние:** камера — друг и враг (урок на десятилетия, ветка Tomb Raider — вторая); управление — аналог как стандарт; процесс — сначала фундамент, потом контент.
- **DSS:** `fixed_timestep_physics`, `motion_matching` (как идеал анимации), `physics_lod_sleeping`.
- **Источники:** Pixelatron-интервью Giles Goddard (https://pixelatron.com/blog/the-making-of-super-mario-64-full-giles-goddard-interview-ngc), Shmuplations 1996 (https://shmuplations.com/mario64/), AVClub о камере (https://www.avclub.com/super-mario-64-introduced-the-camera-as-a-friend-and-fo-1798250469), TCRF early dev (https://tcrf.net/Prerelease:Super_Mario_64_(Nintendo_64)/Early_Development), DevGameClub (https://www.devgameclub.com/blog/2017/11/15/dgc-ep-087-super-mario-64-part-one).

### 20. Minecraft: старая Java и новая Bedrock (Mojang, 2011–…)

- **Движок:** Java Edition (Java, float64) vs Bedrock (C++, float32). Чанки 16×16, процедурный Perlin-шум. Java: мастер-поток 20 TPS (50 мс на тик) + паузы сборщика мусора Stop-the-World при генерации чанков; Bedrock: мешинг в worker threads + жадная триангуляция (−60–80% полигонов), дальность 64–96 чанков против 16–32 в Java.
- **Техническая драма — Дальние земли:** float32 шум даёт сбой на 12 550 824 блоках (Java — int32 переполнение в том же месте, итог один). Bedrock раньше страдает от джиттера (float32: уже на тысячах блоков позиции квантуются), Java держится на float64. Патч Beta 1.8 «починил» Дальние земли модulo-хаком (`p - floor(p/33.5M)*33.5M`), отодвинув проблему за 2^63.
- **Производительность:** Java — два тяжёлых потока (клиент-рендер + сервер-мир) + GC-статтеры; Sodium выносит мешинг чанков в worker-пул (`ChunkBuilder`, graph search остаётся на main thread — ядра грузятся ровно, а статтеры на прогрузке остаются). Независимый замер 1.16.3/16 чанков: vanilla ~103 avg → OptiFine ~343 → Sodium ~408; Bedrock — тикающие vs глазные чанки (дальние не симулируются — только картинка), рендер-дистанция 72 против 32 в Java.
- **Причина репутации:** функционал (кубики как язык творчества, 300M+ копий) + реализация (процедуры, которым прощают всё).
- **Решения:**
  - `+` Чанки + сиды: бесконечность изпериодических функций.
  - `+` Bedrock: разделение тикающих и глазных чанков.
  - `+` Sodium: оптимизация без изменения поведения (идеал модов); companion-моды требуют мост (Continuity + Sodium без Indium крашится на падающих блоках — типовой кейс).
  - `+` VulkanMod: замена OpenGL-рендерера на Vulkan (снижение CPU/GPU-overhead, chunk building) — механизм подтверждён репозиторием; цифры одного автора — наблюдение, не якорь.
  - `−` Float32 в Bedrock: джиттер как врождённый налог.
  - `−` 32-чанковый хардкод Java: смена лимита ломает моды.
- **Влияние:** оптимизация — тикай только видимое/нужное; точность — float-бюджет как проектное ограничение; экосистема — моды чинят перфоманс лучше издателя.
- **DSS:** `gpu_procedural_placement`, `world_partition_streaming`, `async_loading_pipeline`, `physics_lod_sleeping`, `time_sliced_pathfinding`, `network_relevancy_priority`.
- **Источники:** Minecraft Wiki Far Lands (https://minecraft.wiki/w/Java_Edition_Far_Lands), Bedrock distance effects (https://minecraft.wiki/w/Bedrock_Edition_distance_effects), MCDF Bedrock Far Lands (https://mcdf.wiki.gg/wiki/Bedrock_Edition:Far_Lands), Sodium issue #255 (https://github.com/CaffeineMC/sodium/issues/255), FarLandsChronicles #15 (https://github.com/ThisTestUser/FarLandsChronicles/issues/15), Sodium ChunkBuilder (https://github.com/CaffeineMC/sodium/blob/ed6c1afe/common/src/main/java/net/caffeinemc/mods/sodium/client/render/chunk/compile/executor/ChunkBuilder.java), Sodium async chunk loading #2344 (https://github.com/CaffeineMC/sodium-fabric/issues/2344), VulkanMod (https://github.com/xCollateral/VulkanMod), Continuity FAQ + Indium (https://blog.curseforge.com/continuity-mod-frequently-asked-questions/), OptiFine vs Sodium vs Vanilla замеры (https://flightlessmango.com/games/13928/logs/1001).

---
*Партии 1–2 из 6. Продолжение ниже.*

---

## Партия 3

### 21. World of Warcraft (2004, Blizzard)

- **Движок/сеть:** собственный. Главная система — серверная: шардинг (копии зон поверх порога онлайна, у каждой зоны свой лимит), лееринг Classic (склейка шардов в связный мир, чтобы мобов можно было кайтить через границы), кросс-реалм зоны против малолюдья, фейзинг под прогресс сюжета.
- **Релиз ПК:** запуск 2004 — очереди и лаги; архитектурно держалось 20 лет. Кризисы: старт Warlords of Draenor (шардинг рождён за 3 дня и 3 ночи), AQ-открытие в Classic (1500 игроков в зоне, дроп facing-апдейтов, батчинг низкоприоритетных пакетов, кап 60-х уровней).
- **Версии:** Classic → TBC → SoD: лееринг стал вечным, выявились долги (одинаковый кап на все зоны, 16 пустых копий мира ради одного STV, разрыв групп).
- **Причина репутации:** реализация (сеть как геймдизайн) + функционал (второй дом на 12M подписок). Полиномиальная проблема пакетов (20 игроков — 380 пакетов, 1500 — 2.2M) не лечится железом, только дизайном рассылок.
- **Решения:**
  - `+` Шардинг/лееры: кап реалма отвязан от вместимости зоны.
  - `+` Деградация честно: резать facing-апдейты, а не ронять сервер (дедлок = авторебут).
  - `−` Мир рвётся: исчезновения, разные рейды трав, мета-игра со слоями.
  - `−` Один кап на все зоны: PvP-бойня и праздный город стоят одинаково.
- **Влияние:** сеть — O(n²) рассылок как главный враг; CPU — одно ядро на зону как потолок (мультитред не спасает); менеджмент — очереди и капы как часть дизайна.
- **DSS:** `network_relevancy_priority`, `headless_dedicated_server`, `tickrate_budgeting`, `deterministic_lockstep`; риск сетевой нагрузки.
- **Источники:** Blizzard Engineer’s Workshop AQ (https://news.blizzard.com/en-gb/article/23504702/engineers-workshop-recreating-the-ahnqiraj-war-effort), Wowhead/PC Gamer про шардинг и лееры (https://www.pcgamer.com/the-server-tech-that-saved-wow-10-years-ago-is-causing-problems-for-classics-season-of-discovery-dev-reveals-a-layer-is-actually-just-sharding-with-a-lot-of-sticky-tape/), Wowpedia Sharding (https://wowpedia.fandom.com/wiki/Sharding_(term)), Warcraft Wiki Layering (https://warcraft.wiki.gg/wiki/Layering).

### 22. Counter-Strike: Global Offensive (2012, Valve)

- **Движок:** Source. Сеть: тикрейт 64 (MM) / 128 (турниры, FACEIT), интерполяция `cl_interp = ratio/updaterate`, lag compensation (перемотка мира на пинг+интерп), peekers advantage как следствие.
- **Релиз ПК:** ровный; главный спор десятилетия — 64 против 128. Слепой тест: лишь 41% отличают. Правда обеих сторон: 128 точнее, но требует CPU/канала; 64 — доступность.
- **Причина репутации:** реализация (честный хитрег как религия) + функционал (экономика раундов, карты-легенды).
- **Решения:**
  - `+` Lag compensation: играбельность на разных пингах.
  - `+` Интерполяция вместо телепортов сущностей.
  - `−` Peekers advantage: неустраним, только смягчается тиком.
  - `±` 128 tick: точнее, но дороже всем (сервер, канал, ПК).
- **Влияние:** сеть — тикрейт как деньги (прямая цитата для DSS `tickrate_budgeting`); графика вторична.
- **DSS:** `tickrate_budgeting`, `client_prediction_reconciliation`, `deterministic_lockstep`.
- **Источники:** Dignitas tickrate guide (https://dignitas.gg/articles/tickrate-interpolation-lag-compensation-and-you-probably-not-the-reason-why-you-just-missed-that-shot), Profilerr 64 vs 128 (https://profilerr.net/64-ticks-vs-128-ticks-in-csgo-differences-and-what-is-better/).

### 23. Counter-Strike 2 (2023, Valve)

- **Движок:** Source 2. Главная фича — sub-tick: сервер знает точный момент выстрела/гранаты внутри тика, снапшоты по-прежнему 64 Гц. Плюс volumetric smokes, переработанные карты, dynamic resolution/antis?
- **Релиз ПК:** скандал ожиданий — «128 tick не завезли», FACEIT-принуждение к 64, удаление `cl_interp` (плацебо по версии Valve), споры о «ватности». Постепенно: subtick-допилы движения и гранат.
- **Причина репутации:** реализация (sub-tick как ответ на десятилетие споров) + инерция (скины, мейджоры).
- **Решения:**
  - `+` Sub-tick: точность ввода без удвоения тика и цены серверов.
  - `+` Дым-волюметрик как геймплей (пули, HE).
  - `−` Снапшоты всё ещё 64 Гц: джиттер и tick-miss никуда не делись.
  - `−` Коммуникация: «moving beyond tick rate» прочитали как обман.
- **Влияние:** сеть — метрика сместилась с тика на джиттер и tick-miss; оптимизация — маршрут и стабильность важнее цифры в конфиге.
- **DSS:** `tickrate_budgeting`, `volumetric_half_resolution`, `dynamic_resolution_scaling`.
- **Источники:** DotEsports 64-tick (https://dotesports.com/counter-strike/news/valve-is-seemingly-forcing-everyone-to-play-cs2-on-64-tick-rate-including-faceit-servers), Varidata разбор (https://www.varidata.com/blog-en/cs2-64-tick-vs-128-tick-does-it-really-matter/), Reddit PSA (https://www.reddit.com/r/GlobalOffensive/comments/16isn2a/psa_heres_why_64_and_128_tick_still_feel_so/).

### 24. The Last of Us Part I, ПК-версия (2023, Naughty Dog / Iron Galaxy)

- **Движок:** собственный Naughty Dog, порт Iron Galaxy.
- **Релиз ПК — провал:** шейдерная компиляция часами, краши (Intel Arc, Intel GPU, 4K-фото, high-DPI мыши), OOM, ложный «100% шейдеров», просадки. Корень — PSO-кэш и потоковая подгрузка текстур/окружения без бюджета под зоопарк ПК.
- **Патчи:** 1.0.1.5/1.0.1.6 (уменьшен PSO-кэш, память анимационного стриминга, диагностика крашей), 1.0.5 (шейдеры, Intel Arc, загрузки), 1.1.0 (глобальные CPU/GPU-оптимизации, текстуры/окружение, шейдеры). Каждый патч — полный ребилд шейдеров. Итог: играбельно, осадочек с «Overwhelmingly Negative» остался.
- **Причина репутации:** реализация (порт), не игра. Антипример: шейдерный пайплайн нельзя доделать патчами интерфейса.
- **Решения:**
  - `+` Честные чейнджлоги с причинами (PSO, стриминг) вместо «улучшена стабильность».
  - `−` Сборка PSO в фоне без готовности игры: зависания и ложные проценты.
  - `−` Память анимаций и текстур без запаса под ПК-конфигурации.
- **Влияние:** оптимизация — PSO warmup и бюджеты стриминга как must для ПК; процесс — аутсорс портов без времени на шейдеры.
- **DSS:** `pso_precaching_warmup`, `async_loading_pipeline`, `animation_lod_budget`, `lightmap_compression_streaming`.
- **Источники:** Naughty Dog 1.1.0 (https://feedback.naughtydog.com/hc/en-us/articles/16476165410836-The-Last-of-Us-Part-I-v1-1-0-Patch-Notes-for-PC), 1.0.5.0 (https://feedback.naughtydog.com/hc/en-us/articles/15404598599444-The-Last-of-Us-Part-I-v1-0-5-0-Patch-Notes-for-PC), 1.0.4.1 (https://feedback.naughtydog.com/hc/en-us/articles/15220724184468-The-Last-of-Us-Part-I-v1-0-4-1-Patch-Notes-for-PC), DSOG (https://www.dsogaming.com/patches/the-last-of-us-part-i-title-update-1-1-0-released-full-patch-notes), IGN (https://www.ign.com/articles/naughty-dog-releases-first-patch-for-the-last-of-us-part-1-pc).

### 25. Overwatch и изменения (2016→, Blizzard)

- **Движок:** собственный ECS + детерминированная симуляция (доклад Tim Ford, GDC). Сеть: «favor the shooter» — преимущество стреляющему ценой смертей за углом. Тики: 63 Гц клиент, до 120 Гц в соревновательных; переход 5v5 — в том числе сетевая экономика (12 персонажей с аурами/щитами рвали снапшоты и тикрейт).
- **Релиз ПК:** ровный; дальше — Role Queue, а затем Overwatch 2: движок 2.0 (не UE5!), 5v5 вместо 6v6, переписанный неткод (−30% latency), F2P.
- **Причина репутации:** реализация (отзывчивость) + функционал (герои как язык). Переход 5v5 — техно-экономика: 12 игроков не держат 120 fps на старом железе с новыми фичами (контуры, healer vision, сложные киты), очереди танков душили матчмейкинг.
- **Решения:**
  - `+` ECS + детерминизм: отзывчивость и точность симуляции.
  - `+` Favor the shooter: осознанный компромисс, озвученный игрокам.
  - `+` 5v5: меньше mitigation/CC, короче очереди, легче перфоманс.
  - `−` Смерти за углом как вечный налог дизайна.
  - `−` Отмена PvE-обещаний как репутационный удар (не техника).
- **Влияние:** сеть — философия неткода как часть дизайна; движки — свой ECS вместо UE ради отзывчивости; баланс — формат матча как перфоманс-решение.
- **DSS:** `ecs_data_oriented_crowd`, `deterministic_lockstep`, `composition_bootstrap_architecture`, `tickrate_budgeting`, `network_relevancy_priority`.
- **Источники:** VG247 favor the shooter (https://www.vg247.com/overwatch-devs-talk-netcode-and-favouring-the-shooter), GDCVault ECS+netcode (https://www.gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and), Blizzard 5v5 vs 6v6 (https://news.blizzard.com/en-gb/article/24104605/director-s-take-opening-up-the-conversation-on-5v5-and-6v6), Overwatch2Hub engine (https://www.overwatch2hub.com/what-engine-is-overwatch-2-on).

### 26. Elden Ring (2022, FromSoftware)

- **Движок:** собственный, первый DX12 у From. Кап 60 fps, без ультравайда на старте, скудные настройки без пояснений.
- **Релиз ПК — статтеры:** шейдерная компиляция just-in-time (каждый «первый» эффект — пауза до 0.25 сек), фоновый стриминг, катсцены только на ПК; не лечится железом (i9-10900K + RTX 3090 на 720p/low — тоже). Сброс кэша каждым патчем/драйвером. На Deck Valve лечит системно: предсобранный монолитный кэш Fossilize едет через Steam на устройство.
- **Версии/фиксы:** патчи частично; сообщество (StutterFix через VKD3D-приёмы); Valve починила на Deck серверным прекэшем шейдеров + агрессивным кэшированием аллокаций (тысячи command buffers сводили менеджер памяти с ума). Урок: фиксированное железо лечится, зоопарк — нет.
- **Причина репутации:** функционал (открытый мир Souls) перекрыл технику; репутация «не чинят» — тоже часть славы.
- **Решения:**
  - `+` Художественный масштаб вместо технического перфекционизма.
  - `−` JIT-компиляция без предпрогрева: налог на каждое «впервые».
  - `−` DX12-ответственность (память/потоки у разработчика) без готовности.
  - `±` 60 fps кап: стабильность ценой свободы.
- **Влияние:** оптимизация — PSO warmup обязателен в DX12; стриминг — NVMe + XMP как системные требования де-факто; платформы — Deck как эталон фиксированного железа.
- **DSS:** `pso_precaching_warmup`, `async_loading_pipeline`, `hierarchical_lod`, `dynamic_resolution_scaling`.
- **Источники:** DF запуск (https://www.digitalfoundry.net/articles/digitalfoundry-2022-elden-rings-pc-performance-simply-isnt-good-enough), DF Steam Deck (https://www.digitalfoundry.net/articles/digitalfoundry-2022-yes-valve-really-did-fix-elden-ring-for-steam-deck), EldenRingStutterFix (https://github.com/iArtorias/EldenRingStutterFix), Tier1Settings (https://tier1settings.com/elden-ring-stuttering-fix/), SageTweaks (https://www.sagetweaks.com/blog/elden-ring-pc-performance-guide).

### 27. Hollow Knight (2017, Team Cherry)

- **Движок:** Unity + PlayMaker (визуальные FSM для ИИ — дизайнер без программиста), 2D Toolkit, Sprite Packer, Particle System. Арт — ручной покадровый Photoshop + PNG, параллакс, мягкие прозрачные формы вместо 3D-света. Против GC-пауз Mono на Switch: ноль аллокаций в боевых циклах (пулинг всего) + физика на прямых рейкастах вместо PhysX2D.
- **Релиз ПК:** без скандалов; трое разработчиков + Kickstarter. Порты (Switch) — позже и спокойно.
- **Причина репутации:** функционал (метроидвания-эталон, 150+ врагов) + реализация (ручной арт как перфоманс-стратегия).
- **Решения:**
  - `+` 2D вместо 3D осознанно: «технический ад» 3D заменён рисунком.
  - `+` Готовые инструменты Unity вместо своих: фокус на арте, а не движке.
  - `+` PlayMaker: скорость итераций ИИ без программиста.
  - `−` Ручной труд не масштабируется (Silksong как мем долгостроя).
- **Влияние:** оптимизация — выбор размерности важнее всех оптимизаций вместе взятых; арт — `art_direction_stylization` в чистом виде.
- **DSS:** `art_direction_stylization`, `sprite_atlas_batching`, `particle_pooling`, `tilemap_chunk_streaming`.
- **Источники:** Nintendo-интервью (https://www.nintendo.com/au/news-and-articles/the-metamorphosis-of-hollow-knight-with-team-cherry-aussie-developer-interview), Unity case (https://unity.com/made-with-unity/hollow-knight), MCV (https://mcvuk.com/development-news/when-we-made-hollow-knight/), Team Cherry PlayMaker (https://www.teamcherry.com.au/blog/inside-the-mind-of-a-bug-unity-and-playmaker), RedBull (https://www.redbull.com/ie-en/hollow-knight-nintendo-interview).

### 28. Assassin’s Creed Unity (2014, Ubisoft)

- **Движок:** Anvil. Тысячи NPC Парижа, PBR-освещение нового поколения. Масштаб 1:1 дал до 50 000 draw calls на кадр — однопоточный DX11 захлебнулся в драйверных очередях даже на флагманах; сетка волюметрических Light Probes запекалась на серверных кластерах неделями.
- **Релиз ПК — катастрофа:** no-face баг (две видеокарты, лечился day-1 патчем), просадки на любом железе (SLI 980 не спасали), краши, очередь инструкций перегружена. Ключевой факт: толпа оказалась НЕ виновата (тесты Ubisoft), виноваты очередь инструкций и приоритизация ядер + камера на точках обзора.
- **Патчи:** Live Updates блог, патч 3+, драйверы NVIDIA/AMD. Репутационно — извинения и бесплатные игры.
- **Причина репутации:** реализация (профилирование не того: оптимизировали толпу, а давила очередь) + функционал (Париж 1:1 всё равно впечатляет).
- **Решения:**
  - `+` Толпа как фича, а не баг: оставили плотность, чинили очередь.
  - `−` Диагностика по интуиции вместо профайлера на старте.
  - `−` AMD-конфигурации страдали сильнее: зоопарк ПК.
- **Влияние:** оптимизация — меряй очередь инструкций, а не подозреваемых; менеджмент — честный live-блог вместо молчания.
- **DSS:** `crowd_instancing_impostors`, `agent_update_budget`, `ecs_data_oriented_crowd`, `multithreaded_physics_jobs`.
- **Источники:** IGN no-face (https://www.ign.com/articles/2014/11/19/ubisoft-on-ac-unitys-no-face-bug-details-coming-optimizations), MCV толпа не виновата (https://mcvuk.com/business-news/ubisoft-says-in-game-crowd-sizes-not-linked-to-assassins-creed-unity-performance-problems), PCWorld (https://www.pcworld.com/article/436330/warning-assassins-creed-unity-for-pc-is-riddled-with-performance-issues.html), PC Gamer AMD (https://www.pcgamer.com/ubisoft-acknowledges-assassins-creed-unity-problems-on-amd-hardware/), KitGuru очередь (https://www.kitguru.net/gaming/matthew-wilson/ubisoft-has-discovered-acu-low-frame-rate-cause/).

### 29. DOOM Eternal (2020, id Software)

- **Движок:** idTech 7. Полный forward (без G-буфера!), depth pre-pass (пушка → статика → динамика), compute-растеризатор кластеризации света (гексаэдры → тайлы 256px → 32px, битфилды), ~500 uber-шейдеров + bindless + динамический мерж draw calls в indirect-буфер, SSDO, атласы света частиц, атмосферный LUT за 32 кадра. Vulkan only.
- **Релиз ПК — эталон:** сотни fps, позже RT-отражения (−38% на 3080, т.е. 3.5 мс — дёшево) + DLSS (2060 тянет RT). Настройки ultra nightmare отключают LOD — ловушка для энтузиастов (цельтесь в ultra).
- **Причина репутации:** реализация (чистейшая инженерия десятилетия) + функционал (мясорубка как ритм-игра).
- **Решения:**
  - `+` Forward + prepass + compute-кластеризация вместо deferred: прозрачность и MSAA без 250+ МБ буферов.
  - `+` Uber-шейдеры + bindless + мерж: ~500 PSO вместо тысяч, минимум смен состояний.
  - `+` Атласы и LUT с амортизацией: дорогой свет не каждый кадр.
  - `−` Порог входа в такую архитектуру — команда уровня id.
- **Влияние:** оптимизация — хрестоматия GPU-driven подхода; графика — forward жив; процесс — SIGGRAPH-доклад как документация.
- **DSS:** `bindless_uber_shaders`, `tiled_clustered_light_culling`, `depth_prepass_early_z`, `gpu_particle_simulation`, `pso_precaching_warmup`, `temporal_upscaling`, `hardware_raytraced_gi`.
- **Источники:** SIGGRAPH 2020 Hellscape (https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf), Simon Coenen (https://simoncoenen.com/blog/programming/graphics/DoomEternalStudy), DF RT-апгрейд (https://www.digitalfoundry.net/articles/digitalfoundry-2021-doom-eternal-ray-tracing-upgrade-analysed).

### 30. Metro Exodus (2019/2021, 4A Games)

- **Движок:** собственный 4A Engine. 2019: воксельное GI + RTGI первого отскока (солнце) + RTAO как опция. Enhanced Edition (2021): бесконечные отскоки через DDGI-зонды (сетка + накопление во времени), все 256 аналитических источников в сэмпле, эмиссивы, RT-туман/частицы/волосы, VRS Tier 1, DLSS 2.1, Vulkan.
- **Релиз ПК (2019):** достойно; Enhanced — отдельная игра (не патч!), бесплатно владельцам, но только для RT-карт. Результат: на 2060 быстрее оригинала до +16%, картинка уровня офлайна; налог — шум при низком сэмплинге и лаг накопления GI (~20 кадров).
- **Причина репутации:** реализация (первая AAA только-под-RT) + смелость separate-SKU.
- **Решения:**
  - `+` DDGI + temporal accumulation: бесконечность за цену кадра, а не экспоненты.
  - `+` Отдельный SKU вместо двух схем света: минус легаси-костыли.
  - `+` VRS только Tier 1 на прозрачности + DLSS: честные компромиссы с именами.
  - `−` Шум и лаг GI как врождённые; требование RT-карты отсекает аудиторию.
- **Влияние:** графика — RTGI как новый базовый свет; оптимизация — темпоральность везде; дистрибуция — отдельная ветка честнее патча-франкенштейна.
- **DSS:** `hardware_raytraced_gi`, `sdf_global_illumination`, `temporal_radiance_cache`, `temporal_upscaling`, `variable_rate_shading`, `volumetric_half_resolution`.
- **Источники:** DF Enhanced (https://www.digitalfoundry.net/articles/digitalfoundry-2021-inside-metro-exodus-enhanced-edition-pc-exclusive), 4A tech dive (https://www.4a-games.com.mt/4a-dna/in-depth-technical-dive-into-metro-exodus-pc-enhanced-edition).

---
*Партии 1–3 из 6. Продолжение ниже.*

---

## Партия 4

### 31. Cyberpunk 2077 (2020, CDPR)

- **Движок:** REDengine 4. Плотный вертикальный город, PBR-материалы, RT-GI/AO/отражения, позже — RT Overdrive (path tracing: ReSTIR/RTXDI на тысячи источников, SER-пакетирование шейдеров, нейронный кэш, DLSS 3 FG +57%, Ray Reconstruction).
- **Релиз ПК — терпимо на топах, ад на слабом:** баги/вылеты, низкая утилизация GPU, у AMD на старте вообще не было RT. PS4/Xbox One — катастрофа (снятие с PS Store). Патчи 1.04/1.05, затем 1.5/1.6, 2.0 + Phantom Liberty: переписанные системы, дерево навыков, полиция.
- **Причина репутации:** реализация (рели) + искупление (патчи + Overdrive как витрина будущего). Функционал (город, ветвления) был с первого дня.
- **Решения:**
  - `+` RT как опция поверх годного растра: без RT тоже красиво.
  - `+` Overdrive + DLSS/RR: path tracing в реальном времени на 4090.
  - `−` Старые консоли в ТЗ: игра не для этого железа.
  - `−` Дей-ван билд ≠ билд рецензентов.
- **Влияние:** графика — неон как стресс-тест RT; оптимизация — апскейл как часть дизайна, а не костыль; менеджмент — не врать про платформы.
- **DSS:** `hardware_raytraced_gi`, `temporal_upscaling`, `ml_frame_generation`, `crowd_instancing_impostors`, `volumetric_half_resolution`, `post_effect_selective`.
- **Источники:** DF RT Overdrive (https://www.digitalfoundry.net/articles/digitalfoundry-2023-cyberpunk-2077-rt-overdrive-how-is-path-tracing-possible-on-a-triple-a-game), DF high-end PC (https://www.digitalfoundry.net/articles/digitalfoundry-2020-cyberpunk-2077-high-end-pc-tech-analysis), PC Gamer Ray Reconstruction (https://www.pcgamer.com/cyberpunk-2077-2-0-nvidia-ray-reconstruction/), NVIDIA-интервью (https://www.nvidia.com/en-us/geforce/news/cyberpunk-2077-ray-tracing-overdrive-mode-interview/), Windows Central баги (https://www.windowscentral.com/cyberpunk-2077-known-bugs-and-launch-issues).

### 32. Black Myth: Wukong (2024, Game Science)

- **Движок:** Unreal Engine 5. Софтверный Lumen + опциональный полный RT (ReSTIR GI, тени, отражения, каустика), DLSS/FSR/XeSS/TSR + Frame Generation, слайдер суперсемплинга вместо пресетов.
- **Релиз ПК — честный и тяжёлый:** бесплатный Benchmark Tool до релиза (так должны делать все), предкомпиляция шейдеров 1–2 минуты, traversal-статтеры UE5, краши на Intel без baseline-профилей. Цифры: 4090 в 4K DLAA — 22 fps native, DLSS Quality — 41, +FG — 74; 1440p cinematic — 73; адекватен High-пресет (Lumen урезан).
- **Причина репутации:** реализация (первый китайский AAA как техно-витрина) + функционал (мифология, боссы). Жалоб на обман не было — инструмент показал всё заранее.
- **Решения:**
  - `+` Бенчмарк до релиза: ноль сюрпризов.
  - `+` Слайдер апскейла + 4 апскейлера: выбор вместо пресетов.
  - `+` RT как замена Lumen (дешевле на NV): Medium вместо Very High почти бесплатно.
  - `−` UE5-статтеры и шейдеры как налог движка.
  - `−` На AMD path tracing не вариант (ReSTIR под NV).
- **Влияние:** оптимизация — RT Low/Medium вместо Cinematic; процесс — бенчмарк как уважение к игроку.
- **DSS:** `hardware_raytraced_gi`, `temporal_upscaling`, `ml_frame_generation`, `pso_precaching_warmup`, `dynamic_resolution_scaling`.
- **Источники:** Wccftech benchmark tool (https://wccftech.com/black-myth-wukong-pc-benchmark-tool-available-ray-tracing-dlss-fsr-xess-support/), Steam Benchmark Tool (https://store.steampowered.com/app/3132990/Black_Myth_Wukong_Benchmark_Tool/), TechSpot review (https://www.techspot.com/review/2883-black-myth-wukong-benchmark/), DSOG (https://www.dsogaming.com/news/black-myth-wukong-pc-benchmark-tool-released-first-results/), TechSpot optimization guide (https://www.techspot.com/guides/2884-wukong-optimization/).

### 33. Mass Effect 3 (2012, BioWare)

- **Движок:** Unreal Engine 3. Коридорный шутер-RPG, мультиплеер Horde, Origin-обязательность (Steam-версии не было). Стриминга нет как класса: лифты Цитадели, сканеры Нормандии и шлюзы — замаскированные блокирующие загрузки (выгрузка подзоны + чистка сборщика мусора + чтение с диска).
- **Релиз ПК — технически ровно, культурно — взрыв:** концовки обнулили выборы трилогии → Retake Mass Effect (40k+, $80k благотворительности, жалоба в FTC), Extended Cut как бесплатное DLC-извинение. Спор «авторство vs фанаты» (Кен Левин против переписывания).
- **Причина репутации:** функционал (трилогия выборов) против реализации финала, дописанного в последний момент (запись Шина перенесена с августа на ноябрь).
- **Решения:**
  - `+` Extended Cut: объяснение вместо переписывания (Star Child, судьбы по EMS).
  - `+` Отказной финал как честная опция.
  - `−` Три цвета вместо ветвлений: обещание vs доставка.
  - `−` Origin-эксклюзив как дополнительный раздражитель.
- **Влияние:** менеджмент — фанаты как стейкхолдеры сюжета; техника вторична (движок отработал без скандалов).
- **DSS:** `navmesh_tiling_streaming`, `animation_compression`, `particle_pooling`; риск концептуального провала вне перфоманса.
- **Источники:** Wikipedia ending controversy (https://en.wikipedia.org/wiki/Mass_Effect_3_ending_controversy), BioWare Blog Muzyka (https://blog.bioware.com/2012/03/21/4108/), GameInformer Origin (https://gameinformer.com/b/news/archive/2012/01/15/origin-required-for-digital-physical-copies-of-mass-effect-3-on-pc.aspx), Ars (https://arstechnica.com/gaming/2012/03/bioware-responds-to-mass-effect-ending-complaints-as-protest-continues-to-grow/), Ars Muzyka (https://arstechnica.com/gaming/2012/03/bioware-taking-fan-criticism-to-heart-in-crafting-new-mass-effect-3-content/).

### 34. Batman: Arkham City (2011, Rocksteady)

- **Движок:** Unreal Engine 3 + DX11-ветка (тесселяция деревьев/кабелей по displacement-картам, сглаживание мешей), аппаратный PhysX (газеты, тряпки, листва с коллизиями, 500-серия NV).
- **Релиз ПК — сломанный DX11 на старте:** статтеры, лаги, провал на 32-битных Windows; Rocksteady советовала сидеть на DX9 до патча. Позже починили — и вышла эталонная версия (плюс стриминг без поп-ина консолей).
- **Причина репутации:** реализация (лучший ПК-порт года после патча) + функционал (открытый Аркхем, полёты).
- **Решения:**
  - `+` Тесселяция там, где видно (органика), а не везде.
  - `+` PhysX-мелочи как живость мира (газета, обёрнутая вокруг фонаря).
  - `−` DX11-режим как маркетинг раньше готовности.
  - `−` Старый PhysX SDK 2.8.4: низкая утилизация GPU, вторая карта как костыль (+11–23% fps).
- **Влияние:** оптимизация — фичи с измеримой ценой (тесселяция −2–3 fps, PhysX до −13); процесс — патч раньше, чем позор.
- **DSS:** `tiled_clustered_light_culling` (нет), `gpu_particle_simulation`, `physics_lod_sleeping`, `post_effect_selective`; честно: PhysX-цена в requires_conditions.
- **Источники:** DF PC comparison (https://www.digitalfoundry.net/articles/digitalfoundry-pc-tech-comparison-batman-arkham-city), NVIDIA guide (https://www.nvidia.com/en-us/geforce/news/batman-arkham-city-graphics-breakdown-and-performance-guide/), DSOG PhysX (https://www.dsogaming.com/pc-performance-analyses/batman-arkham-city-pc-performance-analysis/), Ars (https://arstechnica.com/gaming/2011/11/batman-arkham-city-on-pc-is-the-version-gotham-needs-and-you-deserve/).

### 35. S.T.A.L.K.E.R. 2: Heart of Chornobyl (2024, GSC Game World)

- **Движок:** Unreal Engine 5.1 (без Nanite на траве!), A-Life 2.0 (онлайн/оффлайн режимы NPC по дистанции стриминга). Та же пара «NVMe против CPU-декомпрессии» — Starfield: traversal-статтеры при пересечении границ секторов.
- **Релиз ПК — CPU-стена:** 9950X загружен на 59% в среднем в 4K, i9-10900K проваливается; traversal-статтеры; компиляция шейдеров при каждом запуске по 5–15 минут; 135 ГБ дей-ван патч; A-Life ужата оптимизацией (NPC спавнятся в воздухе, дальность симуляции срезана) — фичу тихо убрали со Steam-страницы.
- **Версии:** патч 1.7 (2025): +26% в CPU-bound, стабильный фреймтайм, 19 упоминаний «optimised»; PS5-версия; план апгрейда до UE 5.5.4 (дешевле VSM).
- **Причина репутации:** реализация (A-Life как обещание) + контекст (война, отключения света у половины команды) + функционал (Зона жива).
- **Решения:**
  - `+` Честный разбор GSC: дальность A-Life vs память, офлайн/онлайн режимы.
  - `+` Патч 1.7 вместо оправданий: меши, материалы, свет, стриминг.
  - `−` Оптимизация, съевшая фичу: сначала дальность, потом баги поверх.
  - `−` Шейдеры при каждом запуске как налог UE5.
- **Влияние:** ИИ — радиус симуляции как бюджет (урок для DSS `agent_update_budget`); оптимизация — CPU-bound сценарии отдельно от GPU.
- **DSS:** `agent_update_budget`, `ecs_data_oriented_crowd`, `crowd_instancing_impostors`, `time_sliced_pathfinding`, `async_loading_pipeline`, `temporal_upscaling`, `ml_frame_generation`.
- **Источники:** Digital Trends CPU-стена (https://www.digitaltrends.com/computing/stalker-2-pc-performance/), IGN A-Life (https://me.ign.com/en/pc/226710/news/stalker-2-dev-gsc-game-world-explains-for-the-first-time-what-went-wrong-with-a-life-20-and-why-it-was-removed-from-the-game-s-description-on-steam), support.stalker2 (https://support.stalker2.com/hc/en-us/articles/29796874027537-Performance-Optimization-on-PC), DSOG (https://www.dsogaming.com/pc-performance-analyses/stalker-2-benchmarks-pc-performance-analysis/), DF patch 1.7 (https://www.digitalfoundry.net/news/2025/11/analysis-stalker-2-patch-1-7-delivers-dramatic-perf-boosts-on-pc-and-xbox).

### 36. Need for Speed: Most Wanted (2005, EA Black Box)

- **Движок:** собственный EAGL. ИИ — иерархия AIGoals/AIActions: гонщики, копы (BoxIn/RollingBlock/Pit формации, блокпосты, шипы, вертолёт), трафик с паттернами спавна; CARP EventSequencer + Hermes-сообщения для катсцен и триггеров. Физика отделена от рендера: коллизии трассы — сплайновый кэш на километры вперёд (pop-in визуала допустим, провал сквозь дорогу — нет), сцепление — формула Pacejka со стабильным шагом.
- **Релиз ПК:** ровно для эпохи; фурор — Blacklist-прогрессия и погони. Драмы две: Speedbreaker (bullet time за рулём) расколол студию — часть разработчиков уволилась, считая кнопку оскорблением скорости; вечный кранч ежегодных релизов (Carbon уже резали).
- **Причина репутации:** функционал (погони, heat, Blacklist) + реализация (ИИ-экосистема, разобранная реверсерами спустя 20 лет).
- **Решения:**
  - `+` Иерархия целей/действий: тактика копов из кубиков.
  - `+` Heat как регулятор сложности и спавна.
  - `±` Speedbreaker: игрокам — восторг, части команды — предательство скорости.
  - `−` Годовой цикл: вырезанный контент как традиция серии.
- **Влияние:** ИИ — формации вместо скриптов; менеджмент — механика, ради которой увольняются, должна быть опциональной; сообщество — реверс как документация.
- **DSS:** `agent_update_budget`, `flow_field_pathing`, `time_sliced_pathfinding`, `navmesh_tiling_streaming`, `fixed_timestep_physics`.
- **Источники:** DeepWiki AI (https://deepwiki.com/dbalatoni13/nfsmw/5-ai-system), nfsmw-re GitHub (https://github.com/s-b-repo/nfsmw-re), racinggames.gg ретроспектива (https://racinggames.gg/article/the-underground-era-a-retrospective-on-black-boxs-early-need-for-speed-games-pt-1), AMA Speedbreaker (https://tech.yahoo.com/gaming/articles/one-nfs-most-wanted-feature-170614109.html), CARP EventSequencer (https://deepwiki.com/dbalatoni13/nfsmw/7.3-event-and-trigger-system).

### 37. Genshin Impact (2020, HoYoverse)

- **Движок:** глубоко кастомизированный Unity. Два конвейера: консольный и мобильный (мобильный — базовый!). 8 каскадов теней с чередованием обновления (5 в кадр), soft shadows только в penumbra (2.6→1.7 мс), тройное AO (HBAO + volume + капсульное), сжатие теней локального света с compute-распаковкой, SSR 1.5 мс на PS4 Pro, волюметрика + отдельные god rays, PBR-стилизация без ACES. NPR: нормали лиц запечены в сферические векторы + карта полутонов (Face Map) вместо честного света; рендер-таргеты ужаты под on-chip tile-память TBDR-чипов (Adreno/Mali) — иначе троттлинг LPDDR.
- **Релиз ПК/мобайл:** гладко для масштаба; вечная война за гигабайты обновлений и нагрев телефонов. Философия: зрелые техники вместо модных, кроссплей и кроссплатформа с первого дня.
- **Причина репутации:** реализация (один билд на телефон и PS5) + функционал (гача-экономика + регионы каждые 6 недель).
- **Решения:**
  - `+` Mobile-first: потолок задаёт слабое звено — и всё летает везде.
  - `+` Каскады/проходы по расписанию, а не каждый кадр.
  - `+` Считать только penumbra/границы: экономика пикселя.
  - `−` Кастомизация движка = вечная поддержка форка.
- **Влияние:** оптимизация — расписание проходов как первый класс; графика — стилизация + зрелые техники вместо RT-гонки; процесс — Unity China как ресурс.
- **DSS:** `cascaded_shadow_maps`, `volumetric_half_resolution`, `screen_space_gi`, `lightmap_compression_streaming`, `build_size_startup_budgets`, `differential_patch_pipeline`.
- **Источники:** GamesIndustry.biz (https://www.gamesindustry.biz/making-genshin-impact-shine-on-everything-from-mobile-to-ps5), Unity Dojo слайды (https://www.slideshare.net/slideshow/210617-unity-dojo20211mihoyozhenzhongyi/249437133), Nugglet разбор конвейера (https://nugglet.github.io/posts/2022/12/console_graphics_rendering_pipeline_genshin_impact), BrandAnime (https://brandanime.com/how-genshin-impact-is-made/), GenshinGuidesHub 2026 (https://www.genshinguideshub.com/what-engine-does-genshin-impact-use).

### 38. Fall Guys (2020, Mediatonic)

- **Движок:** Unity. Физика вечеринки на 60 бобов, яркие простые материалы. Сеть — гибрид: позиция своего боба считается локально, сервер валидирует коллизии и рассылает интерполяцию (полный авторитетный сим 60 рэгдоллов убил бы тикрейт); в толпе коллизии смягчаются до полупроницаемых, иначе сингулярность разлёта.
- **Релиз ПК (2020):** хит пандемии; затем F2P-перезапуск 2022 (Switch/Xbox/EGS, кроссплей): сервера легли в день перехода (матчмейкинг, лобби отключены), Steam-пик x5, рекорд онлайна. Починили за дни; уроки: память PlayStation, FPS на object-heavy уровнях, хвосты при высоком пинге.
- **Причина репутации:** функционал (доступность + хаос) + реализация (выжили под x-кратной нагрузкой). Платформа как контент.
- **Решения:**
  - `+` Простая картинка = дешёвый кадр на всех платформах.
  - `+` Быстрое отключение лобби/магазина как рубильник нагрузки.
  - `−` F2P-миграция без запаса серверов: предсказуемый обвал.
  - `−` Пинг-зависимые механики (хвосты) без компенсации.
- **Влияние:** сеть — рубильники фич вместо падения; менеджмент — capacity planning под фан, а не среднее.
- **DSS:** `headless_dedicated_server`, `tickrate_budgeting`, `network_relevancy_priority`, `client_prediction_reconciliation`, `physics_lod_sleeping`, `crowd_instancing_impostors`.
- **Источники:** VGC F2P-серверы (https://www.videogameschronicle.com/news/fall-guys-is-suffering-online-problems-as-the-game-goes-free-to-play/), Nintendo Life (https://www.nintendolife.com/news/2022/06/fall-guys-suffers-from-server-issues-after-free-to-play-switch-launch), PC Gamer (https://www.pcgamer.com/fall-guys-steam-player-count-skyrockets-a-day-after-it-becomes-an-epic-exclusive/), fallguys.com patch notes (https://www.fallguys.com/news/fall-guys-free-for-all-release-notes), PSU (https://www.psu.com/news/fall-guys-ultimate-knockouts-free-to-play-launch-causes-multiple-issues-across-platforms/).

### 39. Hades (2018/2020, Supergiant)

- **Движок:** собственный (C# → переписан на нативный C посреди разработки ради портов и перфоманса, с глюками и крашами в процессе). Рендер-иллюзия: строго 2D-спрайты, фиксированная изометрия (0.5 по Y), painter's algorithm сортировкой на CPU (5000 объектов наивным O(n²) уронили бы кадр), физика в 3D с виртуальной Z, рендер — проекция. Память: гигантские атласы сжатых спрайтов с аппаратной декомпрессией — ноль пауз при десятках врагов.
- **Релиз:** Early Access как метод (месячные майлстоуны, одна платформа EGS сначала — иначе не потянуть темп), нарратив как пилотные серии.
- **Причина репутации:** функционал (рогалик с сюжетом, смерть как прогресс) + процесс (EA как соавторство с игроками).
- **Решения:**
  - `+` Фиксированная камера как архитектурный замок: весь рендер упрощается.
  - `+` Разделение симуляции (3D) и рендера (2D): каждой подсистеме своё.
  - `+` Одна платформа на старте EA: темп вместо охвата.
  - `−` Переписывание движка на ходу: глюки и краши как налог.
  - `−` CPU-сортировка вместо z-буфера: потолок объектов.
- **Влияние:** оптимизация — ограничение как фича; процесс — EA как метод, а не скидка.
- **DSS:** `art_direction_stylization`, `sprite_atlas_batching`, `particle_pooling`, `fixed_timestep_physics`.
- **Источники:** ThatGuyGlen док (https://www.youtube.com/watch?v=CIk8Y9qkYx0), GPC Coffee&Code (https://podscan.fm/podcasts/coffee-code-ampamp-shaders-real-time-rendering-conversations/episodes/custom-rendering-engine-for-hades-and-hades-ii), GameDeveloper EA-процесс (https://www.gamedeveloper.com/design/supergiant-s-fourth-outing-i-hades-i-introduces-a-more-mature-organized-dev-process), Film Stories (https://filmstories.co.uk/gaming/hades-interview-were-holding-nothing-back/), GeekDad (https://geekdad.com/2019/10/narrative-and-early-access-supergiants-greg-kasavin-discusses-hades-development/).

### 40. Far Cry (2004, Crytek)

- **Движок:** CryEngine 1. Километровая дальность, HDR OpenEXR FP16 (патч 1.3, только GeForce 6, конфликт с AA в ROP), geometry instancing, ИИ наёмников с флангами.
- **Релиз ПК:** бенчмарк эпохи; требователен (6800 Ultra/X800 XT для максимума). Позже GameGPU-ретротесты: приемлемый fps уже с HD 6850/GTX 650 Ti.
- **Причина репутации:** реализация (открытые тропики + HDR первыми) + функционал (свобода подхода).
- **Решения:**
  - `+` HDR через FP16 + Kawase bloom + Reinhard: глаз-адаптация раньше всех.
  - `+` Инстансинг геометрии и LOD как база открытых уровней до 3 км.
  - `−` HDR vs AA: mutually exclusive в ROP — выбор без хорошего ответа.
  - `−` Fill-rate голод: красиво только на флагманах.
- **Влияние:** графика — HDR как стандарт после; оптимизация — инстансинг и LOD для открытых пространств.
- **DSS:** `voxel_cone_tracing` (нет), `post_effect_selective`, `gpu_instancing_vegetation`, `hierarchical_lod`, `deferred_forward_plus_choice`.
- **Источники:** bit-tech HDR (https://bit-tech.net/reviews/gaming/pc/farcry_patch13_eval/5/), SIGGRAPH CryEngine2 notes (https://advances.realtimerendering.com/s2007/Mittring-Finding_NextGen_CryEngine2(Siggraph07%20Course%20Notes).pdf), GameGPU retro (https://en.gamegpu.com/test-gpu/retro-test-gpu/far-cry-2004-retro-test-gpu), GameGPU 2023 (https://en.gamegpu.com/test-gpu/action-fps-tps/far-cry-2004-retro-test-gpu-cpu), Far Cry+DirectX (https://studylib.net/doc/9861670/far-cry-and-directx).

---
*Партии 1–4 из 6. Продолжение ниже.*

---

## Партия 5

### 41. Hearts of Iron IV (2016, Paradox)

- **Движок:** Clausewitz + TBB. Симуляция мира по подсистемам, UI и рендер — не в отдельных потоках; зерно параллелизма — сущность (самая медленная решает). Почасовой пересчёт снабжения/боёв сотен дивизий по десяткам тысяч провинций; late-game (1943–45) сутки считаются секундами. Многопоточность упёрлась в сетевой детерминизм: расхождение float-порядка = мгновенный Out of Sync.
- **Релиз ПК:** ровно для ниши; вечная тема — поздняя игра и моды: тормозит главный поток. Миф «движок на одном ядре» — наполовину правда: спроектирован под одно, дотянут параллелями.
- **Версии:** DLC наращивают данные (варианты техники × рынок × ленд-лиз) — цель каждого патча «не просесть», net-zero перфоманс; Jomini/CK3-модель (read/write-фазы) как будущее.
- **Причина репутации:** функционал (песочница WWII, моды) + реализация (скрипты как код с квадратичной ценой: решение Болгарии проверяет все страны против всех).
- **Решения:**
  - `+` Триггеры-фильтры (`target_root_trigger`) вместо перебора: порядок от сложности условия.
  - `+` Параллелизация по подсистемам + вынос аллокаций из горячего кода (глобальные локи ОС).
  - `−` Скриптовый язык без статического анализа: дизайнеры пишут O(n²), не зная.
  - `−` Сущность-зерно: одна тяжёлая страна тормозит все ядра.
- **Влияние:** оптимизация — данные первее потоков; процесс — юнит-тесты скриптового движка как условие автооптимизаций.
- **DSS:** `time_sliced_pathfinding`, `agent_update_budget`, `deterministic_lockstep`.
- **Источники:** ACCU 2023 Clausewitz threading (https://accu.org/conf-docs/PDFs_2023/XMultiThreadingModelinParadoxGamesPastPresentandFuture.pdf), HoI4 Dev Diary Performance (https://devtrackers.gg/heartsofiron/p/726ec25f-developer-diary-performance-and-modding), Steam-обсуждение ядер (https://steamcommunity.com/app/394360/discussions/0/1850323802577871303/), Mathieu Ropert скрипты (https://mropert.github.io/2025/05/27/making_games_tick_part4/), eprison mirror (https://www.eprison.de/spiele/hearts-of-iron-4/steam-news/6148070194801725069/2624/80740.html).

### 42. Sniper Elite 5 (2022, Rebellion)

- **Движок:** Asura. Фотограмметрия, улучшенные вода/киллкам/аудио-детект ИИ; RT отложен сознательно. Пост-AA + FSR 1.0 вместо TAA (мерцание листвы!), переменное разрешение, DX12 ≈ Vulkan. X-Ray Kill Cam: баллистика с гравитацией/деривацией/ветром + кавитационная полость и процедурные осколки костей; на время киллкама мир замирает (мощности уходят в локальную симуляцию).
- **Релиз ПК:** спокойно и хорошо: 60+ fps на средних картах, квадрокор достаточно (двухъядерным — нет), Deck — 30 fps. Серия S проседает до 40-х (предложение — кап 30).
- **Причина репутации:** реализация (свой движок инди-студии держит AAA-план) + функционал (x-ray, открытые уровни).
- **Решения:**
  - `+` Отказ от RT и TAA как осознанный выбор под 60 fps.
  - `+` Фотограмметрия вместо полигонов: картинка без цены геометрии.
  - `−` Пост-AA: алиасинг и шиммер как вечный налог.
  - `−` Series S без капа: 40-е вместо стабильных 30.
- **Влияние:** графика — TAA vs пост: temporal побеждает почти всегда; оптимизация — квадрокор как минимум честно.
- **DSS:** `post_effect_selective`, `temporal_upscaling`, `dynamic_resolution_scaling`, `physics_lod_sleeping`, `animation_lod_budget`.
- **Источники:** DSOG PC (https://www.dsogaming.com/pc-performance-analyses/sniper-elite-5-pc-performance-analysis/), DF Asura (https://www.digitalfoundry.net/articles/digitalfoundry-2022-sniper-elite-5-tech-analysis-rebellions-in-house-asura-engine-continues-to-impress), Wccftech Q&A (https://wccftech.com/sniper-elite-5-qa-fsr-1-0-support-engine-advancements-and-game-improvements/), PCBench (https://pcbench.net/benchmarks/sniper-elite-5), DF YouTube (https://www.youtube.com/watch?v=mnwtr07q9eE).

### 43. Portal (2007, Valve)

- **Движок:** Source + студенческий Narbacular Drop (DigiPen, свой движок): Габен нанял команду через 15 минут демо. Портал — бесконечно тонкая плоскость с заменой матрицы: M_out = M_exit × M_enter⁻¹ × M_in; тело клонируется по другую сторону с сохранением импульса.
- **Техника:** порталы = динамическая текстура (рендер сцены с преобразованной камеры + отсечение между камерой и выходом) + stencil-буфер для рекурсии и HDR-bloom; физика с дыркой в стене (полкуба с каждой стороны, коллизия с самим собой); LOD и видимость пересчитаны относительно порталов (дистанция — выбор из трёх отрезков, луч зрения — сквозь порталы).
- **Релиз ПК:** в составе Orange Box, без скандалов. Урок: украсть механику у студентов честнее, чем изобретать.
- **Причина репутации:** реализация (порталы в чужом движке) + функционал (GLaDOS, обучение без слов).
- **Решения:**
  - `+` Stencil вместо костылей: бесконечная рекурсия почти бесплатно.
  - `+` Фрустум-каллинг по краям портала + оптимизация списков рендера (сцены рисуются 2–3 раза!).
  - `−` Переписывание физики и видимости Source под порталы.
- **Влияние:** оптимизация — рендер N+1 раз требует отдельной экономики кадра; процесс — плей desa-тесты решают, что оставить.
- **DSS:** `baked_occlusion_culling`, `fixed_timestep_physics`, `physics_lod_sleeping`.
- **Источники:** Narbacular tech doc (https://nuclearmonkeysoftware.com/documents/narbacular_drop_technical_design_document.pdf), GameDeveloper Thinking With Portals (https://www.gamedeveloper.com/design/thinking-with-portals-creating-valve-s-new-ip), RPS интервью (https://www.rockpapershotgun.com/rps-interview-portals-kim-swift-and-jeep-barnett), IGS 2007 (https://www.youtube.com/watch?v=2F0SVZA9fIo), Narbacular GDD (https://nuclearmonkeysoftware.com/documents/narbacular_drop_game_design_document.pdf).

### 44. Portal 2 (2011, Valve)

- **Движок:** Source. Новое: гели (TAG-команда нанята; отталкивающий/ускоряющий/конверсионный; адгезионный вырезан — укачивание), excursion funnels, мосты света, лазеры; world imposters (упрощённая сцена в атлас) для отражений в воде, сплит-скрина и глубоких порталов; кооп со сплит-скрином и пингами. Гели запечены в текстуры уровня (капли растекаются по сплайнам, меняя трение/упругость полигонов) — вместо гидродинамики частиц.
- **Релиз ПК:** эталонно; кооп — лучший в истории по организации (пинг, обратный отсчёт, совместные жесты).
- **Причина репутации:** функционал (кооп-пазлы, Уитли) + реализация (импостеры как перфоманс-архитектура).
- **Решения:**
  - `+` Импостер мира: отражения/сплит/глубокие порталы за копейки CPU.
  - `+` Гели из чужой студенческой игры (TAG) — хантинг механик.
  - `+` Плей desa-тест как арбитр (адгезионный гель убит укачиванием, воронка страхуется автопорталом).
  - `−` Каждая механика умножает комбинаторику тестов камер.
- **Влияние:** оптимизация — импостер вместо полного рендера; дизайн — вырезать по тошноте, а не по вкусу.
- **DSS:** `splitscreen_render_budget`, `gpu_particle_simulation`, `post_effect_selective`, `fixed_timestep_physics`.
- **Источники:** Portal Wiki funnels (https://theportalwiki.com/wiki/Excursion_Funnel), dev commentary (https://theportalwiki.com/wiki/Portal_2_developer_commentary), Gels (https://theportalwiki.net/wiki/Gels), Wikipedia (https://en.wikipedia.org/wiki/Portal_2), кооп-камера (https://theportalwiki.net/wiki/Portal_2_Co-op_Course_5_Chamber_8).

### 45. Red Dead Redemption (2010, Rockstar San Diego)

- **Движок:** RAGE + Euphoria (тряпичные падения каскадёров, лошади-стантмены с сухожилиями). Экосистема из 40+ видов, прерии вместо улиц. На PS3 декомпрессия текстур и тесселяция рельефа вынесены на микроядра SPU Cell (DMA в Local Store 256 КБ) — иначе split-память 256+256 МБ не тянула.
- **Релиза на ПК не было вообще** (только PS3/Xbox 360; ПК — лишь облако/эмуляция спустя годы). Технически: 360 — 720p + 2xMSAA, PS3 — 1152x640 + quincunx (мыло), агрессивнее LOD и вырезанная листва на PS3 (нет eDRAM под альфу), vsync-кап 30 на PS3 против рваных 40+ на 360.
- **Причина репутации:** функционал (вестерн как главный герой, честь, охота) + реализация (экосистема и Euphoria).
- **Решения:**
  - `+` Пустоши вместо улиц: дальность без плотности.
  - `+` Euphoria вместо анимаций смерти.
  - `−` PS3-порезы: листва, LOD, тени, вода.
  - `−` Отсутствие ПК-версии на десятилетие.
- **Влияние:** графика — пропускная способность памяти решает (eDRAM vs split); аудио/экосистема — живой мир как контент.
- **DSS:** `gpu_procedural_placement`, `vegetation_atlas_lod`, `hierarchical_lod`, `physics_lod_sleeping`, `animation_lod_budget`.
- **Источники:** DF Face-Off (https://www.digitalfoundry.net/articles/digitalfoundry-red-dead-redemption-face-off), GameSpot Q&A Carson (https://web.archive.org/web/20190728221459/https:/www.gamespot.com/articles/red-dead-redemption-exclusive-qanda/1100-6249985/), IQGamer 360 vs PS3 (http://imagequalitymatters.blogspot.com/2010/05/tech-analysis-red-dead-redemption-360.html), CGMagazine (https://www.cgmagonline.com/review/game/red-dead-redemption/), TechRadar Euphoria (https://www.techradar.com/news/gaming/rockstar-pushes-in-game-physics-envelope-597497).

### 46. Red Dead Redemption 2 (2018/2019, Rockstar)

- **Движок:** RAGE. Параллакс, тесселяция снега/грязи, волюметрика (near/far resolution!), вода с физикой, мех лошадей, декали. Рельеф — асинхронный Terrain Clipmapping (концентрические квадраты, логарифмическое падение плотности); на ПК распаковка ассетов и флоры грузит PCIe и требует многопоточного CPU.
- **Релиз ПК (2019):** краши, лаунчерные танцы (Epic+R* по очереди), курсор, статтер мыши (raw vs direct input), дыры в земле на Parallax Ultra. Железо: тред-дефицит статтерит независимо от GPU; Vulkan быстрее DX12 и ровнее на AMD; DLSS слабый (+15–20% и алиасинг) — лучше TAA+шарп.
- **Патчи и уроки DF:** пресеты ниже ультра почти не хуже картинки (вуаля, Xbox One X живёт на «ниже низкого»); MSAA — главный пожиратель; async compute в XML.
- **Причина репутации:** функционал (мир как симуляция эпохи) + реализация (масштаб деталей). Техдолг — цена амбиций.
- **Решения:**
  - `+` Зернистые 40+ настроек вместо 4 пресетов.
  - `+` Встроенный бенчмарк (редкость!).
  - `−` Ultra как ловушка (вуалетри-метрика вместо пользы).
  - `−` Лаунчерная матрёшка Epic+R*.
- **Влияние:** оптимизация — настройки поштучно, а не пресетами; CPU — треды вместо герцовки.
- **DSS:** `volumetric_half_resolution`, `terrain_clipmap`, `vegetation_atlas_lod`, `temporal_upscaling`, `dynamic_resolution_scaling`, `multithreaded_physics_jobs`, `crowd_instancing_impostors`.
- **Источники:** GN settings deep-dive (https://zakruti.com/itech/gamersnexus/video-556), OC3D review (https://overclock3d.net/reviews/software/red-dead-redemption-2-pc-performance-review-and-optimisation-guide/), DF 60fps (https://www.digitalfoundry.net/articles/digitalfoundry-2019-what-does-it-take-to-run-red-dead-redemption-2-at-60fps), GN stutter/hyperthreading (https://zakruti.com/itech/gamersnexus/video-559), DSOG DLSS (https://www.dsogaming.com/pc-performance-analyses/red-dead-redemption-2-dlss-2-2-10-0-benchmarks).

### 47. Ghost of Tsushima (2020/2024, Sucker Punch / Nixxes)

- **Движок:** собственный + Nixxes-порт. Полный набор апскейлов с развязкой: FSR3 FG работает поверх DLSS SR (впервые!), XeSS, DLAA.
- **Релиз ПК — образцовый:** 60 fps даже на двух ядрах (+SMT против статтера), 2080 Ti на 1080p/max, 7900 XTX ≈ 4090 в растре. Ложки: нативный TAA сломан (пикселизация и шиммер — DLSS Performance лучше натива!), DoF пикселит вдали, нет слайдера шарпа, XeSS плох, Arc глючит (меши не там, тени дёргаются), катсцены + FG = микростаттер/чёрные кадры.
- **Причина репутации:** реализация (порт-эталон) + функционал (ветер как интерфейс, дуэли).
- **Решения:**
  - `+` Развязка FG и апскейла: миксуй лучшее с лучшим.
  - `+` CPU не важен (двухъядерник тянет) — редкость.
  - `−` Сломанный нативный TAA заставляет включать апскейл.
  - `−` 8 ГБ VRAM в 4K Very High — заикания в городах.
- **Влияние:** графика — апскейл как дефолт, а не опция; QA — Arc как отдельный континент.
- **DSS:** `temporal_upscaling`, `ml_frame_generation`, `dynamic_resolution_scaling`, `post_effect_selective`, `gpu_instancing_vegetation`.
- **Источники:** PC Gamer (https://www.pcgamer.com/hardware/ghost-of-tsushima-pc-performance/), TechPowerUp DLSS/FSR/XeSS (https://www.techpowerup.com/review/ghost-of-tsushima-dlss-vs-fsr-vs-xess-comparison/), DSOG (https://www.dsogaming.com/pc-performance-analyses/ghost-of-tsushima-benchmarks-pc-performance-analysis/), DSOG FG (https://www.dsogaming.com/articles/ghost-of-tsushima-amd-fsr-3-0-vs-nvidia-dlss-3-benchmarks-comparisons/), TechPowerUp 35 GPU (https://www.techpowerup.com/review/ghost-of-tsushima-benchmark/).

### 48. Forza Horizon 3 (2016, Playground Games)

- **Движок:** ForzaTech, DX12, UWP. Австралия, 4K/21:9.
- **Релиз ПК — одноядерный позор:** одно ядро в полке, остальные <70–80%, 980 Ti на 50–60% (CPU-bottleneck), на medium без MSAA нет стабильных 60; двухъядерным — неиграбельно. Плюс UWP-боли.
- **Патчи:** статтер починили быстро; май 2017 — DX12 out-of-order рендер + новая аффинность потоков + опция Threaded Optimization + Very Low пресеты. Но синглтред-наследие до конца не ушло.
- **Причина репутации:** функционал (фестиваль, Австралия) против реализации (потоки).
- **Решения:**
  - `+` Честный постмортем патчами: out-of-order, аффинность, пресеты.
  - `+` Опции с подписью цены (CPU/GPU/VRAM у каждой настройки).
  - `−` Один поток как архитектурный грех.
  - `−` UWP как платформа боли.
- **Влияние:** оптимизация — потоки раньше контента; презентационная — 30 fps с инпут-лагом хуже честных 30.
- **DSS:** `multithreaded_physics_jobs`, `time_sliced_pathfinding`, `dynamic_resolution_scaling`, `quality_tier_scalability`, `crowd_instancing_impostors`.
- **Источники:** DSOG анализ (https://www.dsogaming.com/pc-performance-analyses/forza-horizon-3-pc-performance-analysis/), первый патч (https://www.dsogaming.com/news/forza-horizon-3-first-patch-detailed-promises-to-fix-stuttering-releases-later-today/), перф-патч май 2017 (https://www.dsogaming.com/news/forza-horizon-3-pc-performance-patch-is-now-live-full-release-notes-revealed/), октябрьский апдейт (https://www.dsogaming.com/news/forza-horizon-3s-latest-update-fixes-stuttering-single-thread-issues-remain-unsolved/), GTPlanet (https://www.gtplanet.net/latest-update-for-forza-horizon-3-addresses-windows-10-performance-issues/).

### 49. Forza Horizon 4 (2018, Playground Games)

- **Движок:** ForzaTech, сезоны (зима меняет физику и карту), 60+ fps цель.
- **Релиз ПК — образцовый:** 60 fps даже на двух ядрах (+HT, без HT не стартует!), 6+ ядер — сладкое место, AMD лучше аналогов NV в DX12; сезоны, дрэг, дрифт. Мелочи: краши при смене настроек/RivaTuner, AMD-артефакты MSAA без рестарта, шейдерный кэш Steam-версии короче MS Store (лечится удалением cef/scratch).
- **Причина репутации:** реализация (уроки FH3 выучены) + функционал (сезоны как живой мир, Британия).
- **Решения:**
  - `+` Многопоточность с запасом: двухъядерник тянет 60.
  - `+` Сезон как переиспользование карты x4 контента.
  - `−` Шейдерный кэш разной длины между сторами.
  - `±` MSAA-артефакты AMD как налог API.
- **Влияние:** оптимизация — сиквел как шанс переписать потоки; контент — сезоны дешевле новой карты.
- **DSS:** `multithreaded_physics_jobs`, `quality_tier_scalability`, `dynamic_resolution_scaling`, `post_effect_selective`, `volumetric_half_resolution`.
- **Источники:** DSOG (https://www.dsogaming.com/pc-performance-analyses/forza-horizon-4-pc-performance-analysis/), GamingBolt патч (https://gamingbolt.com/forza-horizon-4-patch-fixes-xbox-one-x-stutters-improves-pc-performance/amp), Steam-шейдеры (https://steamcommunity.com/app/1293830/discussions/0/3147430952107004048/), PC Gamer требования (https://www.pcgamer.com/almost-every-gpu-can-do-60-fps-in-forza-horizon-4-and-look-great-doing-it/).

### 50. Ultrakill (2020+, Hakita / New Blood)

- **Движок:** Unity. Ретро-FPS: кровь как лечение, стиль как валюта, скорость как религия. Пайплайн имитирует PS1: квантование вершин в экранную сетку (Vertex Snapping, дрожание геометрии), аффинная интерполяция UV без деления на W (Texture Warping); темпоралки и тяжёлый пост вырезаны — инпут-лаг на минимуме дисплея.
- **Релиз (EA):** эталонный ранний доступ: эпизоды-акты, фидбэк с форумов/Discord, без кранча. Техдолг — комнатная загрузка (видны только 2 комнаты!), чекпоинты копируют объекты (статтер нелинейных уровней, пример 1-3), окклюзия Unity, бокс-коллайдеры вместо мешей, батчинг-статики, оптимизация мешей 5×5.
- **Причина репутации:** функционал (скорость + стиль) + реализация (читаемость геометрии вместо деталей) + процесс (EA как диалог).
- **Решения:**
  - `+` Комнаты вместо мира: не видно — не существует (почти буквально).
  - `+` Простой ИИ ради читаемости на скорости.
  - `+` Документация оптимизации уровней как подарок моддерам.
  - `−` Чекпоинт-копии как источник статтера.
- **Влияние:** оптимизация — дизайн уровней как перфоманс (комнаты, двери, точки невозврата); графика — читаемость важнее деталей.
- **DSS:** `baked_occlusion_culling`, `async_loading_pipeline`, `particle_pooling`, `agent_update_budget`, `post_effect_selective`.
- **Источники:** Custom Levels Wiki (https://ultrakillcustoms.miraheze.org/wiki/Optimizing_Your_Level), 80lv интервью (https://80.lv/articles/ultrakill-devs-on-the-game-s-mechanics-npc-ai-and-early-access-experience), itch devlog (https://hakita.itch.io/ultrakill-prelude/devlog/122580/v104-migrating-saves-and-steam-page), itch (https://hakita.itch.io/ultrakill-prelude), dev commentary (https://www.youtube.com/watch?v=mnwtr07q9eE).

---
## Партия 6 (PDF-интеграция: финальный источник)

Интегрирован отчёт `docs/sources/Технический_разбор_прорывных_игр.pdf`
(SHA256 `C80C5C76…0E9D`, 299 КБ; оригинал вне репо не тронут).
Сверка с партиями 1–5: **противоречий нет** — числа PDF (BSP/front-to-back,
128 visplanes, SH 9 коэффициентов, ~500 PSO, DDGI-лаг ~20 кадров, снапшоты
CS2 64 Гц, пакеты WoW 380→2.2M, `stream.ini` 13.5 МБ, NPT чанки 64 КБ)
совпали с карточками. PDF дал точные формулировки — внесены микроправками
в карточки №№ 2, 7, 8, 13, 15, 35. Новые игры из PDF, которых не было
в списке: Alan Wake 2 и Horizon Zero Dawn (Decima) — разобраны ниже.
Crysis и Starfield упомянуты в PDF вскользь (форумные источники / пара
со S.T.A.L.K.E.R. 2) — отдельных карточек не требуют: Starfield зафиксирован
строкой в №35. Слабые источники PDF (reddit/NeoGAF) в работу не брались —
для новых карточек взяты первоисточники (DF, Guerrilla, GDC).

### 51. Alan Wake 2 (2023, Remedy)

- **Движок:** Northlight. Новая ECS-модель (эффективное параллельное исполнение, переменное число ядер CPU) + mesh shaders: окклюзия до пиксельной точности, каллится всё вплоть до мешлетов, рисуется только видимое — ценой обязательной поддержки DX12 Ultimate.
- **Релиз ПК — водораздел по GPU:** GTX 1080 Ti (без mesh shaders) медленнее RTX 2080 в 6.3 раза в тех же сценах (1080p, апскейл с 720p — падения до teens); RX 5700 XT тоже позади 2080. При этом урезанные Turing (GTX 1660/Super/Ti) mesh shaders умеют — тянут PS5-quality в 1080p через FSR2 Quality выше 30 fps; RX 6600 за <$200 даёт PS5-качество в своём 1080p-классе. SSD де-факто обязателен, 16 ГБ RAM, минимум CPU уровня Ryzen 5600 / i5-12400F.
- **Path tracing:** прямой свет (RT-тени всех источников), непрямой specular (high — 3 отскока, low/medium — ~1 + половинное разрешение отражений), диффуз (тонкий: смешан с базовым GI, наследует его ошибки — в отличие от CP77, где PT трансформирует всё), прозрачность (low нестабилен в движении). Денойз: high режет fps вдвое против Ray Reconstruction/low; RR чище в движении и на смене света, но пересвечивает нормали (убивает подповерхностное рассеяние на лицах), даёт шлейфы и постеризацию на низких DLSS-пресетах.
- **Цифры DF:** RTX 3080 на PS5-настройках — почти 2× от PS5, но +PT роняет до ~30 fps (только RT direct + low-денойз ≈ 60); RTX 4070 на 14% медленнее 3080 в растре, но на 26% быстрее в полном PT; +Frame Generation в тяжёлой сцене: 41 → 80 fps. Ложка: статтер мыши на частотах, не кратных 30 (привет Deathloop).
- **Причина репутации:** реализация (первый обязательный mesh-shader AAA + честный PT) + функционал (хоррор-детектив, фоторежим как инструмент). Паника от сис.требований (3070 для 1080p/60 через DLSS с 540p) оказалась перестраховкой.
- **Решения:**
  - `+` Mesh shaders как ставка: плотность геометрии вместо полигонального голода.
  - `+` PT поверх годного software-GI (Lumen-подобный фолбэк): красиво и без RT.
  - `+` Зернистые RT-настройки (отскоки/разрешение/денойз отдельно).
  - `−` Отсечение GTX 10/RDNA1 без апелляции.
  - `−` RR первого поколения: лица и шлейфы.
- **Влияние:** графика — mesh shader как новый минимальный порог (урок для `requires_features`); оптимизация — PT-настройки поштучно; процесс — бенчмарк ожиданий через DF-разборы до покупки.
- **DSS:** `hardware_raytraced_gi`, `temporal_upscaling`, `ml_frame_generation`, `hierarchical_lod`, `gpu_compute_culling`, `pso_precaching_warmup`.
- **Источники:** DF Optimised Settings (https://www.digitalfoundry.net/articles/digitalfoundry-2023-alan-wake-2-optimised-settings-for-pc), DF RT Deep Dive (https://www.digitalfoundry.net/articles/digitalfoundry-2023-alan-wake-2-rt-deep-dive), DF Path Tracing video (https://www.youtube.com/watch?v=tXfwvohROPA), Wccftech Northlight ECS/mesh shaders (https://wccftech.com/alan-wake-2-northlight-engine-evolution-detailed-by-remedy/), DF Weekly mesh-shader reckoning (https://www.digitalfoundry.net/articles/digitalfoundry-2023-df-weekly-alan-wake-2-delivers-a-day-of-reckoning-for-older-pc-gpu-owners), PDF-интеграция.

### 52. Horizon Zero Dawn (2017, Guerrilla / Decima)

- **Движок:** Decima. Переход от линейных Killzone к открытому миру: размер, мелкие куски контента, видимость до горизонта, переменная плотность (поселения, котлы), непрерывный стриминг, запас под случайные столкновения с машинами.
- **Ключевое решение — отказ от предвычисления:** KZ4-мидлварь видимости требовала бейкинга — художники ждали фоновой сборки, прежде чем увидеть правки. Для Horizon выбросили: свобода итераций важнее runtime-цены запроса.
- **StaticScene (видимость через async compute PS4):** мир — иммутабельные static tiles от стриминга; деревья MeshResource ужаты до двух LOD (parent/child, пустые уровни для единообразия); сортировка по Morton + фильтры, кластеры от 4K инстансов (баланс нагрузки); CPU-задача идёт параллельно с динамическим запросом, на видимый кластер — один compute-диспетч; uber-шейдер ~1500 инструкций, общий выходной буфер через атомарный счётчик, батчинг по DrawableSetup прямо на GPU.
- **Процедуры:** GPU-based runtime placement (доклад GDC): граф-правила художников → алгоритмы на GPU собирают мир на ходу — деревья, дороги, звуки, эффекты, живность, геймплейные точки. Покрасил линию деревьев — получил лес.
- **Релиз ПК (2020) — позже и спокойно** (порт не входит в фокус PDF, карточка — про архитектуру): тот же движок уже тянул Death Stranding. Урок связки: движок, переживший смену жанра (FPS→open world), переживёт и платформу.
- **Причина репутации:** реализация (видимость без бейкинга + процедуры) + функционал (охота на машины, экосистема).
- **Решения:**
  - `+` Ноль предвычисления видимости: итерации без ожидания бейка.
  - `+` Async compute под запросы: видимость не ест графическую очередь.
  - `+` Правила вместо расстановки: плотность мира правится кистью.
  - `−` Свой формат данных (parent/child, кластеры) — контент, не влезший в схему, уехал в динамическую систему и доделывался художниками вручную.
- **Влияние:** оптимизация — видимость как compute-задача, а не CPU-граф; процесс — workflow большой команды важнее potency предвычисления; движки — один движок на два жанра (Horizon, Death Stranding).
- **DSS:** `gpu_compute_culling`, `hiz_software_occlusion`, `hierarchical_lod`, `gpu_procedural_placement`, `world_partition_streaming`, `async_loading_pipeline`.
- **Источники:** Guerrilla «Decima Engine: Visibility» (https://www.guerrilla-games.com/read/decima-engine-visibility-in-horizon-zero-dawn), GCAP-слайды (https://www.guerrilla-games.com/media/News/Files/GCAP2017_DecimaVisibility.pdf), GDC Vault Procedural Placement (https://www.gdcvault.com/play/1024700/GPU-Based-Run-Time-Procedural), слайды (https://www.slideshare.net/slideshow/decima-engine-visibility-in-horizon-zero-dawn/82371923), PDF-интеграция.

---
*Все 6 партий завершены: 52 карточки. Материалов достаточно — дальше только правки, калибровка и шлифовка.*

---

## Дополнение (PDF v2: полный отчёт, SHA256 `75E7AB23…F382363`, 517 КБ)

Дописаны разделы 3 (процедуры), 7 (калибровочная матрица −3..+3) и 8 (паттерны),
углублены: SM64/TMEM, AC Unity, Genshin NPR, Ultrakill PS1-пайплайн, GTA V,
RDR1 SPU, RDR2 клипмэппинг, Arkham Knight, ME3-шлюзы, NFS-сплайны, Minecraft
Java/Bedrock, TES Verlet-lock, HoI4 детерминизм, SE5 X-Ray, DD2, Jedi Survivor,
Fall Guys, OW тики, Hollow Knight GC, Hades атласы, Elden Fossilize.
Ниже — только новое: карточка №53 (Dragon's Dogma 2 — отсутствовала в разборах)
и точечные строки в существующие карточки. Jedi Survivor и Arkham Knight
карточек не получили (по одному источнику на игру — ниже порога; факты ушли
в `wild66.json` к их строкам).

### 53. Dragon's Dogma 2 (2024, Capcom / RE Engine)

- **Движок:** RE Engine (линейное наследие Resident Evil). Каждый горожанин
  и пешка (Pawn) в радиусе города симулируются полностью: логика, физика
  тканей и волос, NavMesh, зрение — без разделения на потоки и без динамического
  масштабирования; цикл замыкается на одном мастер-потоке CPU.
- **Релиз ПК — CPU-стена:** в столице Вернворт 25–35 fps даже на i9-14900K
  и Ryzen 7 7800X3D вне зависимости от видеокарты и разрешения; RTX 4090
  простаивает с загрузкой 40–50%. Официальные требования (GTX 1070 / RTX 2080,
  i5-10600 / i7-10700) описывают видеокарту, но молчат про процессор.
- **Патчи:** спустя полгода — ручной ползунок плотности населения (Character
  Population Density) и частичный вынос ИИ в асинхронные пулы. Архитектура
  не переписана — техдолг остался.
- **Причина репутации:** реализация (симуляция без бюджета) + процесс
  (Capcom честно объяснила причину, но чинила полгода).
- **Решения:**
  - `+` Живой город как правда, а не декорация: у каждого NPC полный цикл.
  - `−` Нет actor LOD / бюджета обновлений: дальние едят столько же, сколько ближние.
  - `−` Мастер-поток: 8+ ядер не спасают, спасает только частота.
  - `±` Ползунок плотности постфактум: честно, но это костыль вместо архитектуры.
- **Влияние:** оптимизация — школьный пример для DSS `agent_update_budget`
  (пример №205 в базе); менеджмент — CPU-бюджет толпы закладывается
  в предпродакшне, а не патчем.
- **DSS:** `agent_update_budget`, `ecs_data_oriented_crowd`,
  `crowd_instancing_impostors`, `multithreaded_physics_jobs`,
  `time_sliced_pathfinding`, `dynamic_resolution_scaling`.
- **Источники:** GamersNexus CPU/GPU-бенчмарки и боттлнеки
  (https://gamersnexus.net/game-benchmarks-graphics-guides/dragons-dogma-2-mess-gpu-cpu-benchmarks-bottlenecks-crashes),
  PC Gamer перф-анализ
  (https://www.pcgamer.com/games/rpg/dragons-dogma-2-performance-analysis/),
  DSOG бенчмарки
  (https://www.dsogaming.com/pc-performance-analyses/dragons-dogma-2-benchmarks-pc-performance-analysis/),
  IGN про CPU-зависимость
  (https://www.ign.com/articles/dragons-dogma-2-pc-performance-is-a-mess-but-it-didnt-have-to-be),
  PDF-интеграция v2 (раздел 4).

---

## Партия 7 (кооп/мультиплеер, список 3 — первая дюжина)

### 54. BattleBit Remastered (2023, SgtOkiWeird / Unity)

- **Движок:** Unity. Low-poly/воксельный стиль + 2 ГБ установка: запуск на GTS 450 / i5-2310 (мин), GTX 600 / i5-4xxx (рек), 6–8 ГБ RAM. Серверы до 254 игроков, режимы 254/128/64/32, разрушаемость, техника, proximity voice, EasyAntiCheat + Epic Online Services.
- **Релиз (EA 15.06.2023):** взрыв (~87K онлайна) → просел бэкенд: патч 1.7.2 (backend/CPU/client-оптимизации), хотфикс 1.51 (packet loss и хитрег), 1.5 (DDoS-файрволл), 2.0 (Community Server API).
- **Причина репутации:** реализация (масштаб малой ценой) + процесс (патчи сети по живому).
- **Решения:**
  - `+` Масштаб за счёт арта, а не железа: 254 игрока на GTS 450.
  - `+` Community Server API: контент без роста клиента.
  - `−` Бэкенд — бутылочное горлышко (сбросы прогресса, очереди).
  - `−` Деструкция × 254 игрока: пики CPU/сети, хитрег правится костылями.
- **Влияние:** сеть — stat-sync и очереди как отдельный бюджет; арт — low-poly как перфоманс-стратегия.
- **DSS:** `network_relevancy_priority`, `tickrate_budgeting`, `headless_dedicated_server`, `art_direction_stylization`, `delta_compression_state`.
- **Источники:** Steam (https://store.steampowered.com/app/671860/BattleBit_Remastered/), патчноуты (https://battlebit.wiki.gg/wiki/Patch_Notes), Unity-движок (https://joinbattlebit.com/upcoming-operation-overhaul-playtest/).

### 55. Squad (2020, Offworld / Unreal)

- **Движок:** UE4 на старте → UE5.5 (патч 9.0, 2025): Nanite, Chaos, Metasounds; DX11 отброшен, нужен Shader Model 6. Карты до 4×4 км, 100 игроков 50v50, VoIP, стройбат, SDK/моды.
- **Релиз/эволюция:** CPU-bound с рождения (single-thread, тени/листва); миграция на UE5 усугубила на старом железе (скоп-прицелы в ноль, негативные ревью), лечится сбросом кэша. Актуальные требования Steam: мин 1060/i5-8400/8 ГБ, рек 3060/i5-12400/16 ГБ.
- **Причина репутации:** функционал (combined arms без скриптов) + реализация (Offworld Core, моддинг).
- **Решения:**
  - `+` Системный геймплей вместо скриптов: реиграбельность бесплатно.
  - `+` SDK/моды продлили жизнь (фракции из модов).
  - `−` 100 игроков + техника + PiP = просадки; низкие пресеты чище для видимости.
  - `−` Мажорные миграции ломают моды/кэш (UE5, storage format).
- **Влияние:** сеть — тик vs масштаб; процесс — миграции планировать с запасом на моды.
- **DSS:** `network_relevancy_priority`, `tickrate_budgeting`, `headless_dedicated_server`, `agent_update_budget`, `time_sliced_pathfinding`.
- **Источники:** Steam (https://store.steampowered.com/app/393380/Squad/), 100-player battles (https://www.joinsquad.com/game-features/100-player-battles), 9.0 notes (https://www.joinsquad.com/updates/squad-9-0-release-notes).

### 56. Payday 2 (2013, Overkill / Diesel)

- **Движок:** Diesel 2.0 → Diesel 3.0 (Update 247, 2026): 64-bit, DX11, компрессия установки 86→32 ГБ. Кооп 4 (+NPC), CRIMENET-хабы, Workshop.
- **Релиз/эволюция:** 13 лет на 32-bit/DX9: OOM-крэши с модами, sober-перфоманс на MT-железе. Diesel 3.0 — глубокая модернизация без смены контента ценой полного ре-даунлоада и поломки модов/Linux-ветки.
- **Причина репутации:** процесс (поддержка 13 лет) + реализация (поздняя модернизация).
- **Решения:**
  - `+` 64-bit + DX11 + перепаковка: продление жизни без нового контента.
  - `+` Мелкие хабы переиспользуют AI/лут.
  - `−` 13 лет техдолга: OOM, DX9, MT не используется.
  - `−` Каждый мажор ломает моды, сейвы, платформы.
- **Влияние:** менеджмент — модернизации закладывать окном совместимости; контент — хабы дешевле миров.
- **DSS:** `differential_patch_pipeline`, `build_size_startup_budgets`, `async_loading_pipeline`, `tickrate_budgeting`.
- **Источники:** Steam (https://store.steampowered.com/app/218620/PAYDAY_2), Update 247 (https://www.paydaythegame.com/news/payday2/2026/08/payday-2-update-247-changelog), требования (https://support.starbreeze.com/hc/en-us/articles/38124173572113-PAYDAY-2-PC-System-Requirements).

### 57. Dead by Daylight (2016, Behaviour / Unreal)

- **Движок:** UE4 → UE5 (патч 7.7.0, 2024) намеренно без смены картинки: только фундамент + компрессия (−18 ГБ). Асимметрия 4v1, процедурные пиллары карт. Сеть: killer-hosted P2P в прошлом, выделенные серверы с ~2020.
- **Релиз/эволюция:** P2P-телепорты и хитрег («100-foot machetes»); CPU-bound тики, A-pose регрессии каждый чаптер. Живой сервис: Tome, баланс перков, ремастер ассетов под 4K/60.
- **Причина репутации:** функционал (асимметрия + реиграбельность малой картой) + процесс (консервативные миграции).
- **Решения:**
  - `+` Процедурная раскладка целей: реиграбельность без стриминга open world.
  - `+` Миграции без смены картинки сохраняют low-spec аудиторию.
  - `−` P2P-наследие: хитрег зависит от хоста.
  - `−` Контент-зоопарк (30+ киллеров) усложняет баланс и QA.
- **Влияние:** сеть — топология как часть дизайна; процесс — миграция без визуала как стратегия.
- **DSS:** `deterministic_lockstep`, `client_prediction_reconciliation`, `tickrate_budgeting`, `headless_dedicated_server`.
- **Источники:** Steam (https://store.steampowered.com/app/381210/Dead_by_Daylight), 7.7.0 (https://forums.bhvr.com/dead-by-daylight/kb/articles/445-7-7-0-mid-chapter), дизайн асимметрии (https://www.gamedeveloper.com/design/crafting-an-asymmetric-multiplayer-horror-experience-in-i-dead-by-daylight-i-).

### 58. Ready or Not (2023, VOID / Unreal)

- **Движок:** UE 4.27 → UE5.3 (Vol.74, 2024): PSO-precaching, DLSS 3.7, FSR3, TSR. PhysX, FMOD, Epic Online Services. Кооп 5, CQB-уровни, behavior trees AI.
- **Релиз 1.0:** статтеры и просадки даже на 3060/3080 одинаково на low/high и DX11/DX12; EA шёл плавнее. Требования скромные: мин 960/i5-4430/8 ГБ, рек 1060/R5-1600.
- **Причина репутации:** функционал (тактика + ROE-скоринг) против реализации (шейдер-статтер).
- **Решения:**
  - `+` Переход на UE5.3 ради PSO-precaching и апскейлеров вместо вечных патчей.
  - `+` Behavior trees + perception для AI.
  - `−` Тяжёлый CQB-стриминг без агрессивного PSO-вармапа: CPU/GPU 30–40% и статтер.
  - `−` P2P/EOS-лобби без добора ботов: масштабирование только модами.
- **Влияние:** оптимизация — PSO warmup обязателен в DX12; процесс — UE5-миграция ломает мод-инструменты (bounty).
- **DSS:** `pso_precaching_warmup`, `temporal_upscaling`, `agent_update_budget`, `time_sliced_pathfinding`.
- **Источники:** Steam (https://store.steampowered.com/app/1144200/Ready_Or_Not/), Vol.74 (https://voidinteractive.net/ready-or-not-vol-74-development-briefing/), PCGW (https://www.pcgamingwiki.com/wiki/Ready_or_Not).

### 59. Arma 3 (2013, Bohemia / Real Virtuality 4)

- **Движок:** RV4: DX11, PhysX, звук со скоростью звука. Altis 270 км², редактор Eden, моды (DayZ вырос отсюда). Официально лимита игроков нет, типовые сценарии 2–64 (пример 60v60).
- **Релиз/эволюция:** крайне CPU-bound: 90–95% работы на одном потоке, 20–30 fps на сильном железе; лечится только IPC/частотой и урезанием Objects/Terrain/Visibility (тени Standard = на GPU, Low = на CPU). Патчи до 2.22 (2026).
- **Причина репутации:** реализация (симуляция) + экосистема (моды/серверы).
- **Решения:**
  - `+` Стриминг огромного террейна + техника + ragdoll в одном кадре.
  - `+` Dedicated server Win/Linux + Eden: Wasteland/Domination/Antistasi.
  - `−` Главный поток + DX11-драйверный оверхед: GPU-апгрейд не лечит.
  - `−` View-distance линейно грузит CPU; MP-фрейм зависит от сервера/AI.
- **Влияние:** оптимизация — настройки маппить на подсистемы (тени→GPU, дистанция→CPU); сеть — сервер как часть перфоманса.
- **DSS:** `multithreaded_physics_jobs`, `agent_update_budget`, `time_sliced_pathfinding`, `hierarchical_lod`, `network_relevancy_priority`.
- **Источники:** требования (https://arma3.com/requirements), движок (https://arma3.com/features/engine), мультиплеер (https://arma3.com/features/multiplayer), перфоманс-гайд (https://community.bistudio.com/wiki/Arma_3:_Performance_Optimisation).

### 60. HELLDIVERS 1 (2015, Arrowhead / Bitsquid)

- **Движок:** Bitsquid (куплен Autodesk 2014 → Stingray, закрыт 2018). Top-down twin-stick, процедурные миссии, кооп 4 локально+онлайн с drop-in/drop-out, friendly fire.
- **Релиз ПК (2015):** на удивление чисто: стабильно даже на AMD A6+iGPU; баги — backend/firewall, не fps. Требования: мин 512 МБ/9800, рек 1 ГБ/GTX 460, 4 ГБ RAM.
- **Причина репутации:** реализация (лёгкий движок) + функционал (кооп-формула).
- **Решения:**
  - `+` Нишевый лёгкий движок: низкие требования, shared-screen без серверов.
  - `+` Процедурность + friendly fire: реиграбельность малыми средствами.
  - `−` Ставка на Bitsquid заложила техдолг серии (виден по Helldivers 2).
  - `−` Общая камера без зума: читаемость в коопе страдает.
- **Влияние:** движки — удобство команды vs долг поддержки; дизайн — камера как перфоманс.
- **DSS:** `art_direction_stylization`, `particle_pooling`, `tickrate_budgeting`.
- **Источники:** Steam (https://store.steampowered.com/app/394510/HELLDIVERS_Dive_Harder_Edition/), кооп (https://www.co-optimus.com/game/4041/pc/helldivers.html), порт-репорт (https://www.destructoid.com/pc-port-report-helldivers/).

### 61. Phasmophobia (2020, Kinetic / Unity)

- **Движок:** Unity (2022 ветка; план Unity 6: PCVR Foveated, DX12, Forward+, новый бейк света). Voice recognition, OpenXR, Steam Audio, Vivox, Burst/IL2CPP. Кооп 4, хаб-локации, baked light. Мин specs — для VR.
- **Релиз (EA):** виральный хит с джанком: краши/фризы, UnityPlayer.dll, Citrix-конфликты. Лечится драйверами/верификацией файлов. Патчи: Ascension, Eventide, Crimson Eye (консоли + кроссплей + Upgraded Physics), QOL-пакеты.
- **Причина репутации:** функционал (голос как геймплей) + процесс (соло-инди live-service).
- **Решения:**
  - `+` Middleware-набор (Photon/Vivox/OpenXR/Steam Audio): кроссплей без AAA-бюджета.
  - `+` Маленькие хабы + baked: хоррор на звуке/свете, а не полигонах.
  - `−` Физика дверей/игроков тикала на low-fps клиентах (провалы сквозь пол) — только оверхол v0.11.
  - `−` Каждый мейджор ломает баланс/UX.
- **Влияние:** аудио — голос как механика; физика — тик vs клиентский fps.
- **DSS:** `physics_lod_sleeping`, `fixed_timestep_physics`, `lightmap_atlas_baking`, `tickrate_budgeting`.
- **Источники:** Steam (https://store.steampowered.com/app/739630/Phasmophobia), Kinetic (https://www.kineticgames.co.uk/phasmophobia), Unity-кейс (https://unity.com/blog/thrilling-indie-horror-games-halloween), PCGW (https://www.pcgamingwiki.com/wiki/Phasmophobia).

### 62. Raft (2022, Redbeet / Unity 2018)

- **Движок:** Unity 2018.3.5f1, DX11, FMOD. Бесконечный океан + острова-хабы, кооп, сейвы World/*.rgd + Steam Cloud. Требования: мин GTX 700/i5/6 ГБ, рек GTX 1050.
- **Релиз (1.0 после EA 2018):** спокойно; техдолг — старый движок без современных апскейлеров и мультитред-улучшений; кооп-сеть без заявленного тика.
- **Причина репутации:** функционал (выживание на плоту) + доступность.
- **Решения:**
  - `+` Низкий порог (DX11 без RT): покрытие слабых ПК.
  - `+` Детерминированные сейвы мир/игрок + Cloud.
  - `−` Unity 2018: нет апскейлеров, старый мультитред.
  - `−` Сеть непредсказуема на больших плотах.
- **Влияние:** контент — острова-хабы вместо бесшовности; сейвы — детерминизм.
- **DSS:** `world_partition_streaming`, `gerstner_fft_water`, `physics_lod_sleeping`, `tickrate_budgeting`.
- **Источники:** Steam (https://store.steampowered.com/app/648800/Raft/), PCGW (https://www.pcgamingwiki.com/wiki/Raft).

### 63. Golf With Your Friends (2020, Blacklight / Unity 2021)

- **Движок:** Unity 2021.3.28f1, с 2020 только D3D11+64-bit. Симультанный гольф до 12 игроков (local+online), uncapped FPS, MSAA, FOV, редактор + Workshop, Rewired/Opus. Требования: мин GTX 460/i3/2 ГБ, рек GTX 960/4 ГБ.
- **Релиз:** спокойно; техболь — зависание меню MS Store-версии, рассинхроны физики на 12 игроках, хрупкий сингл-файл сейвов.
- **Причина репутации:** функционал (пати-спорт + редактор) + доступность.
- **Решения:**
  - `+` Симультанная физика мячей + UGC: дёшево по CPU, реиграбельно.
  - `+` Uncapped FPS + MSAA из коробки.
  - `−` Физика на P2P-подобной сети: рассинхроны, тик не заявлен.
  - `−` Сейв одним файлом: повреждения статистики.
- **Влияние:** сеть — симультанность vs детерминизм; сейвы — изоляция файлов.
- **DSS:** `deterministic_lockstep`, `physics_lod_sleeping`, `tickrate_budgeting`, `fixed_timestep_physics`.
- **Источники:** Steam (https://store.steampowered.com/app/431240/Golf_With_Your_Friends/), PCGW (https://www.pcgamingwiki.com/wiki/Golf_With_Your_Friends), Team17 (https://www.team17.com/games/golf-with-your-friends/).

### 64. Among Us (2018, Innersloth / Unity)

- **Движок:** Unity (билды 2019→2020→2022), D3D11 (+force-d3d12), 32-bit exe, Vsync cap 60. До 15 игроков (online/local WiFi), EOS, кроссплей, Rewired. Требования: HD 4600/GTX 650, i3-4330, 1–4 ГБ.
- **Релиз/взрыв 2020:** тихо → вирально. Техболь: статтеры при polling rate мыши >1000 Гц, 4K показывает четверть экрана без DPI-фикса, чужие движения capped 30.
- **Причина репутации:** функционал (социальная дедукция) + доступность (идёт везде).
- **Решения:**
  - `+` Векторное 2D + мизерные требования: идеал для теста netcode.
  - `+` EOS + room-code + local WiFi: дешёвый authoritative-лайт.
  - `−` 30fps-репликация + polling-зависимость: плохой input-путь.
  - `−` Тики/античит не заявлены: читаемость сети низкая.
- **Влияние:** сеть — тик как контракт с игроком; ввод — polling rate как перфоманс.
- **DSS:** `tickrate_budgeting`, `deterministic_lockstep`, `art_direction_stylization`.
- **Источники:** Steam (https://store.steampowered.com/app/945360/Among_Us/), Innersloth (https://innersloth.com/gameAmongUs.php), PCGW (https://www.pcgamingwiki.com/wiki/Among_Us).

### 65. Totally Accurate Battle Simulator (2021, Landfall / Unity 2018)

- **Движок:** Unity 2018.4.13f1, D3D11, FXAA/SMAA, без капа FPS. Wobbly ragdoll-физика сотен тел, Workshop (юниты/карты/фракции), online PvP. Требования: мин GTX 660/i5/8 ГБ, рек GTX 970/i7/8 ГБ.
- **Релиз (EA 2019 → 1.0):** спокойно; техболь — CPU-bound толпы, нестабильность при сотнях тел, звуковые регрессии, 10 МБ Cloud-лимит.
- **Причина репутации:** функционал (физика как геймплей) + UGC.
- **Решения:**
  - `+` Wobbly-физика масштабируется числом юнитов, деградирует весело.
  - `+` In-game Workshop без пересборки билда.
  - `−` CPU-bound толпы на Unity 2018: threading-модель не заявлена.
  - `−` Звук и Cloud-лимит хрупки для песочницы.
- **Влияние:** физика — деградация как фича; UGC — редактор как контент.
- **DSS:** `physics_lod_sleeping`, `agent_update_budget`, `crowd_instancing_impostors`, `particle_pooling`.
- **Источники:** Steam (https://store.steampowered.com/app/508440/Totally_Accurate_Battle_Simulator/), PCGW (https://www.pcgamingwiki.com/wiki/Totally_Accurate_Battle_Simulator).

---

## Партия 8 (список-3, батч 2: №66–73)

### 66. Garry's Mod (2006, Facepunch / Source)

- **Движок:** Source (ветка 2006 / Episode One на старте, позже актуальные Source-ветки); BSP + visleaf, VPhysics для пропов/констрейнтов/ragdoll, сетевой код Source с выделенным сервером, скриптинг GLua.
- **Релиз ПК:** Вышел 29.11.2006 как платная песочница без целей; требования низкие (DX9, ~2 ГГц / 1–4 ГБ ОЗУ). Базовая игра стабильна, но для контента требуются ассеты HL2/CSS/TF2 — иначе ERROR-модели; перегруз энтити/физикой и плохой Lua ведут к просадкам и крашам.
- **Версии/патчи:** Долгая live-поддержка; интеграция Steam Workshop, SteamPipe, порты Mac/Linux, позже 64-битная ветка x86-64; сервер — SteamCMD app 4020 + srcds.
- **Причина репутации:** функционал (песочница + Lua + Workshop как бесконечный UGC).
- **Решения:**
  - `+` GLua с разделением server/client/shared: моды без SDK.
  - `+` Headless dedicated server + монтирование контента Source-игр: дешёвые RP/TTТ-сообщества.
  - `−` Лимиты энтити/физики Source и CPU-упор: спам пропами роняет fps/сервер.
  - `±` Зависимость от чужих ассетов: лёгкий клиент ценой «missing content» у новичков.
- **Влияние:** сеть — эталон долгоживущего Lua-UGC и комьюнити-серверов; оптимизация — урок entity/physics-бюджетов в песочницах.
- **DSS:** `headless_dedicated_server`, `fixed_timestep_physics`, `client_prediction_reconciliation`, `broadphase_spatial_partitioning`, `network_relevancy_priority`.
- **Источники:** Steam (https://store.steampowered.com/app/4000/Garrys_Mod/), Valve Dev (https://developer.valvesoftware.com/wiki/Garry%27s_Mod), Facepunch (https://wiki.facepunch.com/gmod/).

### 67. Call of Duty 4: Modern Warfare (2007, Infinity Ward / IW Engine)

- **Движок:** IW 3.0 (развитие id Tech 3 → IW 2.0); цель 60 fps, динамическое освещение/HDR, depth of field, bullet penetration, выделенные серверы на ПК.
- **Релиз ПК:** На фоне Crysis хвалили за оптимизацию: шёл на GeForce 6600 / Radeon 9800 Pro, 1 ГБ ОЗУ при высоком fps. Жалобы ПК — PunkBuster/читтеры и Steam-патч 1.8, а не рендер.
- **Версии/патчи:** Патчи 1.1–1.7 + Steam 1.8; комьюнити-ветка CoD4x (фиксы сервер-браузера/эксплойтов); Remastered 2016 — отдельная ветка.
- **Причина репутации:** реализация (60 fps + выделенные серверы + перки/create-a-class как стандарт мультиплеера).
- **Решения:**
  - `+` Жёсткий бюджет 60 fps и скейл под слабое железо: широкая база игроков.
  - `+` Headless dedicated server + server browser: низкий пинг, моды/промоды.
  - `+` Пробитие по типу/толщине материала: тактическая глубина без разрушений.
  - `±` Линейная кампания со скриптами: стабильный fps ценой интерактивности.
- **Влияние:** сеть — возврат dedicated servers как нормы; графика — 60 fps важнее brute-force картинки.
- **DSS:** `headless_dedicated_server`, `client_prediction_reconciliation`, `tickrate_budgeting`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/7940/Call_of_Duty_4_Modern_Warfare/), PCGW IW Engine (https://www.pcgamingwiki.com/wiki/Engine:IW_engine).

### 68. Sid Meier's Civilization V (2010, Firaxis / собственный)

- **Движок:** Собственный движок Firaxis (детали pipeline — unstated); гекс-сетка, One Unit Per Tile, два рендер-пути DX9 / DX11, Steamworks + Workshop.
- **Релиз ПК:** Релиз 21.09.2010; на старте — долгие ходы и просадки в лейтгейме на больших картах (ИИ/патфайнд), нестабильность DX11 + AA/оконного режима, десинки в MP. Графически нетребовательна, CPU-bound по ходу игры.
- **Версии/патчи:** Gods & Kings (2012) и Brave New World (2013) — религия/шпионаж/торговля/баланс; осенний патч BNW 2013; порты Aspyr Mac/Linux; позже 2K Launcher и legacy-beta.
- **Причина репутации:** функционал (гексы + 1UPT подняли стоимость ИИ/патфайнда и время хода).
- **Решения:**
  - `+` Гексы + 1UPT + Strategic View: читаемая тактика вместо doomstacks.
  - `+` Два клиента DX9/DX11: запуск на слабом железе ценой ветвления багов.
  - `−` AI/pathfinding без жёсткого time-slicing на старте: залипание лейтгейма.
  - `±` Simultaneous turns в MP: проще с сетью, но десинки/реконнекты.
- **Влияние:** оптимизация — кейс time-sliced ИИ и agent-бюджетов в 4X; сеть — урок deterministic-синхронизации пошаговых игр.
- **DSS:** `async_loading_pipeline`, `time_sliced_pathfinding`, `agent_update_budget`, `deterministic_lockstep`.
- **Источники:** Steam (https://store.steampowered.com/app/8930/Sid_Meiers_Civilization_V/), SteamDB патчноуты (https://steamdb.info/app/8930/patchnotes/).

### 69. Call of Duty: World at War (2008, Treyarch / IW Engine)

- **Движок:** Улучшенный IW 3.0 от CoD4 (Treyarch-ветка); динамическое освещение, HDR, динамические тени, depth of field, разрушаемость авто/построек, кооп + Nazi Zombies.
- **Релиз ПК:** Наследование оптимизации CoD4: минимум P4 3 ГГц / 6600/X1600, 512 МБ–1 ГБ ОЗУ, DX9.0c; хорошая масштабируемость. Критика — ИИ/сеттинг, на консолях просадки PS3 vs 360 (Digital Foundry); на ПК — PunkBuster и патчи.
- **Версии/патчи:** Патчи до v1.7 (фиксы войс-чата/крашей); 3 Map Pack'а, Mod Tools; позже комьюнити-серверы.
- **Причина репутации:** реализация (перенос проверенного IW 3.0 на WWII + кооп/Zombies без смены техбазы).
- **Решения:**
  - `+` Реюз IW 3.0: предсказуемые 60 fps и низкие требования.
  - `+` Кооп кампании + Zombies: рост retention без нового рендера.
  - `+` Ragdoll/деструкция/огонь: «грязная» война малыми средствами.
  - `−` PS3-ветка слабее 360 при том же движке: урок платформенной оптимизации.
- **Влияние:** графика — HDR/свет CoD4 достаточны для WWII; сеть — закрепление dedicated servers + коопа.
- **DSS:** `headless_dedicated_server`, `client_prediction_reconciliation`, `particle_pooling`, `quality_tier_scalability`, `agent_update_budget`.
- **Источники:** Steam (https://store.steampowered.com/app/10090/Call_of_Duty_World_at_War/), TechSpot (https://www.techspot.com/article/128-call-of-duty-5-gpu-performance/).

### 70. The Witcher 2: Assassins of Kings Enhanced Edition (2012, CDPR / REDengine)

- **Движок:** REDengine (первая игра на нём); DX9, Ubersampling (SSAA — рендер кратно выше нативного), TextureMemoryBudget (дефолт 600 МБ), динамические тени.
- **Релиз ПК:** Оригинал 05.2011 крайне требователен: Ubersampling резал fps вдвое даже на топ-GPU, статтеры/поп-ин; стартовая SecuROM-DRM и ложные срабатывания антивирусов.
- **Версии/патчи:** 1.1 убрал SecuROM + перф/инверсия мыши; 1.2–1.35 хотфиксы; 2.0 — Арена/туториал; 3.0 EE — квесты/локации/ролики; 3.1–3.4 — фиксы.
- **Причина репутации:** реализация (Ubersampling как brute-force AA без масштабируемого апскейла).
- **Решения:**
  - `+` Ubersampling: эталонная картинка ценой GPU.
  - `+` Ручной TextureMemoryBudget до ~2048: снимал спайки на картах с большой VRAM.
  - `−` Ubersampling=2 по дефолту у части юзеров: «неиграбельно из коробки».
  - `±` Снятие DRM и конфиг-твики user.ini: перф починили процессом, а не рендером.
- **Влияние:** графика — антипример «ультра-настройки ради настройки»; оптимизация — урок quality tiers и VRAM-бюджетов.
- **DSS:** `quality_tier_scalability`, `post_effect_selective`, `hierarchical_lod`, `virtual_texturing`.
- **Источники:** Steam (https://store.steampowered.com/app/20920/The_Witcher_2_Assassins_of_Kings_Enhanced_Edition/), DSOG (https://www.dsogaming.com/news/the-witcher-2-patch-1-35-hotfix-released/).

### 71. Batman: Arkham Asylum GOTY (2009, Rocksteady / Unreal Engine 3)

- **Движок:** Unreal Engine 3; лайтмапы, GPU PhysX (туман/ткань/мусор/бумаги — патч 1.1), SecuROM + GFWL на старте.
- **Релиз ПК:** 15.09.2009 вышел хорошо оптимизированным (высокий fps на среднем железе), но с вендор-зависимостью: без Nvidia — ошибки Hardware PhysX, плюс активации GFWL/SecuROM. Сглаживатель кадров держал ~60 без .ini-твиков.
- **Версии/патчи:** 1.1 — поддержка PhysX; GOTY (2010) — DLC + 3D; в 10.2013 Steam-патч убрал GFWL + SecuROM (переход на Steamworks/GOTY); Mac-порт Feral 2011 — 32-бит.
- **Причина репутации:** процесс (DRM/сервисная обвязка при отличном ядре игры).
- **Решения:**
  - `+` UE3 + готовые tools: 60 человек за 21 месяц от геймплея с дня 1.
  - `+` GPU PhysX как опциональный слой: «вау» на Nvidia без ветвления геймплея.
  - `−` GFWL + SecuROM: сломанные установки/миграции сейвов, удалены только в 2013.
  - `±` Фикс fps через UserEngine.ini (MaxSmoothedFramerate=120+): разблокировка 120+ вручную.
- **Влияние:** графика — витрина UE3-лайтмапов + selective PhysX; процесс — кейс миграции на Steamworks.
- **DSS:** `lightmap_atlas_baking`, `baked_occlusion_culling`, `gpu_particle_simulation`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/35140/Batman_Arkham_Asylum_GOTY_Edition/), Unreal (https://www.unrealengine.com/blog/batman-arkham-asylum), PCGW (https://www.pcgamingwiki.com/wiki/Batman:_Arkham_Asylum).

### 72. FINAL FANTASY XIV Online (2010/2013, Square Enix / Crystal Tools → новый движок)

- **Движок:** 1.0 — Crystal Tools (кастомизированный, внутренне «broken» для MMO); 2.0/A Realm Reborn — полностью другой движок. Симптом: горшок ~1000 полигонов + 150 строк шейдера = стоимость персонажа; лимит ~20–40 персонажей на экране, copy-paste зоны, медленные серверные тики.
- **Релиз ПК:** 30.09.2010 — катастрофа: низкий fps даже на топ-ПК, UI-лаг и gathering на серверных тиках, пустые зоны; триал продлевали дважды, плату отменили, команду заменили (Yoshida вместо Tanaka), серверы 1.0 закрыли 11.11.2012; перезапуск ARR 27.08.2013 настолько успешен, что остановили продажи из-за очередей.
- **Версии/патчи:** Патчи 1.x под Yoshida, роадмап 2.0 (10.2011), финал «End of an Era», ARR 2013 на ПК/PS3 (позже PS4/Mac), далее экспаншены.
- **Причина репутации:** процесс (obsession с графикой без MMO-пайплайна).
- **Решения:**
  - `−` Ассеты уровня персонажа для мусора (горшки): крах crowd-бюджета.
  - `−` Crystal Tools для онлайна с сотнями моделей: выбор движка против жанра.
  - `+` Полный ребилд движка/серверов/UI + фидбек: редкий успешный релонч.
  - `±` Упрощение картинки в 2.0 ради зон и онлайна: fps и плотность важнее полигонов.
- **Влияние:** сеть — урок tickrate/relevancy и on-screen бюджетов; графика — GDC-кейс «цветочный горшок убил MMO».
- **DSS:** `crowd_instancing_impostors`, `hierarchical_lod`, `tickrate_budgeting`, `network_relevancy_priority`.
- **Источники:** Steam (https://store.steampowered.com/app/39210/FINAL_FANTASY_XIV_Online/), RPS (https://www.rockpapershotgun.com/why-final-fantasy-xiv-failed-and-how-it-recovered).

### 73. Call of Duty: Black Ops (2010, Treyarch / IW Engine)

- **Движок:** Treyarch-ветка IW 3.0; Theater Mode (запись/реплеи), возврат выделенных серверов после IWNet-скандала MW2, Zombies/кооп.
- **Релиз ПК:** 09.11.2010 — худший ПК-старт Treyarch: статтеры 60→15 fps и GPU-hitching даже на Phenom II X4 + HD5850/GTX 460; виновники — `r_multithreaded_device 0` по дефолту и шейдер-стриминг; плюс пустой server browser и лаг (sv_maxrate). Патч 12.11.2010 частично чинил dual/quad-core.
- **Версии/патчи:** Дневной патч 11.2010 (sv_maxrate 25000, dual/quad perf, RCon); позже фикс Theater (02.2011) и DLC; костыли игроков — multithreaded_device 1 / тени off.
- **Причина репутации:** реализация (отгруженная однопоточность и непрогретый шейдерный пайплайн на готовой ветке IW).
- **Решения:**
  - `+` Возврат dedicated servers + sv_maxrate 25000: спасение онлайна после MW2.
  - `+` Theater Mode: реплеи/киберспорт ценой диска и стабильности.
  - `−` Выключенная многопоточность из коробки: статтеры на многоядерниках.
  - `−` GPU/shader hitching без прекэша: микрофризы при новых эффектах.
- **Влияние:** оптимизация — кейс pso_precaching и multithread-by-default; сеть — возврат dedicated servers как обязательный фикс ожиданий ПК.
- **DSS:** `headless_dedicated_server`, `pso_precaching_warmup`, `tickrate_budgeting`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/42700/Call_of_Duty_Black_Ops/), Destructoid (https://www.destructoid.com/call-of-duty-black-ops-pc-lag-patch-released).

---

## Партия 9 (список-3, батч 3: №74–81)

### 74. Terraria (2011, Re-Logic / XNA)

- **Движок:** Microsoft XNA 4.0 (C#, Direct3D 9.0c); порты macOS/Linux позже на FNA/OpenGL, с 1.4.5 на Linux по умолчанию Vulkan с fallback на OpenGL. 2D-тайлмир со спрайт-батчингом, процедурные миры .wld/.plr.
- **Релиз ПК:** 16.05.2011 в Steam, в целом не «сломанный порт». На старте: зависимость XNA/.NET (не запускалась без них), просадки на слабых ПК, телепортация мобов/десинк в MP. Обходы: Frame Skip On + Lighting Retro, кап FPS до 30 против десинка.
- **Версии/патчи:** Долгая бесплатная поддержка: 1.1, 1.2, 1.3, Journey's End 1.4 (2020), 1.4.4 Labor of Love; macOS/Linux 10.08.2015 на FNA.
- **Причина репутации:** функционал (эталон песочницы с бесконечной поддержкой при минимальных требованиях).
- **Решения:**
  - `+` Тайловый мир + спрайт-батчинг: огромные разрушаемые миры на слабом железе.
  - `+` Выделенный сервер TerrariaServer.exe и прямые IP-хосты: простой кооп.
  - `±` Кастомный свет Retro/Trippy/Color/White как тир качества вместо GI.
  - `−` Привязка логики к 60 FPS, XNA-зависимости и single-thread: лаги/десинк в MP.
- **Влияние:** оптимизация — масштабирование через пресеты света/Frame Skip и FNA-порты; сеть — простой кооп без матчмейкинга.
- **DSS:** `tilemap_chunk_streaming`, `sprite_atlas_batching`, `headless_dedicated_server`, `snapshot_slot_saves`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/105600/Terraria/), PCGW (https://www.pcgamingwiki.com/wiki/Terraria).

### 75. Wolfenstein: The New Order (2014, MachineGames / id Tech 5)

- **Движок:** id Tech 5 (OpenGL), Virtual Texturing / MegaTexture, софтверное транскодирование текстур, цель 60 FPS.
- **Релиз ПК:** 19.05.2014. Наследовала проблемы id Tech 5 из RAGE: стриминг текстур, поп-ин и микростаттеры при нехватке VRAM/на AMD, мало настроек графики на старте. Проходима на 60 FPS на GTX 460/HD 5850+, но не эталон плавности.
- **Версии/патчи:** Пострелизные патчи стабильности и драйверных проблем; Old Blood (2015) на том же tech.
- **Причина репутации:** реализация (сильная кампания на спорной стриминговой MegaTexture).
- **Решения:**
  - `+` Virtual Texturing: уникальные текстуры без тайлинга при малом числе draw calls.
  - `+` Таргет 60 FPS и линейные уровни: сгладили стриминг против открытого мира RAGE.
  - `±` OpenGL + предзапечённый свет: кинематографичность ценой драйверных проблем на AMD.
  - `−` Стриминг-хитчи и поп-ин при быстрых поворотах камеры.
- **Влияние:** графика — пределы MegaTexture: уникальность ценой VRAM-стриминга; оптимизация — урок перехода id Tech 6 к другому управлению памятью.
- **DSS:** `virtual_texturing`, `async_loading_pipeline`, `lightmap_atlas_baking`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/201810/Wolfenstein_The_New_Order/), PCGW (https://www.pcgamingwiki.com/wiki/Wolfenstein:_The_New_Order).

### 76. Hitman: Absolution (2012, IO Interactive / Glacier 2)

- **Движок:** Glacier 2 (DirectX 11), толпы до ~1200 NPC на сцене, cloth, eye-adaptation. Точные техники GI/окклюзии — unstated.
- **Релиз ПК:** 20.11.2012. Порт силён визуально и с бенчмарком, держал 60 FPS на среднем железе, но MSAA и толпы грузили CPU/GPU; на AMD и слабых CPU — просадки и микростаттеры. Критика больше геймдизайна, а не крашей.
- **Версии/патчи:** Патчи производительности/DX11 и Contracts-режим; Hitman HD Enhanced Collection (2019) — отдельный ремастер.
- **Причина репутации:** функционал (технология толпы и Contracts при спорном отходе от песочницы).
- **Решения:**
  - `+` Инстансинг толпы + LOD анимации: живые вокзалы/улицы с сотнями агентов.
  - `+` DX11-фичи и бенчмарк для масштабирования.
  - `±` Time-sliced поиск пути толпы ценой упрощённого ИИ отдельных NPC.
  - `−` Цена MSAA/теней, CPU-горлышко в толпах.
- **Влияние:** графика — планка толпы для Glacier 2/Hitman (2016); оптимизация — бюджетирование агентов и анимаций.
- **DSS:** `crowd_instancing_impostors`, `animation_lod_budget`, `agent_update_budget`, `time_sliced_pathfinding`, `post_effect_selective`.
- **Источники:** Steam (https://store.steampowered.com/app/203140/Hitman_Absolution/), PCGW (https://www.pcgamingwiki.com/wiki/Hitman:_Absolution).

### 77. Resident Evil 6 (2012/2013, Capcom / MT Framework)

- **Движок:** MT Framework (DirectX 9 на ПК), стриминговые уровни, QTE-кооп на 2 игроков, Mercenaries-режим.
- **Релиз ПК:** Консоли — 10.2012, ПК — 22.03.2013 с DLC и бенчмарком. Держал 60 FPS на GTX 260/HD 4870, но ругали фиксированный FOV, управление мышью и QTE-дизайн; массовых крашей не было.
- **Версии/патчи:** Все консольные DLC, Left 4 Dead 2-кроссовер в Mercenaries, патчи баланса/производительности.
- **Причина репутации:** функционал (перекос в экшен/кооп и 4 кампании вместо хоррора, а не провал порта).
- **Решения:**
  - `+` Асинхронный стриминг кампаний и бенчмарк: подбор настроек на слабых ПК.
  - `+` Сжатие анимаций и бюджетирование врагов: толпы в коопе.
  - `±` P2P-кооп с предсказанием клиента ценой телепортов при плохом соединении.
  - `−` Узкий FOV и консольный UI/мышь на ПК.
- **Влияние:** сеть — кооперативный экшен как мост к RE Engine; оптимизация — масштабируемый DX9-порт с бенчмарком.
- **DSS:** `async_loading_pipeline`, `animation_compression`, `agent_update_budget`, `client_prediction_reconciliation`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/221040/Resident_Evil_6/), PCGW (https://www.pcgamingwiki.com/wiki/Resident_Evil_6).

### 78. METAL GEAR RISING: REVENGEANCE (2013/2014, PlatinumGames / собственный)

- **Движок:** Собственный движок PlatinumGames (DirectX 9 на ПК), 60 FPS-слэшер, Blade Mode со свободным резом.
- **Релиз ПК:** Консоли — 02.2013, ПК — 09.01.2014. Хвалили за честные 60 FPS и низкие требования, но ругали завязку на 60 Гц, ограниченные опции разрешения/катсцены и проблемы геймпада/звука. Не «broken port», а бюджетный перенос.
- **Версии/патчи:** Пострелизные патчи разрешения/стабильности; DLC (Jetstream, Blade Wolf) в PC-издании.
- **Причина репутации:** реализация (Zandatsu-рез и 60 FPS-бой при скромном бюджете порта).
- **Решения:**
  - `+` Кэш разрушаемой геометрии для резов в реальном времени без пре-анимаций.
  - `+` Фиксированный timestep физики под 60 FPS: точные парирования.
  - `±` Пост-эффекты и сжатие анимаций скрыли бедность ассетов.
  - `−` DX9-наследие и лок 60 FPS/60 Гц ограничили высокие герцовки.
- **Влияние:** графика — резка объектов как геймплей; оптимизация — приоритет фреймрейта над разрешением в слэшере.
- **DSS:** `destruction_geometry_cache`, `fixed_timestep_physics`, `animation_compression`, `post_effect_selective`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/235460/METAL_GEAR_RISING_REVENGEANCE/), PCGW (https://www.pcgamingwiki.com/wiki/Metal_Gear_Rising:_Revengeance).

### 79. Dying Light (2015, Techland / Chrome Engine 6)

- **Движок:** Chrome Engine 6 (DirectX 11, deferred), день/ночь, погода, паркур-анимация, открытый Харран без швов.
- **Релиз ПК:** 27.01.2015. Требовательна: слайдер дальности вида ронял FPS вдвое, статтеры стриминга, зерно/хроматическая аберрация без отключения на старте; на GTX 560/HD 8770 играбельна лишь на низких. Патчи быстро снизили статтеры, но view-distance остался горлышком.
- **Версии/патчи:** The Following (2016) + Enhanced Edition, Hellraid DLC, Definitive Edition (2023); скандал с блокировкой модов патчем и откат.
- **Причина репутации:** реализация (лучший паркур/день-ночь в зомби-песочнице ценой тяжёлого стриминга).
- **Решения:**
  - `+` Партиционирование Харрана + LOD/инстансинг растительности: бесшовный город/трущобы.
  - `+` LOD анимаций зомби и тайловый навмеш: сотни преследователей ночью.
  - `±` Полуразрешённые volumetrics/пост-эффекты ценой мыла на старте.
  - `−` Дальность вида и поп-ин стриминга: хитчи даже на GTX 780/R9 290.
- **Влияние:** оптимизация — урок тиринга дальности вида и Enhanced Edition как долгой поддержки; графика — день/ночь как геймплейный свет.
- **DSS:** `world_partition_streaming`, `hierarchical_lod`, `gpu_instancing_vegetation`, `animation_lod_budget`, `navmesh_tiling_streaming`.
- **Источники:** Steam (https://store.steampowered.com/app/239140/Dying_Light/), PCGW (https://www.pcgamingwiki.com/wiki/Dying_Light).

### 80. Assassin's Creed IV: Black Flag (2013, Ubisoft / AnvilNext)

- **Движок:** AnvilNext (DirectX 11), бесшовные Карибы, океанская симуляция (волны Герстнера/FFT), абордажи без загрузок, толпы Гаваны/Нассау.
- **Релиз ПК:** 19.11.2013. Красива, но неровный фреймпейсинг, CPU-ограничение в городах, тяжёлые TXAA/MSAA и проблемы SLI/CrossFire на старте; требовалась GTX 470/HD 5850 для высоких. Критичных крашей нет, но плавность ниже консолей без твиков.
- **Версии/патчи:** Патчи SLI/производительности и мультиплеера; Freedom Cry и Season Pass; Jackdaw Edition позже.
- **Причина репутации:** реализация (эталонный морской бой и бесшовный океан при неровном pacing ПК-версии).
- **Решения:**
  - `+` FFT/Герстнер-океан + стриминг островов: бесшовный переход штурвал→абордаж→суша.
  - `+` Инстансинг толпы и LOD кораблей: Гавана и морские бои.
  - `±` Пост-эффекты и каскадные тени ценой CPU-узкого места в городах.
  - `−` Однопоточные просадки и тяжёлое сглаживание: pacing 30–45 FPS на рекомендуемом железе.
- **Влияние:** графика — океан Black Flag как референс; оптимизация — цена бесшовности без поточного рендера.
- **DSS:** `gerstner_fft_water`, `world_partition_streaming`, `crowd_instancing_impostors`, `hierarchical_lod`, `cascaded_shadow_maps`.
- **Источники:** Steam (https://store.steampowered.com/app/242050/Assassins_Creed_IV_Black_Flag/), PCGW (https://www.pcgamingwiki.com/wiki/Assassin%27s_Creed_IV:_Black_Flag).

### 81. Watch_Dogs (2014, Ubisoft / Disrupt)

- **Движок:** Disrupt (DirectX 11), Чикаго, динамический ветер/вода/трафик; демо E3 2012 на том же движке.
- **Релиз ПК:** 27.05.2014. Скандал даунгрейда против E3 2012 (мод TheWorse разблокировал скрытые bokeh/настройки); на ПК — статтеры на Ultra даже с 3 ГБ VRAM, мышь с акселерацией как эмуляция стика, долгие запуски. Обходы: -disablepagefilecheck и фикс мыши.
- **Версии/патчи:** Патчи статтеров и SLI, Bad Blood DLC (T-Bone), Complete Edition; мультиплеер Steam-версии позже затронут уходом сервисов.
- **Причина репутации:** процесс (маркетинг E3 против релиза и тяжёлый Ultra-пресет).
- **Решения:**
  - `+` Стриминг Чикаго + инстансинг толпы/трафика: живой город с вторжениями в сингл.
  - `+` Time-sliced трафик-ИИ и бюджеты агентов: погони/ctOS-хаки.
  - `±` Селективные пост-эффекты (bokeh/DOF) в конфигах ценой скандала.
  - `−` Реализация AF, мыши и pagefile-чек: статтеры/инпут-лаг.
- **Влияние:** оптимизация — эталон провала Ultra-пресета и pagefile-аллокации; графика — урок документирования E3-настроек.
- **DSS:** `world_partition_streaming`, `crowd_instancing_impostors`, `time_sliced_pathfinding`, `post_effect_selective`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/243470/Watch_Dogs/), PCGW (https://www.pcgamingwiki.com/wiki/Watch_Dogs).

---

## Партия 10 (список-3, батч 4: №82–89)

### 82. Plague Inc: Evolved (2014/2016, Ndemic / Unity)

- **Движок:** Unity (подтверждено поддержкой/IGDB).
- **Релиз ПК:** Ранний доступ 20.02.2014, полный релиз 18.02.2016. Требования минимальные (2.0 GHz Dual Core, 1 ГБ RAM, интегрированная графика), обычно стабильные 60 fps без массового скандала. Точечно: чёрный/белый экран при старте, Unity-crash в конце партии, битый VideoConfig.txt.
- **Версии/патчи:** Кооп/versus мультиплеер, Scenario Creator + Steam Workshop (>10000 сценариев), графика до 4K; контент-патчи (Mad Cow Disease 21.11.2017), The Cure DLC 28.01.2021; обновление версии Unity для стабильности.
- **Причина репутации:** функционал (симуляция + UGC-редактор при нулевом пороге железа).
- **Решения:**
  - `+` Workshop + Scenario Creator: хвост контента без доплат.
  - `+` Низкие quality tiers и 2D-симуляция: идёт на интегрированной графике.
  - `±` Мультиплеер поверх симуляции без шутерного неткода.
  - `−` Поздние перф-жалобы после апдейтов Unity (репорты 2021).
- **Влияние:** оптимизация — масштабирование пресетами вместо переписывания рендера; контент — редактор как стратегия.
- **DSS:** `sprite_atlas_batching`, `quality_tier_scalability`, `snapshot_slot_saves`, `deterministic_lockstep`.
- **Источники:** Steam (https://store.steampowered.com/app/246620/), Ndemic (https://www.ndemiccreations.com/en/25-plague-inc-evolved), SteamDB (https://steamdb.info/app/246620/patchnotes/).

### 83. Rust (2013 EA / 2018, Facepunch / Unity)

- **Движок:** Unity (старт Unity 4 Legacy в браузере, затем Reboot на Unity 5; позже 5.4/2017.1, апгрейд до Unity 6 в 2026).
- **Релиз ПК:** Early Access 11.12.2013, релиз 08.02.2018. CPU/RAM-bound: статтеры каждые 10–15 сек даже при 150 fps, GC-стопы, долгие генерации карт, просадки от плотности баз и онлайна. Минимум GTX 1050 / i7-3770 / 10 ГБ, рекомендовано RTX 3060 / 16 ГБ + SSD, есть DLSS.
- **Версии/патчи:** Rust Legacy переписан как Reboot с процедурной генерацией и кэшированием мира; ежемесячные вайпы/апдейты и Devblogs; XP-система 2016 со stall сейва БД; даунгрейд Unity 5.4.2f2 из-за бага физики.
- **Причина репутации:** реализация (процедуры + сеть + GC-борьба на Unity в масштабе MMO-выживания).
- **Решения:**
  - `+` Процедурные карты + кэш/стриминг мира с сервера: быстрые повторные заходы.
  - `+` Headless dedicated servers + вайпы: масштабирование онлайна.
  - `±` Relevancy/culling и пулинг (Facepunch.Pool): меньше памяти/сети ценой просадок в мега-базах.
  - `−` Mono/GC-хитчи и gc.buffer-костыли: микрофризы на хорошем железе.
- **Влияние:** сеть — эталон выживания на dedicated servers с вайпами; оптимизация — борьба с GC как архитектурная тема.
- **DSS:** `gpu_procedural_placement`, `headless_dedicated_server`, `tickrate_budgeting`, `network_relevancy_priority`, `hierarchical_lod`, `crowd_instancing_impostors`.
- **Источники:** Steam (https://store.steampowered.com/app/252490/), Facepunch 10 лет (https://rust.facepunch.com/news/10-years-of-rust), Devblog 118 (https://rust.facepunch.com/news/devblog-118).

### 84. Subnautica (2014 EA / 2018, Unknown Worlds / Unity)

- **Движок:** Unity (5.6 на релизе, затем миграция на Unity 2018).
- **Релиз ПК:** Early Access 16.12.2014, релиз 23.01.2018. Прогрессивные фризы/статтеры: падение 100 fps до 10–20 взглядом на базу/kelp, рост CellsCache и раздувание сейвов, медленные сейвы, indoor-хитчи при 35% загрузке GPU. Лечилось очисткой CellsCache/CompiledOctreesCache и новой игрой — признак стриминга/сейвов, а не железа.
- **Версии/патчи:** Eye Candy Update (переработка графики + прирост fps); тяжёлая миграция 5.6→2018; оптимизация Panic Button (порты Xbox/PS4, часть перешла на ПК); Below Zero как отдельная ветка.
- **Причина репутации:** реализация (стриминг/батчинг/сейвы подводного мира на Unity).
- **Решения:**
  - `−` Батч-кэш сущностей/террейна без компактификации: рост CellsCache = просадки.
  - `±` Воксельный террейн + LOD: красивое дно и пещеры ценой попинов и статтеров смены LOD.
  - `−` Draw calls без агрессивного батчинга (репорт: 522 CPU-вызова на базе вместо <5).
  - `+` Snapshot-сейвы со слотами: устойчивость прогресса ценой медленных синхронных сейвов.
- **Влияние:** оптимизация — кейс кэша стриминга и батчинга как главной боли Unity-опенворлда; контент — биомы вместо бесшовности.
- **DSS:** `world_partition_streaming`, `hierarchical_lod`, `async_loading_pipeline`, `snapshot_slot_saves`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/264710/), Unknown Worlds cache guide (https://forums.unknownworlds.com/discussion/146057/cache-clearing-guide-v3-fix-performance-crashes-lag-stuttering-and-fix-saves-that-dont-update).

### 85. Cuphead (2017, Studio MDHR / Unity)

- **Движок:** Unity (прототип XNA → Unity; Sprite Renderer/Packer, 2D Physics, particles).
- **Релиз ПК:** 29.09.2017. Дизайн: анимация 24 fps в стиле 1930-х поверх геймплея 60 fps, ~50000 кадров ручной анимации; порт лёгкий и стабильный. Точечно: спайки лага (лечились windowed/VSync), cuphead.exe has stopped working на загрузке, конфликт DX11-рендера на части систем.
- **Версии/патчи:** Релизные хотфиксы стабильности; флаг -force-d3d9 как fallback с DX11; DLC The Delicious Last Course.
- **Причина репутации:** реализация (разделение 24 fps арта и 60 fps симуляции/инпута).
- **Решения:**
  - `+` 24 fps анимации + 60 fps симуляции/инпута: отзывчивость при «мультяшности».
  - `+` Sprite Packer + layer-sorting/параллакс: дешёвый батчинг 2D.
  - `+` Фиксированный тайминг боссов под 60 fps: честная сложность.
  - `±` DX11 по умолчанию с fallback -force-d3d9: стабильность ценой качества в D3D9.
- **Влияние:** графика — ручная анимация как стиль без цены 3D; оптимизация — разделение частоты арта и симуляции.
- **DSS:** `sprite_atlas_batching`, `fixed_timestep_physics`, `art_direction_stylization`, `post_effect_selective`.
- **Источники:** Steam (https://store.steampowered.com/app/268910/), Unity Cuphead (https://unity.com/made-with-unity/cuphead).

### 86. BlazeRush (2014, Targem / собственный)

- **Движок:** Собственный движок Targem (название unstated; в Steam/PCGW движок не указан) — null по деталям.
- **Релиз ПК:** Windows 28.10.2014. Легковесная аркада (~300 МБ, Core2 Duo E4500, GeForce 7300GT, 2 ГБ RAM), вид сверху, стабильные 60 fps, Very Positive 88%. Массовых крашей не зафиксировано; критика — мёртвый онлайн-подбор и камера в сплите.
- **Версии/патчи:** 1.0.1 19.11.2014 (баги/стабильность); Linux/macOS 19.12.2014; PS4 15.12.2015; Oculus Rift 28.03.2016; Switch 19.02.2019; Anniversary + Star Track DLC 2024; конец поддержки Linux/macOS/SteamVR 05.2024.
- **Причина репутации:** функционал (couch 4p + онлайн 8p с низким порогом).
- **Решения:**
  - `+` Couch 4p + онлайн 8p с join-anytime: низкий порог входа.
  - `+` Фиксированная камера сверху и маленькие арены: дешёвый culling и сеть.
  - `+` Рандом оружия + catch-up бусты против доминирования лидера.
  - `+` Sub-1GB футпринт и низкие tiers: идёт на слабом железе.
- **Влияние:** оптимизация — маленькая арена + фикс-камера как бесплатный перфоманс; сеть — join-anytime без матчмейкинга.
- **DSS:** `fixed_timestep_physics`, `deterministic_lockstep`, `client_prediction_reconciliation`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/302710/), Targem (https://targem.com/project/blazerush/), PCGW (https://www.pcgamingwiki.com/wiki/BlazeRush).

### 87. Metro 2033 Redux (2014, 4A Games / 4A Engine)

- **Движок:** 4A Engine (итерация Last Light, на которую перестроен 2033).
- **Релиз ПК:** 26–28.08.2014 в составе Metro Redux. Масштабируемая DX11-версия: от Intel-iGPU на 720p до Titan-класса на максимуме; убрана часть затратных мелочей оригинала (тени от вспышек, часть volumetrics). Digital Foundry: консоли locked 60 fps (PS4 1080p, Xbox One 912p, adaptive VSync); на ПК — улучшенные AI/стелс/ганплей и освещение при лучшей производительности на слабом железе.
- **Версии/патчи:** Пересборка 2033 на фреймворке Last Light (AI, анимации, кастомизация оружия, mask-wipe, takedowns); режимы Spartan/Survival + Ranger/Hardcore без HUD; Last Light Redux с DLC; Switch-порт 2020.
- **Причина репутации:** реализация (пересадка на свежий движок как ремастер без полного ремейка).
- **Решения:**
  - `+` Пересадка на Last Light-движок: один пайплайн, свет/погода/физика дешевле.
  - `+` Spartan/Survival tiers + Ranger Mode: реиграбельность без форка билдов.
  - `+` Стелс-AI без psychic-агро: честный стелс и репозиционирование.
  - `+` 60 fps таргет с adaptive VSync и скейл на ПК.
- **Влияние:** графика — ремастер через движок, а не ассеты; оптимизация — тиры сложности как контент без цены.
- **DSS:** `lightmap_atlas_baking`, `volumetric_half_resolution`, `particle_pooling`, `cascaded_shadow_maps`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/286690/), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2014-metro-redux-face-off), TechSpot (https://www.techspot.com/review/878-metro-redux-benchmarks/).

### 88. FINAL FANTASY XIII (2009/2014 ПК, Square Enix / Crystal Tools)

- **Движок:** Crystal Tools.
- **Релиз ПК:** Steam 09.10.2014, ~59–60 ГБ (тяжёлые FMV). Порт заблокирован на 720p внутреннем рендере без AA/AF/VSync/теней в опциях, ESC мгновенно закрывает игру. Регулярные лаги каждые ~2 сек и статтеры катсцен даже на сильном железе, даунгрейд Bink-FMV; однопоточная логика (наследие Cell) и недогруз CPU/GPU.
- **Версии/патчи:** GeDoSaTo Beta 0.14 от Durante (рендер до 3840x2160, HUD-toggle); официальный патч 11.12.2014 — кастомные разрешения и опции; community FF13Fix (снятие frame-pacer/triple-buffer, фикс инпута, 1440p) + 4GB Patch + HD-FMV моды.
- **Причина репутации:** процесс (порт без скейлимости, починенный сообществом и поздним патчем).
- **Решения:**
  - `−` Лок 720p + отсутствие меню графики: нулевая скейлимость.
  - `−` Агрессивный frame-pacer и опрос инпута каждый кадр: микростаттеры на Titan-классе.
  - `−` 32-бит/2GB лимит и тяжёлые FMV: краши и 60 ГБ вес.
  - `−` ESC-quit без паузы и минимум портовых функций.
- **Влияние:** оптимизация — антипример порта: лок разрешения + пейсер + 2GB-лимит; процесс — Durante/FF13Fix как внешняя служба поддержки.
- **DSS:** `quality_tier_scalability`, `baked_occlusion_culling`, `animation_compression`.
- **Источники:** Steam (https://store.steampowered.com/app/292120/), PCGW (https://www.pcgamingwiki.com/wiki/Final_Fantasy_XIII), FF13Fix (https://github.com/rebtd7/FF13Fix).

### 89. FINAL FANTASY XIII-2 (2011/2014 ПК, Square Enix / Crystal Tools)

- **Движок:** Crystal Tools (Square Enix + tri-Ace).
- **Релиз ПК:** Steam 11.12.2014. Лучше XIII: высокие разрешения, 60 fps таргет, тени высокого разрешения, MSAA, улучшенный звук, почти все DLC и JP-озвучка. Остались: нестабильный fps от frame-pacer (30–50 на Titan X), краши от 2 ГБ RAM, битая прозрачность дождя, игнор alpha-канала в тенях.
- **Версии/патчи:** Официальной переделки нет; фиксы community: FF13Fix (снятие пейсера, triple-buffer, анкап, HUD/вибрация/1440p), 4GB Patch, Leviathan's Tears для дождя.
- **Причина репутации:** процесс (шаг вперёд от XIII, но те же системные болячки Crystal Tools-порта).
- **Решения:**
  - `+` Сразу высокие разрешения/60fps/тени/MSAA и DLC в комплекте.
  - `−` 2GB-лимит без LargeAware: краши в скриптовых сегментах.
  - `−` Сломанные тени от alpha-test геометрии и дождь без transparency.
  - `−` Конфликт внутриигровых cloud-сейвов со Steam Cloud.
- **Влияние:** оптимизация — те же уроки XIII: пейсер + 2GB + тени; процесс — community-фиксы как обязательный слой.
- **DSS:** `quality_tier_scalability`, `cascaded_shadow_maps`, `snapshot_slot_saves`, `async_incremental_saves`.
- **Источники:** Steam (https://store.steampowered.com/app/292140/), PCGW (https://www.pcgamingwiki.com/wiki/Final_Fantasy_XIII-2), FF13Fix (https://github.com/rebtd7/FF13Fix).

---

## Партия 11 (список-3, батч 5: №90–97)

### 90. FOR HONOR (2017, Ubisoft Montreal / AnvilNext)

- **Движок:** AnvilNext 2.0.
- **Релиз ПК:** 14.02.2017 на ПК/PS4/Xbox One (Steam + Uplay), требует постоянного онлайна для всех режимов. Клиент 31–37 ГБ в зависимости от платформы/региона.
- **Версии/патчи:** Сезон 5 Age of Wolves (15.02.2018); выделенные серверы на ПК 19.02.2018, на консолях позже; далее многолетние сезоны Year / Marching Fire.
- **Причина репутации:** процесс (P2P-сессии без выделенных серверов: миграции, разрывы, NAT/лаги, критичные для дуэльной melee-системы; позже — спасение переходом на серверы).
- **Решения:**
  - `+` Переход P2P → dedicated: уборка миграций сессий и NAT-требований.
  - `±` Перебалансировка героев и борьба с defensive-meta при ~100 мс.
  - `+` Тренировочные режимы и переработка прогрессии/ранкеда в Age of Wolves.
  - `±` EasyAntiCheat + серверные фиксы группировки и матчмейкинга.
- **Влияние:** сеть — хрестоматийный кейс P2P → dedicated в файтинге с жёстким требованием к задержке.
- **DSS:** `headless_dedicated_server`, `client_prediction_reconciliation`, `tickrate_budgeting`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/For_Honor), SteamDB (https://steamdb.info/app/304390/patchnotes/), Ubisoft (https://news.ubisoft.com/en-us/article/5vpVACm004BZquaodiArA9/for-honor-dedicated-servers-launching-february-19-on-pc).

### 91. Mortal Kombat X (2015, NetherRealm / Unreal Engine 3 мод.)

- **Движок:** Unreal Engine 3 (модифицированный).
- **Релиз ПК:** Windows 14.04.2015; порт — High Voltage Software. Краши на CPU с >8 ядрами, порча/потеря сейвов, краши драйверов в онлайне, просадки FPS и плохой неткод на старте.
- **Версии/патчи:** Патч 07.05.2015 ~15 ГБ (краши, сейвы, онлайн, перф); обновление XL 04.10.2016 силами QLOC: оптимизация, поддержка ПК и сетевого кода.
- **Причина репутации:** процесс (один из самых проблемных ПК-портов 2015: аутсорс-порт, починенный сменой подрядчика).
- **Решения:**
  - `+` Проверка целостности сейвов и защита от порчи при закрытии.
  - `+` Фикс стартового краша на многоядерных CPU и крашей лобби/QTE/реплеев.
  - `±` Дополнительные графические опции и общая производительность.
  - `+` Передача ПК-версии QLOC для XL: оптимизация и неткод.
- **Влияние:** процесс — кейс аутсорс-порта High Voltage → QLOC; практика отдачи ПК-фиксов специализированным студиям.
- **DSS:** `deterministic_lockstep`, `fixed_timestep_physics`, `animation_compression`, `quality_tier_scalability`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Mortal_Kombat_X), QLOC (https://q-loc.com/mortal-kombat-xl-pc-developed-qloc/), Steam (https://store.steampowered.com/app/307780/Mortal_Kombat_X/).

### 92. Call of Duty: Black Ops III (2015, Treyarch / IW Engine)

- **Движок:** IW Engine, сильно модифицированная ветка Treyarch.
- **Релиз ПК:** 06.11.2015; заявлялись 100% ранкед-выделенные серверы, FOV-слайдер, SLI/CrossFire, 4K. На старте — статтеры и утечка памяти при 6–12 ГБ ОЗУ; Intel i5-баг.
- **Версии/патчи:** Стартовые хотфиксы 11.2015; DSOG-анализ: тяжёлые тени Extra, Order Independent Transparency и волюметрика, прожорливость к VRAM, битые текстуры High/Extra High после апдейта.
- **Причина репутации:** реализация (GPU-bound с завышенными требованиями: 1080p/60 на максимуме требовал GTX 980 Ti; Extra-тени неиграбельны).
- **Решения:**
  - `±` Увеличение ОЗУ до 16 ГБ и VRAM до 12 ГБ снимало статтеры (проблема бюджетирования памяти).
  - `±` Правка config.ini WorkerThreads 4→2 и VRAM-фракции от сообщества.
  - `+` Снижение теней Extra→High, OIT и волюметрики вместо разрешения.
  - `±` VSync + кап FPS чуть ниже герцовки по рекомендации Treyarch.
- **Влияние:** оптимизация — разрыв минимальных требований и реального потребления (~10 ГБ); урок memory budgeting в CoD.
- **DSS:** `async_loading_pipeline`, `headless_dedicated_server`, `dynamic_resolution_scaling`, `quality_tier_scalability`.
- **Источники:** DSOG (https://www.dsogaming.com/pc-performance-analyses/call-of-duty-black-ops-iii-pc-performance-analysis/), PCWorld (https://www.pcworld.com/article/424313/pc-gamers-in-uproar-over-call-of-duty-black-ops-iii-stuttering-problems.html), Steam (https://store.steampowered.com/app/311210/Call_of_Duty_Black_Ops_III/).

### 93. Arma Tactics (2013, Bohemia / Unity)

- **Движок:** Unity.
- **Релиз ПК:** Мобильный старт (Nvidia Shield/iOS) 2013; ПК в Steam 01.10.2013 ($8.99, предзаказ −15% + бета). Разработчик — Bohemia + Centauri Production.
- **Версии/патчи:** Только мелкие багфиксы (прогрессия кампании, размещение миссий, совместимость с ОС). DLC и крупных обновлений не было.
- **Причина репутации:** функционал (mobile-first пошаговая тактика без переработки ядра: ~33% положительных, баги и неровная сложность).
- **Решения:**
  - `+` ПК-апгрейд графики: HD-текстуры, пост-эффекты, лайтмапы, шейдеры и тени.
  - `+` Управление под мышь+клавиатуру + полная поддержка геймпада.
  - `±` Процедурные миссии с рандом-целями для реиграбельности.
  - `−` Точечные патчи стабильности вместо смены движка/редизайна.
- **Влияние:** процесс — пример неудачного переноса mobile→PC, перекрытый успехом Arma 3 того же года.
- **DSS:** `lightmap_atlas_baking`, `time_sliced_pathfinding`, `agent_update_budget`, `quality_tier_scalability`.
- **Источники:** Bohemia (https://www.bohemia.net/blog/arma-tactics-released-for-pc-via-steam), Steam (https://store.steampowered.com/app/224860/Arma_Tactics/), PCGW (https://www.pcgamingwiki.com/wiki/Arma_Tactics).

### 94. We Happy Few (2016 EA/2018, Compulsion / Unreal Engine 4)

- **Движок:** Unreal Engine 4 + PhysX/APEX; процедурная генерация Веллингтон-Уэллс.
- **Релиз ПК:** Ранний доступ с 2016; полный релиз 10.08.2018 (Windows/Mac/Linux, Gearbox Publishing). CPU-bound просадки и фризы даже на топ-ПК 2018, гоустинг FXAA/TAA, претензии к AMD.
- **Версии/патчи:** Патч 1.4 (09.2018) и 1.5: fps, краши, блокеры прогрессии, баги, локализация; далее DLC Lightbearer / They Came From Below / We All Fall Down.
- **Причина репутации:** реализация (цена процедурного open-world на UE4 для инди-студии: CPU-бюджет и стриминг вместо графики).
- **Решения:**
  - `±` Пострелизные патчи производительности и стабильности.
  - `±` Ручной resolution scaling и правки Config для переноса нагрузки на GPU.
  - `−` Костыль с капом 72 FPS для стабильных 60 на AMD.
  - `+` Отключение внутриигрового AA против гостинга.
- **Влияние:** оптимизация — упор на CPU-бюджетирование и стриминг; учтено при поглощении Compulsion Xbox Game Studios.
- **DSS:** `world_partition_streaming`, `async_loading_pipeline`, `crowd_instancing_impostors`, `quality_tier_scalability`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/We_Happy_Few), SteamDB (https://steamdb.info/app/320240/patchnotes/).

### 95. Geometry Dash (2013, RobTop / Cocos2d-x)

- **Движок:** Cocos2d-x.
- **Релиз ПК:** Мобильный релиз iOS/Android 13.08.2013; Windows Phone 12.06.2014; Steam Windows/macOS 22.12.2014. Разработка ~4 месяца, соло.
- **Версии/патчи:** Долгие циклы: 2.1, затем 2.2 (12.2023) с пиком >88 000 онлайна в Steam; редактор уровней и UGC-серверы — основа долголетия.
- **Причина репутации:** функционал (строгая синхронизация с музыкой, детерминированный тайминг, UGC-каталог, стабильность на слабом железе).
- **Решения:**
  - `+` Фиксированный таймстеп и привязка логики к 60 Гц: детерминированные прыжки и музыка.
  - `+` Спрайт-батчинг и атласы Cocos2d-x для тысяч объектов без просадок.
  - `+` Локальные слоты сейвов и бэкап прогресса/редактора.
  - `+` Минимальные требования и тиринг качества вместо тяжёлых эффектов.
- **Влияние:** контент — доказательство силы UGC + лёгкого движка: 10+ лет без смены движка.
- **DSS:** `fixed_timestep_physics`, `sprite_atlas_batching`, `snapshot_slot_saves`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/322170/Geometry_Dash/), PCGW (https://www.pcgamingwiki.com/wiki/Geometry_Dash).

### 96. Frostpunk (2018, 11 bit / Liquid Engine)

- **Движок:** Liquid Engine (собственный).
- **Релиз ПК:** Windows 24.04.2018; PS4/Xbox One 11.10.2019; macOS 24.02.2021. Первая society survival студии после This War of Mine, команда ~60 человек. Технически цельно, но без официальной модподдержки из-за ограничений движка.
- **Версии/патчи:** 1.3.3 Photo Mode/Mac/Ansel/квиксейвы, 1.4 Season Pass + Rifts, 1.5 The Last Autumn, 1.6 On The Edge + тех-апдейты 2020–2022 (сейвы, статтеры видео, стабильность).
- **Причина репутации:** функционал (симуляция горожан, тепла и narrative-триггеров) + реализация (предел проприетарного движка).
- **Решения:**
  - `+` Бюджетирование апдейтов агентов и поиск пути по тикам для сотен горожан.
  - `±` Оверлеи тепла и перебалансировка сценариев вместо роста симуляции.
  - `±` Фиксы пропадающих сейвов и обратная совместимость сейвов до 1.3.3.
  - `+` Ansel-интеграция и F5/F9 квиксейвы как дешёвое расширение UX.
- **Влияние:** процесс — предел Liquid Engine привёл к ремейку Frostpunk 1886 на Unreal Engine 5 ради модподдержки и найма.
- **DSS:** `agent_update_budget`, `time_sliced_pathfinding`, `snapshot_slot_saves`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/323190/Frostpunk/), Fandom патчноуты (https://frostpunk.fandom.com/wiki/Patch_notes), 11bit (https://11bitstudios.com/the-reveal-of-frostpunk-1886/).

### 97. Devil May Cry 4 Special Edition (2015, Capcom / MT Framework)

- **Движок:** MT Framework.
- **Релиз ПК:** 06.2015, через 7 лет после оригинала 2008. Добавляет Вергилия/Триш/Леди, Legendary Dark Knight Mode, апскейл текстур, костюмы и баланс. Не ремастер, а расширенное издание.
- **Версии/патчи:** Значимых контент-патчей не было. Известны HEX-правка отключения motion blur и DDMK для borderless/ультравайд. Проблемы 16:10 и ультравайд из коробки.
- **Причина репутации:** реализация (парадокс: оригинал — эталонный ПК-порт с DX10, а SE при той же картинке ~на 100 FPS хуже по DSOG + мыльный blur/bloom/haze без опции).
- **Решения:**
  - `+` Отключение motion blur через HEX-редактор.
  - `+` DDMK-мод для borderless, ultrawide-фикса и твиков.
  - `±` Откат пост-эффектов и отключение SLI для честного сравнения.
  - `−` Использование гайдов Steam вместо официальных патчей.
- **Влияние:** процесс — кейс регрессии переиздания; требование отключаемых пост-эффектов в Capcom-портах до RE Engine.
- **DSS:** `animation_compression`, `post_effect_selective`, `mesh_index_optimization`, `quality_tier_scalability`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Devil_May_Cry_4:_Special_Edition), DSOG (https://www.dsogaming.com/first-impressions/devil-may-cry-4-special-edition-first-impressions-first-15-minutes-playthrough/), Steam (https://store.steampowered.com/app/329050/Devil_May_Cry_4_Special_Edition/).

---

## Партия 12 (список-3, батч 6: №98–105)

### 98. DARK SOULS II: Scholar of the First Sin (2015, FromSoftware / собственный)

- **Движок:** Фирменный движок FromSoftware; Scholar — переход DX9→DX11 с улучшенными текстурами/светом/тенями.
- **Релиз ПК:** Оригинал 24.04.2014; Scholar как отдельная DX11-версия 02.04.2015. «Director's Cut»: новая расстановка врагов, NPC Forlorn, все 3 DLC, отдельный клиент без бесплатного апгрейда.
- **Версии/патчи:** Разные клиенты DX9/DX11 в Steam; патчами правили баланс и баг двукратной потери прочности при 60 FPS (фанатский DS2Fix64 вышел раньше официального признания).
- **Причина репутации:** реализация (при 60 FPS оружие ломалось вдвое быстрее: проверка прочности срабатывала чаще за кадр; на 30 FPS эффект пропадал).
- **Решения:**
  - `−` Ограничение FPS до 30 через драйвер для нормальной скорости износа.
  - `±` Игра при 60 FPS со сменой оружия и ремонтным порошком.
  - `+` Фанатский фикс прочности DS2Fix64.
  - `±` Патч Scholar с корректировкой прочности.
- **Влияние:** оптимизация — хрестоматийный пример привязки логики к кадрам; недоверие к 60 FPS в Souls-портах до DS3.
- **DSS:** `fixed_timestep_physics`, `tickrate_budgeting`, `collision_layer_matrix`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/335300/DARK_SOULS_II_Scholar_of_the_First_Sin/), Kotaku (https://kotaku.com/annoying-dark-souls-2-glitch-has-gone-unfixed-for-nearl-1697992451), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2014-dark-souls-2-pc-face-off).

### 99. Fallout 4 VR (2017, Bethesda / Creation Engine)

- **Движок:** Creation Engine, Direct3D 11, Havok Physics и Nvidia Flex.
- **Релиз ПК:** 12.12.2017 только для VR через SteamVR. Отдельная покупка без DLC на старте (перенос модами вручную). Требовала стабильных 90 FPS, что резко подняло требования против плоской Fallout 4.
- **Версии/патчи:** Версия 1.2.x; крупных официальных оптимизационных патчей почти не было. Поддержка — INI-файлы, гайды Steam и мод VR Optimization Project с перегенерацией precombined-объектов.
- **Причина репутации:** реализация (предел Creation Engine для VR без переработки стриминга: статтеры, reprojection, VRAM, вылеты).
- **Решения:**
  - `+` Снижение supersampling и дальностей в INI для удержания 90 FPS.
  - `+` Мод VR Optimization Project с precombined для центра Бостона.
  - `±` Принудительное использование дискретной GPU и обновление драйверов.
  - `±` Слияние установок плоской и VR для экономии ~20 ГБ и ручной перенос DLC.
- **Влияние:** оптимизация — движок с тяжёлыми draw call в городе плохо масштабируется под стереорендер; проект сообщества, а не Bethesda.
- **DSS:** `world_partition_streaming`, `async_loading_pipeline`, `baked_occlusion_culling`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/611660/Fallout_4_VR/), PCGW (https://www.pcgamingwiki.com/wiki/Fallout_4_VR), Nexus (https://www.nexusmods.com/fallout4/mods/28850).

### 100. ARK: Survival Evolved (2015 EA/2017, Studio Wildcard / Unreal Engine 4)

- **Движок:** Unreal Engine 4 + BattlEye + Epic Online Services.
- **Релиз ПК:** Ранний доступ 02.06.2015; 1.0 — 29.08.2017. Синоним «неоптимизированного UE4-сурвайвала»: огромные карты, дино, строительство, сетевые серверы.
- **Версии/патчи:** Сотни патчей (DX10/SM4-режим, тени, foliage, сетевой код), но фундаментальная тяжесть осталась; сообщество массово использовало Engine.ini / GameUserSettings.ini твики.
- **Причина репутации:** реализация (даже 2x Titan Xp + i9-10900K не держали 60 FPS в 4K на Epic; статтеры при повороте камеры).
- **Решения:**
  - `±` Launch-опции `-USEALLAVAILABLECORES -sm4 -d3d10` для слабых ПК.
  - `+` Правка Engine.ini / GameUserSettings.ini по гайдам.
  - `+` Снижение теней, draw distance и пост-эффектов в первую очередь.
  - `−` Апгрейд драйверов и закрытие оверлеев, снижение разрешения.
- **Влияние:** оптимизация — эталон «плохой оптимизации UE4» и источник типовых Engine.ini-твиков, перекочевавших в Ascended на UE5.
- **DSS:** `hierarchical_lod`, `gpu_instancing_vegetation`, `cascaded_shadow_maps`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/346110/ARK_Survival_Evolved/), SteamDB (https://steamdb.info/app/346110/patchnotes/).

### 101. NARUTO SHIPPUDEN: Ultimate Ninja STORM 4 (2016, CyberConnect2 / собственный)

- **Движок:** Фирменный движок CyberConnect2, DirectX 11 на ПК (название не раскрывалось) — null по деталям.
- **Релиз ПК:** Steam 04–05.02.2016 одновременно с консолями. При скромных требованиях (i3-530, 4 ГБ ОЗУ) — жалобы: лок 30 FPS, отсутствие выбора GPU, вылеты каждые 10–15 минут на Windows 10, `DX11 device creation fail 0x80010010` у AMD, падение до 10 FPS на ноутбуках с GTX 960M (автовыбор Intel HD).
- **Версии/патчи:** Патчи чинили вылеты/стабильность, но лок 30 FPS и скудные опции сохранились; апдейт 02.2017 добавил баг удвоенной скорости шкалы подмены.
- **Причина репутации:** процесс (слабый Bandai-порт эпохи; стереотип «все STORM на ПК — 30 FPS»).
- **Решения:**
  - `+` Принудительный выбор дискретной GPU в панели Nvidia.
  - `±` Правка разрешения в config.ini и VSync.
  - `±` Совместимость с Windows 7 и отключение сенсорной клавиатуры.
  - `−` Обновление DirectX/драйверов и проверка дискретной GPU по гайдам.
- **Влияние:** процесс — очередной пример слабого Bandai-порта; урок выбора GPU в ноутбуках.
- **DSS:** `fixed_timestep_physics`, `quality_tier_scalability`, `post_effect_selective`, `animation_lod_budget`.
- **Источники:** Steam (https://store.steampowered.com/app/349040/NARUTO_SHIPPUDEN_Ultimate_Ninja_STORM_4/), Prima (https://primagames.com/news/naruto-shippuden-ultimate-ninja-storm-4-pc-port-problems).

### 102. Elite Dangerous (2014, Frontier / Cobra Engine)

- **Движок:** Собственный Cobra Engine.
- **Релиз ПК:** Windows 16.12.2014. База и Horizons хорошо оптимизированы под GTX 470/R7 240. Репутацию сломало дополнение Odyssey (19.05.2021) с FPS-режимом и поселениями.
- **Версии/патчи:** После Odyssey 15+ апдейтов (поселения, свет, тени); к 2023–2024 FPS вырос, но паритет с Horizons не достигнут. Утечки памяти и зависимость от скорости ОЗУ.
- **Причина репутации:** реализация (просадки до 15–30 FPS в поселениях даже на GTX 1080 Ti / RTX 3060 Ti; зависимость от CPU/RAM, гонка текстур RAM↔VRAM).
- **Решения:**
  - `+` Сброс папки графических опций + обновление драйверов и XMP профиля ОЗУ.
  - `+` Снижение supersampling до 1.0 и лок FPS.
  - `±` Кастомные конфиги и 3DMigoto-твики шейдеров от сообщества.
  - `−` Отсутствие отдельного конвейера LOD/окклюзии для FPS-режима на старте.
- **Влияние:** оптимизация — добавление FPS-режима к космическому движку требует отдельного LOD/окклюзии; учебник CPU/RAM-горлышка Cobra.
- **DSS:** `hierarchical_lod`, `baked_occlusion_culling`, `cascaded_shadow_maps`, `dynamic_resolution_scaling`.
- **Источники:** Steam (https://store.steampowered.com/app/359320/Elite_Dangerous/), Frontier (https://forums.frontier.co.uk/threads/boost-your-graphics-performance-in-elite-dangerous-odyssey-using-these-simple-tricks.575616/).

### 103. Mafia III: Definitive Edition (2016/2020, Hangar 13 / Illusion Engine)

- **Движок:** Эволюция Illusion Engine для открытого Нью-Бордо.
- **Релиз ПК:** Оригинал 07.10.2016 с локом 30 FPS. Патч с анлоком 30/60/Unlimited через несколько дней после скандала. Definitive Edition (бандл со всеми DLC) 19.05.2020 унаследовала проблемы производительности.
- **Версии/патчи:** Патч 1.01 — выбор 30/60/Unlimited; хотфикс 14.10.2020 — мыльный рендер и стабильность. Отдельной оптимизацией отражений/волюметрики не занимались.
- **Причина репутации:** процесс (лок 30 FPS на ПК в 2016 + плохой скейлинг: отражения и волюметрика убивали FPS даже на GTX 970/i7-4790K, мыльный TAA, оверхед 2K-лаунчера).
- **Решения:**
  - `+` Патч-анлок и связка VSync + Unlimited с лимитом через драйвер.
  - `+` Снижение Reflection Quality и Volumetric Effects до Low в первую очередь.
  - `+` Обход 2K-лаунчера через прямой exe.
  - `±` Отключение Fullscreen Optimizations и ReShade-пресеты сообщества.
- **Влияние:** процесс — классика «30 FPS на ПК в 2016»; пример, как один лок хоронит приём игры.
- **DSS:** `volumetric_half_resolution`, `post_effect_selective`, `cascaded_shadow_maps`, `quality_tier_scalability`.
- **Источники:** Steam News (https://store.steampowered.com/news/app/360430/view/5222443045214885244), Steam Discussions (https://steamcommunity.com/app/360430/discussions/0/343788552542984112?l=russian).

### 104. DARK SOULS III (2016, FromSoftware / собственный)

- **Движок:** Фирменный движок FromSoftware, DirectX 11 на ПК.
- **Релиз ПК:** 11–12.04.2016 одновременно с мировым релизом. По Digital Foundry ПК-версия сразу дефинитивна: 1080p60 против 30–40 FPS на PS4/Xbox One. Остался жёсткий кап 60 FPS без high-refresh.
- **Версии/патчи:** Стартовый патч 1.03 (01.04) и 1.03.1/1.04 (18.04.2016) — баланс и перф; далее балансные Regulation до 1.35 / App 1.15.2 (01.2023) и патч под PS4 Pro.
- **Причина репутации:** реализация (микростаттеры и просадки при варпах, CPU-горлышко draw calls на i3, однопоточная нагрузка, отсутствие borderless).
- **Решения:**
  - `+` Связка i5 + GTX 970 / R9 390 как sweet spot для 1080p60 по DF.
  - `+` Снижение теней и семплирования motion blur в первую очередь.
  - `±` Установка на SSD и перезапуск при просадке VRAM после варпа.
  - `−` Лок 30 FPS на слабых i3/GTX 750 Ti с консольными настройками.
- **Влияние:** оптимизация — реабилитация FromSoftware на ПК после DS1/DS2; стандарт «Souls — 60 FPS на ПК, но с капой и статтером загрузок».
- **DSS:** `pso_precaching_warmup`, `async_loading_pipeline`, `cascaded_shadow_maps`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2016-what-does-it-take-to-run-dark-souls-3-at-1080p60), Fextralife патчи (https://darksouls3.wiki.fextralife.com/Patches).

### 105. Fallout 4 (2015, Bethesda / Creation Engine)

- **Движок:** Creation Engine (форк Gamebryo), DirectX 11, Havok и Scaleform.
- **Релиз ПК:** 10.11.2015 одновременно на ПК и консолях. Хвалили дальность и моддинг, ругали физику на 60 FPS и просадки в центре Бостона. Типичный Bethesda-релиз: большой мир ценой CPU-стабильности.
- **Версии/патчи:** Патчи 1.2–1.10, Survival-режим и High-Resolution Texture Pack. Next-gen апдейт 25.04.2024 — Performance/Quality и ultrawide, но сломал моды; Update 2 (13.05.2024) частично починил.
- **Причина репутации:** реализация (падение FPS и хитчи 100+ мс в Корвеге/Даунтауне из-за draw calls и стриминга; поломки скриптов/физики выше 60 FPS).
- **Решения:**
  - `+` Кап 60 FPS через iPresentInterval для стабильности физики.
  - `+` Снижение дальности теней и отключение Godrays в Бостоне.
  - `+` SSD, Unofficial Patch и прекомбайн-фиксы сообщества.
  - `±` Next-gen Quality при 30/40 FPS вместо рваных 60.
- **Влияние:** процесс — «Creation Engine = моды чинят лучше Bethesda»; аргумент за капремонт движка к Starfield.
- **DSS:** `fixed_timestep_physics`, `baked_occlusion_culling`, `world_partition_streaming`, `async_loading_pipeline`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/377160/Fallout_4/), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2015-fallout-4-performance-analysis), Digital Foundry next-gen (https://www.digitalfoundry.net/articles/digitalfoundry-2024-fallout-4s-next-gen-upgrade-feels-like-a-wasted-opportunity).

---

## Партия 13 (список-3, батч 7: №106–113)

### 106. Kingdom Come: Deliverance (2018, Warhorse / CRYENGINE)

- **Движок:** CRYENGINE.
- **Релиз ПК:** 13.02.2018 на ПК/PS4/Xbox One с Day-1 патчем. Требовательна к GPU/CPU, пресеты Low–Ultra High (Ultra High — задел на будущее железо).
- **Версии/патчи:** Day-1 / Week-1 патч 1.2; хотфикс 1.2.5; 1.5 (05.06.2018); 1.6/1.6.2 (07.2018) и DLC From the Ashes. Фиксы квестов, сохранений, CPU-нагрузки, освещения, стриминга текстур и деспавна.
- **Причина репутации:** реализация (амбициозный open-world от небольшой команды: баги квестов, поп-ин LOD, 20–30 fps и статтеры; на ПК лучше консолей, но без locked 60 на High+).
- **Решения:**
  - `+` Пять пресетов и тонкие настройки дальности/теней/освещения/вегетации.
  - `+` Улучшенный стриминг текстур, uberlod-фиксы и деспавн предметов.
  - `−` Главный/рендер потоки упираются в 100% одного ядра; города просаживают fps.
  - `±` Indoor shadow-casting и full real-time GI только на топ-пресете ценой fps.
- **Влияние:** оптимизация — цена CryEngine-мира без упрощений; практика «ultra для будущих GPU»; наследник Crysis как бенчмарк.
- **DSS:** `world_partition_streaming`, `hierarchical_lod`, `gpu_instancing_vegetation`, `cascaded_shadow_maps`, `agent_update_budget`.
- **Источники:** CryEngine (https://press.cryengine.com/achieved-with-cryengine-kingdom-come-deliverance-launches-today), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2018-kingdom-come-deliverance-on-pc-offers-huge-upgrade-over-console), Steam (https://store.steampowered.com/app/379430/Kingdom_Come_Deliverance/).

### 107. LEGO STAR WARS: The Force Awakens (2016, TT Games / Nu2)

- **Движок:** Nu2.
- **Релиз ПК:** Windows 28.06.2016, OS X от Feral 30.06.2016 (TT Fusion, Warner Bros.). Deluxe Edition, Season Pass и PS-эксклюзивы. Рутинный TT-релиз без технопровала.
- **Версии/патчи:** Номера ПК-патчей — unstated. Зафиксировано: выбор DX9/11 с 32/64-бит exe, настройки PCCONFIG.TXT, Steam Cloud.
- **Причина репутации:** процесс (точечные жалобы: сброс refresh rate к 60 Гц, разрешение/окно, дисбаланс аудио, краши на взрывах).
- **Решения:**
  - `+` Переключатель DX9/DX11 для совместимости и fps.
  - `+` Локальный кооп на 2 игроков и Steam Cloud.
  - `−` Настройки разрешения/частоты иногда не сохраняются без ручной правки pcconfig.txt.
  - `±` PSO-кеширование и прогрев шейдеров — unstated.
- **Влияние:** null как техно-влияние; последний LEGO-релиз для PS3/X360/Wii U и 3DS/Vita.
- **DSS:** `async_loading_pipeline`, `snapshot_slot_saves`, `quality_tier_scalability`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Lego_Star_Wars:_The_Force_Awakens), Wikipedia (https://en.wikipedia.org/wiki/Lego_Star_Wars:_The_Force_Awakens).

### 108. Scrap Mechanic (2016 EA, Axolot / собственный)

- **Движок:** Собственный Axolot; на старте OGRE + Bullet, с Winter Update 0.2.0 — собственный in-house рендер.
- **Релиз ПК:** Ранний доступ 19.01.2016 только с Creative Mode и 100+ деталями. Survival Mode 07.05.2020; полный релиз с Chapter 2 — 24.07.2026.
- **Версии/патчи:** Winter Update 0.2.0 (19.12.2016): новый движок, мердж боксов/цилиндров, меньше collision-проверок, новый particle engine. Ветка 0.4.4–0.4.8 (2020): рейды, рэгдоллы, вода, Beacon.
- **Причина репутации:** функционал (хит песочницы креативных машин с коопом, но долголетнее EA и просадки при больших постройках/рейдах из-за физики и воды).
- **Решения:**
  - `+` Переписанный движок и мердж коллизий боксов/цилиндров.
  - `+` Оптимизация рейдов и рэгдоллов для массовых сцен.
  - `−` Сложные contraptions роняют fps и провоцируют лаги в коопе.
  - `±` Выделенные серверы и тикрейт сети — unstated.
- **Влияние:** контент — пример physics-конструктора в реальном времени; долгий EA-цикл с возвратом в топ Steam после Survival.
- **DSS:** `fixed_timestep_physics`, `multithreaded_physics_jobs`, `broadphase_spatial_partitioning`, `particle_pooling`.
- **Источники:** Steam (https://store.steampowered.com/app/387990/Scrap_Mechanic/), Wikipedia (https://en.wikipedia.org/wiki/Scrap_Mechanic).

### 109. Undertale (2015, Toby Fox / GameMaker: Studio)

- **Движок:** GameMaker: Studio.
- **Релиз ПК:** v1.00 — 15.09.2015 на Windows/macOS в Steam. 2D RPG с room_speed 30 fps и привязкой логики к кадрам. Консольные порты позже потребовали переработки (нет экспорта GameMaker на Nintendo).
- **Версии/патчи:** v1.001 (20.01.2016): диалоги, статы, colorblind-спрайты, фиксы графики; v1.05 (22.08.2017): японский; 1.06–1.08 (02.2018): багфиксы и фикс замедлений на Windows 10.
- **Причина репутации:** функционал (культовый инди-хит: нетехнологичная, но цельная игра).
- **Решения:**
  - `+` Атлас спрайтов и лёгкие комнаты для мгновенной загрузки.
  - `+` Фиксы графики, текстов и Win10-торможений в 1.06–1.08.
  - `−` Логика от room_speed: повышение fps вдвое ускоряет игру без переработки.
  - `±` Динамическое разрешение и апскейл — unstated.
- **Влияние:** оптимизация — пределы GameMaker для портов и частоты кадров; смена языка/движка для Deltarune.
- **DSS:** `sprite_atlas_batching`, `async_loading_pipeline`, `fixed_timestep_physics`.
- **Источники:** Undertale Wiki (https://undertale.wiki/w/Version_differences), Patches (https://www.mobygames.com/game/74938/undertale/patches/).

### 110. Metro: Last Light Redux (2014, 4A Games / 4A Engine)

- **Движок:** 4A Engine.
- **Релиз ПК:** 08.2014 как отдельная игра в Steam, не патч. Включает все DLC Last Light, режимы Survival/Spartan, Ranger Mode, check watch/inventory и full-body анимации. Для Last Light — перенос на обновлённый движок.
- **Версии/патчи:** Отдельные entry, бесплатный апгрейд невозможен (отказ от 32-бит, переработка движка). Владельцам оригинала — скидка 50%. Движок: Global Illumination, тесселяция террейна, оптимизация перфоманса.
- **Причина репутации:** процесс (образцовый Redux для новичков, но спорная ценность для владельцев + DLC; честное объяснение «почему не бесплатный патч»).
- **Решения:**
  - `+` Отказ от 32-бит и консолидация на 64-бит сборке.
  - `+` Global Illumination, тесселяция и сшивка уровней без части загрузок.
  - `−` Нет upgrade-пути патчем и переноса DLC, только повторная покупка.
  - `±` Survival-перебалансировка экономикой вместо нового контента.
- **Влияние:** процесс — кейс честного объяснения платного Redux и раздельных приложений в Steam.
- **DSS:** `lightmap_atlas_baking`, `baked_occlusion_culling`, `volumetric_half_resolution`.
- **Источники:** DSOG (https://www.dsogaming.com/news/4a-games-details-new-4a-engine-features-explains-why-metro-redux-is-not-a-free-upgrade/), Steam (https://store.steampowered.com/app/287390/Metro_Last_Light_Redux/).

### 111. Resident Evil 7 Biohazard (2017, Capcom / RE Engine)

- **Движок:** RE Engine.
- **Релиз ПК:** 24.01.2017 (PS4/Windows/Xbox One; Япония 26.01). Первая полноразмерная игра на RE Engine с видом от первого лица; ставка на хоррор после экшена RE6. Стартовала с Denuvo, взломанной за пять дней.
- **Версии/патчи:** Day-1 патч 1.0.1 (806 МБ); Patch #1 (27.01.2017); Patch #2 (07.02) снял требование SSSE3 для старых CPU; Patch #3 (18.02) — графика/ввод; 06.2022 — бесплатный некстген-патч с ray-tracing и high-framerate.
- **Причина репутации:** функционал (возвращение к хоррору; хвалили RE Engine, атмосферу, пазлы и VR).
- **Решения:**
  - `+` Новый RE Engine с VR-инструментами и детализированными текстурами.
  - `+` Снятие требования SSSE3 и расширение совместимости CPU.
  - `−` Линейный коридорный масштаб и ограниченный бестиарий вместо системной глубины.
  - `±` Denuvo-защита на старте при быстром обходе.
- **Влияние:** контент — запуск линейки RE Engine и VR-подхода Capcom; стандарт детализации для VR.
- **DSS:** `async_loading_pipeline`, `volumetric_half_resolution`, `lightmap_atlas_baking`.
- **Источники:** Wikipedia (https://en.wikipedia.org/wiki/Resident_Evil_7:_Biohazard), DSOG (https://www.dsogaming.com/news/resident-evil-7-new-patch-adds-support-for-older-generation-cpus/), Steam (https://store.steampowered.com/app/418370/Resident_Evil_7_Biohazard/).

### 112. Factorio (2016 EA/2020, Wube / собственный C++)

- **Движок:** Собственный custom-движок на C++.
- **Релиз ПК:** Ранний доступ с 2016; 1.0 — 14.08.2020 (перенесли на 5 недель раньше из-за Cyberpunk 2077). Разработка 8,5 лет; в 0.18 контент готов, для 1.0 добавили Spidertron. В 0.18.28 — нативный Lua-сериализатор: сейв 60-МБ script.dat ускорен с ~285 с до ~2,8 с, загрузка с ~47 с до ~22 с.
- **Версии/патчи:** Ветка 0.18 experimental; 1.0.0 (14.08.2020); план 1.1 — добор фич и ~150 форумных багов без крупного контента.
- **Причина репутации:** реализация (эталон оптимизации для сотен тысяч сущностей; deterministic lockstep без центрального сервера: только действия, все пиры симулируют мир).
- **Решения:**
  - `+` Lockstep с минимумом трафика независимо от числа объектов.
  - `+` Замена Allegro-рендера на собственный код и переход окон/ввода на SDL (план OpenGL 3.2 / DX11).
  - `−` Чистый P2P требует коннектов всех ко всем и NAT-punching.
  - `±` Отказ от сериализации Lua-функций в global ради скорости сейвов ценой поломки части модов.
- **Влияние:** сеть — школа детерминизма для симуляторов; публикация train pathfinding и философии open-source после DLC.
- **DSS:** `deterministic_lockstep`, `headless_dedicated_server`, `tickrate_budgeting`, `broadphase_spatial_partitioning`.
- **Источники:** Factorio FFF-360 (https://factorio.com/blog/post/fff-360), FFF-76 (https://direct.factorio.com/blog/post/fff-76), Version history (https://wiki.factorio.com/Version_history/1.0.0).

### 113. Watch_Dogs 2 (2016, Ubisoft / Disrupt)

- **Движок:** Disrupt.
- **Релиз ПК:** PS4/Xbox One 15.11.2016, Windows задержана до 29.11.2016 ради оптимизации. Апгрейднутый Disrupt под Bay Area с бесшовным онлайном и коопом. Кооп/бесшовный мультиплеер на старте сбоили и включались позже.
- **Версии/патчи:** 1.06.135.3 (03.12.2016): CrossFire, Donut-NPC, краши, matchmaking. Title Update 1.08/1.07.141.6 (13.12): реплей миссий, вторжения, стрельба, кооп, туман Karl по таймеру, CrossFire-перф.
- **Причина репутации:** функционал (шаг вперёд от Watch_Dogs по тону/хакингу/вождению, но ПК-старт с CrossFire, Donut-людьми, детектом сквозь стены и багами онлайна).
- **Решения:**
  - `+` Отложенный ПК-релиз и быстрые хотфиксы стабильности/крашей.
  - `+` Переключаемый туман Karl и правки GPS-трафика/AI.
  - `−` CrossFire и мульти-GPU требовали отдельных фиксов.
  - `±` Seamless-вторжения с кулдаунами и ребалансом частоты вместо отключения.
- **Влияние:** контент — Disrupt как движок плотного города с толпами и хакингом; кейс починки бесшовного онлайна патчами.
- **DSS:** `world_partition_streaming`, `crowd_instancing_impostors`, `hierarchical_lod`, `async_loading_pipeline`.
- **Источники:** Wikipedia (https://en.wikipedia.org/wiki/Watch_Dogs_2), DSOG (https://www.dsogaming.com/news/watch_dogs-2-first-pc-update-is-now-available/).

---

## Партия 14 (список-3, батч 8: №114–121)

### 114. DRAGON BALL XENOVERSE 2 (2016, Dimps / собственный)

- **Движок:** Собственный движок Dimps (название — unstated).
- **Релиз ПК:** Windows в Steam 27.10.2016 (PS4/Xbox One 25.10.2016). Заявлены 60 FPS и хаб Conton City в разы крупнее первой части.
- **Версии/патчи:** Долгая сервисная поддержка с DLC и бесплатными обновлениями; порты PS5/Xbox Series 24.05.2024 как бесплатный апгрейд. Номера промежуточных патчей — unstated.
- **Причина репутации:** функционал (долгоживущий аниме-сервис: 10+ млн копий; стабильный хабовый мультиплеер и кастомизация).
- **Решения:**
  - `±` Хаб Conton City до 300 игроков в инстансе с приоритизацией репликации.
  - `+` Фиксированный 60 FPS за счёт скромных требований DX11.
  - `±` Инстансированные PvE/PvP-миссии из хаба без бесшовного мира.
  - `+` Низкий порог: 2–4 ГБ ОЗУ, GT 650/HD 6570 в минимуме.
- **Влияние:** контент — эталон монетизации Bandai Namco: многолетние DLC-сезоны без смены движка.
- **DSS:** `network_relevancy_priority`, `tickrate_budgeting`, `animation_lod_budget`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/454650/DRAGON_BALL_XENOVERSE_2/), Wikipedia (https://en.wikipedia.org/wiki/Dragon_Ball_Xenoverse_2).

### 115. Bayonetta (2009/2017 ПК, PlatinumGames / собственный)

- **Движок:** Собственный движок PlatinumGames (название — unstated).
- **Релиз ПК:** Порт в Steam 11.04.2017 от SEGA при участии PlatinumGames. Разблокированные разрешения до 4K и 60 FPS.
- **Версии/патчи:** Разовый релиз без DLC. Опции: AA, AF, SSAO, текстуры/тени. Крупные патчи — unstated.
- **Причина репутации:** реализация (образцовый порт каталога SEGA: PC Gamer «This is how you port a classic»).
- **Решения:**
  - `+` Разблокированные разрешения и 60 FPS вместо 60/30 оригинала.
  - `+` Масштабируемые AA/AF/SSAO/тени/текстуры.
  - `+` KB+M, Achievements, Cloud, Trading Cards, Big Picture.
  - `±` Без переработки ассетов: старые модели/ролики на 4K архаичны.
- **Влияние:** контент — открыл волну ПК-портов SEGA/Platinum (Vanquish, NieR:Automata).
- **DSS:** `fixed_timestep_physics`, `animation_compression`, `post_effect_selective`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/460790/Bayonetta/), PlatinumGames (https://www.platinumgames.com/official-blog/article/9263).

### 116. Nioh: Complete Edition (2017, Team Ninja / собственный)

- **Движок:** Собственный движок Team Ninja (название — unstated).
- **Релиз ПК:** Windows в Steam 07.11.2017 (KOEI TECMO). Включает 3 DLC: Dragon of the North, Defiant Honor, Bloodshed's End.
- **Версии/патчи:** Steam-бонус — шлем Dharmachakra Kabuto; детали ПК-патчей — unstated.
- **Причина репутации:** процесс (сложный souls-like порт: DX11, 80 ГБ, бедные настройки графики и KB+M-подсказки на старте).
- **Решения:**
  - `+` Святилища как слоты сохранений/респауна.
  - `+` Миссионная структура вместо открытого мира: меньше стриминга.
  - `−` Ограниченные графические опции и KB+M на старте.
  - `±` Высокие требования к диску/CPU при DX11 без RT/апскейлеров.
- **Влияние:** контент — спрос на souls-like Team Ninja на ПК; база для Nioh 2 Complete Edition.
- **DSS:** `snapshot_slot_saves`, `animation_lod_budget`, `collision_layer_matrix`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/485510/Nioh_Complete_Edition/), KOEI TECMO (https://www.koeitecmoamerica.com/games/nioh-complete-edition/).

### 117. Hello Neighbor (2016 EA/2017, Dynamic Pixels / Unreal Engine 4)

- **Движок:** Unreal Engine 4.
- **Релиз ПК:** Публичные альфы 2016, Early Access по Greenlight; полный релиз Windows/Xbox One 08.12.2017 (tinyBuild; перенос с 29.08).
- **Версии/патчи:** Alpha 1–4 и бета летом 2017; номера текущих патчей — unstated.
- **Причина репутации:** функционал (вирусный хит YouTube с обещанием самообучающегося AI; на релизе — баги, упрощённый AI).
- **Решения:**
  - `±` AI соседа на NavMesh с изучением маршрутов игрока.
  - `+` Маленький дом как плотная navmesh-зона вместо большого мира.
  - `+` UE4-стриминг альфа-билдов для быстрой итерации с комьюнити.
  - `−` Баги физики/сохранений и просадки на релизе.
- **Влияние:** процесс — кейс alpha-маркетинга: хоррор для блогеров важнее техсостояния.
- **DSS:** `navmesh_tiling_streaming`, `time_sliced_pathfinding`, `agent_update_budget`, `baked_occlusion_culling`.
- **Источники:** Steam (https://store.steampowered.com/app/521890/Hello_Neighbor/), Wikipedia (https://en.wikipedia.org/wiki/Hello_Neighbor_(video_game)).

### 118. NieR:Automata (2017, PlatinumGames / собственный)

- **Движок:** Собственный движок PlatinumGames (название — unstated).
- **Релиз ПК:** Steam 17.03.2017 (PS4 07–10.03.2017; Square Enix). Базовый релиз без апскейлеров, 4K — неофициально.
- **Версии/патчи:** Крупный Steam-патч только в 2021; версия BECOME AS GODS 2018/2021. Детали версий — unstated.
- **Причина репутации:** процесс (проблемный ПК-порт: фиксированное разрешение, статтеры катсцен, нужен фанатский FAR-мод; позже Very Positive).
- **Решения:**
  - `+` Комбинация слешера/шутера/RPG-камер в одном пайплайне.
  - `±` Асинхронная подгрузка зон без бесшовного опенворлда.
  - `−` Отсутствие borderless/правильного fullscreen-скейла на старте.
  - `+` Низкие минимальные требования: i3-2100/GTX 770, 4 ГБ ОЗУ.
- **Влияние:** процесс — символ эпохи плохих портов; FAR как стандарт community-фиксов.
- **DSS:** `async_loading_pipeline`, `animation_lod_budget`, `post_effect_selective`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/524220/NieRAutomata/), PlatinumGames (https://www.platinumgames.com/works/nier-automata).

### 119. Dying Light 2 Stay Human (2022, Techland / C-Engine)

- **Движок:** C-Engine (собственный).
- **Релиз ПК:** Windows/PS4/PS5/Xbox 04.02.2022 (в Steam 03.02 из-за часовых поясов). Амбициозный паркур-опенворлд с днём/ночью и коопом; критика сюжета, баги на старте, хвалили паркур/бой и поддержку.
- **Версии/патчи:** Инструмент CityBuilder для сборки города; пострелизные патчи добавили XeSS, FSR 2.0, DLSS 3, улучшили ragdoll. Номера патчей — unstated.
- **Причина репутации:** реализация (собственный C-Engine после Chrome Engine; тяжёлый RT и зависимость от temporal-апскейлеров на старте).
- **Решения:**
  - `+` CityBuilder: сборка зданий из леджей/окон для быстрого редизайна Villedor.
  - `±` Стриминг районов и тайлованный NavMesh для толп днём/ночью.
  - `+` Временный и постоянный слои города для хрупкости цивилизации.
  - `−` Тяжёлый RT и зависимость от апскейлеров на старте.
- **Влияние:** контент — доказательство жизнеспособности C-Engine; Reloaded Edition как модель перезапуска.
- **DSS:** `world_partition_streaming`, `navmesh_tiling_streaming`, `temporal_upscaling`, `dynamic_resolution_scaling`, `crowd_instancing_impostors`.
- **Источники:** Steam (https://store.steampowered.com/app/534380/Dying_Light_2_Stay_Human_Reloaded_Edition/), PCGW (https://www.pcgamingwiki.com/wiki/Dying_Light_2_Stay_Human).

### 120. Little Nightmares (2017, Tarsier / Unreal Engine 4)

- **Движок:** Unreal Engine 4.
- **Релиз ПК:** PS4/Windows/Xbox One 28.04.2017 (Steam 27.04; Bandai Namco). Сингл без DLC в базе.
- **Версии/патчи:** Порты Switch 2018, Stadia 2020, Enhanced Edition 2025 (4K/60/RT). ПК-патчи — unstated.
- **Причина репутации:** функционал (стильный пазл-платформер-хоррор; технически скромный, стабильный UE4-порт).
- **Решения:**
  - `+` Кукольная стилизация и запечённое освещение вместо дорогой GI.
  - `+` Линейное Чрево с запечённой окклюзией и малыми аренами.
  - `+` Сжатая анимация гигантов против крошки Six для масштаба.
  - `±` Фиксированная камера: упрощает батчинг ценой свободы.
- **Влияние:** контент — эталон UE4-хоррора малой команды; формула продолжена в Little Nightmares II.
- **DSS:** `lightmap_atlas_baking`, `baked_occlusion_culling`, `art_direction_stylization`, `animation_compression`.
- **Источники:** Steam (https://store.steampowered.com/app/424840/Little_Nightmares/), Tarsier (https://tarsier.se/games/little-nightmares/).

### 121. HELLDIVERS 2 (2024, Arrowhead / Stingray мод.)

- **Движок:** Autodesk Stingray (Bitsquid), сильно модифицированный; снят с поддержки в 2018.
- **Релиз ПК:** PS5/Steam 08.02.2024 (PlayStation Publishing). Крупнейший ПК-запуск Sony на тот момент (~457 тыс. онлайна).
- **Версии/патчи:** Паритет с современными движками делали без поддержки вендора; пострелиз — патчи серверов, баланса и GameGuard. Номера — unstated.
- **Причина репутации:** функционал (мегахит на abandonware-движке; очереди, краши, споры о нерфах при общем Very Positive).
- **Решения:**
  - `±` Выделенные серверы и релевантность репликации для 4-кооп сессий с friendly fire.
  - `±` Бюджетирование тикрейта и пулинг партиклов/трупов при хаосе взрывов.
  - `−` Client-prediction поверх старого неткода.
  - `+` Свои доработки рендера/онлайна поверх Stingray 1.9 без вендора.
- **Влияние:** процесс — «Ship of Theseus»: мёртвый Stingray доведён до AAA-онлайна своими силами.
- **DSS:** `headless_dedicated_server`, `tickrate_budgeting`, `client_prediction_reconciliation`, `network_relevancy_priority`, `particle_pooling`.
- **Источники:** Steam (https://store.steampowered.com/app/553850/HELLDIVERS_2/), PC Gamer (https://www.pcgamer.com/helldivers-2-engine-bitsquid-autodesk-stingray/).

---

## Партия 15 (список-3, батч 9: №122–129)

### 122. DARK SOULS: REMASTERED (2018, FromSoftware/QLOC / собственный)

- **Движок:** Проприетарный движок FromSoftware; ремастер для ПК/PS4/Xbox One — QLOC.
- **Релиз ПК:** Steam 24.05.2018, заменил снятое Prepare to Die Edition. Цель 1080p/4K при 60 fps вместо 720p/30 оригинала с DSFix. Digital Foundry: «remarkably unambitious», но исправляет базу: произвольное разрешение и стабильные 60 fps.
- **Версии/патчи:** Добавлены TAA/FXAA, Motion Blur, Depth of Field, Ambient Occlusion. Скорость привязана к 60 fps, ниже ~45 — slow-motion (PCGW). Жалобы на читеров и старые баги; точный список патчноутов — unstated.
- **Причина репутации:** процесс (исправление худшего порта FromSoftware: оригинал 2012 — locked 1024x720 и 30 fps без DSFix от Durante).
- **Решения:**
  - `+` Нативный рендер до 4K + анизотропка и TAA вместо инъекции DSFix.
  - `−` Жёсткий кап 60 fps и привязка логики к фреймрейту.
  - `−` Скудный набор настроек без слайдеров, форсируются через драйвер.
  - `±` Сохранение оригинальных ассетов без смены движка на Dark Souls 3.
- **Влияние:** оптимизация — модель минимально-безопасного ремастера: снять CPU/GPU-бутылку Blighttown, не ломая вижн; 60 fps как минимум для переизданий Souls.
- **DSS:** `fixed_timestep_physics`, `quality_tier_scalability`, `post_effect_selective`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2018-dark-souls-remastered-console-pc-face-off), PCGW (https://www.pcgamingwiki.com/wiki/Dark_Souls_Remastered).

### 123. Monster Hunter: World (2018, Capcom / MT Framework)

- **Движок:** MT Framework, сильно модифицированный под бесшовные карты.
- **Релиз ПК:** Steam 09.08.2018, через ~6 месяцев после консолей. Digital Foundry: высокая нагрузка на CPU/GPU, сломанные опции графики и текстуры хуже Xbox One X на старте. Требовал Special K и ручной оптимизации для 1080p60.
- **Версии/патчи:** Iceborne-патч 10.12.01 (01.2020) — аномальная загрузка CPU и сейвы; Denuvo удалён 06.2021 (exe −481 МБ); DX12, FidelityFX CAS/Upscaling к Iceborne.
- **Причина репутации:** реализация (первый бесшовный Monster Hunter без зон-загрузок, но тяжёлый «грязный» порт Capcom).
- **Решения:**
  - `±` Бесшовные биомы с полной загрузкой в RAM и instant fast-travel.
  - `−` Постоянный volumetric-туман на весь кадр + god rays вместо дистанционного фога.
  - `±` Temporal-реконструкция для сглаживания ценой мыла в движении.
  - `−` Расширенные настройки, часть опций без видимой разницы на старте.
- **Влияние:** оптимизация — кейс «MT Framework на пределе»; ускорил переход Capcom на RE Engine для Rise/Wilds.
- **DSS:** `world_partition_streaming`, `volumetric_half_resolution`, `temporal_upscaling`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2018-what-does-it-takes-to-run-monster-hunter-world-pc-at-1080p60), DSOG (https://www.dsogaming.com/news/capcom-has-removed-denuvo-from-monster-hunter-world).

### 124. Black Desert (2014 KR/2017 Steam, Pearl Abyss / собственный)

- **Движок:** Собственный движок Pearl Abyss (Black Desert Engine).
- **Релиз ПК:** Корея 12.2014, NA/EU 03.2016, Steam NA/EU 24.05.2017. Требует сторонний аккаунт и XIGNCODE3. Бесшовный мир, осады, life-системы.
- **Версии/патчи:** Black Desert Remastered 22.08.2018 — визуал/аудио, пост-эффекты YEBIS от Silicon Studio; далее еженедельные патчи 100+ пунктов, классы и регионы.
- **Причина репутации:** реализация (одна из самых требовательных MMO: дальность, физика, массовые PvP-осады; хвалили кастомизацию и ремастер, ругали гринд/монетизацию/просадки в городах).
- **Решения:**
  - `+` Бесшовный мир на собственном стриминге без инстансов зон.
  - `±` Массовые осады/Node War с упором на отрисовку множества персонажей.
  - `+` Пост-пайплайн YEBIS в Remastered для bloom/DOF/тона.
  - `−` Тяжёлые CPU/GPU-требования без честной скалярности для слабых ПК.
- **Влияние:** контент — жизнеспособность собственного MMO-движка против UE/Unity; база для BlackSpace Engine (Crimson Desert).
- **DSS:** `world_partition_streaming`, `crowd_instancing_impostors`, `post_effect_selective`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/582660/Black_Desert), Wikipedia (https://en.wikipedia.org/wiki/Black_Desert_Online).

### 125. Hunt: Showdown 1896 (2019/2024, Crytek / CryEngine)

- **Движок:** CryEngine (на релизе 1896 — CRYENGINE 5.11).
- **Релиз ПК:** Ранний доступ 02.2018, 1.0 — 08.2019. Перезапуск 1896 — 15.08.2024 с картой Mammon's Gulch, прекращением поддержки PS4/Xbox One и free-weekend. Заявлены визуальный апгрейд, аудио и рендер-перф.
- **Версии/патчи:** Патч 4.2 (07.02.2019) — threading, −15% памяти, рост fps на слабом железе; патчноуты 1896 в 3 частях; Update 2.2 evergreen-оптимизации. Часть игроков сообщала о падении fps после 5.11.
- **Причина репутации:** реализация (редкий долгоживущий CryEngine-проект с PvPvE на 12 игроков; «красиво, но CPU-тяжело»: стриминг/фолиадж, VRAM, шейдерная компиляция).
- **Решения:**
  - `±` Стриминг компаундов и фолиаджа с прицелом на NVMe SSD.
  - `+` Переработка threading для снятия сталлов в 4.2.
  - `−` Подъём требований в 1896 ради света/текстур без бесшовного апгрейда для 8 ГБ VRAM.
  - `±` Матч-формат Bounty Hunt/Soul Survivor с высокой ценой кадра в перестрелке.
- **Влияние:** оптимизация — эталон постподдержки CryEngine-сервиса: 6 лет патчей threading/стриминга.
- **DSS:** `async_loading_pipeline`, `multithreaded_physics_jobs`, `client_prediction_reconciliation`, `quality_tier_scalability`.
- **Источники:** Crytek (https://www.crytek.com/news/hunt-showdown-1896-out-now), Crytek perf (https://www.crytek.com/news/hunt-showdown-releases-major-performance-update).

### 126. FINAL FANTASY XII THE ZODIAC AGE (2017/2018 ПК, Square Enix / unstated)

- **Движок:** null/unstated (ремастер PS2-оригинала при участии Virtuos Games).
- **Релиз ПК:** PS4 11.07.2017, Steam 01.02.2018. Впервые 60 fps против 30 на PS4/Pro и 21:9 до 48:9 на трёх мониторах. Digital Foundry/DSOG: неожиданно высокие GPU-требования для PS2-ремастера, слабая AMD на старте.
- **Версии/патчи:** На старте — 60/30-переключатель, Double/Triple Buffering, MSAA до 8x, AO, Water/Shadows, NG+/ускорение/speed-mode. Постпатчи правили мелочи; changelog ПК — unstated.
- **Причина репутации:** процесс (лучший способ играть в FFXII после PS2: 60 fps, мышь с камерой, keyboard prompts; ругали MSAA/AO-цену и мёртвую зону мыши).
- **Решения:**
  - `+` Переработка 30-fps логики/анимаций под 60 fps без поломок.
  - `−` MSAA 8x + полноразрешёнческое AO как главные пожиратели GPU.
  - `±` Опции Half-Resolution AO, DOF, Glare, Soft Particles для скалярности.
  - `+` Ultra-wide и NG+/ускорение/speed-mode из коробки.
- **Влияние:** оптимизация — даже PS2-ремастер требует честного performance-бюджета пост-эффектов; референс хорошего FF-порта до FFXV.
- **DSS:** `fixed_timestep_physics`, `post_effect_selective`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2018-final-fantasy-12-pc-analysis), DSOG (https://www.dsogaming.com/pc-performance-analyses/final-fantasy-xii-the-zodiac-age-pc-performance-analysis), Virtuos (https://www.virtuosgames.com/projects/final-fantasy-xii-the-zodiac-age).

### 127. Devil May Cry 5 (2019, Capcom / RE Engine)

- **Движок:** RE Engine (Reach for the moon).
- **Релиз ПК:** Одновременно PS4/Xbox One/Steam 08.03.2019. Digital Foundry/DSOG: образцовый RE Engine-порт: лёгкий CPU-след, упор в GPU, DX11/DX12 и interlace для слабых карт. Denuvo давал хит только в CPU-bound 480p-тестах.
- **Версии/патчи:** Bloody Palace на 101 этаж (01.04.2019); Vergil как DLC (12.2020) вместе с Special Edition-логикой; удаление Denuvo дало прирост в CPU-лимитах и загрузках.
- **Причина репутации:** реализация (контраст с MHW того же издателя: фотоскан до ~190k полигонов, PBR-кожа, 60/120+ fps на среднем железе).
- **Решения:**
  - `+` Лёгкие CPU-системы + масштабирование до высоких fps на многолетних CPU.
  - `+` Фотореалистичные ассеты и cloth/skin-шейдинг при бесшовных миссиях.
  - `−` Раздельные меню-апгрейды через загрузки вместо in-world UI.
  - `±` Пресеты, DX11/DX12 и Resolution Scaling без явного dynamic-res.
- **Влияние:** контент — RE Engine как эталон Capcom-оптимизации после RE7/RE2; Denuvo-тест DF как методология замеров DRM.
- **DSS:** `quality_tier_scalability`, `post_effect_selective`, `async_loading_pipeline`, `animation_lod_budget`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitafoundry-2019-devil-may-cry-5-tech-analysis-all-consoles-tested), DSOG (https://www.dsogaming.com/pc-performance-analyses/devil-may-cry-5-pc-performance-analysis/).

### 128. SUPERHOT VR (2016/2017, SUPERHOT Team / Unity 5)

- **Движок:** Unity 5.
- **Релиз ПК:** Oculus Rift-эксклюзив 05–06.12.2016 вместе с Oculus Touch при поддержке Oculus; Steam для Vive 25.05.2017; PS VR 07.2017. Не порт, а rebuilt-версия под room-scale и hand-tracking.
- **Версии/патчи:** Базовый билд переносили на Quest в 2019 почти без потерь кроме света/загрузок. Список ПК-патчей — unstated; требует VR-шлем.
- **Причина репутации:** функционал (главный VR-демо-тайтл: «time moves only when you move» идеально лёг на room-scale; десятки VR-GOTY).
- **Решения:**
  - `+` Минималистичная бело-красная стилизация вместо тяжёлых шейдеров.
  - `+` Привязка времени к движению тела/головы для комфорта и пазл-шутера.
  - `+` Малые арены-комнаты с жёстким дизайном под standing play-area.
  - `±` Отсутствие плоского режима, только VR.
- **Влияние:** контент — art-direction важнее полигонов для VR-перфоманса и комфорта; wire-aware дизайн.
- **DSS:** `art_direction_stylization`, `fixed_timestep_physics`, `baked_occlusion_culling`.
- **Источники:** Steam (https://store.steampowered.com/app/617830/SUPERHOT_VR), PCGW (https://www.pcgamingwiki.com/wiki/Superhot_VR).

### 129. Wolfenstein II: The New Colossus (2017, MachineGames / id Tech 6)

- **Движок:** id Tech 6.
- **Релиз ПК:** Мировой релиз 27.10.2017, ПК — только Vulkan без OpenGL-фолбэка. DSOG: одна из самых оптимизированных в 2017: 60+ fps даже на dual-core-симуляции, RX 580 на уровне GTX 980 Ti. На старте краши/глитчи у части NVIDIA без Game-Ready драйвера.
- **Версии/патчи:** Day-one и ранние хотфиксы стабильности Vulkan; настройки: Lights/Shadows/Reflections/Decals, Deferred Rendering, GPU Culling, Resolution Scaler, TAA/FXAA/SMAA/TSSAA, FOV 70–120.
- **Причина репутации:** реализация (контраст с id Tech 5: полностью динамическое освещение, GPU-партиклы, uncapped fps, скейлинг за 4 потока).
- **Решения:**
  - `±` Только Vulkan с тонкой настройкой под GCN/Vega.
  - `+` Deferred Rendering + GPU Culling как переключаемые опции.
  - `+` GPU-партиклы и динамический свет/тени.
  - `±` Resolution Scaler и 6 пресетов (слабая разница Low–Ultra в fps).
- **Влияние:** контент — первый Vulkan-only AAA, закрепивший Vulkan как путь к высокому fps и multicore-скейлингу.
- **DSS:** `deferred_forward_plus_choice`, `dynamic_resolution_scaling`, `gpu_particle_simulation`, `multithreaded_physics_jobs`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2017-how-wolfenstein-2-scales-across-the-console-power-ladder), DSOG (https://www.dsogaming.com/pc-performance-analyses/wolfenstein-ii-new-colossus-pc-performance-analysis).

---

## Партия 16 (список-3, батч 10: №130–137)

### 130. FINAL FANTASY XV WINDOWS EDITION (2018, Square Enix / Luminous Engine)

- **Движок:** Luminous Studio Engine.
- **Релиз ПК:** Steam 06.03.2018 после бенчмарка 02.2018. Включал весь консольный контент с DLC Royal Pack, режим от первого лица, произвольные разрешения и ultra-wide. Отдельно бесплатный High-Resolution Pack с 4K-текстурами.
- **Версии/патчи:** Бенчмарк 02.2018; релиз 03.2018 с улучшением GameWorks и LOD; DLSS-бенчмарк 11.2018; DLSS-beta в игре 12.2018 (Game Ready 417.35).
- **Причина репутации:** реализация (очень требовательная к GPU; красивая картинка, но высокая цена в fps, слабая AMD в бенчмарке, дорогие GameWorks).
- **Решения:**
  - `+` Опциональный 4K High-Res Pack отдельным DLC: качество без форсирования для всех.
  - `±` Переключаемые NVIDIA GameWorks: TurfEffects, VXAO, ShadowWorks.
  - `+` Произвольные разрешения, ultra-wide, до 120 fps и эксклюзивный fullscreen вместо borderless бенчмарка.
  - `±` DLSS 1.0 beta для 4K60 на RTX 2080 Ti (ранний neural-апскейл с мылом).
- **Влияние:** контент — один из первых публичных кейсов DLSS 1.0 и цены GameWorks; эталон требовательного открытого мира 2018 для тестов GPU.
- **DSS:** `temporal_upscaling`, `quality_tier_scalability`, `gpu_instancing_vegetation`, `cascaded_shadow_maps`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2018-final-fantasy-15-windows-edition-pc-analysis), NVIDIA DLSS (https://www.nvidia.com/en-us/geforce/news/final-fantasy-xv-windows-edition-geforce-rtx-dlss-benchmark/), Steam (https://store.steampowered.com/app/637650/FINAL_FANTASY_XV_WINDOWS_EDITION/).

### 131. Farming Simulator 19 (2018, GIANTS / GIANTS Engine 8)

- **Движок:** GIANTS Engine 8.
- **Релиз ПК:** Steam 19–20.11.2018. Переработка движка с PBR-освещением и крупнейшим парком техники, впервые с John Deere. Минимальные требования низкие: i3-2100T / FX-4100, GTX 650 / HD 7770, DX11.
- **Версии/патчи:** Детали perf-патчей — unstated (в проверенных выдачах не найдены).
- **Причина репутации:** функционал (нет репутации провала оптимизации; Very Positive 93%; критика — эволюционность, та же физика после FS17).
- **Решения:**
  - `+` DX11 как первичный API + низкие минимальные требования.
  - `+` Переработанное освещение: солнце и фары с материалами, тени и отражения металлов.
  - `+` Три открытые карты + мультиплеер до 16 игроков с сохранением масштабируемости.
  - `±` Встроенный ландшафтный инструмент и моды: долголетие ценой разброса качества модов.
- **Влияние:** контент — хорошо масштабируемый симулятор для слабого железа; моды как основа серии.
- **DSS:** `quality_tier_scalability`, `cascaded_shadow_maps`, `gpu_instancing_vegetation`, `headless_dedicated_server`.
- **Источники:** Steam (https://store.steampowered.com/app/787860/Farming_Simulator_19/), PCGW Engine (https://www.pcgamingwiki.com/wiki/Engine:GIANTS_Engine_8).

### 132. SCUM (2018 EA, Gamepires / Unreal Engine 4)

- **Движок:** Unreal Engine 4.
- **Релиз ПК:** Ранний доступ 29.08.2018; 1.0 — 17.06.2025 после ~7 лет EA. Карта 225 км² с биомами, серверы 64–128 игроков, глубокий метаболизм и крафт.
- **Версии/патчи:** 1.0 с переработанным миром/текстурами/оружием и оптимизациями кода; хотфиксы 1.0.0.1, 1.0.1.x и ветка Into the Wild 1.3.x (2025–2026) с фиксами крашей/перф.
- **Причина репутации:** процесс (долгая EA: статтеры, краши клиента/сервера, десинк и rubber-banding пассажиров; маркетинг 1.0 обещал рефакторинг, хотфиксы продолжили править перф).
- **Решения:**
  - `±` Полная перестройка мира и графического пасса к 1.0.
  - `+` Выделенные серверы + настройки популяций/MaxPlayers для бюджетирования.
  - `+` NVIDIA DLSS, FrameGen, Reflex, Streamline для апскейла и латентности.
  - `±` BattlEye + EOS-сессии для античита ценой оверхеда.
- **Влияние:** сеть — кейс долгого EA-выживания на UE4: серверный бюджет популяций и сетевой код важнее графики.
- **DSS:** `world_partition_streaming`, `headless_dedicated_server`, `network_relevancy_priority`, `tickrate_budgeting`, `temporal_upscaling`, `crowd_instancing_impostors`.
- **Источники:** SteamDB (https://steamdb.info/app/513710/patchnotes), G-Portal (https://www.g-portal.com/en/news/scum-10-release-en).

### 133. Sekiro: Shadows Die Twice (2019, FromSoftware / собственный)

- **Движок:** Проприетарный движок FromSoftware (эволюция Dark Souls 3).
- **Релиз ПК:** 21–22.03.2019. Лок 60 fps, GTX 1060 / RX 580 тянут 1080p60 на максимуме и близко к 1440p60; RTX 2080 Ti — 4K60 без просадок (DF/DSOG).
- **Версии/патчи:** Значимых perf-патчей движка — unstated; разблокировка выше 60 fps — только модом.
- **Причина репутации:** реализация (лучший ПК-порт FromSoftware на тот момент: нетребовательность, чистое TAA, без крупных статтеров; бедные опции, нет ultra-wide/FOV).
- **Решения:**
  - `+` Temporal super-sampling AA вместо шумного AA Bloodborne/DS3.
  - `+` Жёсткий лок 60 fps + лёгкая нагрузка на GPU: стабильность парирования.
  - `+` Детальные пресеты: тени, освещение, эффекты, volumetrics, отражения, вода, шейдеры.
  - `+` Быстрый стриминг мира под крюк-кошку и вертикальность с минимумом pop-in.
- **Влияние:** контент — контраст с консолями с неровным fps; отзывчивость важнее фотореализма для action-игры.
- **DSS:** `temporal_upscaling`, `quality_tier_scalability`, `hierarchical_lod`, `async_loading_pipeline`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2019-sekiro-shadows-die-twice-pc-performance-analysis), DSOG (https://www.dsogaming.com/pc-performance-analyses/sekiro-shadows-die-twice-pc-performance-analysis/).

### 134. Subnautica: Below Zero (2019 EA/2021, Unknown Worlds / Unity 2019)

- **Движок:** Unity 2019 (сборка 2019.4.36f1 по PCGW).
- **Релиз ПК:** Ранний доступ 30.01.2019; полный релиз 14.05.2021 (ПК/Mac/консоли). Акцент на сюжет и арктический Sector Zero вместо тропиков.
- **Версии/патчи:** EA1–EA13 (Seatruck, Snowfox, Spy Pengling, Arctic Living, Ice Worm, Deep Dive, Frostbite); микро-апдейт 05.2019 — world-streaming улучшения Glacial Basin/Twisty Bridges; финальный релиз + языковые патчи.
- **Причина репутации:** реализация (доводка Unity-стриминга через длинный EA; сиквел стабильнее оригинала на 1.0).
- **Решения:**
  - `+` Итеративные world-streaming фиксы в EA для подгрузок.
  - `+` Опция качества погоды и масштабируемые настройки Unity.
  - `±` Меньшая карта Sector Zero с сушей: предсказуемее для стриминга, чем океан.
  - `+` Стилизованный арт вместо фотореализма: дешевле для GPU.
- **Влияние:** оптимизация — доводка Unity-стриминга через EA; сиквел стабильнее оригинала.
- **DSS:** `world_partition_streaming`, `async_loading_pipeline`, `quality_tier_scalability`, `art_direction_stylization`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Subnautica:_Below_Zero).

### 135. King of Retail (2019 EA/2022, Freaking Games / Unreal Engine)

- **Движок:** Unreal Engine (детект SteamDB: Unreal + PhysX/APEX/NvCloth).
- **Релиз ПК:** Ранний доступ 26.03.2019; полный релиз 14.09.2022 (Iceberg Interactive). Менеджмент магазинов: персонал, витрины, реклама, сеть.
- **Версии/патчи:** Множественные EA-обновления и rework перед 1.0; детали perf-патчей — unstated.
- **Причина репутации:** процесс (нишевый лёгкий сим без fps-скандала, Very Positive).
- **Решения:**
  - `+` Камерный масштаб одного магазина: мало draw calls и физики.
  - `+` UE-рендер интерьеров с кастомизацией без открытого мира.
  - `+` Симуляция покупателей/сотрудников малыми толпами вместо городской толпы.
  - `±` Фокус на UI/менеджмент-логике вместо эффектов: идёт на слабом железе.
- **Влияние:** null как техно-влияние; типовой UE-инди менеджмент.
- **DSS:** `crowd_instancing_impostors`, `agent_update_budget`, `quality_tier_scalability`, `art_direction_stylization`.
- **Источники:** Steam (https://store.steampowered.com/app/968250/King_of_Retail/), SteamDB (https://steamdb.info/app/968250/info/).

### 136. Granblue Fantasy: Relink (2024, Cygames / собственный)

- **Движок:** Собственный внутренний движок Cygames (наследник наработок PlatinumGames; Unreal в кредитах/файлах нет).
- **Релиз ПК:** 01.02.2024 на PS5/PS4/Steam. На ПК анкап fps, 60–120 fps на RX 6600 — RTX 4070 в 1440p. Опций мало, DLSS на старте нет, ultra-wide нет.
- **Версии/патчи:** Perf-патчи — unstated в проверенных источниках.
- **Причина репутации:** функционал (плавный бой и почти железные 60 fps в perf-режиме PS5 1080p и лёгкий 120 fps на сильном ПК; ругали скудные настройки и 30 fps quality).
- **Решения:**
  - `+` Аниме-стилизация: плоское shading, штриховка, рисованные облака — дёшево и чётко.
  - `±` Разделение perf 1080p60 и quality 4K30 на PS5 вместо динамического разрешения.
  - `+` TAA для чистых кромок персонажей при низкой цене.
  - `+` Плотные эффекты Link Attacks/Skybound Arts с сохранением фреймпейса в perf-режиме.
- **Влияние:** контент — stylization + лок 60 fps важнее разрешения для экшен-RPG; кросс-ген без UE может быть стабильнее.
- **DSS:** `art_direction_stylization`, `temporal_upscaling`, `post_effect_selective`, `animation_compression`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2024-granblue-fantasy-relink-is-a-striking-fantasy-rpg).

### 137. Zup! F (2019, Quiet River / Clickteam Fusion 2.5)

- **Движок:** Clickteam Fusion 2.5 (указано в Steam: powered by Clickteam Fusion 2.5).
- **Релиз ПК:** Steam 11.12.2019; серия Zup! с 04.10.2016. Минималистичная 2D физическая головоломка со взрывами, 60 уровней, цель — удержать синий шар 3 секунды.
- **Версии/патчи:** null/unstated.
- **Причина репутации:** функционал (Overwhelmingly Positive 96%: идёт везде, mouse-only, короткая).
- **Решения:**
  - `+` Минималистичный 2D-скоп: один экран, мало объектов.
  - `+` Готовый 2D-рантайм Clickteam Fusion вместо тяжёлого движка.
  - `+` Короткие уровни с мгновенной перезагрузкой без стриминга.
  - `+` Лёгкие Steam-фичи: ачивки, карточки, облако без влияния на fps.
- **Влияние:** null как техно-влияние.
- **DSS:** `fixed_timestep_physics`, `sprite_atlas_batching`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/601220/Zup_F/), Steam Zup! (https://store.steampowered.com/app/533300/Zup/).

---

## Партия 17 (список-3, батч 11: №138–145)

### 138. Cities: Skylines II (2023, Colossal Order / Unity)

- **Движок:** Unity (SteamDB Technologies: Unity Engine).
- **Релиз ПК:** Windows 24.10.2023. Пик >100 тыс. concurrent в Steam, оценка Mixed ~53% из-за производительности. Консольные версии задержаны, ПК остался основной платформой.
- **Версии/патчи:** 1.0.11f1 — первый performance-патч; 1.0.12f1 — свет и pathfinding; 1.1.0f1 Modding Wavelet — LOD и симуляция трафика; City Corner #4 — разбор GPU/CPU и бенчмарк-тул.
- **Причина репутации:** реализация (провал CPU/GPU-оптимизации градостроителя: низкий FPS даже на high-end, избыточные полигоны, дорогой pathfinding при росте города).
- **Решения:**
  - `±` Улучшенные LOD-модели и эффективность теней для снижения треугольников.
  - `±` Переработка симуляции воды и генерации геометрии террейна за кадром.
  - `+` Умный pathfinding, фикс застревания NPC, лимит велосипедов.
  - `±` Бенчмарк-инструмент и работа с Unity для сбора данных по железу.
- **Влияние:** оптимизация — «ничего нельзя предвычислить в динамическом городе»: урок CPU-симуляции, LOD-дисциплины и честных требований.
- **DSS:** `hierarchical_lod`, `time_sliced_pathfinding`, `agent_update_budget`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/949230/Cities_Skylines_II/), PC Gamer (https://www.pcgamer.com/a-tech-analysis-of-cities-skylines-2-proves-its-rendering-way-too-many-polygons-making-cyberpunk-2077-look-like-minecraft-in-comparison/), SteamDB (https://steamdb.info/app/949230/patchnotes/).

### 139. Resident Evil 3 Remake (2020, Capcom / RE Engine)

- **Движок:** RE Engine (DX11 и DX12 на ПК).
- **Релиз ПК:** 03.04.2020. DSOG/TechPowerUp: отличная масштабируемость на слабых и средних GPU. Высокое качество персонажей, взрывов и volumetric lighting при шумных screen-space отражениях.
- **Версии/патчи:** Крупные ПК-патчи баланса — unstated; current-gen апгрейд 2022 для RE2/RE3/RE7 — checkerboard 4K, RT-reflections/GI, 120Hz на PS5/Xbox Series.
- **Причина репутации:** реализация (образцовая масштабируемость RE Engine + дилемма DX11 vs DX12 в зависимости от CPU).
- **Решения:**
  - `+` Два API: DX11 для CPU с <6 потоков, DX12 для CPU с >6 потоков.
  - `+` Снижение Volumetric Lighting как главной точки затрат.
  - `±` Half-rate 30fps анимации дальних зомби (снимается модом).
  - `−` Предупреждение о завышенных требованиях VRAM в меню (фактически ниже).
- **Влияние:** оптимизация — жизнеспособность dual-API стратегии и важность volumetric-настроек; репутация RE Engine как эффективного ПК-движка.
- **DSS:** `animation_lod_budget`, `volumetric_half_resolution`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/952060/RESIDENT_EVIL_3/), DSOG (https://www.dsogaming.com/pc-performance-analyses/resident-evil-3-remake-pc-performance-analysis/), PCGW (https://www.pcgamingwiki.com/wiki/RE3R).

### 140. Mortal Kombat 11 (2019, NetherRealm / Unreal Engine 3 мод.)

- **Движок:** Custom Unreal Engine 3; ПК-порт — QLOC.
- **Релиз ПК:** 04.2019. Бои в 60fps даже на dual-core и RX580 в 1080p/Ultra. Критика: 30fps-кап меню, Krypt, Fatal Blow/Fatality/катсцен, нет DSR на старте.
- **Версии/патчи:** 05.2019 — официальный 60fps-патч (меню/катсцены/Krypt); далее синхронизация с консольной и фиксы десинков онлайна.
- **Причина репутации:** реализация (отличное ядро 60fps при «неоптимизированном» Krypt и спорном 30fps-капе кинематографики).
- **Решения:**
  - `±` Фиксированные 60fps для боёв, 30fps для Krypt/фаталити/катсцен как бюджет стабильности.
  - `+` Dynamic Resolution Scaling на консолях (PS4 1080p, Pro до 1440p, Xbox One 900–972p).
  - `+` Официальный тумблер 60fps для меню/Krypt после модов сообщества.
  - `−` Ограниченные настройки без DSR на старте, 4K только через разрешение десктопа.
- **Влияние:** оптимизация — цена 30fps-капа для восприятия на ПК; польза DRS-масштабируемости от Switch до 4K.
- **DSS:** `deterministic_lockstep`, `dynamic_resolution_scaling`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/976310/Mortal_Kombat_11/), DSOG (https://www.dsogaming.com/pc-performance-analyses/mortal-kombat-11-pc-performance-analysis), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2019-mortal-kombat-11-tech-analysis).

### 141. Halo: The Master Chief Collection (2019 ПК, 343 Industries / legacy)

- **Движок:** null — сборник на разных legacy-движках оригиналов; ПК-порты при участии Splash Damage / Ruffian.
- **Релиз ПК:** Reach 03.12.2019 в Steam/Windows Store, №1 топа продаж Steam; далее CE Anniversary, Halo 2 Anniversary, Halo 3, ODST, Halo 4. Стартовые жалобы: краши, звук, >60fps-анимации.
- **Версии/патчи:** Сезоны 1–8 (2019–2021): фиксы аудио Reach, FOV-слайдер, enhanced draw distance, интерполяция кадров Halo 3, кроссплей/input-based MM в 2020.
- **Причина репутации:** процесс (долгожданное возвращение Halo на ПК с неровным качеством: от проблемного Reach до лучшего Halo 3).
- **Решения:**
  - `+` Enhanced Graphics: дальность статики/динамики, трупов, травы + Performance-режим.
  - `+` Frame-rate интерполяция в Halo 3 (анимации >60fps, сломанные в Reach).
  - `+` Фикс приглушённого аудио Reach, обновление текстур оружия CE.
  - `−` Нет motion blur Reach, низкий AF, статтер камеры катсцен.
- **Влияние:** процесс — стандарт итеративного доведения коллекции: каждый следующий порт компетентнее; уроки интерполяции и аудио переносятся назад.
- **DSS:** `hierarchical_lod`, `tickrate_budgeting`, `headless_dedicated_server`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/976730/Halo_The_Master_Chief_Collection/), Digital Foundry Reach (https://www.digitalfoundry.net/articles/digitalfoundry-2019-halo-reach-master-chief-collection-analysis), Digital Foundry Halo 3 (https://www.digitalfoundry.net/articles/digitalfoundry-2020-halo-3-master-chief-collection-tech-review).

### 142. Hogwarts Legacy (2023, Avalanche / Unreal Engine 4)

- **Движок:** Unreal Engine 4.
- **Релиз ПК:** 10.02.2023 (Steam/Epic). Открытый мир Хогвартса/Хогсмида с тяжёлым RT. Массовые жалобы: traversal-статтеры, просадки в Хогсмиде, VRAM-аппетит, долгая компиляция шейдеров даже на 13900K+4090.
- **Версии/патчи:** Патч 14.02.2023: фикс RTAO хуже SSAO, дефолт Medium, DLSS Frame Generation без Super Resolution, shader compilation optimization, фикс memory leak HL-313; traversal-статтеры по DSOG не исправлены.
- **Причина репутации:** реализация (символ UE4-статтера 2023: шейдерный и траверсал-статтер + прожорливый RT).
- **Решения:**
  - `±` Предкомпиляция шейдеров при первом запуске и оптимизация compilation в патче.
  - `+` DLSS/FSR 2 + Frame Generation для среднего FPS.
  - `+` Отключение/снижение RT Reflections/Shadows/AO как главный способ убрать статтер.
  - `−` Потоковая подгрузка мира без достаточного префетча: хитчи при траверсе.
- **Влияние:** оптимизация — требование PSO-precache и осторожного RT по умолчанию; Engine.ini-твики как массовый ответ.
- **DSS:** `world_partition_streaming`, `pso_precaching_warmup`, `temporal_upscaling`, `hardware_raytraced_gi`, `crowd_instancing_impostors`.
- **Источники:** Steam (https://store.steampowered.com/app/990080/Hogwarts_Legacy/), DSOG (https://www.dsogaming.com/patches/first-hogwarts-legacy-pc-update-released-full-patch-notes-revealed/), PCGW (https://www.pcgamingwiki.com/wiki/Hogwarts_Legacy).

### 143. Marvel's Avengers (2020, Crystal Dynamics / Foundation; снята с продажи)

- **Движок:** Foundation; ПК-версия — Nixxes Software.
- **Релиз ПК:** 04.09.2020. Лёгкие требования к CPU (i7-4930K ~73fps среднее 1080p/Ultra), но тяжёлые к GPU и VRAM. DSOG: framepacing-проблемы и плохая масштабируемость Medium–Ultra. Снята с продажи 30.09.2023.
- **Версии/патчи:** 2.7 — последний контент (Winter Soldier); 2.8 (31.03.2023) — финальный баланс, отключение Credits, вся косметика бесплатно; 30.09.2023 — конец поддержки.
- **Причина репутации:** процесс (провал live-service: баги, нехватка контента, низкая масштабируемость; невозможность 4K60 даже на RTX 2080 Ti в Low).
- **Решения:**
  - `±` Обильные настройки Textures/Shadows/DoF/LOD/AO/Volumetrics + HD-пак.
  - `+` Позже добавленные DLSS/FSR для 4K.
  - `−` Разделение Ultra 10.5GB vs High 8GB VRAM как костыль вместо стриминга.
  - `−` Малая дельта Medium–Ultra при сохранении низкого FPS.
- **Влияние:** процесс — учебник конца games-as-service: delisting по лицензиям, сохранение сингла/коопа, раздача косметики как прощальный жест.
- **DSS:** `virtual_texturing`, `temporal_upscaling`, `async_loading_pipeline`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/997070/Marvels_Avengers__The_Definitive_Edition/), DSOG (https://www.dsogaming.com/pc-performance-analyses/marvels-avengers-pc-performance-analysis/), PCGW (https://www.pcgamingwiki.com/wiki/Marvel%27s_Avengers).

### 144. The Medium (2021, Bloober Team / Unreal Engine 4)

- **Движок:** Unreal Engine 4; фиксированная камера, рендер двух миров одновременно.
- **Релиз ПК:** 28.01.2021. Треть игры — split-reality dual-viewport, удваивающая нагрузку на GPU. DSOG: 16fps в 1440p/High/RT Ultra + DLSS Quality; DF: невозможность стабильных 1080p60 даже на RTX 3090 с DLSS.
- **Версии/патчи:** Опции RT On/Ultra и DLSS Quality/Balanced/Performance на старте; крупные perf-патчи — unstated.
- **Причина репутации:** реализация (цена dual-reality: 100+fps в single-view падают до <30fps в dual-view + микростаттер).
- **Решения:**
  - `±` RT On только для single-reality, Ultra — для single+split (AO, reflections, transparent).
  - `±` DLSS как обязательный апскейл (до +100% по Nvidia, но слаб в split-screen).
  - `−` Отсутствие DRS на ПК при радикальных сдвигах разрешения на консолях.
  - `+` Фиксированные ракурсы для дешёвых raster-теней и контактных теней UE4 вместо RT-теней.
- **Влияние:** оптимизация — необходимость DRS и гранулярных RT-настроек для dual-viewport; эталон вариативной нагрузки контента.
- **DSS:** `temporal_upscaling`, `hardware_raytraced_gi`, `dynamic_resolution_scaling`.
- **Источники:** Steam (https://store.steampowered.com/app/1293160/The_Medium/), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2021-the-medium-pc-tech-review), DSOG (https://www.dsogaming.com/pc-performance-analyses/the-medium-ray-tracing-dlss-benchmarks/).

### 145. Timberborn (2021 EA, Mechanistry / Unity URP)

- **Движок:** Unity, URP (UnityURP SDK по SteamDB).
- **Релиз ПК:** Early Access 15.09.2021 (Steam/GOG/Epic); 1.0 — 12.03.2026. Семь крупных EA-апдейтов, >1 млн копий, Overwhelmingly Positive ~94–95%, Steam Deck Playable.
- **Версии/патчи:** Update 1 — фракции/здания; Update 2 — боты/терраформинг; Update 3 — склады; Update 4 — еда/монументы; Update 5 — badwater/badtides; Update 6 — 3D water physics overhaul (sluices/pumps); 1.0 — автоматизация, карты Oasis/Pressure, ачивки; 1.1 — Unity 6000.5.
- **Причина репутации:** функционал (положительный антипод скандалам: итерация с сообществом, вертикальная архитектура, честная симуляция воды).
- **Решения:**
  - `+` 3D-симуляция воды с давлением, испарением и потоком для плотин/шлюзов.
  - `+` Вертикальное строительство на платформах/лестницах для экономии места.
  - `+` Автоматизация на сенсорах/реле/таймерах для автономных поселений.
  - `−` Сброс сейвов при смене склада в Update 3 как цена рефакторинга.
- **Влияние:** контент — сила focused-симуляции на Unity для инди-градстроя: вода как геймплей, а не декор.
- **DSS:** `gerstner_fft_water`, `fixed_timestep_physics`, `time_sliced_pathfinding`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/1062090/Timberborn/), Steam News (https://store.steampowered.com/news/app/1062090/view/2904248558369348496).

---

## Партия 18 (список-3, батч 12: №146–153)

### 146. ONE PIECE ODYSSEY (2023, ILCA / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (DirectX 11; точный билд — unstated).
- **Релиз ПК:** Steam 12.01.2023 одновременно с PS4/PS5/Xbox Series. Минимум i5-6600 / Ryzen 5 2400G, GTX 780 / R9 290X; рекомендовано i5-8400 / Ryzen 3 3100, GTX 1060 / RX 590; 35 ГБ.
- **Версии/патчи:** Deluxe Edition и DLC. Номера ПК-патчей — unstated.
- **Причина репутации:** процесс (среднебюджетная JRPG без скандалов; стабильный, но не витринный UE4-порт, Very Positive).
- **Решения:**
  - `+` Коридорно-зональные локации с фиксированными переходами вместо открытого мира.
  - `+` Пошаговая боёвка без real-time физики и толп: минимум тик/animation-бюджетов.
  - `±` Пресеты Low/High с таргетом 1080p/60 и оговоркой просадок в насыщенных сценах.
  - `±` Ставка на baked-свет без RT/апскейлеров: стабильность ценой потолка.
- **Влияние:** null как технический ориентир; пример экономичной UE4-JRPG.
- **DSS:** `hierarchical_lod`, `lightmap_atlas_baking`, `async_loading_pipeline`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/814000/ONE_PIECE_ODYSSEY/), Bandai Namco (https://www.bandainamcoent.com/news/one-piece-odyssey-global-launch-pc-consoles).

### 147. Mortal Shell (2020, Cold Symmetry / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (Cold Symmetry, Playstack).
- **Релиз ПК:** Первично 18.08.2020 (EGS-эксклюзив на год); в Steam 18.08.2021 одновременно с DLC The Virtuous Cycle. Минимум GTX 970 / R9 290, рекомендовано GTX 1070 / RX Vega 56; 12 ГБ.
- **Версии/патчи:** Steam-версия соответствует Enhanced-изданию; DLC The Virtuous Cycle. Номера хотфиксов — unstated.
- **Причина репутации:** функционал (инди-soulslike малой команды; плотность и арт при малых ресурсах; Mixed 69% EN).
- **Решения:**
  - `+` Компактные связанные локации Fallgrim вместо открытого мира.
  - `+` Механика Harden вместо сложного ragdoll/контактного слоя.
  - `±` Ограниченный бестиарий и дуэльные арены: экономия animation/VFX-пулов.
  - `−` UE4-дефолтный пайплайн без RT/апскейлеров: низкая цена входа, плоский запас на high-end.
- **Влияние:** null; локальный пример бюджетной souls-формулы на UE4.
- **DSS:** `hierarchical_lod`, `lightmap_atlas_baking`, `cascaded_shadow_maps`, `pso_precaching_warmup`.
- **Источники:** Steam (https://store.steampowered.com/app/1110910/Mortal_Shell/), SteamDB (https://steamdb.info/app/1110910/).

### 148. NieR Replicant ver.1.22474487139... (2021, Toylogic / unstated)

- **Движок:** unstated/null (ремейк Toylogic; публичного подтверждения UE/собственного нет).
- **Релиз ПК:** Steam 23.04.2021 одновременно с консолями. Лимит 60 fps, жалобы на статтеры, нет ультрашироких/high-refresh опций (PCGW, DSOG).
- **Версии/патчи:** Пост-релизный патч стабильности fps; точные номера — unstated.
- **Причина репутации:** процесс (проблемный порт: кап частоты, фризы, зависимость от Special K для uncapped).
- **Решения:**
  - `±` Ремейк зон оригинала 2010 без бесшовного мира: малые стриминговые окна.
  - `−` Жёсткий кап 60 fps: стабильная логика ценой high-refresh.
  - `−` Минимальный набор графических опций: быстрый порт, слабая scalability.
  - `±` Сохранение структуры сейвов/слотов: совместимость ценой modern incremental-сейвов.
- **Влияние:** null как витрина; кейс о вреде fps-капа для репутации порта.
- **DSS:** `quality_tier_scalability`, `animation_compression`, `snapshot_slot_saves`, `async_loading_pipeline`.
- **Источники:** Steam (https://store.steampowered.com/app/1685240/NieR_Replicant_ver122474487139/), PCGW (https://www.pcgamingwiki.com/wiki/NieR_Replicant_ver.1.22474487139...).

### 149. Ghostrunner (2020, One More Level / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (One More Level / Slipgate Ironworks, 505 Games).
- **Релиз ПК:** 27.10.2020 (Steam/GOG/EGS). На старте DX12, трассировка лучей и DLSS. Дизайн one-hit-kill требует высокого fps и низкой задержки.
- **Версии/патчи:** Пострелизные режимы и RT-улучшения; переход на Complete Edition. Номера патчей — unstated.
- **Причина репутации:** реализация (скоростной UE4-слешер: отзывчивое управление и RT-витрина, но UE4-статтеры компиляции шейдеров и требовательность RT).
- **Решения:**
  - `+` Линейные уровни-башни с чекпоинтами и мгновенным рестартом.
  - `±` RT-отражения/тени + temporal-апскейлинг (DLSS) для компенсации цены RT.
  - `+` Паркур от первого лица без толп/транспорта: экономия crowd/physics-бюджетов.
  - `−` UE4 DX12 без предзагрузки PSO: фризы-подгрузки на части конфигураций.
- **Влияние:** null как системное; витрина RTX/DLSS для UE4-инди.
- **DSS:** `temporal_upscaling`, `hardware_raytraced_gi`, `async_loading_pipeline`, `pso_precaching_warmup`.
- **Источники:** Steam (https://store.steampowered.com/app/1139900/Ghostrunner/), PCGW (https://www.pcgamingwiki.com/wiki/Ghostrunner).

### 150. Hades II EA (2024, Supergiant / собственный)

- **Движок:** Собственный движок Supergiant (эволюция Hades); номер версии — unstated.
- **Релиз ПК:** Ранний доступ 06.05.2024; 1.0 — 25.09.2025 по Steam. Требования низкие: минимум GTX 950 / R7 360 / HD 630, рекомендовано RTX 2060 / RX 5600 XT. Windows и macOS.
- **Версии/патчи:** Итеративные EA-патчи (регионы/боги/баланс, Olympic Update). Точный список — см. историю Steam.
- **Причина репутации:** процесс (образцовый EA: стабильный fps, отзывчивый изометрический бой, частые контент-патчи, Overwhelmingly Positive 96%).
- **Решения:**
  - `+` Изометрические арены-камеры вместо бесшовного мира: ноль world-streaming цены.
  - `+` Ручной stylized-арт и атласированные спрайты/VFX вместо тяжёлого PBR/GI.
  - `+` Пулинг проджектайлов/частиц для bullet-hell плотности без аллокаций в кадре.
  - `±` Фиксированный sim-тик под бой с дэшами: предсказуемость ценой сложной физики.
- **Влияние:** контент — продуктовый эталон ведения roguelite-EA.
- **DSS:** `sprite_atlas_batching`, `particle_pooling`, `art_direction_stylization`, `fixed_timestep_physics`.
- **Источники:** Steam (https://store.steampowered.com/app/1145350/Hades_II/), Supergiant (https://www.supergiantgames.com/games/hades-ii/).

### 151. Crusader Kings III (2020, Paradox / Clausewitz)

- **Движок:** Clausewitz (Paradox Development Studio).
- **Релиз ПК:** 01.09.2020 на Windows/macOS/Linux (Steam/MS Store). Минимум GTX 660 / HD 7870, рекомендовано GTX 970 / RX 480. Direct3D 11, Vulkan 1.1 добавлен в 1.8 Robe (дефолт на Linux/macOS).
- **Версии/патчи:** Живая модель DLC/Flavor Pack/Expansion (Northern Lords, Royal Court, Tours & Tournaments). Номера билдов — см. патчноуты Paradox.
- **Причина репутации:** функционал (эталон grand strategy по доступности и стабильности симуляции; критика — DLC-монетизация и десинки, а не рендер).
- **Решения:**
  - `+` Тик-симуляция персонажей/вассалов с бюджетами обновления вместо per-frame AI.
  - `+` Слотовые сейвы + Steam Cloud и инкрементальные автосейвы.
  - `±` Онлайн-MP до 32 игроков с кроссплеем Steam/MS Store: determinism ценой десинков.
  - `+` MSAA и сдержанный post/VFX вместо тяжёлого deferred/RT: читаемость карты.
- **Влияние:** контент — продуктовый стандарт поддержки grand strategy DLC.
- **DSS:** `agent_update_budget`, `snapshot_slot_saves`, `async_incremental_saves`, `deterministic_lockstep`.
- **Источники:** Steam (https://store.steampowered.com/app/1158310/Crusader_Kings_III/), PCGW (https://www.pcgamingwiki.com/wiki/Crusader_Kings_III).

### 152. Teardown (2020 EA/2022, Tuxedo Labs / собственный воксельный C++)

- **Движок:** Собственный воксельный движок на C++; ранний доступ 29.10.2020; 1.0 — 21.04.2022.
- **Релиз ПК:** Только Windows в Steam; минимум GTX 1060 4 ГБ, рекомендовано GTX 1080. Принудительное software-RT (AO/тени/specular occlusion) без отключения, TAA, физика залочена на 60 fps. Direct3D 12 добавлен в 1.5.
- **Версии/патчи:** EA Part 1 / Part 2 (роботы, торнадо), 0.5.5 — улучшение на AMD, 1.5 — DX12, DLC Time Campers/Folkrace/Greenwash Gambit/Relics of Barkuna.
- **Причина репутации:** реализация (технологическая витрина: полностью разрушаемые воксели + RT-освещение от малой команды; Overwhelmingly Positive 95%).
- **Решения:**
  - `+` Тысячи малых воксельных volumes вместо единого volume миллиардов вокселей.
  - `+` Реймаршинг bounding-box в шейдере + палитровые материалы вместо полигонов.
  - `±` Фиксированная физика 60 fps и воксель-vs-воксель коллизии на CPU.
  - `±` Полумодульные volumetric-дым/огонь/вода за счёт упрощённых отражений (SSR).
- **Влияние:** контент — доказательство воксель+RT пайплайна малой командой; влияние на инди-деструкцию и Workshop.
- **DSS:** `destruction_geometry_cache`, `fixed_timestep_physics`, `volumetric_half_resolution`, `broadphase_spatial_partitioning`.
- **Источники:** Steam (https://store.steampowered.com/app/1167630/Teardown/), PCGW (https://www.pcgamingwiki.com/wiki/Teardown).

### 153. STAR WARS Jedi: Fallen Order (2019, Respawn / Unreal Engine 4.21)

- **Движок:** Unreal Engine 4.21.2.0 (PCGW); middleware PhysX, Wwise, Bink.
- **Релиз ПК:** 15.11.2019 (14.11 по Steam в ряде регионов); Direct3D 11, 55 ГБ. Лимитер 30/45/60/90/120/144 без uncapped из меню. Denuvo снят 09.11.2021.
- **Версии/патчи:** Пострелизные фиксы стабильности/сохранений и фоторежим; точные номера — unstated.
- **Причина репутации:** реализация (сильная метроидвания, но хрестоматийный UE4-кейс шейдерных статтеров, traversal-подгрузок и CPU-нагрузки; костыли DXVK/r.CreateShadersOnLoad).
- **Решения:**
  - `±` Полуоткрытые биомы с force-узкостями/лифтами для скрытия async-подгрузок.
  - `±` TAA + scalability-группы UE4 и ручные INI-твики (неотключаемый per-object motion blur).
  - `−` Отсутствие предкомпиляции PSO/прогрева: фризы при первом появлении шейдеров.
  - `−` Бэкинг сейвов и Origin/EA-оверлей как источник статтеров.
- **Влияние:** оптимизация — кейс, закрепивший тему UE4 traversal/shader-stutter; влияние на дискуссию о PSO-precaching.
- **DSS:** `async_loading_pipeline`, `pso_precaching_warmup`, `hierarchical_lod`, `post_effect_selective`.
- **Источники:** Steam (https://store.steampowered.com/app/1172380/STAR_WARS_Jedi_Fallen_Order/), PCGW (https://www.pcgamingwiki.com/wiki/Star_Wars_Jedi:_Fallen_Order).

---

## Партия 19 (список-3, батч 13: №154–161)

### 154. Sea of Thieves (2018/2020 Steam, Rare / Unreal Engine 4)

- **Движок:** Unreal Engine 4.
- **Релиз ПК:** Изначально Windows 10 / Xbox One 20.03.2018 (Play Anywhere + Game Pass); в Steam 03.06.2020 ($39.99) с кроссплеем/кросспрогрессом. Живая модель: Seasons, Tall Tales, расширения мира.
- **Версии/патчи:** Anniversary Update / Seasons / Safer Seas / PS5-релиз 2024. Детали билдов Steam — unstated.
- **Причина репутации:** функционал (эталон shared-world пиратской песочницы: бесшовный океан, корабли-экипажи, emergent PvPvE).
- **Решения:**
  - `+` Общий мир на серверах с экипажами 1–4 и кораблями как сетевыми объектами.
  - `+` Синхронизированная океанская волна для всех игроков сессии.
  - `+` Стилизация + масштабируемые пресеты ПК, упор на читаемость на дальности.
  - `±` Загрузочные швы при переходах/островах и дальний LOD растительности.
- **Влияние:** сеть — UE4 live-service с водой и физикой кораблей без шардинга в инстансы.
- **DSS:** `gerstner_fft_water`, `network_relevancy_priority`, `client_prediction_reconciliation`, `delta_compression_state`, `quality_tier_scalability`.
- **Источники:** Xbox (https://news.xbox.com/en-us/2020/05/21/sea-of-thieves-coming-to-steam-on-june-3/), SoT Steam FAQ (https://www.seaofthieves.com/news/sea-of-thieves-steam-faq), PCGW (https://www.pcgamingwiki.com/wiki/Sea_of_Thieves).

### 155. House Flipper 2 (2023, Frozen District / Unity)

- **Движок:** Unity.
- **Релиз ПК:** Windows в Steam 14.12.2023 (Frozen District). Новая кодовая база относительно House Flipper (2018), упор на Sandbox и стройку с нуля. PS5/Xbox Series 10.04.2024.
- **Версии/патчи:** Базовый релиз 14.12.2023; далее обновления с co-op 2–4 игрока для story/sandbox. Номера хотфиксов — unstated.
- **Причина репутации:** функционал (спокойный симулятор ремонта с низкой ценой входа; хвалят за перф на слабых ПК и Steam Deck Verified).
- **Решения:**
  - `+` Отдельные дома-задания как компактные уровни со снепшот-сейвами.
  - `+` SRP/батчинг реквизита и атласирование для интерьеров.
  - `+` Запечённое освещение интерьеров вместо дорогой динамики.
  - `±` Упрощённая физика мусора/уборки и коллизий ради стабильности.
- **Влияние:** контент — Unity-симулятор, где art-direction и батчинг важнее фотореализма.
- **DSS:** `srp_batcher_discipline`, `lightmap_atlas_baking`, `snapshot_slot_saves`, `quality_tier_scalability`, `mesh_index_optimization`.
- **Источники:** Steam (https://store.steampowered.com/app/1190970/House_Flipper_2/), PCGW (https://www.pcgamingwiki.com/wiki/House_Flipper_2).

### 156. Resident Evil Village (2021, Capcom / RE Engine)

- **Движок:** RE Engine.
- **Релиз ПК:** Steam 06–07.05.2021 одновременно с консолями, вид от первого лица, DirectX 12. Высокие аппетиты к VRAM (деревня/замок). Winters’ Expansion 10.2022.
- **Версии/патчи:** Стартовый билд 05.2021 со статтерами; июльский патч 2021 улучшил перф (подтверждено DF). Далее RT, FSR, Winters’ Expansion. Номера билдов — unstated.
- **Причина репутации:** реализация (плотная детализация, быстрый стриминг без загрузок, но ПК-старт омрачён микрофризами DRM/загрузочного пайплайна).
- **Решения:**
  - `+` Линейно-хабовые уровни с запечённой окклюзией и агрессивными LOD.
  - `±` Предкомпиляция/прогрев PSO и асинхронный стриминг текстур.
  - `+` Волюметрика, SSR/RT, temporal-апскейл для 60+ fps.
  - `−` Тяжёлые пост-эффекты и нестабильные статтеры на старте.
- **Влияние:** оптимизация — кейс, как DRM/шейдерный пайплайн нивелирует сильный движок; исправлено пост-патчами.
- **DSS:** `baked_occlusion_culling`, `hierarchical_lod`, `pso_precaching_warmup`, `temporal_upscaling`, `volumetric_half_resolution`.
- **Источники:** Steam (https://store.steampowered.com/app/1196590/Resident_Evil_Village/), PCGW (https://www.pcgamingwiki.com/wiki/Resident_Evil_Village).

### 157. Detroit: Become Human (2018/2019 ПК, Quantic Dream / собственный)

- **Движок:** Собственный движок Quantic Dream, ПК-версия с 4K/60 fps.
- **Релиз ПК:** PS4-эксклюзив 25.05.2018; ПК сначала EGS 12.12.2019 (демо, UI под мышь/клавиатуру); Steam 18.06.2020.
- **Версии/патчи:** EGS-билд 12.12.2019; Steam-билд 18.06.2020. Детальный чейнджлог ПК-патчей — unstated.
- **Причина репутации:** функционал (киношная ветвящаяся драма с захватом актёров; на ПК чистый 4K/60 и невысокие требования для лицевой анимации).
- **Решения:**
  - `+` Коридорные арены + потоковая подгрузка глав без открытых миров.
  - `+` Сжатие и LOD-бюджеты лицевой/телесной анимации.
  - `+` Слотовые сейвы/чекпоинты под дерево выборов и flowchart.
  - `±` Ограниченная интерактивность физики и толп ради кинематографичности.
- **Влияние:** контент — перенос консольного кинодвижка на ПК с упором на разрешение/фреймрейт.
- **DSS:** `animation_compression`, `animation_lod_budget`, `async_loading_pipeline`, `snapshot_slot_saves`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/1222140/Detroit_Become_Human/), PC Gamer (https://www.pcgamer.com/detroit-become-human-becomes-a-pc-game-in-december/).

### 158. Dragon Age: The Veilguard (2024, BioWare / Frostbite)

- **Движок:** Frostbite.
- **Релиз ПК:** 31.10.2024 на PS5/Xbox Series/ПК (Steam/EA App/EGS), Steam Deck Verified. Single-player RPG без микротранзакций ($59.99). Крупнейший Steam-запуск BioWare, но ниже ожиданий EA по продажам.
- **Версии/патчи:** Патчи 1–4 (конец 2024 — начало 2025); далее сворачивание поддержки. Номера/даты хотфиксов — unstated.
- **Причина репутации:** реализация (технически один из самых чистых Frostbite-релизов: стабильный фреймрейт, компиляция шейдеров при старте, RT-select, масштабирование; спорили о геймдизайне, рендер хвалили).
- **Решения:**
  - `+` Хабовые зоны вместо бесшовного open world + стриминг партиций.
  - `+` Предкомпиляция шейдеров и temporal-апскейл/динамическое разрешение.
  - `+` Иерархические LOD и бюджеты анимации компаньонов.
  - `±` Упрощение разрушения и симуляции ради стабильных 60 fps.
- **Влияние:** оптимизация — реабилитация Frostbite для party-RPG после Andromeda/Anthem: hubs + PSO-warmup.
- **DSS:** `world_partition_streaming`, `hierarchical_lod`, `pso_precaching_warmup`, `temporal_upscaling`, `dynamic_resolution_scaling`.
- **Источники:** Steam (https://store.steampowered.com/app/1845910/Dragon_Age_The_Veilguard/), EA (https://www.ea.com/games/dragon-age/dragon-age-the-veilguard/news/release-date-preorders).

### 159. Sailwind EA (2021, Raw Lion Workshop / Unity)

- **Движок:** Unity (David Evans / Raw Lion Workshop).
- **Релиз ПК:** Early Access 18.10.2021. Парусный симулятор с выживанием, грузоперевозками и навигацией по солнцу/звёздам. На 2026 остаётся в Early Access.
- **Версии/патчи:** Стартовый EA-билд 18.10.2021; итеративные EA-обновления (острова, рыбалка, мебель, океанские переходы). Номера билдов — unstated.
- **Причина репутации:** функционал (нишевый хит за честную парусную физику и огромный спокойный океан силами микро-команды).
- **Решения:**
  - `+` Открытая вода с герстнеровскими волнами и ветровой моделью парусов.
  - `+` Фиксированный шаг физики лодок для стабильности такелажа.
  - `±` Чанк-стриминг островов/океана вместо бесшовной планеты.
  - `+` Низкополигональная стилизация + жёсткий quality-tier под слабые ПК.
- **Влияние:** контент — один разработчик вытягивает океанский sim на Unity за счёт физики и стриминга.
- **DSS:** `gerstner_fft_water`, `fixed_timestep_physics`, `world_partition_streaming`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/1764530/Sailwind/).

### 160. Battlefield V (2018, DICE / Frostbite 3)

- **Движок:** Frostbite 3.
- **Релиз ПК:** Ранний доступ 09.11.2018, полный релиз 20.11.2018 (ПК/PS4/Xbox One, Origin; в Steam с 06.2020 как Definitive Edition). Вторая мировая, 64 игрока, Grand Operations, Combined Arms. Финальный контент — лето 2020.
- **Версии/патчи:** Tides of War (главы 1–7), патчи Chapter 4–6, DXR/DLSS-патчи для RTX; последний крупный — Summer Update 2020. Номера билдов — unstated.
- **Причина репутации:** реализация (лучшая стрельба/звук/разрушаемость, но запуск без обещанного, баланс TTK, DXR-цена, сворачивание live-поддержки).
- **Решения:**
  - `±` Выделенные серверы 64 игрока + тикрейт-бюджет и relevancy-приоритеты.
  - `+` Клиентская предикция/реконсиляция движения и техники.
  - `+` Кэш разрушаемой геометрии и партиклы-пулы взрывов.
  - `−` RT-отражения/освещение первой волны с тяжёлой ценой fps.
- **Влияние:** оптимизация — предел цены real-time RT в мультиплеере 64 игрока; откат ставки на RT в следующих частях.
- **DSS:** `headless_dedicated_server`, `tickrate_budgeting`, `client_prediction_reconciliation`, `network_relevancy_priority`, `destruction_geometry_cache`.
- **Источники:** Steam (https://store.steampowered.com/app/1238810/Battlefield_V/), EA (https://www.ea.com/games/battlefield/battlefield-5).

### 161. Battlefield 4 (2013, DICE / Frostbite 3)

- **Движок:** Frostbite 3.
- **Релиз ПК:** ПК/PS3/X360 29.10.2013 (Origin), PS4/Xbox One 11.2013; Steam ре-релиз 2020. Кампания + 64 игрока, Levolution, морские бои. Старт омрачён крашами и netcode-скандалом.
- **Версии/патчи:** Катастрофный запуск осени 2013; спасение через CTE (Community Test Environment) и осенние патчи 2014 с повышением тикрейта и фиксом netcode. Номера билдов — unstated.
- **Причина репутации:** процесс (эталон разрушения/масштаба и символ сломанного netcode: rubber-banding, trade-kills; реабилитирована после года CTE).
- **Решения:**
  - `+` Выделенные серверы + дельта-компрессия состояния и relevancy.
  - `+` Клиентская предикция, позже — повышение тикрейта в CTE.
  - `+` Кэш Levolution-разрушений (Шанхай, дамба).
  - `−` Запуск с недостаточным tickrate/интерполяцией.
- **Влияние:** сеть — практика CTE и повышение тикрейта как стандарт; урок для Battlefield 1/V/2042.
- **DSS:** `headless_dedicated_server`, `tickrate_budgeting`, `client_prediction_reconciliation`, `delta_compression_state`, `destruction_geometry_cache`.
- **Источники:** Steam (https://store.steampowered.com/app/1238860/Battlefield_4/).

---

## Партия 20 (список-3, батч 14: №162–169)

### 162. Battlefield 1 (2016, DICE / Frostbite 3)

- **Движок:** Frostbite 3 (подтверждено DF/PC Gamer).
- **Релиз ПК:** 21.10.2016 (Origin/PS4/Xbox One), current-gen-only. Day-one 1.01: quality/stability/performance.
- **Версии/патчи:** 1.01 day-one; 1.02 (24.10.2016): краши ПК, UI War Story, TAA по умолчанию на Medium, артефакты теней.
- **Причина репутации:** реализация (эталон масштабируемого Frostbite: 1080p60 на RX 480 / GTX 1060, 4K60 Ultra на GTX 1080; почти нулевая польза DX12).
- **Решения:**
  - `+` Deferred rendering + фотограмметрия, debris/undergrowth и частицы разрушений на Ultra.
  - `+` Dynamic resolution на консолях + resolution scaler на ПК.
  - `±` TAA по умолчанию на Medium, FXAA-опции, тени/дальность/стриминг на ПК.
  - `−` 64 игрока, Operations, дедики, деформация terrain: нагрузка упирается в CPU.
- **Влияние:** оптимизация — масштабируемость Frostbite против слабого старта DX12 без переработки рендера.
- **DSS:** `destruction_geometry_cache`, `deferred_forward_plus_choice`, `dynamic_resolution_scaling`, `headless_dedicated_server`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2016-battlefield-1-face-off), PC Gamer (https://www.pcgamer.com/battlefield-1-performance-analysis/), PCGW (https://www.pcgamingwiki.com/wiki/Battlefield_1).

### 163. Battlefield 3 (2011, DICE / Frostbite 2)

- **Движок:** Frostbite 2 (EA/DF).
- **Релиз ПК:** NA 10.2011, EU 27.10.2011 (ПК/Xbox 360/PS3). ~3 млн предзаказов, крупнейший FPS-запуск EA. ПК — lead-платформа.
- **Версии/патчи:** Клиент+сервер через Origin/Battlelog (несовместимые); клиентный апдейт — Back to Karkand; Multiplayer Update 4 (09.2012): ~2.2 ГБ + Armored Kill 3.2 ГБ.
- **Причина репутации:** реализация (PC showcase: maxed PC «light-years ahead» консолей, DX11 Compute Shader, отдельный поток текстур/мешей, инстансинг в один draw call; консоли 1280x704 ~ Low ПК).
- **Решения:**
  - `+` Отказ от DX9/XP, только DX10/11, Compute Shader, OIT, параллельный стриминг гигантских текстур.
  - `+` Инстансинг повторяемых объектов, дальность при одном draw call.
  - `±` Единый стандарт визуала: геометрия/модели даже на Low, режутся текстуры/тени.
  - `±` 64 игрока на ПК против урезанных консолей: цена в требованиях CPU/GPU.
- **Влияние:** контент — PC-first Frostbite 2 и мостик DX11 к следующему поколению консолей.
- **DSS:** `deferred_forward_plus_choice`, `destruction_geometry_cache`, `async_loading_pipeline`, `headless_dedicated_server`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-battlefield-3-pc-tech-analysis), PCGW (https://www.pcgamingwiki.com/wiki/Battlefield_3).

### 164. Battlefield: Bad Company 2 (2010, DICE/Coldwood / Frostbite 1.5)

- **Движок:** Frostbite 1.5 (PCGW).
- **Релиз ПК:** 02.03.2010 NA, 05.03.2010 EU (ПК/PS3/Xbox 360). ПК делала Coldwood отдельной командой; заявлены выделенные серверы.
- **Версии/патчи:** SPECACT Kit 04.2010; Vietnam 12.2010. Снята с продажи 28.04.2023, онлайн закрыт 08.12.2023. Нумерованные хотфиксы — unstated.
- **Причина репутации:** функционал (Destruction 2.0 с micro-destruction, squad play, техника; в ретроспективе DF: меньше окружения и 32 игрока против 64 в BF3).
- **Решения:**
  - `+` Destruction 2.0: послойное скалывание укрытий и обрушение зданий.
  - `+` Выделенные серверы и squad-режимы, техника земля/вода/воздух.
  - `+` Отдельная ПК-команда, мышь/клавиатура как core-ввод.
  - `−` Лимит 32 игроков и меньший масштаб карт: компромисс стабильности.
- **Влияние:** контент — мост от консольной Bad Company к PC-ориентированной BF3 с возвратом 64 игроков.
- **DSS:** `destruction_geometry_cache`, `headless_dedicated_server`, `tickrate_budgeting`, `quality_tier_scalability`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Battlefield:_Bad_Company_2), Steam (https://store.steampowered.com/app/24960/).

### 165. Remnant II (2023, Gunfire Games / Unreal Engine 5 + Nanite)

- **Движок:** Unreal Engine 5 с Nanite (Lumen/VSM/RT — отсутствуют по DSOG/DF).
- **Релиз ПК:** 07.2023 (ПК/PS5/Xbox Series, current-gen-only). Только DX12, из коробки DLSS/FSR/XeSS/Frame Generation. Процедурная структура миров от первой части.
- **Версии/патчи:** Номера патчей — unstated; заявлены performance updates после релиза; игра спроектирована с расчётом на апскейл.
- **Причина репутации:** реализация (тяжёлый натив: 1080p Ultra 60 fps только RX 6900XT / 7900XTX / RTX 4090; Nanite убирает traversal stutters и pop-in, на Low без Nanite — статтеры; бэклэш «апскейл как baseline»).
- **Решения:**
  - `+` Nanite: нет pop-in, меньше traversal stutters, ниже нагрузка CPU в хабе.
  - `±` Временные апскейлеры как обязательный baseline (почти x2 fps в Quality 4K).
  - `±` Динамическое разрешение на консолях + TSR вместо FSR2-артефактов.
  - `−` Отказ от Lumen/RT при сохранении высоких требований GPU и слабом SSAO.
- **Влияние:** оптимизация — кейс Nanite против цены натива и нормализации апскейла как требования.
- **DSS:** `mesh_index_optimization`, `temporal_upscaling`, `dynamic_resolution_scaling`, `world_partition_streaming`.
- **Источники:** DSOG (https://www.dsogaming.com/pc-performance-analyses/remnant-2-pc-performance-analysis/), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2023-remnant-2-is-a-fitting-showcase-for-unreal-engine-5-nanite-and-a-current-gen-focus).

### 166. Undisputed (2024, Steel City Interactive / Unity)

- **Движок:** Unity (PCGW, Unity/GDC Vault).
- **Релиз ПК:** Ранний доступ 31.01.2023; полный релиз Windows 08.10.2024 (консоли 10.2024). Требования: Denuvo, 40 ГБ, DX11 минимум / DX12 рекомендовано.
- **Версии/патчи:** Патч 1.0: fps, загрузки, aspect ratio, стабильность; 1.1.3 (14.10.2024): коллайдеры блока, порог пробития, ливеры Ranked; план — декабрьское обновление.
- **Причина репутации:** функционал (первый крупный бокс за десятилетие: от туториального Unity-прототипа до 100+ боксёров; баланс блока, квиттеры, софтлоки).
- **Решения:**
  - `+` Симуляционный бокс на Unity: footwork, углы, выносливость, лицензии.
  - `±` Перестройка block colliders и порога power punches в 1.1.3.
  - `±` Ranked-арбитраж квиттеров, P2P-лобби с invite code на 2 игроков.
  - `−` Ранний доступ как полигон баланса ценой софтлоков и перепадов fps до 1.0.
- **Влияние:** процесс — инди-спорт на Unity от прототипа до лицензионного релиза итеративными баланс-патчами.
- **DSS:** `fixed_timestep_physics`, `collision_layer_matrix`, `tickrate_budgeting`, `quality_tier_scalability`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Undisputed), Steam (https://store.steampowered.com/app/1451190/).

### 167. CarX Street (2024, CarX Technologies / Unity 2022 + Havok)

- **Движок:** Unity 2022.3.19f1 (PCGW); физика CarX на Havok, FMOD, EAC.
- **Релиз ПК:** 29.08.2024 в Steam полным релизом после мобайла 2022. Открытый Sunset City, тюнинг и дрифт. Постоянный интернет и SSD, DX11 на старте.
- **Версии/патчи:** 1.0.2 (09.2024); ветка 1.13.x: физика шин Racing/Racing+, аэродинамика, центр масс, инерция, тормоза, коллизия тандема/бордюров, апдейт движка, DX12, раздельные draw distance/texture/reflection.
- **Причина репутации:** функционал (глубина постройки/настройки против always-online и стартовых требований GTX 1050 Ti / RX 570 мин, RTX 2060 Super / RX 5700 XT рек).
- **Решения:**
  - `±` Открытый Sunset City + онлайн до 16 игроков на Epic Online Services.
  - `±` Физика CarX на Havok: шины, аэро, масса, инерция, тормоза итеративно перебалансированы.
  - `+` Раздельные настройки дальности/текстур/отражений + DX12 для AMD-ливрей.
  - `−` Always-online для всех режимов и SSD как обязательное требование.
- **Влияние:** процесс — перевод мобайл-гонки на ПК через Unity-апдейт, DX12 и порезку настроек.
- **DSS:** `world_partition_streaming`, `fixed_timestep_physics`, `async_loading_pipeline`, `quality_tier_scalability`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/CarX_Street), Steam (https://store.steampowered.com/app/1114150/CarX_Street/).

### 168. Slime Rancher 2 EA (2022, Monomi Park / Unity 2021)

- **Движок:** Unity 2021.3.28f1 (PCGW); URP/HDRP — unstated.
- **Релиз ПК:** Ранний доступ 22.09.2022 (Steam/EGS/Xbox Game Preview); 1.0 — 23.09.2025. Сингл first-person sandbox.
- **Версии/патчи:** EA-концепция: большой мир, слаймы, Rainbow Island в полированном состоянии, но без всех фич/зон/сюжета финала. Номера EA-патчей — unstated.
- **Причина репутации:** функционал (полированный EA с cartoon-стилем и низкими требованиями: GTX 960 / R9 280 мин, RTX 2070 / RX 5700 рек, DX11).
- **Решения:**
  - `+` Cartoon art direction вместо фотореализма: низкая цена кадра.
  - `+` Островная структура Rainbow Island под порционное расширение в EA.
  - `±` Слотовые сейвы Steam Cloud + локальные .sav/.prf.
  - `±` DX11-база и скромные VRAM 2–3 ГБ: доступность ценой детализации.
- **Влияние:** контент — успешный cartoon-EA: полированное ядро с наращиванием контента к 1.0.
- **DSS:** `art_direction_stylization`, `gpu_instancing_vegetation`, `quality_tier_scalability`, `snapshot_slot_saves`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Slime_Rancher_2), Steam (https://store.steampowered.com/app/1657630/Slime_Rancher_2/).

### 169. Cult of the Lamb (2022, Massive Monster / Unity 2022 + FMOD)

- **Движок:** Unity 2022.3.62f2 (PCGW); DX11, только FXAA-тоггл; FMOD / Resonance Audio / Rewired.
- **Релиз ПК:** 11.08.2022 (Steam/GOG, Devolver Digital). Action/building/roguelike, вид сверху, сингл + локальный кооп на 2. Metacritic 82, OpenCritic 84.
- **Версии/патчи:** Хотфиксы 1.0.5 (15.08), 1.0.11 (22.08), 1.0.12 (24.08.2022); позже 1.5.x (просадки от ranchables, софтлоки, квесты, краши катсцен).
- **Причина репутации:** функционал (хит про культ с данжами и базой, но софтлоки, краши и деградация fps на базе 50+ последователей; Steam Cloud не синхронизирует Win/Mac).
- **Решения:**
  - `+` Гибрид roguelike-забегов и базы культа с cartoon-стилизацией и стерео.
  - `+` Ранний конвейер хотфиксов 1.0.5–1.0.12 и 1.5.x по софтлокам/прогрессии.
  - `−` Локальные JSON-сейвы + Steam Cloud с раздельными Win/Mac: рассинхрон и блоат DLC.
  - `−` Рост симуляции последователей/ранчо без агрессивного LOD: просадки и RAM 8–16 ГБ.
- **Влияние:** оптимизация — база-менеджмент как главный потребитель CPU/памяти и источник софтлоков в Unity-рогалике.
- **DSS:** `crowd_instancing_impostors`, `agent_update_budget`, `snapshot_slot_saves`, `art_direction_stylization`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Cult_of_the_Lamb), Steam News (https://store.steampowered.com/news/app/1313140/view/3257812203963831239).

---

## Партия 21 (список-3, батч 15: №170–177)

### 170. Mortal Kombat 1 (2023, NetherRealm / Unreal Engine 4.27; порт QLOC)

- **Движок:** Unreal Engine 4, билд 4.27.2.0; порт Windows — QLOC.
- **Релиз ПК:** 19.09.2023 (Steam/EGS) одновременно с консолями (Warner Bros.). Denuvo, ~140 ГБ, заявлены DLSS/FSR/XeSS.
- **Версии/патчи:** Сезонные патчи и баланс, Krossplay/Kross-Progression; 18.06.2024 — 60 FPS для меню/сюжетных сцен/Invasions/добиваний; 21.01.2025 — опция Ray-Traced Reflections.
- **Причина репутации:** процесс (на фоне разгромленной Switch-версии ПК приемлем, но капы 30/40/50/60 FPS, пререндер-катсцены 30 FPS, тяжеловесность).
- **Решения:**
  - `+` Кап логики боя и rollback-сессия с детерминированным шагом: 60 FPS в матче важнее картинки.
  - `±` Предкомпиляция PSO/прогрев шейдеров UE4 для снижения фризов арен.
  - `+` Апскейлы DLSS/FSR/XeSS + пресеты Temporal/Spatial.
  - `+` Сжатие и бюджетирование анимаций Fatality/Fatal Blow/интро при 60 FPS катсценах.
- **Влияние:** оптимизация — файтинг на UE4 с поздним RT и расширением 60 FPS за пределы боя.
- **DSS:** `deterministic_lockstep`, `pso_precaching_warmup`, `temporal_upscaling`, `animation_compression`.
- **Источники:** Steam (https://store.steampowered.com/app/1971870/), PCGW (https://www.pcgamingwiki.com/wiki/Mortal_Kombat_1).

### 171. Dead Space Remake (2023, Motive / Frostbite)

- **Движок:** Frostbite.
- **Релиз ПК:** 27.01.2023 (Steam/EA App/EGS, Motive/EA). Полный ремейк 2008 с бесшовной Ишимурой. ~32–36 ГБ, заявлены DLSS/FSR 2.0/VRS.
- **Версии/патчи:** Хотфиксы 1.000.003 / 1.03 / 1.04 (конец 01 — начало 02.2023). Патч 1.04 заявлял прирост перф, фиксы UI/статтеров/стабильности; траверс-статтеры сохранились; польза ReBAR на NVIDIA.
- **Причина репутации:** реализация (высокооценённый ремейк, но траверс-статтеры, принудительный VRS с мылом при апскейлах, нестабильный фреймпейсинг).
- **Решения:**
  - `−` Бесшовный стриминг без загрузок через async pipeline: траверс-хитчи при сборке шейдов.
  - `±` Temporal-апскейлы DLSS/FSR 2.0 + VRS для 4K (изначально без отключения VRS).
  - `±` Динамическое разрешение и лимиты качества для тяжёлых отсеков.
  - `+` Половинное разрешение волюметрики и пост-эффектов для интерьеров.
- **Влияние:** оптимизация — показательный кейс 2023 по траверс-статтеру и спору VRS + апскейл.
- **DSS:** `async_loading_pipeline`, `temporal_upscaling`, `dynamic_resolution_scaling`, `volumetric_half_resolution`.
- **Источники:** Steam (https://store.steampowered.com/app/1693980/), DSOG (https://www.dsogaming.com/patches/dead-space-remake-update-1-04-full-patch-notes/).

### 172. MONSTER HUNTER RISE (2021/2022 ПК, Capcom / RE Engine)

- **Движок:** RE Engine (впервые для zoneless-Monster Hunter).
- **Релиз ПК:** Switch 26.03.2021; ПК в Steam 12.01.2022 (демо 13.10.2021). Поддержка 4K, высоких текстур, несжатого фреймрейта, 21:9, KB+M и голосового чата. Кроссплей/кросс-сейвы отсутствуют.
- **Версии/патчи:** ПК вышла со всем пострелизным контентом Switch; далее Title Updates и Sunbreak (лето 2022).
- **Причина репутации:** реализация (образцовый порт: лёгкое Switch-наследие, высокие FPS на слабом железе, ультравайд и корректный KB+M).
- **Решения:**
  - `+` Иерархические LOD и стриминг бесшовных локаций без зон под RE Engine.
  - `+` Асинхронный пайплайн загрузок охот и возвратов в Камуру.
  - `+` Лестница качества текстур/теней/листвы от Switch до 4K-ПК.
  - `+` Бюджетирование анимаций монстров и Palamute/Palico в коопе до 4 игроков.
- **Влияние:** контент — масштабируемость RE Engine от Switch до 4K-ПК без смены дизайна уровней.
- **DSS:** `hierarchical_lod`, `async_loading_pipeline`, `quality_tier_scalability`, `animation_lod_budget`.
- **Источники:** Steam (https://store.steampowered.com/app/1446780/), Capcom IR (https://www.capcom.co.jp/ir/english/news/html/e211001.html).

### 173. Persona 5 Royal (2019/2022 ПК, Atlus / собственный GFD)

- **Движок:** Собственный движок Atlus (GFD по PCGW).
- **Релиз ПК:** Royal PS4 Япония 31.10.2019, Запад 31.03.2020; ПК 21.10.2022 (Steam/MS Store, SEGA). Включает 40+ DLC оригинала, заявлены 4K и до 120 FPS, есть Denuvo.
- **Версии/патчи:** Завершённое издание без контентных сезонов; патчи — совместимость и контроллеры.
- **Причина репутации:** реализация (отличный, но минималистичный порт: идеальный перф на слабом железе и Steam Deck, но бедный набор опций).
- **Решения:**
  - `+` Стилизованный арт вместо тяжёлого PBR: низкие требования при 120 FPS.
  - `+` Сжатие анимаций и UI-атласы для тысяч спрайтов меню/Confidant/Mementos.
  - `+` Простой скейлер качества под 720p60 на iGPU до 4K120.
  - `+` Асинхронные загрузки дворцов и города за переходами.
- **Влияние:** контент — эталон JRPG-порта по цена/FPS, но критика за отсутствие расширенных настроек.
- **DSS:** `art_direction_stylization`, `animation_compression`, `quality_tier_scalability`, `async_loading_pipeline`.
- **Источники:** Steam (https://store.steampowered.com/app/1687950/), PCGW (https://www.pcgamingwiki.com/wiki/Persona_5_Royal).

### 174. FINAL FANTASY VII REMAKE INTERGRADE (2021 ПК, Square Enix / Unreal Engine 4)

- **Движок:** Unreal Engine 4.
- **Релиз ПК:** PS5 Intergrade 10.06.2021; ПК сначала EGS 16.12.2021, затем Steam 17.06.2022. Критиковали узкие настройки и высокую цену EGS-старта.
- **Версии/патчи:** ПК-патч 1.001 стабилизировал 90+ FPS; полного решения статтера не было; сообщество — FFVIIHook, Engine.ini, DX11-флаг, DLL для асинхронной компиляции.
- **Причина репутации:** процесс (главный пример DX12 PSO-статтера на UE4: фризы при перемещениях, нет динамического разрешения и DLSS на старте, низкие настройки).
- **Решения:**
  - `−` PSO-precache/warmup фактически отсутствует: компиляция в фоне во время игры.
  - `±` Стриминг текстур и уровней Мидгара через async pipeline без предзагрузки.
  - `±` Виртуальное текстурирование UE4 для города при резких сменах ракурсов.
  - `−` Временной апскейл и динамическое разрешение на старте ограничены, позже частично модами.
- **Влияние:** оптимизация — хрестоматийный кейс shader compilation stutter в UE4-портах с PS5.
- **DSS:** `pso_precaching_warmup`, `async_loading_pipeline`, `virtual_texturing`, `dynamic_resolution_scaling`.
- **Источники:** Steam (https://store.steampowered.com/app/1462040/), PCGW (https://www.pcgamingwiki.com/wiki/Final_Fantasy_VII_Remake_Intergrade).

### 175. Dune: Spice Wars (2022 EA/2023, Shiro Games / Heaps/HashLink)

- **Движок:** Heaps.io / HashLink (SteamDB: HashLink + Heaps Engine; не Unity).
- **Релиз ПК:** Ранний доступ 26.04.2022; 1.0 — 14.09.2023 (Shiro Games/Funcom). Гибрид 4X и RTS в реальном времени по Дюне.
- **Версии/патчи:** Мультиплеер-апдейт 20.06.2022 (2v2, FFA до 4); переработка веток развития, баланс Харконненов, ИИ, политика, регионы, Conquest-апдейты до релиза.
- **Причина репутации:** функционал (крепкая EA-стратегия от авторов Northgard: связка 4X+RTS; критиковали баланс, аггро милиций и ИИ на старте).
- **Решения:**
  - `+` Детерминированный lockstep для синхронных MP-сессий RTS.
  - `+` Time-sliced поиск пути и бюджет апдейтов агентов для сотен юнитов.
  - `±` Flow-field/тайловые поля для массовых перемещений и червей.
  - `+` Пространственное разбиение broadphase и матрица коллизий для милиций.
- **Влияние:** процесс — не-Unity RTS на Haxe-стеке Shiro с долгим EA-циклом баланса.
- **DSS:** `deterministic_lockstep`, `time_sliced_pathfinding`, `agent_update_budget`, `flow_field_pathing`.
- **Источники:** Steam (https://store.steampowered.com/app/1605220/), Steam Discussions (https://steamcommunity.com/app/1605220/discussions/0/3266809271716584017/).

### 176. The Planet Crafter (2022 EA/2024, Miju Games / Unity)

- **Движок:** Unity.
- **Релиз ПК:** Ранний доступ 24.03.2022; полный релиз 10.04.2024 (Miju Games). Сурвайвал-крафт про терраформирование.
- **Версии/патчи:** Длительный EA-цикл с контент-апдейтами биомов, машин терраформирования и кооператива; к релизу — 55 достижений и демо.
- **Причина репутации:** функционал (инди-хит выживания: понятная прогрессия индекса терраформирования, темп открытий, соло/кооп без жёсткого гринда).
- **Решения:**
  - `+` Процедурное размещение ресурсов и обломков по сетке терраформирования.
  - `+` GPU-инстансинг растительности и построек при росте биомассы.
  - `+` Партиционированный стриминг мира для бесшовных переходов между кратерами.
  - `±` Инкрементальные автосейвы базы при тысячах объектов.
- **Влияние:** контент — Unity-сурвайвал малой команды с прогрессией мира как главной механикой.
- **DSS:** `gpu_procedural_placement`, `gpu_instancing_vegetation`, `world_partition_streaming`, `async_incremental_saves`.
- **Источники:** Steam (https://store.steampowered.com/app/1284190/), PCGW (https://www.pcgamingwiki.com/wiki/The_Planet_Crafter).

### 177. Demon Slayer -Kimetsu no Yaiba- The Hinokami Chronicles (2021, CyberConnect2 / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (CyberConnect2, SEGA).
- **Релиз ПК:** Windows в Steam 15.10.2021 (Deluxe ранний доступ с 13.10). Арена-файтинг по аниме с Adventure и Versus.
- **Версии/патчи:** Пострелизные Character Pack (Руи, Аказа, Тенген, Незуко и др.). Технических оверхаулов ПК-версии не заявлено.
- **Причина репутации:** процесс (средний аниме-порт: кап 30/60 FPS, катсцены/ульты/онлайн capped 30 FPS, ультравайд пилларбоксом 16:9, бедные настройки).
- **Решения:**
  - `+` Стилизация под аниме с сел-шейдингом вместо фотореалистичного света.
  - `±` Сжатие и кат катсценных анимаций под 30 FPS ультов.
  - `+` Пулинг частиц эффектов дыхания/крови для арен.
  - `+` Селективные пост-эффекты для читаемости ударов на слабом железе.
- **Влияние:** контент — типичный UE4 аниме-файтинг CyberConnect2: читаемость приёмов важнее частоты кадров.
- **DSS:** `art_direction_stylization`, `animation_compression`, `particle_pooling`, `post_effect_selective`.
- **Источники:** Steam (https://store.steampowered.com/app/1490890/), PCGW (https://www.pcgamingwiki.com/wiki/Demon_Slayer_-Kimetsu_no_Yaiba-_The_Hinokami_Chronicles).

---

## Партия 22 (список-3, батч 16: №178–185)

### 178. Lords of the Fallen (2023, Hexworks / Unreal Engine 5 + Nanite/Lumen/Chaos)

- **Движок:** Unreal Engine 5, Nanite + Lumen, Chaos Physics (подтверждено DF/DSOG).
- **Релиз ПК:** 13.10.2023 одновременно ПК/PS5/Xbox Series как перезапуск серии. Расширенные настройки, DLSS 3 и FSR, ультра-пресет крайне требователен даже для RTX 4090 в native 4K. Жалобы на краши и traversal-статтеры; серия хотфиксов 1.1.xxx.
- **Версии/патчи:** 1.1.203 — substantial performance improvements; 1.1.243 — оптимизация Lumen (+1–2 мс GPU) и Umbral-мешей; DF тестировал 1.1.293/1.1.310.
- **Причина репутации:** реализация (один из самых красивых UE5-soulslike, но ongoing tech issues: Ultra 1080p только RX 7900 XTX / RTX 4090 в стресс-сцене, 4K native 60 fps ни на одной карте; просадки до однозначных fps, DRS до 648–1152p в perf, Series S 432–720p).
- **Решения:**
  - `+` Nanite-виртуализированная геометрия для двух миров Axiom/Umbral без поп-ина.
  - `±` Lumen GI гибридного типа + программная/аппаратная трассировка (позже −1–2 мс).
  - `+` DLSS 3 / FSR + детальные пресеты View Distance/Shadows/GI/Effects.
  - `±` Отсутствие шейдер-компиляционных статтеров, но сохранение traversal-статтеров.
- **Влияние:** оптимизация — кейс раннего UE5-ААА: красивая картинка ценой DRS и статтеров; пример Engine.ini-твиков Lumen/Nanite.
- **DSS:** `hardware_raytraced_gi`, `temporal_upscaling`, `dynamic_resolution_scaling`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/2107090/Lords_of_the_Fallen/), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2023-lords-of-the-fallen-is-a-stunning-ue5-soulslike-with-ongoing-tech-issues), DSOG (https://www.dsogaming.com/pc-performance-analyses/lords-of-the-fallen-benchmarks-pc-performance-analysis/).

### 179. Battlefield 2042 (2021, DICE / Frostbite)

- **Движок:** Frostbite (SteamDB: Frostbite Engine, EA AntiCheat).
- **Релиз ПК:** Steam 19.11.2021. 128 игроков (All-Out Warfare, Hazard Zone, Portal). Стартовый known issues DICE: rubber-banding, десинх разрушаемости, баги XP, боты, UI, Recon Drone, прицелы. Смешанные отзывы Steam.
- **Версии/патчи:** Live-service сезоны и патчноуты на EA.com/SteamDB; фиксы карт Breakaway/Kaleidoscope/Discarded/Manifest, ботов Ranger, аудио и UI серией обновлений.
- **Причина репутации:** реализация (128 игроков + разрушения + кроссплей вскрыли хит-рег/netcode/тикрейт, пустые карты, специалисты вместо классов).
- **Решения:**
  - `−` 128p Conquest/Breakthrough с ботами для добивки лобби.
  - `+` Portal-конструктор с логикой и dedicated-браузером серверов.
  - `−` Levolution-подобная разрушаемость с десинками при позднем входе.
  - `±` Пострелизные фиксы коллизий, возрождений, прицелов и баланса специалистов.
- **Влияние:** сеть — переоценка масштаба: возврат классовой системы и 64p-режимов; урок tickrate/relevancy и плотности контента.
- **DSS:** `tickrate_budgeting`, `client_prediction_reconciliation`, `network_relevancy_priority`, `destruction_geometry_cache`.
- **Источники:** Steam (https://store.steampowered.com/app/1517290/Battlefield_2042/), SteamDB (https://steamdb.info/app/1517290/patchnotes/), VG247 (https://www.vg247.com/battlefield-2042-bugs-fixes-known-issues).

### 180. God of War (2018/2022 ПК, Santa Monica / собственный; порт Jetpack)

- **Движок:** Собственный движок Santa Monica Studio (PS4 GNM); ПК-порт — Jetpack Interactive (~2 года, 4 инженера).
- **Релиз ПК:** Оригинал PS4 2018; ПК Steam 14.01.2022. DF: simply sensational: высокие fps, ultrawide, DLSS/FSR/Reflex, собственный TAA-апскейл. DSOG: на high-end CPU статтеров нет, KBM exceptional. Минусы — только Window/Borderless без Exclusive Fullscreen, нет FOV-слайдера (one-shot камера).
- **Версии/патчи:** Пострелизные фиксы Jetpack (номера — unstated). Остались на DirectX 11 из-за HLSL-пайплайна (перенос на DX12 — out of scope).
- **Причина репутации:** реализация (эталонный Sony-порт: улучшенные AO-тени GTAO+SSAO, отражения, атмосферка против PS4/PS5; корректный сплит VRAM/RAM; переписанная particle-система).
- **Решения:**
  - `±` DX11-база + сохранение контент-пайплайна без переавторинга.
  - `+` Встроенный temporal upsample + DLSS 2 / FSR 1.0 + Reflex.
  - `+` GTAO/SSAO-апгрейд и улучшенные тени за пару мс для high-end.
  - `−` Отказ от Exclusive Fullscreen, даунсемплинг только через разрешение десктопа.
- **Влияние:** контент — планка Sony-портов (Horizon, Days Gone, Ragnarök уже на DX12); разбор GNM→PC и unified→split memory.
- **DSS:** `temporal_upscaling`, `dynamic_resolution_scaling`, `pso_precaching_warmup`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/1593500/God_of_War/), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2022-god-of-war-on-pc-is-a-simply-sensational-port), DSOG (https://www.dsogaming.com/pc-performance-analyses/god-of-war-pc-performance-analysis).

### 181. Frostpunk 2 (2024, 11 bit / Unreal Engine 5)

- **Движок:** Unreal Engine 5 (первая часть — Liquid Engine; сиквел и ремейк 1886 — на UE5).
- **Релиз ПК:** Windows/macOS 20.09.2024 (PS5/Xbox Series 18.09.2025). DLSS 3, FSR 3.0, XeSS. DSOG: Ultra крайне требователен, Medium выглядит отлично и рекомендуется. Не шейдерные, а повторяемые статтеры при ротации камеры Q/E и object-limit краши огромных городов.
- **Версии/патчи:** Пять хотфиксов к 10.2024, затем 1.1.0 Quality of Life + large-scale optimizations; Hotfix 1.0.5, 1.4.2 с фиксом object-limit (воркэраунд gc.MaxObjects), ветка 1.5.x (2025–2026).
- **Причина репутации:** реализация (тяжёлый UE5-градостроитель: FSR 3.0 с артефактами и Frame Generation с framepacing-проблемами, DLSS 3 лучше; UI/UX-споры, правленные в 1.1.0).
- **Решения:**
  - `±` Пресеты Textures/Terrain/Shadows/Lighting + DLSS 3 FG против FSR 3.0 FG.
  - `+` Масштабные оптимизации 1.1.0 и балансные правки общества.
  - `−` Фикс object-limit через ручное повышение лимита в Engine.ini как last resort.
  - `±` Поддержка контроллера/edge scrolling/cursor lock постфактум.
- **Влияние:** оптимизация — UE5-стратегия, где CPU-симуляция и late-game города упираются в лимиты движка.
- **DSS:** `temporal_upscaling`, `ml_frame_generation`, `agent_update_budget`, `crowd_instancing_impostors`.
- **Источники:** Steam (https://store.steampowered.com/app/1601580/Frostpunk_2/), DSOG (https://www.dsogaming.com/pc-performance-analyses/frostpunk-2-pc-performance-analysis/).

### 182. Palworld EA (2024, Pocketpair / Unreal Engine 5)

- **Движок:** Unreal Engine 5 (EA-ветка; 1.0 — на UE 5.4).
- **Релиз ПК:** Ранний доступ 19.01.2024. Open-world survival: сбор Палов, базы, мультиплеер/кооп с выделенными серверами. Феномен продаж на фоне сырой оптимизации: shader/traversal-статтеры, просадки у крупных баз, высокое потребление VRAM/стриминга.
- **Версии/патчи:** Десятки EA-хотфиксов в 2024 через Steam (номера — unstated). Движение к 1.0 в 2026 на UE 5.4 с более тяжёлым освещением/стримингом.
- **Причина репутации:** функционал (виральный хит + UE5-болезни: дорогие Shadows/View Distance, AI-симуляция десятков Палов, сотни дропов, колебания GPU-загрузки).
- **Решения:**
  - `±` World Partition-стриминг открытого мира + данжи/кейвы как передышка для GPU.
  - `+` Базовый пресет с Shadows Medium и View Distance Medium/High как главный рычаг fps.
  - `+` DLSS/FSR-апскейл + Fullscreen и кап fps для ровного фреймпейсинга.
  - `−` Отсутствие предкомпиляции шейдеров и дефолтный UE5-конфиг с поздним кешированием.
- **Влияние:** контент — хрестоматийный EA-кейс: геймплей-петля перекрыла техдолг; Engine.ini-твики как стандарт UE5-выживачей.
- **DSS:** `world_partition_streaming`, `pso_precaching_warmup`, `temporal_upscaling`, `agent_update_budget`, `headless_dedicated_server`.
- **Источники:** Steam (https://store.steampowered.com/app/1623730/Palworld/).

### 183. Lies of P (2023, Round8 / Unreal Engine 4 + Denuvo)

- **Движок:** Unreal Engine 4 (Round8, NEOWIZ, Denuvo на релизе).
- **Релиз ПК:** Steam 19.09.2023. Soulslike по Пиноккио с bloodborne-артом Крата. DSOG: GTX 980 Ti даёт 60 fps+ в 1080p Max, топ-4 GPU — 60 fps в native 4K Max, CPU-нагрузка мизерная (двухъядерник 200+ fps). Нет Exclusive Fullscreen, только Window/Borderless.
- **Версии/патчи:** Ветка 1.2.x–1.5.x (1.5.0.0 в 02.2024 с контентом/багфиксами), затем 1.9–1.13, Overture DLC и Complete Edition, Switch 2 и EGS (2025–2026).
- **Причина репутации:** реализация (один из best optimized PC games 2023: прекеш шейдеров при первом запуске убрал статтеры несмотря на UE4 и Denuvo).
- **Решения:**
  - `+` Шейдерный прекеш при первом запуске против статтеров.
  - `+` DLSS 2 + FSR 2.0 при узком наборе настроек Visibility/AA/Textures/Shadows.
  - `+` Низкие CPU-требования и охват от RX 580/Vega 64.
  - `−` Отказ от Exclusive Fullscreen, даунсемплинг только через десктоп.
- **Влияние:** оптимизация — доказательство, что UE4 при дисциплине даёт ровный souls-like; контрпример поздним UE5-релизам.
- **DSS:** `pso_precaching_warmup`, `temporal_upscaling`, `quality_tier_scalability`, `animation_lod_budget`.
- **Источники:** Steam (https://store.steampowered.com/app/1627720/Lies_of_P/), DSOG (https://www.dsogaming.com/pc-performance-analyses/lies-of-p-pc-performance-analysis/).

### 184. Minecraft Dungeons (2020, Mojang / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (Mojang; порты консолей — Double Eleven; выбор UE вместо Java/Bedrock подтверждён на E3 2019).
- **Релиз ПК:** Windows/Xbox One/PS4/Switch 26.05.2020 (перенос с апреля из-за COVID-19); Steam 22.09.2021; Xbox Series оптимизация 24.02.2021. Изометрический ARPG до 4 игроков (Diablo/Torchlight/L4D). Финальная 1.17.0.0.
- **Версии/патчи:** DLC-сезоны: Jungle Awakens, Creeping Winter, Howling Peaks, Flames of the Nether, Hidden Depths, Echoing Void. Баланс-патчи — unstated.
- **Причина репутации:** функционал (доступный семейный Diablo-клон: простые билды, voxel-cartoon арт, низкие требования, стабильность на слабом железе и Switch).
- **Решения:**
  - `+` Стилизация voxel/cartoon вместо фотореализма для масштаба на слабом железе.
  - `+` Линейно-чанковые уровни с простым пулом мобов и снарядов.
  - `±` Онлайн/локальный кооп до 4 игроков через Xbox Live бэкенд.
  - `−` Урезанные настройки графики UE4 без гибкого скейла для энтузиастов.
- **Влияние:** контент — жизнеспособность UE4 для Minecraft-спиноффов; мостик к Dungeons II (анонс 29.09.2026).
- **DSS:** `art_direction_stylization`, `quality_tier_scalability`, `agent_update_budget`, `async_loading_pipeline`.
- **Источники:** Steam (https://store.steampowered.com/app/1672970/Minecraft_Dungeons/), PCGW (https://www.pcgamingwiki.com/wiki/Minecraft_Dungeons).

### 185. ARMORED CORE VI FIRES OF RUBICON (2023, FromSoftware / собственный, DX12)

- **Движок:** Собственный in-house движок FromSoftware (линейка Souls/Sekiro/Elden Ring), DirectX 12 на ПК.
- **Релиз ПК:** Steam 24–25.08.2023 (зависит от таймзоны), первый Armored Core на ПК. Первый FromSoftware-проект с 120 fps и ultrawide. Very Positive (~93%). Рейтрейсинг — только в гараже, в миссиях недоступен.
- **Версии/патчи:** Регуляторные и баланс-патчи оружия/боссов после релиза (номера — unstated). PCGW: Issues unresolved — random frame pacing issues and frame rate drops.
- **Причина репутации:** реализация (DF: a brilliant game with the standard From performance issues: PS5 Quality fixed 3840x2160 с просадками, Performance DRS 2688x1512–3840x2160; на ПК лёгкость запуска, но микрофризы/пейсинг и бедные настройки).
- **Решения:**
  - `±` DRS на консолях + TAA против просадок в омни-боях.
  - `+` 120 fps и ultrawide впервые для студии.
  - `±` RT только в гараже для ограничения цены кадра.
  - `−` Скудные PC-опции без DLSS/FSR на старте и frame-pacing дропы.
- **Влияние:** оптимизация — формула From на ПК: отличный геймплей при сдержанной графике; прецедент гаражного RT как маркетингового лимита.
- **DSS:** `dynamic_resolution_scaling`, `hardware_raytraced_gi`, `quality_tier_scalability`, `pso_precaching_warmup`.
- **Источники:** Steam (https://store.steampowered.com/app/1888160/ARMORED_CORE_VI_FIRES_OF_RUBICON), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2023-armored-core-6-a-brilliant-game-with-the-standard-from-performance-issues).

---

## Партия 23 (список-3, батч 17: №186–193)

### 186. Prince of Persia: The Lost Crown (2024, Ubisoft Montpellier / Unity)

- **Движок:** Unity (подтверждено Ubisoft Montpellier; не Anvil/UbiArt).
- **Релиз ПК:** Первоначально 18.01.2024 (Ubisoft Connect/EGS); Steam 08.08.2024. 2.5D action-metroidvania с фиксированной камерой и акцентом на 60+ FPS. Репутация очень лёгкой и стабильной игры, включая Steam Deck.
- **Версии/патчи:** Title Updates в 2024: блокеры прогресса, баги карты/квестов, баланс. Точный changelog ПК — unstated.
- **Причина репутации:** функционал (компактный стилизованный релиз Ubisoft без тяжёлого RT и открытого мира: стабильный фреймрейт на слабом железе).
- **Решения:**
  - `+` Стилизованная 2.5D-подача вместо фотореализма: низкая цена кадра.
  - `+` Чанкированная метроидвания с быстрыми переходами без бесшовного стриминга.
  - `+` Атлас спрайтов/UI и ограниченный пул эффектов: меньше draw calls.
  - `±` Масштабируемые пресеты и лимит FPS для портативов, но без RT/Frame Gen.
- **Влияние:** оптимизация — Unity-проект среднего масштаба без шейдерных статтеров 2023–2024 при дисциплине скопа.
- **DSS:** `art_direction_stylization`, `sprite_atlas_batching`, `tilemap_chunk_streaming`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/2751000/Prince_of_Persia_The_Lost_Crown/), PCGW (https://www.pcgamingwiki.com/wiki/Prince_of_Persia:_The_Lost_Crown), Ubisoft (https://www.ubisoft.com/en-gb/game/prince-of-persia/the-lost-crown).

### 187. STAR WARS Jedi: Survivor (2023, Respawn / Unreal Engine 4 мод.)

- **Движок:** Unreal Engine 4 (сильно модифицированный; не UE5 вопреки ожиданиям).
- **Релиз ПК:** 28.04.2023 (Steam/EA App/EGS). Тяжёлые traversal-статтеры, проблемы компиляции шейдеров, CPU-горлышко даже на топ-GPU (DF/DSOG: просадки и микрофризы независимо от настроек).
- **Версии/патчи:** Патчи 1–9 (2023–2024): кэширование шейдеров, CPU-перф, RT, Denuvo-сценарии; позже DLSS 3 Frame Generation и multi-core улучшения. Полного устранения статтеров обхода не дали.
- **Причина репутации:** реализация (один из самых критикуемых AAA-портов 2023: высокий аппетит при нестабильном frame pacing).
- **Решения:**
  - `−` Крупные полуоткрытые локации Koboh/Jedha на стриминге с traversal-загрузками.
  - `−` Отложенная догрузка PSO/шейдерного кэша без prewarm: фризы при первом появлении эффектов.
  - `±` RT-отражения/освещение и тени при слабом CPU-скейлинге.
  - `±` FSR 2 / DLSS 2 (+ поздний DLSS 3 FG) и динамическое разрешение: поднимают средний FPS, но не лечат hitch.
- **Влияние:** оптимизация — хрестоматийный пример рисков UE4 open-zone без жёсткого PSO-precaching и traversal-бюджета.
- **DSS:** `world_partition_streaming`, `pso_precaching_warmup`, `temporal_upscaling`, `dynamic_resolution_scaling`, `hardware_raytraced_gi`.
- **Источники:** Steam (https://store.steampowered.com/app/1774580/STAR_WARS_Jedi_Survivor/), PCGW (https://www.pcgamingwiki.com/wiki/Star_Wars_Jedi:_Survivor), EA патчноуты (https://www.ea.com/games/starwars/jedi/jedi-survivor/news/patch-notes).

### 188. Forza Motorsport (2023, Turn 10 / ForzaTech)

- **Движок:** ForzaTech (новый рендер текущего поколения: динамическая погода/время суток, RT).
- **Релиз ПК:** Ранний доступ 05.10.2023, полный релиз 10.10.2023 (Steam/MS Store + Game Pass). Обязательный shader optimization при первом запуске (~20 сек на i9-12900K по DF) — почти без shader stutter. Сильная зависимость от single-core CPU, слабый скейлинг свыше 6 ядер.
- **Версии/патчи:** Update 1.0+ (конец 2023 — начало 2024): стабильность, CPU-перф, DLSS/FSR, баги графики/мультиплеера. Обещанная RTGI на ПК на старте отсутствовала.
- **Причина репутации:** реализация (образцовая борьба с шейдерными фризами, но CPU-лимиты, запутанное Performance Target / Dynamic Optimization, урезанный RT).
- **Решения:**
  - `+` Явная предкомпиляция PSO/шейдеров перед меню: устранение главного статтера 2023.
  - `±` Ограниченный RT: отражения только авто + RTAO вместо полного RTGI.
  - `+` TAA/DLAA/DLSS/FSR 2 + бенчмарк с отчётом.
  - `−` Привязка Performance Target к v-sync и отсутствие прозрачного dynamic resolution на ПК.
- **Влияние:** оптимизация — PSO-precaching решает шейдерный статтер, но не компенсирует однопоточный CPU-дизайн.
- **DSS:** `pso_precaching_warmup`, `temporal_upscaling`, `hardware_raytraced_gi`, `screen_space_gi`, `dynamic_resolution_scaling`.
- **Источники:** Steam (https://store.steampowered.com/app/2440510/Forza_Motorsport/), Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2023-forza-motorsport-pc-tech-review), DSOG (https://www.dsogaming.com/pc-performance-analyses/forza-motorsport-benchmarks-pc-performance-analysis/).

### 189. DRAGON BALL: Sparking! ZERO (2024, Spike Chunsoft / Unreal Engine 5)

- **Движок:** Unreal Engine 5 (без значимого Lumen/Nanite по анализу требований).
- **Релиз ПК:** 11.10.2024 в Steam (Deluxe ранний доступ 08.10.2024). Арена-файтинг 3D с cel-shading. Низкие требования: GTX 980 / RX 590 для 1080p/60 Low, RTX 2060 для High. Гладкий 60 FPS на мейнстрим-железе.
- **Версии/патчи:** Пострелизные патчи баланса, вылетов, сетевых ошибок/десинков. Точный список ПК-фиксов рендера — unstated.
- **Причина репутации:** реализация (лёгкий UE5-релиз за счёт стилизации и закрытых арен вместо открытого мира и тяжёлого GI).
- **Решения:**
  - `+` Аниме-стилизация с запечённым светом вместо hardware Lumen.
  - `+` Закрытые арены малого размера без world partition: нет traversal-статтеров.
  - `±` Пул частиц/ки-бластов и GPU-симуляция для ультов.
  - `±` Ограниченные графические опции и кап фреймрейта в бою: предсказуемость ценой high-refresh.
- **Влияние:** оптимизация — использование UE5 как рендера для файтинга без цены Lumen/Nanite (скоп, а не фичи).
- **DSS:** `art_direction_stylization`, `temporal_upscaling`, `particle_pooling`, `gpu_particle_simulation`, `animation_compression`.
- **Источники:** Steam (https://store.steampowered.com/app/1790600/DRAGON_BALL_Sparking_ZERO/), DSOG требования (https://www.dsogaming.com/news/dragon-ball-sparking-zero-official-pc-requirements/).

### 190. LEGO Star Wars: The Skywalker Saga (2022, TT Games / NTT)

- **Движок:** NTT (entity) — новый проприетарный движок TT Games; единственная выпущенная игра на нём.
- **Релиз ПК:** 05.04.2022 (Steam/EGS). Первый LEGO с полуоткрытыми хабами, Mumble Mode, боем от третьего лица. Хвалили за скачок графики, ругали за нестабильный FPS, вылеты, нет FOV-слайдера.
- **Версии/патчи:** Патчи 2022: вылеты, сейвы, кооп, перф; DLC-паки персонажей. Точные номера хотфиксов — unstated.
- **Причина репутации:** процесс (технологический перезапуск, омрачённый трудностью нового движка — Polygon 01.2022 о кранче; после релиза TT Games решила переходить на Unreal Engine).
- **Решения:**
  - `±` Хабовая структура из 24 планет-зон со стримингом вместо бесшовного open world.
  - `+` Иерархические LOD кирпичных ассетов и запечённая окклюзия интерьеров.
  - `+` Стилизация LEGO + селективный пост: читаемость на слабом железе (Switch/Steam Deck).
  - `−` Кооп split-screen и онлайн-ограничения + нет FOV/ultrawide.
- **Влияние:** процесс — риски смены движка внутри франшизы: визуальный скачок ценой пайплайна и поддержки.
- **DSS:** `async_loading_pipeline`, `hierarchical_lod`, `baked_occlusion_culling`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/920210/LEGO_Star_Wars_The_Skywalker_Saga/), PCGW (https://www.pcgamingwiki.com/wiki/Lego_Star_Wars:_The_Skywalker_Saga), Engine NTT (https://www.pcgamingwiki.com/wiki/Engine:NTT).

### 191. Marvel's Spider-Man Remastered ПК (2022, Insomniac/Nixxes / Insomniac Engine)

- **Движок:** Insomniac Engine (оригинал PS4/PS5) + порт Nixxes Software.
- **Релиз ПК:** 12.08.2022 (Steam/EGS). Предкомпиляция шейдеров, DLSS/FSR, тиры RT, ultrawide 21:9/32:9, DualSense. DF/DSOG: стабильный frame pacing, масштабирование от Steam Deck до RTX 4090.
- **Версии/патчи:** Патчи 1.x: HBAO+, XeSS, улучшения RT, фиксы вылетов, DLSS/Sharpness. Steam Deck Verified.
- **Причина репутации:** реализация (эталонный ПК-порт Sony 2022: полный набор апскейлеров и RT-тиров без статтеров релизной недели).
- **Решения:**
  - `+` PSO-precaching/warmup при запуске и смене настроек: нет shader stutter.
  - `+` Тирированный RT (отражения разного качества/разрешения) + screen-space fallback.
  - `+` DLSS/FSR/XeSS + dynamic resolution scaling: линейный рост FPS в свинге.
  - `±` Стриминг города на скорости веб-шутера с async-загрузкой: нет загрузок при фаст-тревеле на SSD, высокое требование к I/O на HDD.
- **Влияние:** контент — планка портов Nixxes для Sony: prewarm + RT-tiers + ultrawide из коробки.
- **DSS:** `world_partition_streaming`, `pso_precaching_warmup`, `temporal_upscaling`, `dynamic_resolution_scaling`, `hardware_raytraced_gi`.
- **Источники:** Steam (https://store.steampowered.com/app/1817070/Marvels_SpiderMan_Remastered/), PCGW (https://www.pcgamingwiki.com/wiki/Marvel%27s_Spider-Man_Remastered).

### 192. Marvel's Spider-Man: Miles Morales ПК (2022, Insomniac/Nixxes / Insomniac Engine)

- **Движок:** Insomniac Engine + порт Nixxes Software (та же ветка, что Remastered).
- **Релиз ПК:** 18.11.2022 (Steam/EGS). Более короткая зимняя история в Гарлеме с тем же набором DLSS/FSR/XeSS, RT-отражениями, ultrawide. Требования чуть выше (снег, толпа, RT).
- **Версии/патчи:** Патчи синхронны с Remastered: XeSS, HBAO+, фиксы RT/ultrawide и вылетов. Номера — unstated.
- **Причина репутации:** реализация (подтверждение повторяемости качества Nixxes: второй порт без регресса перф).
- **Решения:**
  - `+` Тот же PSO-warmup и async-стриминг snowy Manhattan.
  - `+` Crowd-толпа на инстансинге/импостерах в праздничных сценах.
  - `±` Volumetric-снег и пост-эффекты в половинном разрешении.
  - `±` Более тяжёлые RT-сцены с отражениями в снегу/слякоти.
- **Влияние:** контент — масштабируемость Insomniac Engine на ПК при смене сезона/толпы без смены пайплайна.
- **DSS:** `world_partition_streaming`, `crowd_instancing_impostors`, `temporal_upscaling`, `volumetric_half_resolution`, `hardware_raytraced_gi`.
- **Источники:** Steam (https://store.steampowered.com/app/1817190/Marvels_SpiderMan_Miles_Morales/), PCGW (https://www.pcgamingwiki.com/wiki/Marvel%27s_Spider-Man:_Miles_Morales).

### 193. DEATH STRANDING DIRECTOR'S CUT ПК (2022, Kojima / Decima)

- **Движок:** Decima (Guerrilla Games) — тот же, что у Horizon Zero Dawn.
- **Релиз ПК:** Director's Cut 30.03.2022 (Steam/EGS, 505 Games); оригинал на ПК с 14.07.2020. Добавил трассу, оружие, механики доставки, расширенный сюжет. Ultrawide, DLSS 2, одна из первых игр с Intel XeSS.
- **Версии/патчи:** Патчи XeSS/DLSS, ultrawide-катсцены, вылеты; производительность изначально высокая — 60–120+ FPS на среднем железе с быстрыми загрузками на SSD.
- **Причина репутации:** реализация (образцовый Decima-порт: линейно-открытый мир без статтеров обхода, отличный temporal AA).
- **Решения:**
  - `+` Асинхронный пайплайн загрузки ландшафта Decima + SSD-стриминг.
  - `+` Временные апскейлеры DLSS 2 / XeSS + качественный TAA.
  - `+` Иерархические LOD скал/грузов и instancing растительности.
  - `±` Качественные тиры без hardware RT GI: художественный свет без цены трассировки.
- **Влияние:** контент — Decima как один из самых ПК-дружелюбных движков; раннее внедрение XeSS повлияло на другие порты 505 Games.
- **DSS:** `async_loading_pipeline`, `temporal_upscaling`, `hierarchical_lod`, `gpu_instancing_vegetation`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/1850570/DEATH_STRANDING_DIRECTORS_CUT/), PCGW (https://www.pcgamingwiki.com/wiki/Death_Stranding_Director%27s_Cut).

---

## Партия 24 (список-3, батч 18: №194–201)

### 194. The Quarry (2022, Supermassive / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (PhysX, Wwise, Bink, SpeedTree по MobyGames).
- **Релиз ПК:** Windows 10.06.2022 одновременно с PS4/PS5/Xbox One/Series (2K). Single-player, co-op, shared/split-screen, Movie Mode. Spiritual successor Until Dawn про девять вожатых лагеря Хакетта.
- **Версии/патчи:** Standard/Deluxe с Gorefest-режимом Movie Mode, Death Rewind, Horror History Visual Filter Pack. Пострелизные ПК-патчи — unstated.
- **Причина репутации:** функционал (Generally positive: нарратив, каст, графика, оммажи слэшерам 80-х; ругали мало интерактива, abrupt endings, камеру; громкого ПК-скандала со статтерами не было).
- **Решения:**
  - `+` Линейные кинематографичные уровни с запечённым светом и окклюзией: стабильные 60 fps.
  - `±` Movie Mode + Death Rewind / слот-сейвы для интерактивного кино.
  - `−` Лицевая анимация и performance capture ансамбля: цена кадра.
  - `+` Tiered-настройки без RT-флага, упор на temporal AA и пост-эффекты.
- **Влияние:** null; формула Supermassive после Until Dawn / Dark Pictures без технологического сдвига.
- **DSS:** `baked_occlusion_culling`, `lightmap_atlas_baking`, `animation_compression`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/1577120/The_Quarry/), Wikipedia (https://en.wikipedia.org/wiki/The_Quarry_(video_game)).

### 195. Tiny Tina's Wonderlands (2022, Gearbox / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (PCGW).
- **Релиз ПК:** Первично 25.03.2022 как EGS-эксклюзив с консолями; в Steam 23.06.2022, crossplay PS5/PS4/Xbox/EGS/Steam. Спин-офф Borderlands: multiclass-герой против Dragon Lord.
- **Версии/патчи:** Chaotic Great Edition, Season Pass / 4 DLC (Coiled Captors и др.). Баланс, co-op, Shift-crossplay правились хотфиксами; детали — unstated.
- **Причина репутации:** функционал (Mostly Positive ~71%: юмор, билд-крафт, кооп; ругали эндгейм-гринд, баланс хаоса, техсостояние порта; шейдерного скандала уровня Callisto не было).
- **Решения:**
  - `+` Stylized-арт + инстансинг лута/врагов для кооп-шутера.
  - `±` Async-загрузка зон Overworld и данжей для бесшовного коопа.
  - `+` Пул частиц стволов/заклинаний вместо уникальных симуляций.
  - `−` Relevancy-фильтрация репликации лута/эффектов в коопе 1–4 игрока.
- **Влияние:** null; подтверждение Borderlands-формулы в фэнтези-обёртке.
- **DSS:** `async_loading_pipeline`, `particle_pooling`, `network_relevancy_priority`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/1286680/Tiny_Tinas_Wonderlands/), PCGW (https://www.pcgamingwiki.com/wiki/Tiny_Tina%27s_Wonderlands).

### 196. The Callisto Protocol (2022, Striking Distance / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (Krafton).
- **Релиз ПК:** 02.12.2022 (ПК/консоли). Хоррор Glen Schofield (экс-Dead Space) про тюрьму Black Iron на Каллисто. Лавина негативных отзывов Steam из-за статтеров.
- **Версии/патчи:** Day-1 патч содержал wrong file (clerical error по Schofield). Патч 03–04.12.2022 вынес компиляцию шейдеров в меню при первом запуске; дальнейшие оптимизации — последующими апдейтами.
- **Причина репутации:** реализация (The Stuttering Protocol: UE4 без прекомпиляции — фриз при каждом появлении ассетов, хуже на слабых CPU; DSOG: первый патч фиксит только shader stutters, остаются traversal-микростаттеры и тяжёлый RT).
- **Решения:**
  - `−` Отсутствие PSO-прекеша на релизе: статтеры компиляции при стриминге.
  - `±` Вынос шейдерной компиляции в меню первым патчем.
  - `−` Half-res volumetrics + RT-отражения без fallback-пресета для слабых ПК.
  - `+` Линейный хоррор-коридор с высоким качеством ассетов/освещения.
- **Влияние:** оптимизация — хрестоматийный кейс UE4 shader compilation stutter 2022 наряду с Gotham Knights / Elden Ring; требование PSO-precaching.
- **DSS:** `pso_precaching_warmup`, `async_loading_pipeline`, `volumetric_half_resolution`, `hardware_raytraced_gi`.
- **Источники:** PC Gamer (https://www.pcgamer.com/patch-fixes-the-callisto-protocols-stuttering-which-glen-schofield-blames-on-a-freakin-error/), Engadget (https://www.engadget.com/the-callisto-protocol-patch-performance-patch-225131596.html).

### 197. Suicide Squad: Kill the Justice League (2024, Rocksteady / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (Warner Bros.).
- **Релиз ПК:** Ранний доступ Deluxe 29.01.2024, полный релиз 02.02.2024 (PS5/Xbox Series/Windows; EGS задержан до 03.2024). Open-world action-shooter от создателей Arkham.
- **Версии/патчи:** Несколько переносов с 2022 на 2024. Day-1 баг полного автопрохождения с остановкой серверов и компенсацией; сезонные story-апдейты, финал поддержки 01.2025.
- **Причина репутации:** процесс (Mixed ~62%, Metacritic 63: хвалили нарратив/геймплей, ругали репетитивность и live-service; коммерческий провал против ожиданий Warner Bros.).
- **Решения:**
  - `±` Open-world Metropolis на UE4 со стримингом районов для траверса/полётов.
  - `−` Кооп 1–4 с приоритизацией репликации и тикрейт-бюджетом.
  - `±` Крауд/трафик и импостеры для живого города при CPU-бюджете.
  - `−` Live-service сезоны поверх сингловой кампании: повторный гринд.
- **Влияние:** процесс — усталость от live-service переделки сингл-студии; откат Warner Bros. от GAAS-модели.
- **DSS:** `world_partition_streaming`, `network_relevancy_priority`, `crowd_instancing_impostors`, `tickrate_budgeting`.
- **Источники:** Steam (https://store.steampowered.com/app/315210/Suicide_Squad_Kill_the_Justice_League/), Wikipedia (https://en.wikipedia.org/wiki/Suicide_Squad:_Kill_the_Justice_League).

### 198. Call of Duty: Modern Warfare II (2022, Infinity Ward / IW 9.0)

- **Движок:** IW 9.0 (Havok, Bink, Umbra 3 по MobyGames).
- **Релиз ПК:** Ранний доступ кампании 20.10.2022, полный релиз 28.10.2022 (PS4/PS5/Xbox One/Series, ПК Steam + Battle.net). Первая CoD в Steam с 2017. Единый движок и лаунчер Call of Duty HQ с Warzone 2.0 (16.11.2022).
- **Версии/патчи:** Бета 16–26.09.2022 (крупнейшая в истории серии); сезонные апдейты, Ricochet Anti-Cheat на старте, Vault/Cross-Gen Edition. Техдетали патчей — unstated.
- **Причина репутации:** функционал (блокбастер: хвалили графику/звук, критиковали SBMM, UI HQ-лаунчера, DMZ/Warzone-интеграцию; на ПК — требовательность и читеры против Ricochet, а не шейдерный статтер).
- **Решения:**
  - `±` Новая hybrid tile-based streaming + PBR decals + GPU geometry pipeline для 4K HDR.
  - `+` Единый движок MWII / Warzone 2.0 для бесшовного контента и прогрессии.
  - `−` Client prediction + relevancy-приоритеты для 64+ игроков и DMZ AI.
  - `+` Temporal upscaling + dynamic resolution для 120+ fps в мультиплеере.
- **Влияние:** контент — стандарт unified engine/launcher для CoD (HQ); PBR и volumetric IW 9 как база Warzone 2.0.
- **DSS:** `world_partition_streaming`, `client_prediction_reconciliation`, `network_relevancy_priority`, `temporal_upscaling`, `dynamic_resolution_scaling`.
- **Источники:** PCGW (https://www.pcgamingwiki.com/wiki/Call_of_Duty:_Modern_Warfare_II), Wikipedia (https://en.wikipedia.org/wiki/Call_of_Duty:_Modern_Warfare_II).

### 199. NBA 2K23 (2022, Visual Concepts / собственный; ПК previous-gen)

- **Движок:** null — проприетарный движок Visual Concepts; ПК — previous-gen ветка (не PS5/Xbox Series).
- **Релиз ПК:** 08–09.09.2022 (PS5/PS4/Xbox Series/Xbox One/Switch/ПК). ПК сознательно оставлен на previous-gen базе (FAQ 2K / IGN).
- **Версии/патчи:** MyCAREER-круизер, Jordan Challenge, MyTEAM/MyGM/MyLEAGUE. Серверы отключены 31.12.2024, продажа прекращена 30.11.2024. Номера патчей — unstated.
- **Причина репутации:** процесс (негатив ПК за второй год без next-gen апгрейда при полной цене + монетизация MyTEAM, читеры).
- **Решения:**
  - `−` Previous-gen ветка на ПК: низкий порог (GT 450 / HD 7770, 4 ГБ RAM) ценой визуала.
  - `±` Круизер-хаб вместо City next-gen для онлайна и матчмейкинга.
  - `+` Анимационный пул dribble/contact-систем с компрессией для 10 игроков.
  - `±` Relevancy-приоритеты онлайна для Park/Rec при P2P/серверной модели.
- **Влияние:** процесс — практика двух веток 2K (next-gen vs PC/Switch); давление привело к next-gen ПК только с NBA 2K24.
- **DSS:** `animation_compression`, `animation_lod_budget`, `crowd_instancing_impostors`, `network_relevancy_priority`.
- **Источники:** Steam (https://store.steampowered.com/app/1919590/NBA_2K23/), IGN (https://www.ign.com/articles/nba-2k23-on-pc-is-still-the-previous-gen-version).

### 200. Lethal Company EA (2023, Zeekerss / Unity)

- **Движок:** Unity (соло-разработчик Zeekerss, ex-Roblox).
- **Релиз ПК:** Early Access 23.10.2023 только Windows. Кооп survival-horror про сбор скрапа на лунах с квотой; Overwhelmingly Positive (~97%).
- **Версии/патчи:** EA-старт с 7+ планетами, 9+ существами, 8 инструментами, бестиарием. План завершить за 6 месяцев не выполнен — осталась в EA с контент/баланс-апдейтами.
- **Причина репутации:** функционал (феномен Twitch/YouTube: proximity voice, кооп до 4, хоррор-джанк, $9.99, 100 тыс.+ онлайна при примитивной графике).
- **Решения:**
  - `+` Низкополигональный Unity-рендер + quality tiers для GTX 1050 и слабых CPU.
  - `+` Процедурные интерьеры комплексов поверх статичных лун: реиграбельность малыми средствами.
  - `−` P2P кооп Steam + proximity voice без dedicated-серверов: дёшево, но читы/десинки.
  - `±` Пул врагов/лута и сканирование в бестиарий вместо тяжёлой симуляции.
- **Влияние:** контент — эталон соло-EA 2023; сила системного кооп-хоррора и UGC-мемов над графикой.
- **DSS:** `quality_tier_scalability`, `network_relevancy_priority`, `particle_pooling`, `snapshot_slot_saves`.
- **Источники:** Steam (https://store.steampowered.com/app/1966720/Lethal_Company/), Wikipedia (https://en.wikipedia.org/wiki/Lethal_Company).

### 201. Resident Evil 4 Remake (2023, Capcom / RE Engine)

- **Движок:** RE Engine (проприетарный Capcom).
- **Релиз ПК:** 24.03.2023 (PS5/PS4/Xbox Series, ПК $59.99; Deluxe $69.99). Ремейк RE4 (2005): Леон и Эшли против Los Iluminados (стелс, парирование, кейс). Chainsaw Demo, Mercenaries как free DLC 07.04.2023, VR Mode как free DLC. Поддержка RT-отражений и FSR 2 на старте без DLSS 2; патчи — мышь и перф.
- **Версии/патчи:** Chainsaw Demo; Mercenaries 07.04.2023; VR Mode; патчи управления мышью и производительности.
- **Причина репутации:** реализация (образцовый ремейк и ПК-порт DSOG/OC3D: богатейшие настройки с превью, дружелюбный RT, высокие fps; минусы — traversal-статтеры, прожорливость Max-текстур к VRAM, чувствительность мыши).
- **Решения:**
  - `+` Только RT-отражения вместо полного RT GI: большой выигрыш при малой цене.
  - `±` FSR 2 + temporal AA и детальные пресеты текстур/волос/трупов.
  - `−` Async-стриминг деревни/замка/шахт с редкими traversal-статтерами.
  - `+` Расширенные слайдеры с live-превью и FOV-слайдер.
- **Влияние:** оптимизация — эталон RE Engine-порта после Village; планка настроек/превью для Capcom-портов.
- **DSS:** `hardware_raytraced_gi`, `temporal_upscaling`, `async_loading_pipeline`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/2050650/Resident_Evil_4/), DSOG (https://www.dsogaming.com/pc-performance-analyses/resident-evil-4-remake-pc-performance-analysis/).

---

## Партия 25 (список-3, батч 19: №202–209)

### 202. Starfield (2023, Bethesda / Creation Engine 2)

- **Движок:** Creation Engine 2 (Havok, Wwise, Scaleform GFx, Bink; участие id Software в части id Tech-технологий по IGN).
- **Релиз ПК:** Windows (Steam/MS Store) 06.09.2023, ранний доступ Premium с 01.09; также Game Pass for PC. Критика за перф, особенно на Nvidia, и отсутствие DLSS/XeSS без модов.
- **Версии/патчи:** Update 1.8.86 (20.11.2023) — DLSS + DLSS Frame Generation, HDR Brightness; 1.9.51.0 (30.01.2024) — 32:9/21:9/16:10; 1.9.67 — FSR 3 + FG, XeSS 1.2.
- **Причина репутации:** реализация (CPU-зависимость в New Atlantis/Akila City, низкий FPS без апскейла, перекос AMD/Nvidia на старте по DSOG).
- **Решения:**
  - `+` Добавление DLSS/DLAA+FG в 1.8.86: выбор апскейла вместо только FSR2.
  - `+` Добавление FSR 3+FG и XeSS 1.2 в 1.9.67: покрытие Intel/AMD.
  - `±` Драйверные оптимизации Nvidia + последующие патчи перф.
  - `±` Моды SFSE/StarUI/Undelayed Menus и StarfieldCustom.ini (FOV, HUD, пропуск интро): лечат UI/UX, не ядро рендера.
- **Влияние:** оптимизация — кейс обязательного DLSS/XeSS на старте для AAA на DX12; давление на Bethesda по открытости настроек.
- **DSS:** `async_loading_pipeline`, `hierarchical_lod`, `temporal_upscaling`, `dynamic_resolution_scaling`.
- **Источники:** Steam (https://store.steampowered.com/app/1716740/Starfield/), PCGW (https://www.pcgamingwiki.com/wiki/Starfield), DSOG (https://www.dsogaming.com/pc-performance-analyses/starfield-pc-performance-analysis/).

### 203. Pacific Drive (2024, Ironwood / Unreal Engine 4)

- **Движок:** Unreal Engine 4.
- **Релиз ПК:** 22.02.2024 (ПК Steam/EGS, PS5). Survival-драйвинг в Зоне: хаб-гараж + вылазки. На старте жалобы Steam на статтеры обхода мира и просадки на средних ПК.
- **Версии/патчи:** Хотфиксы Ironwood 2024 (Steam News): перф, зависания при переходах, генерация шейдеров, стабильность. Номера версий — unstated.
- **Причина репутации:** реализация (траверс-хитчи UE4 при стриминге локаций и шейдерные фризы на DX12 без прогретого PSO-кэша).
- **Решения:**
  - `±` Патчи оптимизации стриминга и фиксы утечек/зависаний.
  - `±` Настройки качества/масштаб разрешения + FSR/TSR UE4.
  - `±` Обход через снижение растительности/теней/дальности.
  - `−` Ручное предкомпилирование шейдеров средствами игры — unstated.
- **Влияние:** null как отдельный кейс; типовой пример UE4-статтера 2024.
- **DSS:** `pso_precaching_warmup`, `world_partition_streaming`, `quality_tier_scalability`, `dynamic_resolution_scaling`.
- **Источники:** Steam (https://store.steampowered.com/app/1458140/Pacific_Drive/), PCGW (https://www.pcgamingwiki.com/wiki/Pacific_Drive), DSOG (https://www.dsogaming.com/pc-performance-analyses/pacific-drive-pc-performance-analysis/).

### 204. SOUTH PARK: SNOW DAY! (2024, Question / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (Question/THQ Nordic).
- **Релиз ПК:** 26.03.2024 (ПК/PS5/Xbox Series/Switch). Кооп-рогулайк 3D вместо 2D-формулы Stick of Truth/Fractured. Низкие оценки прессы и смешанно-негативные Steam: короткая, сырая, баланс, сеть.
- **Версии/патчи:** Хотфиксы: краши, матчмейкинг, баланс карт/оружия. Номера — unstated.
- **Причина репутации:** функционал (провал смены формулы франшизы; малая длительность, повторяемость, баги коопа; технически скромный UE4-проект).
- **Решения:**
  - `±` Хотфиксы крашей и подбора игроков.
  - `+` Стилизованный арт вместо фотореализма: низкие требования.
  - `±` Скейл качества UE4 + кап FPS.
  - `−` Выделенные серверы — unstated (P2P/сессионная модель).
- **Влияние:** null в рендер-технике; пример провала смены формулы франшизы.
- **DSS:** `art_direction_stylization`, `quality_tier_scalability`, `client_prediction_reconciliation`, `gpu_particle_simulation`.
- **Источники:** Steam (https://store.steampowered.com/app/1214650/SOUTH_PARK_SNOW_DAY/), PCGW (https://www.pcgamingwiki.com/wiki/South_Park:_Snow_Day!), PC Gamer (https://www.pcgamer.com/south-park-snow-day-review/).

### 205. PAYDAY 3 (2023, Starbreeze / Unreal Engine 4)

- **Движок:** Unreal Engine 4 (Starbreeze).
- **Релиз ПК:** 21.09.2023 (ПК/PS5/Xbox Series). Always-online с кроссплеем. Лаунч провален очередями, ошибками матчмейкинга Nebula, недоступностью даже соло. Пик негатива Steam.
- **Версии/патчи:** Патчи 1.x осени 2023 + план Operation Medic Bag (2024): серверная ёмкость, стабильность, позже соло offline-бета. Номера — unstated.
- **Причина репутации:** процесс (серверная инфраструктура и обязательный онлайн, а не сырой FPS; фактически неиграбельна первую неделю).
- **Решения:**
  - `±` Расширение/починка бэкенда и очередей Nebula.
  - `+` Введение офлайн-соло: снятие зависимости от серверов.
  - `±` Апскейлы UE4 (DLSS/FSR) + пресеты качества.
  - `−` Переход на выделенные региональные серверы — unstated.
- **Влияние:** сеть — хрестоматийный кейс вреда always-online для кооп-шутера; причина Medic Bag.
- **DSS:** `headless_dedicated_server`, `client_prediction_reconciliation`, `network_relevancy_priority`, `temporal_upscaling`.
- **Источники:** Steam (https://store.steampowered.com/app/1272080/PAYDAY_3/), PCGW (https://www.pcgamingwiki.com/wiki/Payday_3), PC Gamer (https://www.pcgamer.com/payday-3-review/).

### 206. Warhammer 40,000: Space Marine 2 (2024, Saber / Swarm Engine)

- **Движок:** Swarm Engine (собственный Saber).
- **Релиз ПК:** 09.09.2024 (ПК/PS5/Xbox Series; ранний доступ 05.09 для Gold/Ultra). Кооп-кампания + Eternal War + Operations с сотнями тиранидов. Жалобы на CPU-горлышко, компиляцию шейдеров, краши.
- **Версии/патчи:** Хотфиксы и крупные патчи Saber/Focus (осень 2024–2025, Steam News): краши, CPU-оптимизация, ultrawide/FOV, DLSS/FSR. Номера — unstated.
- **Причина репутации:** реализация (роевой рендер и ИИ толпы грузят CPU даже на 6–8 ядрах; DSOG/DF тех-обзор).
- **Решения:**
  - `+` Толпа через инстансинг/импостеры и LOD анимации: масштаб без поштучных draw calls.
  - `+` Многопоточные джобы физики/ИИ роя.
  - `±` DLSS/FSR + динамическое разрешение.
  - `±` PSO-прогрев/кэш при первом запуске: меньше фризов ценой долгой первой загрузки.
- **Влияние:** оптимизация — эталон swarm-tech 2024 для инстансинга толп; пример CPU-лимита при сотнях агентов.
- **DSS:** `crowd_instancing_impostors`, `animation_lod_budget`, `multithreaded_physics_jobs`, `temporal_upscaling`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/2183900/Warhammer_40000_Space_Marine_2/), PCGW (https://www.pcgamingwiki.com/wiki/Warhammer_40,000:_Space_Marine_2), DSOG (https://www.dsogaming.com/pc-performance-analyses/warhammer-40000-space-marine-2-pc-performance-analysis/).

### 207. EA SPORTS FC 24 (2023, EA Canada / Frostbite; снята с продажи)

- **Движок:** Frostbite (EA Canada).
- **Релиз ПК:** 29.09.2023 (ПК/консоли), первая игра после разрыва с FIFA. Версия ПК с HyperMotionV и кроссплеем. Снята с продажи в Steam/EA App ahead FC 25.
- **Версии/патчи:** Title Updates EA Canada 2023–2024: геймплей, Ultimate Team, стабильность, контроллеры. Номера TU — unstated.
- **Причина репутации:** процесс (микростаттеры в катсценах/меню, лок 30 fps в повторах, конфликты EA anticheat, краши; слабая разница с FIFA 23 за полную цену).
- **Решения:**
  - `±` Патчи TU + обновления EAAC-драйвера.
  - `±` Лок катсцен/ограничение FPS для ровного пейсинга.
  - `±` Снижение пресетов/отключение Strand Hair/толпы.
  - `−` Полное устранение шейдерных хитчей Frostbite — unstated.
- **Влияние:** null в технике; кейс делистинга спортивных ежегодников EA.
- **DSS:** `animation_compression`, `animation_lod_budget`, `temporal_upscaling`, `pso_precaching_warmup`, `quality_tier_scalability`, `crowd_instancing_impostors`.
- **Источники:** Steam (https://store.steampowered.com/app/2195250/EA_SPORTS_FC_24/), PCGW (https://www.pcgamingwiki.com/wiki/EA_Sports_FC_24).

### 208. Enshrouded EA (2024, Keen Games / собственный Holistic Engine, воксельный)

- **Движок:** Собственный Holistic Engine (воксельный).
- **Релиз ПК:** Ранний доступ 24.01.2024 только ПК (Steam). Воксельный survival-craft до 16 игроков с терраформингом/строительством. Хит EA с жалобами на просадки в крупных базах и дальности.
- **Версии/патчи:** Частые хотфиксы Keen Games 2024 (Steam News) + крупные EA-обновления (Hollow Halls и далее): LOD вокселей, растительность, DLSS/FSR, стабильность серверов. Номера — unstated.
- **Причина репутации:** реализация (позитивная EA, но требовательность воксельного мира: CPU/GPU от разрушения/строительства и растительности).
- **Решения:**
  - `+` Воксельные LOD и кэш геометрии разрушений.
  - `+` GPU-инстансинг растительности + дистанционные LOD.
  - `±` Временной апскейл + скейл воксельной детализации/дальности.
  - `±` Асинхронный стриминг чанков.
- **Влияние:** контент — кастомный воксельный движок для survival в эпоху UE5; ориентир оптимизации строительства.
- **DSS:** `hierarchical_lod`, `destruction_geometry_cache`, `gpu_instancing_vegetation`, `temporal_upscaling`, `async_loading_pipeline`, `headless_dedicated_server`.
- **Источники:** Steam (https://store.steampowered.com/app/1203620/Enshrouded/), PCGW (https://www.pcgamingwiki.com/wiki/Enshrouded), Enshrouded News (https://enshrouded.com/news/).

### 209. God of War Ragnarök ПК (2024, Santa Monica/Jetpack / собственный)

- **Движок:** Собственный движок Santa Monica Studio, ПК-порт Jetpack Interactive.
- **Релиз ПК:** 19.09.2024 (Steam/EGS), включая Valhalla. Поддержка 21:9/32:9, DLSS/FSR/XeSS + генерация кадров, unlocked FPS. DF/DSOG: качественный порт, но старт с требованием PSN-аккаунта и шейдерной компиляцией при первом запуске.
- **Версии/патчи:** Пост-релизные патчи Jetpack/SMS (осень 2024–2025, Steam News): краши на RTX, HDR, контроллеры, перф. Номера — unstated.
- **Причина репутации:** реализация (позитивная техническая репутация: стабильный пейсинг, широкие опции апскейла, корректный HDR/ultrawide; негатив — вокруг PSN, а не рендера).
- **Решения:**
  - `+` Предкомпиляция PSO при первом запуске: убирает ин-гейм статтер ценой ожидания.
  - `+` Полный набор DLSS/FSR/XeSS + Frame Generation.
  - `+` Гибкие пресеты + динамическое разрешение.
  - `±` Каскадные тени высокого разрешения без RT GI: стабильность без прорыва освещения.
- **Влияние:** оптимизация — эталон ПК-порта Sony 2024 наряду с Ghost of Tsushima; стандарт PSO-прогрева и ultrawide.
- **DSS:** `pso_precaching_warmup`, `temporal_upscaling`, `ml_frame_generation`, `cascaded_shadow_maps`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/2322010/God_of_War_Ragnarok/), PCGW (https://www.pcgamingwiki.com/wiki/God_of_War_Ragnar%C3%B6k), DSOG (https://www.dsogaming.com/pc-performance-analyses/god-of-war-ragnarok-pc-performance-analysis/).

---

## Партия 26 (список-3, финал A: №210–217)

### 210. Diablo IV (2023, Blizzard / собственный)

- **Движок:** Собственный движок Blizzard, без трассировки на старте.
- **Релиз ПК:** Ранний доступ Ultimate 02.06.2023, полный релиз 06.06.2023. Масштабируется от GTX 1060 / i7-3770K в 1080p до 4K/100+ fps на RTX 4080 + i7-13700K. Always-online, нет офлайна.
- **Версии/патчи:** Патч 1.3.5 (26.03.2024): RT-тени, RT-отражения, обновлённые AO и Contact Shadows + DLSS 3 Frame Generation / Reflex.
- **Причина репутации:** реализация (эталон масштабируемости Blizzard, но скандал с VRAM: Ultra-текстуры = уровень PS5 только на 16 ГБ VRAM, на 8 ГБ — статтеры до 500 мс).
- **Решения:**
  - `+` FSR 2-реконструкция на консолях (~1260p → 4K), DLSS/FSR на ПК + масштабируемость (двухъядерник тянет 150 fps в 1080p Ultra).
  - `−` Ultra-текстуры требуют ~15 ГБ VRAM в 4K; High заметно хуже, Medium/Low — мыло.
  - `±` Теневые карты + SSAO: снижение SSAO High→Medium +12% fps, теней Highest→High +5.5% почти без потери качества.
  - `±` Шейдерный статтер минимален, но спорадические 500-мс просадки (похожи на сетевые из-за always-online).
- **Влияние:** оптимизация — проблема 2023 не шейдеры, а VRAM-бюджет текстур; ComputerBase: RTX 4070 12 ГБ проигрывает RX 6800 XT 16 ГБ.
- **DSS:** `temporal_upscaling`, `quality_tier_scalability`, `async_loading_pipeline`, `cascaded_shadow_maps`, `agent_update_budget`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2023-diablo-4-is-a-great-pc-port-except-you-need-a-16gb-graphics-card-to-match-ps5-quality), Blizzard RT (https://news.blizzard.com/en-us/article/24077218/hells-beauty-burns-anew-with-ray-tracing), DSOG (https://www.dsogaming.com/pc-performance-analyses/diablo-4-pc-performance-analysis/).

### 211. Senua's Saga: Hellblade II (2024, Ninja Theory / Unreal Engine 5.3)

- **Движок:** Unreal Engine 5.3, Nanite + software Lumen + Virtual Shadow Maps + TSR.
- **Релиз ПК:** 21.05.2024 день-в-день с Xbox Series. Линейное кино ~1296p–1440p на Series X с чёрными полосами; на ПК разблокированный fps, DRS, DLSS/FSR/XeSS + FG.
- **Версии/патчи:** Крупные технопатчи — unstated; шиппинг-версия UE 5.3 с поддержкой движущейся фолиадж-Nanite (DF).
- **Причина репутации:** реализация (витрина UE5 и образцовое ПК-меню с превью и ms-метриками, но traversal-статтер и шипы VRAM на 8 ГБ).
- **Решения:**
  - `+` Фоновая прекомпиляция шейдеров при настройке (40 сек на 7800X3D, ~90 сек на 3600): почти нет PSO-статтера.
  - `+` Меню с live-превью, ms-стоимостью опций, V-Sync 1/2/1/3/1/4 и редкий для UE5 DRS.
  - `−` Traversal-статтер на границах стриминга: 16–24 мс на 7800X3D, x2 на 3600; на Xbox его нет.
  - `−` 8 ГБ VRAM: волна в интро на RTX 4060 8 ГБ даёт огромный шип в 1440p, на RTX 3060 12 ГБ его нет; лечится Low-текстурами + 1080p.
- **Влияние:** оптимизация — урок UE5-студиям: прекомпиляцию + прозрачное меню копировать, стриминг и VRAM-менеджмент чинить на уровне Epic.
- **DSS:** `pso_precaching_warmup`, `temporal_upscaling`, `dynamic_resolution_scaling`, `volumetric_half_resolution`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2024-senuas-saga-hellblade-2-pc-tech-review), DSOG (https://www.dsogaming.com/pc-performance-analyses/senuas-saga-hellblade-2-benchmarks-pc-performance-analysis/).

### 212. SILENT HILL 2 Remake (2024, Bloober Team / Unreal Engine 5 + Lumen/Nanite)

- **Движок:** Unreal Engine 5, Lumen (software на PS5, software/hardware на ПК), Nanite.
- **Релиз ПК:** 08.10.2024 одновременно с PS5. На ПК выше PS5 за счёт hardware Lumen (опция Ray Tracing), DLSS/XeSS/FSR, DRS на TSR. Шейдерного статтера нет — компиляция в загрузке со всеми ядрами.
- **Версии/патчи:** Патч 1.04 (21.10.2024): нативный DLSS 3 Frame Generation + Reflex, FSR 3.1.1 + Fluid Motion Frames, фикс статтера sky map, тоггл HZB culling, фикс DLSS-глитчей.
- **Причина репутации:** реализация («stutter struggle» UE5: traversal-статтер + animation-статтер при каппе 30 fps из-за delta-time + лок 30 fps катсцен и тканей).
- **Решения:**
  - `+` Отсутствие PSO-статтера за счёт компиляции в фоне/загрузке.
  - `±` Hardware Lumen на ПК заметно лучше software (отражения, непрямой свет), но flicker травы, boiling-денойз, трейлы листвы.
  - `−` Traversal-статтер везде: 16–25 мс на 7800X3D, ~33–75 мс на 3600, на PS5 пачки 50–66 мс.
  - `−` Кап 30 fps не прячет рывки: анимация дёргается при идеальных 33.3 мс; фикс только fixed-tick launch-параметром.
- **Влияние:** оптимизация — кейс DF о фундаментальной болезни UE5, не чинящейся модами и DLSS-свопами.
- **DSS:** `world_partition_streaming`, `pso_precaching_warmup`, `temporal_upscaling`, `hardware_raytraced_gi`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2024-silent-hill-2-on-pc-another-unreal-engine-5-game-blighted-by-stuttering-issues), DSOG (https://www.dsogaming.com/pc-performance-analyses/silent-hill-2-remake-pc-performance-analysis/).

### 213. Until Dawn Remake (2024, Ballistic Moon / Unreal Engine 5; оригинал 2015 Decima)

- **Движок:** Ремейк — перевод с Decima на Unreal Engine 5; оригинал 2015 — Supermassive / Decima.
- **Релиз ПК:** 04.10.2024 одновременно с PS5. На ПК Ultra-пресет, VSM, DLSS/FSR 3 + FG; на PS5 30 fps, DRS 1440p–4K (типично 1800p). Долгая первичная компиляция шейдеров убирает PSO-статтер.
- **Версии/патчи:** Патч 1.05: на PS5 починен пейсинг 30 fps, но сломаны пререндер-ролики (тиринг); на ПК RT стал давать −33% fps, но FSR 3 FG не включается, тоггл VSM не меняет картинку.
- **Причина репутации:** процесс (провальный запуск: неработающие RT, FSR FG, HDR в SDR-контейнере, VSM-артефакты, деградация при смене апскейлера).
- **Решения:**
  - `+` Переход Decima→UE5: новые материалы, VSM-тени без фликера, чистые волюметрики, RT AO.
  - `−` DLSS FG работает (RTX 4090 ~100 fps в 4K DLAA+FG), FSR 3 FG самовыключался/без эффекта.
  - `−` RT-отражения/AO на 1.04 не влияли на fps и картинку, VSM — просадка + блочные артефакты.
  - `−` Смена Native/DLSS/FSR без рестарта роняет fps (54→47 в 4K), смена настроек — фризы до 30 сек, процесс висит 1–2 мин после выхода.
- **Влияние:** процесс — смена движка без QA ломает фичи-флаги; DF требует чинить тогглы меню в приоритете.
- **DSS:** `pso_precaching_warmup`, `temporal_upscaling`, `ml_frame_generation`, `cascaded_shadow_maps`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2024-until-dawn-remake-disappoints-on-ps5-and-has-broken-features-on-pc), DSOG (https://www.dsogaming.com/pc-performance-analyses/until-dawn-remake-pc-performance-analysis/).

### 214. Horizon Zero Dawn Remastered (2024, Guerrilla/Nixxes / Decima) — ДЕЛЬТА к оригиналу 2017

- **Движок:** Decima, ветка Forbidden West; ремастер — Nixxes при поддержке Guerrilla.
- **Релиз ПК:** 10.2024 одновременно с PS5, апгрейд $10 с переносом сейвов PS4. На PS5 режимы 30/40/60 fps как в Forbidden West с DRS (Quality ~4K, Performance <1800p), все держат таргет + VRR-анлок.
- **Версии/патчи:** Крупные технопатчи на момент DF-разбора 23.10.2024 — unstated; PS5 Pro-поддержка из коробки.
- **Причина репутации:** реализация («почти ремейк»: Nixxes перелопатил мир до уровня сиквела при сохранении арта 2017).
- **Решения:**
  - `+` Дельта террейна/фолиаджа: все материалы заменены на Forbidden West, полы Меридиана перемоделированы, +LOD и плотность, реакция на Элой.
  - `+` Дельта света/воды/атмо: новый бейк в 2x детальнее, 12 времён суток, Nubis-облака, деформируемые снег/песок, вода с SSR + каустикой вместо кубмап.
  - `+` Дельта персонажей: 10+ часов нового мокапа на 300 диалогов/3100 реплик через Python-пайплайн, 5-точечный риг света вместо 2-точечного.
  - `±` Оригинал и так 60 fps на PS5, поэтому прирост — в деталях close-up, а не в производительности.
- **Влияние:** контент — стандарт бережного ремастера: перенос tech-stack сиквела + ручной релайт вместо bump-резолюции.
- **DSS:** `lightmap_atlas_baking`, `gpu_instancing_vegetation`, `dynamic_resolution_scaling`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2024-horizon-zero-dawn-remastered-review-the-upgrades-are-worthwhile), PlayStation (https://blog.playstation.com/2024/10/17/horizon-zero-dawn-remastered-a-deep-dive-into-its-enhancements/).

### 215. Indiana Jones and the Great Circle (2024, MachineGames / id Tech 7 + RT)

- **Движок:** id Tech 7 (итерация MachineGames/id), обязательный hardware RT: RTGI из коробки, Full RT-патч с 09.12.
- **Релиз ПК:** Ранний доступ 06.12.2024, полный релиз 09.12.2024. Нет PSO- и traversal-статтера, нет software-фолбэка — нужна RT-карта. Xbox Series X ~1800p DRS 60 fps, S ~1080p + VRS.
- **Версии/патчи:** Full Ray Tracing-апгрейд 09.12: RT-солнце + 1-баунс RT-отражения вместо SSR/кубмап; DLSS 3 + FG, без FSR/XeSS на старте, DRS только с TAA.
- **Причина репутации:** реализация (анти-UE5 кейс: RTGI в 60 fps на консолях при 1800p, но VRAM-стена 12 ГБ и низкий LOD/тени из коробки).
- **Решения:**
  - `+` RTGI обязателен везде, включая Series S; Full RT на ПК даёт офлайн-качество света на RTX 4070 в 1440p Quality.
  - `±` Texture Cache = виртуальный пул: 8 ГБ — только Medium/Low, 10 ГБ — High, 12 ГБ — Supreme/Ultra; переполнение = обвал fps.
  - `−` Чекпоинт-статтер в Ватикане и 30-fps анимации + 100-мс шипы на склейках катсцен при общем 60 fps.
  - `−` LOD-поппинг у камеры даже на Max (лечится r_lodscale 5), тени Ultra низкодетальны с каскадным швом.
- **Влияние:** оптимизация — RTGI 60 fps возможен без UE5 ценой VRAM-дисциплины и ручного LOD.
- **DSS:** `hardware_raytraced_gi`, `virtual_texturing`, `temporal_upscaling`, `async_loading_pipeline`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2024-indiana-jones-and-the-great-circle-pc-impressive-performance-but-care-is-needed-with-8gb-graphics-cards), DSOG (https://www.dsogaming.com/pc-performance-analyses/indiana-jones-and-the-great-circle-benchmarks-pc-performance-analysis/).

### 216. Metaphor: ReFantazio (2024, Studio Zero / собственный P-Studio)

- **Движок:** Собственный движок P-Studio (наследник Persona 5), без RT, без DLSS/FSR.
- **Релиз ПК:** 11.10.2024; демо Prologue 09.2024. На топ-ПК 4K Max не держал 60 fps при недогрузе GPU; маус-контроль и выбор iGPU на ноутбуках сломаны на старте.
- **Версии/патчи:** Демо-патч 1.02: снижение нагрузки GPU + принудительный выбор дискретной GPU; 1.03: SMAA/FXAA + Rendering Scale до 200%; 1.09: тоггл Dash Effects, фиксы мыши/контроллера/AZERTY.
- **Причина репутации:** реализация (худший ПК-порт Atlus: drawcall/RAM-бутылка + однопоточный CPU-лимит, чиненный только Special K).
- **Решения:**
  - `−` Низкие систреки (GTX 750 Ti / 6 ГБ RAM для 720p30) не отражают реальность: DDR5-6000 душится drawcall-потоком.
  - `−` Special K показал insane timing-баг: фикс даёт 90+ fps вместо <60, но вскрывает упор в 1 ядро CPU.
  - `−` AA слабое из-за тяжёлого пост-процесса; SMAA мылит меньше FXAA, но алиасинг остаётся даже в 3440x1440.
  - `±` Rendering Scale 25–200% с шагом 25% + форсированный 8x AF: единственный рабочий скейлер вместо temporal-апскейлеров.
- **Влияние:** оптимизация — стилизация не спасает без многопоточности и Job-системы сабмишена; Ultrawide/FOV/HDR только модами Lyall MetaphorFix / RenoDX.
- **DSS:** `quality_tier_scalability`, `post_effect_selective`.
- **Источники:** DSOG (https://www.dsogaming.com/articles/metaphor-refantazio-is-an-unoptimized-mess-on-pc/), PCGW (https://www.pcgamingwiki.com/wiki/Metaphor:_ReFantazio), Atlus патчноуты (https://atlus.com/metaphor-refantazio-patch-notes-1-09/).

### 217. Kingdom Come: Deliverance II (2025, Warhorse / CryEngine + SVOGI, DX12)

- **Движок:** CryEngine, DirectX 12 + software SVOGI (воксельный cone-traced GI).
- **Релиз ПК:** 04.02.2025. На Ryzen 5 3600 + RTX 4060 Medium держит плоский 60 fps без шейдерного и traversal-статтера, включая Куттенберг; пресет Experimental — для будущих GPU.
- **Версии/патчи:** Крупные технопатчи на момент DF-разбора 20.02.2025 — unstated; шиппинг-билд без PSO-экрана.
- **Причина репутации:** реализация (old-school успех: полная отполированная игра день-в-день на фоне рваных CPU-фреймтаймов конкурентов).
- **Решения:**
  - `+` PSO-кэширование в загрузках/фоне: за 8 часов на 3600 только 2 шипа в прологе.
  - `±` SVOGI даёт 1–2 баунса и естественные поля/леса при копеечном CPU-косте, но течёт через тонкие стены и глух к мелким динамическим объектам.
  - `−` Отражения только SSR + кубмапы без RT-опции: металлы светятся, вода с disocclusion-артефактами.
  - `−` Наследие CryEngine: растения/вода тикают 30 fps с неровным пейсингом, катсцены залочены 30 fps (анлок модами), нет HDR, кап ломается при несовпадении разрешений.
- **Влияние:** оптимизация — отказ от UE5 + ставка на SVOGI и CPU-оптимизацию даёт лучший open-world фреймпейс 2025 без path tracing.
- **DSS:** `pso_precaching_warmup`, `world_partition_streaming`, `screen_space_gi`, `quality_tier_scalability`.
- **Источники:** Digital Foundry (https://www.digitalfoundry.net/articles/digitalfoundry-2025-kingdom-come-deliverance-2-is-an-old-school-technical-success-on-pc), DSOG (https://www.dsogaming.com/pc-performance-analyses/kingdom-come-deliverance-2-pc-performance-analysis/).

---

## Партия 27 (список-3, финал B: №218–225)

### 218. Fallout: London (2024, Team FOLON / Creation Engine, конверсия Fallout 4)

- **Движок:** Creation Engine (база Fallout 4 + все DLC). Отдельного движка нет.
- **Релиз ПК:** 25.07.2024, ПК-only, бесплатно через GOG (требуется Fallout 4: GOTY). В Steam отдельной страницы нет. Задержка из-за Fallout 4 Next-Gen Update (04.2024), требовался даунгрейд Fallout 4.
- **Версии/патчи:** Хотфиксы после 25.07.2024 (детали — см. патчноуты Team FOLON/GOG changelog; здесь unstated).
- **Причина репутации:** функционал (крупнейшая fan-конверсия: новый Лондон, озвучка, квесты на движке 2015; техрепутация — краши/вылеты, просадки, конфликты с Next-Gen, чистая установка).
- **Решения:**
  - `+` Полная конверсия на Creation Engine без смены движка.
  - `+` Распространение через GOG с downgrader для совместимости.
  - `−` Наследованные лимиты Creation Engine: стриминг ячеек, CPU-зависимость, script-lag.
  - `−` Стартовые краши/buffout-зависимость.
- **Влияние:** контент — долгожительство Creation Engine модами; для DSS — только как мод-профиль Fallout 4, не отдельный движок.
- **DSS:** `fixed_timestep_physics`, `baked_occlusion_culling`, `async_loading_pipeline`, `quality_tier_scalability`.
- **Источники:** GOG (https://www.gog.com/game/fallout_london), Steam Fallout 4 (https://store.steampowered.com/app/377160/Fallout_4/), PCGW (https://www.pcgamingwiki.com/wiki/Fallout:_London).

### 219. Euro Truck Simulator 2 (2012, SCS Software / Prism3D)

- **Движок:** Prism3D (собственный SCS).
- **Релиз ПК:** 18.10.2012 (Steam 227300); Windows + позже macOS/Linux. Живая игра-сервис с DLC-картами по 2024–2026.
- **Версии/патчи:** Continuous updates 1.x (Convoy MP, DX11, реворки освещения/Германии/Швейцарии). Точные номера текущих билдов — unstated.
- **Причина репутации:** функционал (эталон долгой поддержки и масштабирования слабого железа; CPU-single-thread зависимость в городах, моды/Workshop).
- **Решения:**
  - `+` Prism3D + инкрементальные апгрейды рендера без смены движка.
  - `+` Convoy multiplayer, World of Trucks, Workshop.
  - `±` DX11, SMAA/SSAO-опции, скейлинг: легко на слабом ПК, ограничено на топ-ПК.
  - `−` Старый конвейер: просадки в городах/модах, трафик-AI CPU-bound.
- **Влияние:** контент — service-sim: долгая стабильность, калибровка по CPU-лимиту, а не GPU.
- **DSS:** `world_partition_streaming`, `time_sliced_pathfinding`, `snapshot_slot_saves`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/227300/Euro_Truck_Simulator_2/), PCGW (https://www.pcgamingwiki.com/wiki/Euro_Truck_Simulator_2), SCS (https://eurotrucksimulator2.com/).

### 220. Far Cry 3 + 4 + 5 + New Dawn + 6 — групповая карточка (2012–2021, Ubisoft / Dunia Engine)

- **Движок:** Dunia Engine во всех пяти. Dunia 2 (FC3) → Dunia 2 + погода/вода (FC4) → Dunia + HD-текстуры/фотограмметрия (FC5/New Dawn) → Dunia 2 + DX12/HD-текстуры (FC6; RT-отражения только на консолях нового поколения, на ПК RT нет). Версии Dunia Ubisoft не публикует — unstated по веткам.
- **Релиз ПК:** Far Cry 3 — 29.11.2012 (220240); Far Cry 4 — 18.11.2014 (298110); Far Cry 5 — 27.03.2018 (552520); New Dawn — 15.02.2019 (781300); Far Cry 6 — 07.10.2021 (Ubisoft Connect/Epic, Steam с 11.05.2023, 2369390).
- **Версии/патчи:** ПК-патчи в основном фиксы крашей/Uplay, HD-текстурпаки для FC5/FC6. Номера билдов и правки рендера — unstated.
- **Причина репутации:** реализация (общий техпрофиль: открытый мир, огонь/растительность/дальность, CPU-bound в городах/аванпостах; FC3 — stutter/GPU-память эпохи; FC4 — FOV/мышь-аксель; FC5/6 — стабильнее, но мыло TAA, нет RT на ПК в FC6).
- **Решения:**
  - `+` Dunia: бесшовный open-world, огонь/физика растительности, редактор карт (FC3–5).
  - `+` DX11→DX12 к FC6, FSR на ПК в FC6.
  - `±` TAA + высокая дальность: чисто, но мыльно без шарпа; HD-пак жрёт VRAM.
  - `−` Микростаттеры/CPU-лимит, DRM/Uplay-зависимость, нет RT на ПК.
- **Влияние:** контент — эволюция без смены движка; для DSS — один Dunia-профиль с подверсиями, а не 5 разных движков.
- **DSS:** `world_partition_streaming`, `hierarchical_lod`, `gpu_instancing_vegetation`, `quality_tier_scalability`.
- **Источники:** Steam FC3 (https://store.steampowered.com/app/220240/Far_Cry_3/), Steam FC4 (https://store.steampowered.com/app/298110/Far_Cry_4/), Steam FC5 (https://store.steampowered.com/app/552520/Far_Cry_5/), PCGW FC6 (https://www.pcgamingwiki.com/wiki/Far_Cry_6).

### 221. S.T.A.L.K.E.R.: Shadow of Chornobyl (2007, GSC Game World / X-Ray Engine 1.0)

- **Движок:** X-Ray Engine 1.0 (build 1.000x).
- **Релиз ПК:** 20.03.2007 NA / 23.03.2007 EU (Steam 4500 позднее). Только ПК на старте.
- **Версии/патчи:** 1.0001 → 1.0006 (экономика/ранги/A-Life, мультиплеер). Точный чейнджлог — см. патчноуты GSC.
- **Причина репутации:** реализация (A-Life, динамическое освещение Static/Dynamic/Full, X-Ray [FATAL ERROR], save-коррапты, просадки на Dynamic Lighting эпохи).
- **Решения:**
  - `+` X-Ray deferred dynamic lights + A-Life симуляция.
  - `+` Три рендера на выбор (Static/Dynamic) для слабого железа.
  - `−` Утечки памяти/вылеты, лимит 2GB без Community Patch.
  - `−` CPU-single-thread + HDD-стриминг: фризы на локациях.
- **Влияние:** оптимизация — оригинал отдельно от S.T.A.L.K.E.R. 2 (UE5); DSS-профиль только X-Ray 1.0.
- **DSS:** `baked_occlusion_culling`, `agent_update_budget`, `async_loading_pipeline`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/4500/STALKER_Shadow_of_Chernobyl/), PCGW (https://www.pcgamingwiki.com/wiki/S.T.A.L.K.E.R.:_Shadow_of_Chernobyl).

### 222. Ghost of Tsushima DIRECTOR'S CUT ПК (2024, Sucker Punch/Nixxes) — ДЕЛЬТА к базе

- **Движок:** Базовый движок Sucker Punch (PS) + Nixxes ПК-слой. Отдельного ПК-движка нет.
- **Релиз ПК:** 16.05.2024 (Steam 2215430). База — PS4 2020 / PS5 Director's Cut 2021. Дельта только ПК.
- **Версии/патчи:** Nixxes-патчи (ultrawide/UI, FSR/DLSS, контроллеры). Номера билдов — unstated.
- **Причина репутации:** реализация дельты (образцовый Nixxes-порт: ultrawide 21:9/32:9/48:9, DLSS 3 / FSR 3 / XeSS, DualSense, разблокированный FPS; критика — PSN-привязка для Legends на старте).
- **Решения (только дельта):**
  - `+` Ultrawide + тройной монитор + FOV-настройки Nixxes.
  - `+` DLSS 3 Frame Gen / FSR 3 / XeSS + DLAA.
  - `±` Требования выше PS-эквивалента: SSD + 6-ядерный CPU для стабильных 60+.
  - `−` PSN-оверлей/Legends-ограничения на старте.
- **Влияние:** оптимизация — дельта не меняет базу, только расширяет ПК-профиль; базовые коды Tsushima + ПК-апскейл модификаторы.
- **DSS:** `temporal_upscaling`, `dynamic_resolution_scaling`, `pso_precaching_warmup`, `quality_tier_scalability`.
- **Источники:** Steam (https://store.steampowered.com/app/2215430/Ghost_of_Tsushima_DIRECTORS_CUT/), PCGW (https://www.pcgamingwiki.com/wiki/Ghost_of_Tsushima_Director%27s_Cut).

### 223. ELDEN RING Shadow of the Erdtree (2024, FromSoftware / собственный) — ДЕЛЬТА к Elden Ring

- **Движок:** Собственный FromSoftware (эволюция Dark Souls III / Sekiro). Отдельного движка DLC нет.
- **Релиз ПК:** DLC 21.06.2024 к базе 25.02.2022 (база 1245620, DLC 2778580). Требует базу.
- **Версии/патчи:** Базовый патч 1.12 (под DLC) + 1.12.2/1.12.3 (баланс/перф); RT-режим добавлен патчем базы 1.09 (2023): только AO/тени/освещение, без DLSS Frame Gen на старте.
- **Причина репутации:** реализация дельты (новая карта + боссы без смены рендера; те же 60fps-cap, CPU-спайки/шейдер-статтеры в новых зонах, RT тяжёлый для малого прироста).
- **Решения (дельта):**
  - `+` Крупный контент без повышения системных требований vs база.
  - `+` Патчи баланса/перфа 1.12.x после релиза DLC.
  - `±` RT (с 1.09): чуть лучше тени/AO, минус ~20–30% FPS.
  - `−` Сохранены лимиты базы: 60fps cap, EAC, нет ultrawide-натива.
- **Влияние:** оптимизация — база Elden Ring без новых кодов; Erdtree только контент-флаг.
- **DSS:** `fixed_timestep_physics`, `hierarchical_lod`, `quality_tier_scalability`.
- **Источники:** Steam база (https://store.steampowered.com/app/1245620/ELDEN_RING/), Steam DLC (https://store.steampowered.com/app/2778580/ELDEN_RING_Shadow_of_the_Erdtree/), PCGW (https://www.pcgamingwiki.com/wiki/Elden_Ring).

### 224. Obscure-инди пакет (King of the Bridge / DRAGON BROOD / Machine Party / BOMBANANA!)

- **Движок:** Все четыре — null/unstated (Steam-страницы не указывают движок, покрытия DF/DSOG/PC Gamer нет; не выдумываю Unity/Unreal/Godot).
- **Релиз ПК:** Steam-факты — null/unstated в данном проходе (требуют проверки AppID); даты/разработчики/издатели — null без Steam-fetch.
- **Версии/патчи:** null/unstated для всех четырёх.
- **Причина репутации:** null — нет покрытия в Steam/DF/DSOG/PC Gamer/PCGW в данном проходе; не является техрепутацией.
- **Решения:**
  - `±` null — нет проверяемых техрешений.
  - `−` Данных для анализа нет.
  - `−` Движок/рендер/API/апскейлы — null.
  - `−` Перф/баги/патчи — null.
- **Влияние:** null — данных для DSS-калибровки нет; в DSS не включать, оставить как null-заглушки до ручной проверки Steam AppID.
- **DSS:** — (нет данных; коды не присваиваются, чтобы не создавать ложное подтверждение).
- **Источники:** Steam поиск King of the Bridge (https://store.steampowered.com/search/?term=King+of+the+Bridge), DRAGON BROOD (https://store.steampowered.com/search/?term=DRAGON+BROOD), Machine Party (https://store.steampowered.com/search/?term=Machine+Party), BOMBANANA (https://store.steampowered.com/search/?term=BOMBANANA).

### 225. Мета-проверка дедупликации списка-217

- **Движок:** null — это мета-карточка, не игра.
- **Релиз ПК:** null — проверка дедупликации, а не релиз.
- **Версии/патчи:** null.
- **Причина репутации:** дубликаты и уже покрытые позиции, которым детальная карточка не нужна: HELLDIVERS Dive Harder = HELLDIVERS 1 (издание, не отдельная игра); Call of Duty: Black Ops AppID 202970 = мультиплеер-AppID Black Ops 1 (база 42700); Garry's mod = дубль упоминания; Dragon's Dogma 2, Black Myth: Wukong уже покрыты.
- **Решения:**
  - `+` Дедупликация по AppID/названию сохраняет DSS-чистоту.
  - `+` Повторное использование существующих карточек для DD2/Wukong.
  - `±` Dive Harder и 202970 оставить как алиасы, не как N.
  - `−` Новые техфакты по дублям — null.
- **Влияние:** процесс — итог закрыт без дублей; свободные N — только реально непокрытые.
- **DSS:** — (мета-проверка, кодов нет).
- **Источники:** Steam Black Ops 202970 (https://store.steampowered.com/app/202970/Call_of_Duty_Black_Ops/), Steam Garry's Mod (https://store.steampowered.com/app/4000/Garrys_Mod/).
