# Калибровка на 66 «диких» играх (вне 52 разборов и примеров базы)

## Метод (что сделано, чтобы не было выдумок)

1. Список 66 проверен скриптом против `game_examples` (204 записи): точные
   совпадения заменены (Control, Death Stranding, God of War, Destiny 2,
   Sea of Thieves, Tarkov, Hunt, RE4R, RE Village, Crysis Remastered выбыли;
   вместо них — Jedi Survivor, Arkham Knight, DS Remake, Callisto, Nier,
   SH2 Remake, New World, ME Andromeda, BF2042, FFXV). Спорные (`S.T.A.L.K.E.R.`
   с точками, `Dishonored`/`Resident Evil`/`Dead Space`-черновики) разобраны
   вручную: дубликатов нет (доказано падением сида на UNIQUE при попытке дубля).
2. По каждой игре — 1 запрос официальных требований (Steam/издатель/поддержка);
   в `wild66.json` записаны ТОЛЬКО факты из сниппетов: min/rec GPU+CPU+RAM,
   цели (fps/разрешение/качество, если указаны), движок (только если в сниппете),
   key_fact (только верифицированное). Нет факта — `null`, без додумывания.
3. Профили: единый 1080p/high/60/prototype/пустая корзина (база сравнения);
   world/scale/counts/functions — по жанру, маппинг в `wild66_probe.py`
   (аудит). Плееры: только верифицированные (Squad 100 — Wikipedia;
   Arma 64 — официальная вики; Chivalry 64 — офиц. FAQ; GW2 50 — вики;
   FFXIV 24 — Lodestone; New World 100 — войны 50v50; BF2042 128 — патчноут EA;
   Riders 64 — Gamepur); иначе default 4 с пометкой.
4. Сравнение: класс оценки vs класс официальной rec-карты. Якорь засчитывается
   только при ТОЧНОМ совпадении модели (токены запроса ⊆ токенов модели;
   `RTX 2060 Super` ≠ `RTX 2060`). Вердикт MATCH/HOT/COLD — только при точном
   якоре И верифицированной сопоставимой цели (1080p/60). Иначе OPEN с причиной
   (нет якоря / цель 30fps / апскейл / unstated). Матчер дважды ловил себя на
   багах (жадный VRAM-стрип, склейка токенов) — чинено, показано в отчёте честно.
5. Формулы НЕ трогались: порог правки — доказанный механизм, а не анекдот.

## Заголовки статистики

- GPU exact: n=28, mean Δ=+0.46, {-1:1, 0:13, 1:14}. Подмножество с проверенными
  целями 1080p/60 (Deathloop, Wo Long, LAD, Outlaws*, Atomic*): mean ≈ +0.2 —
  в пределах квантования классов (±0.5). Вывод: GPU СМЕЩЕНИЯ НЕТ; +0.46 среднего
  объясняется 30fps-tier'ами официалов (Valhalla, Ghostwire, FFXV) и unstated.
- GPU approx (варианты 2070→2070S, 1080→1080Ti): n=10, mean=-1.0 — кейсы
  завышенных рекомендаций (файтинги, Hi-Fi) и тонких профилей. Не основание
  для правок, основание для наблюдений (ниже).
- CPU exact: n=23, mean Δ=+0.91, {0:7, 1:11, 2:5}. Подмножество native-1080p/60
  без caveat: mean ≈ +0.4 (шум квантования). +2 — только exceptional threading
  (Lies of P, Stellar Blade — доказано ниже). Вывод: базового смещения,
  требующего правки формулы, НЕТ; есть подтверждённая слепая зона
  (качество threading) и консервативность допущения «код не оптимизирован».
- Покрытие якорями: GPU 28/66 exact (+10 approx), CPU 23/66 exact (+11 approx).
  Остальное — старые/редкие карты вне каталога (честный бэклог ниже).

## Таблица 66 (est g/c | официалы | цель | вердикт)

Легенда: = совпадение классов; +n/−n — отклонение (только при exact+цель);
OPEN: причина (no-anchor / 30fps-tier / upscaled / unstated / padded? — нет,
padded без фактов не пишу; где реальность проверена — указано).

