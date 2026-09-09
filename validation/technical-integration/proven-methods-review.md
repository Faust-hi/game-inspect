# Проверка и интеграция списка proven-methods.md

Проверено 9 сентября 2026 года. Исходный файл сохранён. Его SHA-256, номера строк и результат сопоставления каждой записи — в [proven-methods-review.json](proven-methods-review.json); инвентаризация воспроизводится `validation/review_proven_methods.py`.

## Что найдено и перенесено

В документе 124 уникальных кода: 119 уже существующих записей и пять дополнений. Все коды сопоставлены, дубликаты не созданы. Дополнения интегрированы после проверки механизмов, условий и связей; исходные проценты, аппаратные баллы и уверенность не импортировались как измерения.

| Код | Результат проверки и размещение |
|---|---|
| `ai_director_pacing` | Контроллер популяции в `advanced_npc_ai`. Входит технический автомат управления NPC; повествовательная ценность и реиграбельность не входят в аппаратные коэффициенты. |
| `subtick_networking` | Временные метки команд в `multiplayer_netcode`. Существование подхода подтверждено Valve; обязательные 64 Гц, float-формат и превосходство над 128 Гц не установлены как свойства общего метода. |
| `lag_compensation_rewind` | Историческая серверная проверка в `multiplayer_netcode`. Потребность в sub-tick отвергнута: открытая реализация Source использует историю и такты без него. |
| `directstorage_io` | Очереди I/O и декомпрессия в `open_world_streaming`, поскольку это путь загрузки ресурсов в рантайме. Технические ограничения CPU/GPU-пути разделены. |
| `async_compute_overlap` | Перекрытие очередей в `rendering_architecture`. Не уменьшает количество вычислений; изменение времени кадра зависит от фактического перекрытия и конкуренции ресурсов. |

### Источники и исправленные утверждения

