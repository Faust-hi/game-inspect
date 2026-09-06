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
- **DSS:** `headless_dedicated_server` (антипример зависимости от сервисов), `multithreaded_physics_jobs`, `time_sliced_pathfinding`; риск `late_streaming`/`deadline_pressure`.
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
- **DSS:** `gpu_procedural_placement`, `hierarchical_lod`, `async_loading_pipeline`; риск `deadline_pressure`/`prototype_needed`.
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
- **DSS:** `async_loading_pipeline`, `baked_occlusion_culling`, `animation_compression`, `sprite_atlas_batching`.
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
- **DSS:** `headless_dedicated_server`, `tickrate_budgeting`, `client_prediction_reconciliation`, `deterministic_lockstep`; риск `deadline_pressure`.
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
- **DSS:** `crowd_instancing_impostors`, `agent_update_budget`, `ecs_data_oriented_crowd`, `hierarchical_lod`, `multithreaded_physics_jobs`; риск `crowd_budget`.
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
- **DSS:** `async_loading_pipeline`, `hierarchical_lod`, `navmesh_tiling_streaming`; риск `memory_budget`.
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
- **DSS:** `gpu_procedural_placement`, `world_partition_streaming`, `async_loading_pipeline`, `physics_lod_sleeping`, `time_sliced_pathfinding`.
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
- **DSS:** `ecs_data_oriented_crowd`, `deterministic_lockstep`, `composition_bootstrap_architecture`, `tickrate_budgeting`, `crowd_simulation`.
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
- **DSS:** `hardware_raytraced_gi`, `temporal_upscaling`, `ml_frame_generation`, `crowd_simulation`, `volumetric_effects`, `post_effect_selective`.
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
- **DSS:** `tiled_clustered_light_culling` (нет), `gpu_particle_simulation`, `physics_lod_sleeping`, `post_effect_selective`; честно: PhysX-цена в `requires_conditions`.
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
- **DSS:** `headless_dedicated_server`, `tickrate_budgeting`, `network_relevancy_priority`, `client_prediction_reconciliation`, `physics_lod_sleeping`.
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
- **DSS:** `multithreaded_physics_jobs`, `time_sliced_pathfinding`, `agent_update_budget`, `deterministic_lockstep`.
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
- **DSS:** `volumetric_half_resolution`, `terrain_clipmap`, `vegetation_atlas_lod`, `temporal_upscaling`, `dynamic_resolution_scaling`, `multithreaded_physics_jobs`.
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
- **DSS:** `multithreaded_physics_jobs`, `time_sliced_pathfinding`, `dynamic_resolution_scaling`, `quality_tier_scalability`.
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
- **DSS:** `baked_occlusion_culling`, `tilemap_chunk_streaming` (аналог комнат), `particle_pooling`, `agent_update_budget`, `post_effect_selective`.
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
- **DSS:** `open_world_streaming`, `water_simulation`, `physics_lod_sleeping`, `tickrate_budgeting`.
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