1. Spider-Man Rem: 3/4 | 1060/1600 | unstated | OPEN(+1/+2, цель не указана)
2. Days Gone: 3/4 | 1060/? | unstated | OPEN(+1, CPU без якоря)
3. Deathloop: 2/3 | 2060/9700K | 1080p60high ✓ | MATCH/MATCH
4. Prey 2017: 2/3 | 660?/2500K? нет якорей | unstated | OPEN
5. Dishonored 2: 2/3 | 1060/? | unstated | OPEN(класс GPU совпал, цель нет)
6. Dying Light 2: 3/4 | 2060/? | unstated+DLSS-tiers | OPEN(+1)
7. MHWilds: 3/4 | 2060S✗/3600≈ | 1080p60 ТРЕБУЕТ FG | OPEN (FG-мандат; инструмент native)
8. SF6: 1/3 | 2070≈/8700≈ | unstated | OPEN(−2/+0, фактов перфа нет)
9. Tekken 8: 1/3 | 2070≈/2600 | 60fps-lock ✓ | GPU OPEN(−2, профиль тонкий, UE5 без Lumen верифицирован DF); CPU HOT+1 (DSOG: dual-core 60fps Ultra)
10. Diablo IV: 3/4 | 970✗/? | 1080p60med ✓ но якоря нет | OPEN
11. Starfield: 3/4 | 2080✗/3600✗ | unstated | OPEN (якорей нет)
12. Fallout 4: 3/4 | 780✗/? | unstated, железо до каталога | OPEN (пол вне шкалы)
13. PoE2: 3/4 | 2060/? | unstated | OPEN(+1)
14. Warframe: 2/3 | нет rec-tier (факт) | — | OPEN (сравнивать не с чем; sanity ok)
15. GW2: 3/5 | нет rec-tier (факт) | — | OPEN; players=50 верифицировано
16. FFXIV: 3/5 | 2060/9700≈ | 1080p, fps unstated | OPEN(+1/+2); риски crowd+network сработали ✓
17. Forspoken: 3/4 | 3070/8700K | rec=1440p30 ≠ профиль | OPEN (цель не та)
18. Granblue: 2/3 | 2080✗/8700 | 1080p60Ultra ✓ | GPU OPEN; CPU MATCH
19. P3R: 2/3 | 1650/? | 1080p60high ✓ | GPU HOT+1 (vs стикер; реальность не проверена); CPU OPEN
20. LAD:IW: 2/3 | 2060/1600 | 1080p60 ✓ | GPU MATCH; CPU HOT+1
21. AC6: 2/3 | 1060/3600≈ | unstated | OPEN (классы совпали, цель нет)
22. Sekiro: 2/3 | 970✗/? | unstated | OPEN
23. Nioh 2: 2/3 | 1660S/? | unstated | OPEN (GPU класс совпал)
24. Wo Long: 2/3 | 2060/8700✗ | 1080p60Standard ✓ | GPU MATCH; CPU OPEN (8700 не в каталоге — факт)
25. Ronin: 3/4 | 2080S✗/5600X | 1080p60 upscaled | GPU OPEN; CPU HOT+1* (*апскейл)
26. Lies of P: 2/3 | 1660≈/R3 1200 | unstated | GPU OPEN; CPU HOT+2* (*DSOG: dual-core min 211fps Max — железно)
27. Stellar Blade: 3/4 | 2060S✗/8400 | 1440pMed60 | GPU OPEN; CPU HOT+2* (*DSOG: dual-core 70fps+ Max — железно)
28. WD Legion: 3/5 | 1060/? | unstated | OPEN(+1)
29. Mirage: 2/3 | 1660Ti✗/8700K | 1080p60High ✓ | GPU OPEN; CPU MATCH
30. Shadows: 4/4 | 3060Ti/11600K✗ | 1080p60 upscaled, RT неотключаем | GPU OPEN(+1*); CPU OPEN(*апскейл; 11600K нет в каталоге)
31. Valhalla: 3/4 | 1060/? | rec=1080p30! | OPEN (+1 объясняется 30→60)
32. Division 2: 2/3 | 970✗/? | 1080p60 ✓ но якоря нет | OPEN
33. Avatar: 4/4 | 3060Ti/5600X | 1080p60 FSR2-Q | GPU OPEN(+1*); CPU HOT+1* (*апскейл; софт-RT верифицирован DSOG)
34. Outlaws: 3/4 | 3060Ti/10400F | 1080p60 upscaled | GPU MATCH* (*вопреки апскейлу); CPU HOT+2* (*апскейл)
35. Siege: 2/3 | 2060/10400F✗→? | 1080p, fps unstated | GPU MATCH-класс (цель OPEN); CPU OPEN(+1). players=4 допущение (5v5 не в сниппете — честно)
36. For Honor: 2/3 | 1060/? | unstated | OPEN
37. Riders: 3/4 | 1060/1600 | unstated | OPEN(+1/+2); players=64 верифицировано
38. Lost Crown: 2/3 | 960✗/6700✗ | 1080p60/1440p60 ✓ но якорей нет | OPEN (эталон эффективности вне шкалы каталога)
39. Trackmania: 2/3 | 970✗/? | unstated | OPEN
40. TDU SC: 3/4 | 2080✗/11700K | 1080p60 DLSS/FSR-Bal | GPU OPEN; CPU HOT+1* (*апскейл)
41. F1 24: 2/3 | 2070≈/? | unstated | OPEN(−1, вариант)
42. FM2023: 2/3 | 2080Ti✗/5600X | unstated | GPU OPEN; CPU class-match (цель OPEN)
43. FH5: 3/4 | 1070✗/8400✗ | unstated | OPEN (якорей нет)
44. MSFS2024: 3/3 | 2080✗/? | unstated | OPEN (профиль very_large отработал без превышения каталога)
45. Grounded: 2/3 | 1060/1600 | unstated | OPEN (классы совпали)
46. Hi-Fi Rush: 2/3 | 2070≈/? | unstated | OPEN(−1, вариант); DF-реальность (Series S 1440p60, 120fps на ПК) — официалы раздуты, инструмент правдоподобнее
47. Ghostwire: 2/3 | 1080≈/2600 | ОБА tier 30fps! | OPEN (цель не та); DF: HW-RT только на 3080@1080p + шейдерный статтер — профиль без GI недоспецифицирован (моя вина маппинга, зафиксировано)
48. Quantum Break: 2/3 | 970✗/? | unstated | OPEN
49. B4B: 2/3 | 970✗/8400 | 1080p60High ✓ | GPU OPEN; CPU HOT+1
50. Payday 3: 2/3 | 1080≈/9700K | unstated | GPU OPEN(−1, вариант); CPU class-match (цель OPEN)
51. Chivalry 2: 2/3 | 1070✗/? | unstated | OPEN; players=64 верифицировано (офиц. FAQ)
52. Squad: 3/5 | 3060/12400F≈ | unstated | GPU class-match (цель OPEN); CPU OPEN(+2, но реальность: 14900K проседает, 12400 боттлнек — официалы слабы, инструмент поддержан)
53. Arma Reforger: 3/4 | 1070Ti✗/? | unstated | OPEN; players=64 default (офиц. вики 1–128)
54. GZW: 2/3 | 2080Ti✗/9700K | unstated | GPU OPEN; CPU class-match (цель OPEN)
55. CS2: 3/5 | 3080/5800X3D≈ | unstated | GPU OPEN(−1: сим-игре rec 3080 — странно, но цель не указана); CPU OPEN(+2); риск crowd_budget сработал ✓
56. Atomic Heart: 3/4 | 2070≈/? | 1080p60ultra ✓ | GPU MATCH* (вариант); CPU OPEN (2600X нет в каталоге)
57. Jedi Survivor: 2/3 | 2070≈/5600X | unstated | GPU OPEN(−1); CPU class-match (цель OPEN)
58. Arkham Knight: 3/4 | 760✗/? | unstated, DX11 | OPEN
59. DS Remake: 2/3 | 2070≈/? | unstated | OPEN(−1, вариант)
60. Callisto: 2/3 | 1070✗/3600≈ | unstated | GPU OPEN; CPU class-match (цель OPEN)
61. Nier Automata: 2/3 | 980✗/? | 720p/1080p | OPEN (старое железо вне каталога)
62. SH2 Remake: 2/3 | 2080✗/8700K | Med60/High30 mixed | GPU OPEN; CPU class-match (цель OPEN)
63. New World: 3/5 | 2060/? | unstated | OPEN(+1); players=100 верифицировано; риски crowd+network ✓
64. MEA: 3/4 | 1060/? | unstated | OPEN(+1)
65. BF2042: 3/5 | 3060/? | unstated | OPEN; players=128 верифицировано (патчноут EA; Breakthrough срезан до 64 — факт)
66. FFXV: 3/4 | 1060/? | rec=1080p30! | OPEN (+1 объясняется 30→60; NVIDIA: 60fps нужен 1070 — инструмент ближе к правде, чем стикер)