- **AI Director:** [доклад Michael Booth, Valve](https://cdn.akamai.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf), страницы 78–81: управление интенсивностью и популяцией. Из использования навигации не следует обязательная зависимость от тайлового стриминга navmesh. Это инженерный вывод о различии интерфейса навигации и конкретной реализации.
- **Sub-tick:** [Valve, Counter-Strike 2](https://www.counter-strike.net/cs2). Официальное описание подтверждает уточнённое время событий. Публикации о конкретной версии CS2 не превращены в универсальные требования к своей игре; гарантии меньшего bandwidth и «честности для любого пинга» не приняты.
- **Rewind:** [исходный код Valve](https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/server/player_lagcompensation.cpp) и [статья Yahn Bernier о компенсации задержки](https://developer.valvesoftware.com/w/index.php?title=Latency_Compensating_Methods_in_Client%2FServer_In-game_Protocol_Design_and_Optimization&uselang=en). В коде есть ограниченное окно истории, интерполяция, проверка времени и восстановление состояния. История находится на сервере: её хранение само по себе не добавляет трафик. Формула «всегда вычесть полный пинг» не переносится без определения метрики задержки.
- **DirectStorage:** [Microsoft Developer Guidance](https://github.com/microsoft/DirectStorage/blob/main/Docs/DeveloperGuidance.md), [GPU-декомпрессия 1.1](https://devblogs.microsoft.com/directx/directstorage-1-1-now-available/), [buffered I/O и проверка пути в 1.2](https://devblogs.microsoft.com/directx/directstorage-1-2-available-now/). GPU-путь требует DX12/SM6.0, а не обязательно DX12 Ultimate; HDD поддерживается. Есть промежуточные буферы и CPU fallback. Обязательные NVMe, размер чанка 256 КБ, «напрямую без промежуточной памяти» и универсальное освобождение CPU исправлены. Выигрыш демонстрации Intel не перенесён в модель.
- **Async compute:** [Khronos Vulkan sample](https://docs.vulkan.org/samples/latest/samples/performance/async_compute/README.html) и [материалы AMD о DX12/Vulkan](https://gpuopen.com/wp-content/uploads/2016/03/d3d12_vulkan_lessons_learned.pdf). Наличие нескольких очередей не гарантирует независимых вычислительных ресурсов. Барьеры необходимы; задача — корректные зависимости, а не запрет определённого направления барьера. PSO precaching не является обязательным условием. Проценты из партий не применены к другой сцене или GPU.

## Связи и аппаратная модель

Добавлены 12 связей: дополнения и риски. Ложных обязательных зависимостей или взаимоисключений из документа нет. Sub-tick совместим с выбором тикрейта и rewind; Director дополняет поведение/восприятие; DirectStorage может обслуживать async loading и виртуальные текстуры. Отдельно указан риск конкуренции GPU-декомпрессии и async compute. Эти связи — проверяемые инженерные предположения, не измеренные совместные ускорения.

Для пяти дополнений аппаратные эффекты описаны качественно с явными ограничениями. Пока нет отдельного измеренного бюджета, метод не уменьшает весь CPU/GPU и не придумывает количество RAM/VRAM. Для sub-tick и rewind область оценки — сервер; расходы клиентской отправки и локального хоста указаны как неоценённые. Направления и баллы в карточках остаются экспертными. Их `confidence=0.5` не означает сомнения в существовании технологии.

DirectStorage предлагается для Windows; на Linux и смешанной Windows/Linux цели не применяется как общий путь. При другом RHI поясняется необходимость CPU-пути или отдельного D3D12 interop. Вариант async compute с явными очередями требует DX12/Vulkan. Серверные методы исключаются в одиночной игре и при выбранном чистом lockstep.

Сохранённая корзина продолжает служить реализованной основой. Добавление дополнения не считается заменой; смена стадии без технических изменений не начисляет повторное внедрение. Изменение накопителя, API, сетевой схемы и других значимых параметров запускает оценку адаптации. Диапазоны трудозатрат не являются часами.

## Почему раздел «недоказано: 12» нельзя принимать буквально

Наличие URL, плана проверки и `confidence >= 0.65` не является доказательством измеренного эффекта. Обратное тоже неверно: меньший балл не делает метод вымышленным. Дополнительный поиск нашёл описания механизмов:

| Записи исходного раздела | Дополнительные источники и ограничение |
|---|---|
| `voxel_cone_tracing` | [Исследование Crassin et al.](https://research.nvidia.com/labs/rtr/publication/crassin2011givoxels/). Есть алгоритм и результаты для его сцен; показатели не универсальны. Источник каталога заменён со статьи о SVO на сам метод. |
| `motion_matching` | [Epic Pose Search / Motion Matching](https://dev.epicgames.com/documentation/unreal-engine/motion-matching-in-unreal-engine?lang=en-US). Поиск по базе поз требует памяти и вычислений; объём базы и каналов важен. |
| `neural_texture_compression` | [NVIDIA SDK](https://github.com/NVIDIA-RTX/Rtxntc), [настройки качества](https://github.com/NVIDIA-RTX/RTXNTC/blob/main/docs/SettingsAndQuality.md), [доклад о производительности](https://vulkan.org/user/pages/09.events/vulkanised-2025/T48-Jeff-Bolz-NVIDIA.pdf). Компромисс памяти, декодирования и качества зависит от режима и устройства. |
| `meshlet_pipeline_adoption` | [Спецификация Microsoft](https://github.com/microsoft/DirectX-Specs/blob/master/d3d/MeshShader.md), [образцы](https://learn.microsoft.com/en-us/samples/microsoft/directx-graphics-samples/d3d12-mesh-shader-samples-win32/). Поддержка GPU и fallback проверяются отдельно. |
| `portal_scene_capture_budget` | [Epic CaptureScene](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/Components/USceneCaptureComponent2D/CaptureScene?application_version=5.5). Повторный захват при уже включённом покадровом захвате создаёт лишнюю отрисовку; масштаб эффекта требует сцены. |
| `hair_strand_simulation`, `hair_cards_lod` | [Описание Frostbite](https://www.ea.com/frostbite/amp/news/frostbite-hair-rendering-and-simulation-2), [генератор карточек Epic](https://dev.epicgames.com/documentation/metahuman/hair-card-generator-in-dataflow-in-unreal-engine). Разные представления; качество переходов и overdraw проверяются отдельно. |
| `cloth_constraint_simulation`, `cloth_baked_animation` | [Unity Cloth](https://docs.unity3d.com/6000.0/Documentation/Manual/class-Cloth.html), [Epic Panel Cloth](https://dev.epicgames.com/documentation/unreal-engine/panel-cloth-editor-overview). Ограничения/коллизии и кэширование — реальные подходы; кэш не обеспечивает произвольную реакцию на новые воздействия. |
| `runtime_fracture_budget` | [Chaos Destruction](https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-destruction-overview?application_version=4.27). Кластеры, поля и кэширование описаны; произвольный предел обломков требует нагрузочного теста. |
| `audio_convolution_reverb` | [Epic Convolution Reverb](https://dev.epicgames.com/documentation/unreal-engine/convolution-reverb-in-unreal-engine). DSP и данные импульсного отклика; стоимость не универсальна. |
| `runtime_security_budget` | [Пример интеграции Epic EOS](https://github.com/EpicGames/EOS-Getting-Started/blob/main/OnlineSubsystemEOS/Plugins/EOSAntiCheat/README.md), [FACEIT integration](https://labs-docs.faceit.com/AntiCheat/GettingStarted/). Клиент/сервер и транспортные сообщения; фиксированную потерю FPS эти источники не устанавливают. |

Все 12 уже были в каталоге и сохранены без дублирования. Эта проверка не является независимой повторной верификацией каждого утверждения остальных 107 карточек. В обнаруженных ошибках исправлены:

- Flow field: переиспользуется построение поля, но работа всех агентов не становится постоянной. [Глава Elijah Emerson](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf).
- Стилизация: конкретные проходы, материалы и overdraw определяют стоимость; стиль не гарантирует 60 FPS. [Рекомендации Unity по GPU](https://unity.com/how-to/gpu-optimization).
- Origin shifting: универсального обязательного порога 5 км нет; важны единицы, точность и используемые типы координат. [Epic Large World Coordinates](https://dev.epicgames.com/documentation/unreal-engine/large-world-coordinates-in-unreal-engine-5).

Исправления старых полей применяются только при точном совпадении с прежним встроенным значением. Поля администратора, существующие методы и изменённые типы связей не перезаписываются. Новые методы добавляются идемпотентно при старте существующей SQLite-базы. Ручное пересоздание базы не требуется.

## Проверки

Итог: **backend 506 passed, 1 skipped; frontend 42 passed**. TypeScript/Vite production build выполнен успешно. Все 41 поле профиля проверены по одному; 12 численных инвариантов выполнены. Браузерный сценарий прошёл без ошибок страницы: выбор всех пяти дополнений, фиксация реализации, обновление страницы; также сохранены проверки замены и смены стадии. Снимок `reviewed-basket-browser.png` просмотрен. Журналы: `reviewed-backend-tests.txt`, `reviewed-reactivity-check.txt`, `browser.json`.

Браузерная проверка выявила и помогла исправить блокировку фиксации из-за условного риска. Такой риск теперь допускает сохранение и остаётся видимым; несовместимость, неизвестная связь в списке конфликтов и неучтённое решение продолжают блокировать фиксацию. Шесть frontend-регрессий защищают это различие.

Регрессии: пять API-карточек, отсутствие выдуманных аппаратных скидок, независимость rewind, Windows/Linux и RHI, офлайн/lockstep, совместное применение, сохранённая основа, реакция на накопитель, идемпотентное обновление и сохранение правок администратора. Дополнительно — полный backend, проверка всех 41 полей и браузерный выбор/сохранение пяти методов.

Результаты тестов подтверждают поведение приложения. Они не измеряют FPS, bandwidth, память или трудозатраты конкретного игрового проекта.