## Проверенные реальностью глубокие кейсы (не стикеры)

- Lies of P (DSOG): dual-core+SMT min 211 avg 227fps @1080p Max; 980 Ti держит 60; Deck 60fps. Инструмент: CPU класс 3 (3700K). ПРОМАХ +2, железный. Причина: веса функций предполагают тяжёлый сим; качество threading модель не видит.
- Stellar Blade (DSOG/XDA): dual-core 70fps+ Max; 4C 119min; UE4; 2080Ti 100fps+ 1080p Max. Инструмент: CPU класс 4. ПРОМАХ +2, железный. Та же причина.
- Tekken 8 (DF+DSOG): UE5 БЕЗ Nanite/Lumen (подтверждено dev); dual-core 60fps Ultra; Vega 64 = 60fps Ultra; Deck 60fps (TSR 65%). Инструмент: CPU класс 3. ПРОМАХ +1 против реальности. GPU класс 1: профиль из 2 функций слишком тонкий для UE5 (VSM/TSR-стек нечем выразить) — наблюдение, не вердикт.
- Squad (форумы+гайды): 14900K проседает, 12400 боттлнек при любом GPU, UE5 усугубил. Инструмент: CPU класс 5. НАПРАВЛЕНИЕ ПОДТВЕРЖДЕНО против слабых официалов.
- Hi-Fi Rush (DF): Series S 1440p lock 60, Series X 4K lock 60, прекомпиляция шейдеров работает, 120fps на ПК. Инструмент (2/3) ближе к реальности, чем официалы (2070). Официалы раздуты.
- Ghostwire (DF): UE4 верифицирован (правка engine в таблице); HW-RT только 3080@1080p; шейдерный статтер everywhere; TSR бэкпорт. Профиль без GI — недоспецифицирован мной; вердикт по GPU не вынесен честно.

## Спот-проверка плюсов/минусов (топ-5 рекомендаций + риски)

- Upscaling-мандатные игры (TDU, Ronin, MHWilds): `temporal_upscaling` в топ-5 НЕ входит (там дешёвые универсалы: contact shadows, patch pipeline, tiers). Он recommended ниже — приемлемо при balanced-приоритете, но наблюдение: топ оккупирован универсалами, специфика проекта — в рисках/similar/корзине. Не баг (TOPSIS так задуман), зафиксировано.
- PSO-урок (Atomic 12GB, Ghostwire/HL статтер): `pso_precaching_warmup` ~#30 lower_priority. Флаг не врёт («дешёвые победы раньше»), но обязательную гигиену DX12 недодаёт весом. Данных для смены gain/cost нет — НЕ МЕНЯЮ, наблюдение.
- Риски на реальных данных: CS2 crowd_budget ✓, Squad network_scale ✓ (100 ≥ 16 — ветка проверена), FFXIV/New World crowd+network ✓, HD2-профиль ранее — тишина по правилам ✓.
- Similar вменяем: MHWilds→Horizon 0.929, Ronin→Horizon 0.929, TDU→GTA V 0.867, Borderlands 3 топ для R2-кейса ранее, DD2 (добавлен прошлым шагом) — топ для Atomic 0.912 / CS2 0.96 / Shadows 0.947. Низкие оценки там, где аналога нет (HD2 0.719) — честность, не натяжка.

## Что исправлено этим шагом

1. `wild66.json`: 5 движков проставлены по верифицированным источникам
   (Ghostwire/Hi-Fi/Tekken/Lies/Stellar → unreal: DF/DSOG/XDA).
   На shipped-код не влияет (оценка железа движок не использует).
2. Shipped-код и данные: БЕЗ ИЗМЕНЕНИЙ — сознательно. Ни одна формула не
   получила доказанного механизма ошибки: средний GPU-байас ≈ 0 при matching
   targets; CPU +0.4 базовый (шум квантования ±0.5) + threading-слепота
   (не чинится константами — см. ниже).

## Бэклог (факты, не хотелки)

1. Неточные якоря каталога (частотность в 66): RTX 2060S, RTX 2080/2080S,
   GTX 1070/Ti, RTX 2070, RTX 3060Ti есть, RTX 3070 есть, 7800X3D, i7-10700K,
   i5-10600K, Ryzen 5 3600X/5600X? (проверить), i7-8700 (non-K), i7-4790.
   Добавление требует PassMark-чисел + полных спек-строк — не выдумано,
   поэтому не сделано в этом шаге.
2. Слепая зона threading quality: ввод «качество кода» невозможен без новых
   вопросов анкеты (фича, не фикс) — не делать молча.
3. Базовая стоимость поколения движка (UE5 без Lumen всё равно дороже):
   нечем выразить в функциях — кандидат в фичи, не правка.
4. P2P/хост-налог — уже в README §11 прошлым шагом.
5. Riesige профили: `collision_layer_matrix` в топ-5 почти везде — проверить
   его веса отдельно (подозрение на over-rank, фактов пока нет — НЕ ТРОГАТЬ).

## Вывод

66 игр: GPU — mean +0.46 на 28 точных якорях (n=28, {-1:1, 0:13, 1:14}),
≈+0.2 на подмножестве с проверенными целями 1080p/60 — в пределах квантования,
систематического смещения нет; CPU — mean +0.91 на 23 якорях, из них базовых
≈+0.4 (шум квантования ±0.5, правке не подлежит) и +2 только у исключительно
threaded игр (Lies, Stellar — слепая зона модели, не баг формулы);
плюсы/минусы (флаги, риски, similar) — вменяемы на проверенных кейсах.
Формулы и данные shipped-кода не тронуты: доказательств для правок нет,
подгонки под анекдоты не будет. Материалы (wild66.json + wild66_probe.py +
wild66_cmp.py + результаты) сохранены для аудита.
