# Системные требования игр из прогонов — обновление 2026-09-12

## Зачем

Эталон, по которому сверялась модель железа, был кураторским набором без источников.
В нём нашлись ошибки — одну (Ashes, 8 ГБ вместо 6) нашёл пользователь вручную. Проверка
всех строк показала, что ошибка не одна: **в 15 играх из 25 была неверна память**, ещё
в двух — уточнены процессор и видеокарта. Любой вывод, опиравшийся на этот эталон,
наследовал эти ошибки.

## Как собиралось

* Для 20 игр — витрина Steam, поле `pc_requirements` (`store.steampowered.com/api/appdetails`).
  Это требования, которые издатель публикует на своей странице сейчас.
* Для 4 игр, которых в Steam нет: VALORANT — страница Riot, Alan Wake 2 — служба поддержки
  Epic, Minecraft — статья Mojang, Fortnite — агрегатор technical.city (Epic не публикует
  отдельной страницы требований).
* Где издатель не указывает модель процессора или видеокарты, стоит «модель не указана».
  Прежние правдоподобные модели («Core i5-4690» для Minecraft) убраны: они были выдуманы.
* Сырые ответы витрины сохранены в `tmp/cache/steam/`, поэтому выгрузка воспроизводима.

**Важная оговорка: это требования текущей версии, а не релиза.** Для живых игр
(BeamNG.drive, SW:TOR, Hunt: Showdown, No Man's Sky) издатель поднимал их со временем,
иногда кратно. Сравнение с моделью теперь сопоставляет «проект под сегодняшнюю цель» с
«требованиями сегодняшнего билда» — это честнее, чем сравнивать с релизными, но это не
«требования на момент выхода».

## Таблица

`—` означает «издатель эту ступень не публикует», а не «равно минимуму».

| id | игра | год | мин. CPU | мин. GPU | мин. RAM | рек. CPU | рек. GPU | рек. RAM |
|---|---|---|---|---|---|---|---|---|
| S01 | Left 4 Dead | 2008 | Pentium 4 3.0 ГГц | 128 МБ, SM 2.0 (Radeon 9600 / GeForce 6600) | 1 ГБ | Core 2 Duo 2.4 ГГц | GeForce 7600 / Radeon X1600 | 1 ГБ |
| S02 | Counter-Strike 2 | 2023 | 4 потока, Core i5 750 или выше | 1 ГБ, DirectX 11 | 8 ГБ | — (только минимум) | — | — |
| S03 | Portal 2 | 2011 | 3.0 ГГц P4 / Dual Core 2.0 / AMD64X2 | 128 МБ, PS 2.0b (Radeon X800 / GeForce 7600) | 2 ГБ | — (только минимум) | — | — |
| S04 | It Takes Two | 2021 | Core i3-2100T / FX-6100 | GeForce GTX 660 / Radeon R7 260X | 8 ГБ | Core i5-3570K / Ryzen 3 1300X | GeForce GTX 980 / R9 290X | 16 ГБ |
| S05 | Split Fiction | 2025 | Core i5-6600K / Ryzen 5 2600X | GTX 970 4 ГБ / RX 470 4 ГБ | 16 ГБ | Core i7-11700K / Ryzen 7 5800X | RTX 3070 8 ГБ / RX 6700 XT 12 ГБ | 16 ГБ |
| S06 | Unreal Engine City Sample | 2021 | — (демо движка) | — | — | 12-ядерный CPU (Epic) | GeForce RTX 2080 | 64 ГБ |
| S07 | Fortnite | 2017 | Core i3-3225 3.3 ГГц | Intel HD 4000 / Radeon Vega 8 | 8 ГБ | Core i5-7300U / Ryzen 3 3300U | GTX 960 / R9 280, 2 ГБ | 8 ГБ |
| S08 | VALORANT | 2020 | Core i3-540 / Athlon 200GE | Intel HD 4000 / Radeon R5 220 | 4 ГБ | Core i3-4150 / Ryzen 3 1200 | GT 730 / Radeon R7 240 | 4 ГБ |
| S09 | DOOM Eternal | 2020 | Core i5 3.3 ГГц / Ryzen 3 3.1 ГГц | GTX 1050 Ti 4 ГБ / GTX 1060 3 ГБ / R9 280 3 ГБ | 8 ГБ | Core i7-6700K / Ryzen 7 1800X | GTX 1060 6 ГБ / GTX 970 4 ГБ / RX 480 8 ГБ | 8 ГБ |
| S10 | Cyberpunk 2077 | 2020 | Core i7-6700 / Ryzen 5 1600 | GTX 1060 6 ГБ / RX 580 8 ГБ / Arc A380 | 12 ГБ | Core i7-12700 / Ryzen 7 7800X3D | RTX 2060 Super / RX 5700 XT / Arc A770 | 16 ГБ |
| S11 | No Man's Sky | 2016 | Core i3 | GTX 1060 3 ГБ / RX 470 4 ГБ / UHD 630 | 8 ГБ | — (только минимум) | — | — |
| S12 | Microsoft Flight Simulator | 2020 | Core i5-4460 / Ryzen 3 1200 | GTX 770 / RX 570 | 8 ГБ | Core i5-8400 / Ryzen 5 1500X | GTX 970 / RX 590 | 16 ГБ |
| S13 | Teardown | 2020 | 4-ядерный | GTX 1060 или аналогичная, 4 ГБ VRAM | 8 ГБ | Core i7 или лучше | GTX 1080 или аналогичная, 4 ГБ VRAM | 8 ГБ |
| S14 | BeamNG.drive | 2015 | Ryzen 5 1600 / Core i5-8400 | RX 570 / GTX 1060, от 6 ГБ VRAM | 16 ГБ | Ryzen 7 3700X / Core i7-9700 | RX 6700 / RTX 3060, от 8 ГБ VRAM | 32 ГБ |
| S15 | Ashes of the Singularity | 2016 | 4-ядерный Intel / AMD | GeForce 660 / R7 360, 2 ГБ GDDR5 | 6 ГБ | Core i5 или эквивалент | GTX 970 / R9 390, 4 ГБ GDDR5 | 16 ГБ |
| S16 | Horizon Zero Dawn | 2017 | Core i5-2500K / FX-6300 | GTX 780 3 ГБ / R9 290 4 ГБ | 8 ГБ | Core i7-4770K / Ryzen 5 1500X | GTX 1060 6 ГБ / RX 580 8 ГБ | 16 ГБ |
| S17 | Alan Wake 2 | 2023 | Core i5-7600K / AMD эквивалент | GTX 1070 / RX 5600 XT | 16 ГБ | Ryzen 7 3700X / Intel эквивалент | RTX 3060 / RX 6600 XT | 16 ГБ |
| S18 | F.E.A.R. | 2005 | Pentium 4 1.7 ГГц | 64 МБ, GeForce 4 Ti / Radeon 9000 | 512 МБ | Pentium 4 3.0 ГГц | Radeon 9800 Pro / GeForce 6600, 256 МБ | 1 ГБ |
| S19 | Uncharted 4: A Thief's End | 2016 | Core i5-4430 / Ryzen 3 1200 | GTX 960 4 ГБ / R9 290X 4 ГБ | 8 ГБ | Core i7-4770 / Ryzen 5 1500X | GTX 1060 6 ГБ / RX 570 4 ГБ | 16 ГБ |
| S20 | Red Faction: Guerrilla | 2009 | 2.0 ГГц двухъядерный | 128 МБ, SM 3.0 (GeForce 7600 / X1300) | 1 ГБ | 3.2 ГГц двухъядерный | 256 МБ, SM 3.0 (GeForce 8800 / HD 3850) | 2 ГБ |
| S21 | Minecraft | 2011 | 4-ядерный 64-битный, модель не указана | Vulkan 1.3, от 2 ГБ VRAM, модель не указана | 8 ГБ (12 ГБ при встроенной графике) | современный, модель не указана | Vulkan 1.3, от 6 ГБ VRAM, модель не указана | 16 ГБ |
| S22 | Hunt: Showdown | 2019 | Core i7-7700 / Ryzen 5 2600 | GTX 1650 Super / RX 5500 XT, от 4 ГБ | 8 ГБ | Core i7-8700 / Ryzen 5 2700 | RTX 2060 Super / RX 6600 XT, от 8 ГБ | 12 ГБ |
| S23 | V Rising | 2022 | Core i5-6600 / Ryzen 5 1500X | GTX 750 Ti 2 ГБ / R7 360 2 ГБ | 12 ГБ | Core i5-11600K / Ryzen 5 5600X | GTX 1070 8 ГБ / RX 590 8 ГБ | 12 ГБ |
| S24 | Brotato | 2023 | 2 ГГц | 128 МБ, OpenGL 3+ | 4 ГБ | — (только минимум) | — | — |
| S25 | Star Wars: The Old Republic | 2011 | Athlon 64 X2 4000+ / Core 2 Duo 2.0 ГГц | от 1 ГБ VRAM, SM 3.0 | 6 ГБ | — (только минимум) | — | — |

## Источники

| id | источник | тип |
|---|---|---|
| S01 | https://store.steampowered.com/app/500/ | первичный, Steam |
| S02 | https://store.steampowered.com/app/730/ | первичный, Steam |
| S03 | https://store.steampowered.com/app/620/ | первичный, Steam |
| S04 | https://store.steampowered.com/app/1426210/ | первичный, Steam |
| S05 | https://store.steampowered.com/app/2001120/ | первичный, Steam |
| S06 | (демо движка, в сравнении не участвует) | — |
| S07 | https://technical.city/en/system-requirements/fortnite | агрегатор: у Epic нет страницы требований |
| S08 | https://playvalorant.com/en-us/specs/ | первичный, Riot |
| S09 | https://store.steampowered.com/app/782330/ | первичный, Steam |
| S10 | https://store.steampowered.com/app/1091500/ | первичный, Steam |
| S11 | https://store.steampowered.com/app/275850/ | первичный, Steam |
| S12 | https://store.steampowered.com/app/1250410/ | первичный, Steam |
| S13 | https://store.steampowered.com/app/1167630/ | первичный, Steam |
| S14 | https://store.steampowered.com/app/284160/ | первичный, Steam |
| S15 | https://store.steampowered.com/app/507490/ | первичный, Steam (издание Escalation) |
| S16 | https://store.steampowered.com/app/1151640/ | первичный, Steam |
| S17 | https://www.epicgames.com/help/c-202300000001644/c-202300000001749/what-are-the-minimum-system-requirements-for-alan-wake-2-a202300000012420?lang=en-US | первичный, Epic |
| S18 | https://store.steampowered.com/app/21090/ | первичный, Steam |
| S19 | https://store.steampowered.com/app/1659420/ | первичный, Steam (Legacy of Thieves Collection) |
| S20 | https://store.steampowered.com/app/20500/ | первичный, Steam |
| S21 | https://www.minecraft.net/en-us/article/minecraft-java-edition-system-requirements | первичный, Mojang; обновлено 2026-07-21 |
| S22 | https://store.steampowered.com/app/594650/ | первичный, Steam (Hunt: Showdown 1896) |
| S23 | https://store.steampowered.com/app/1604030/ | первичный, Steam |
| S24 | https://store.steampowered.com/app/1942280/ | первичный, Steam |
| S25 | https://store.steampowered.com/app/1286830/ | первичный, Steam |

## Что именно было неверно

| id | было | стало |
|---|---|---|
| S01 | рек. RAM 2 ГБ | 1 ГБ |
| S03 | мин. RAM 1 ГБ | 2 ГБ |
| S07 | рек. RAM 16 ГБ | 8 ГБ |
| S08 | рек. RAM 16 ГБ | 4 ГБ — **такой ступени нет, Riot её не публикует** |
| S09 | рек. RAM 16 ГБ | 8 ГБ |
| S10 | мин. 8 ГБ, рек. 12 ГБ | мин. 12 ГБ, рек. 16 ГБ |
| S11 | рек. RAM 8 ГБ | не публикуется |
| S12 | рек. RAM 32 ГБ | 16 ГБ (32 ГБ — уровень «Ideal», не «Recommended») |
| S13 | мин. 4 ГБ, рек. нет | мин. 8 ГБ, рек. 8 ГБ |
| S14 | мин. 4 ГБ, рек. 8 ГБ | мин. 16 ГБ, рек. 32 ГБ |
| S20 | рек. нет | рек. 2 ГБ |
| S21 | мин. 4 ГБ, рек. 8 ГБ | мин. 8 ГБ (12 ГБ при встроенной графике), рек. 16 ГБ |
| S23 | мин. 8 ГБ | 12 ГБ |
| S24 | мин. 2 ГБ | 4 ГБ |
| S25 | мин. 2 ГБ, рек. 4 ГБ | мин. 6 ГБ, рек. не публикуется |

Отдельно: **S15** — минимум 8 ГБ → 6 ГБ (нашёл пользователь, подтверждено); **S19** —
сверено с PC-портом, а не с консольным релизом.

Две ошибки заслуживают отдельного внимания, потому что они не «устарели», а были
выдуманы:

* **VALORANT, «рекомендуемые 16 ГБ».** У Riot три ступени (30 / 60 / 144+ FPS) и одна
  строка памяти на все — 4 ГБ. Отношение «рекомендуемо / минимум» ×4.0, которое я раньше
  считал главным свидетельством шаблонности published-спецификаций, оказалось просто
  несуществующей величиной.
* **Minecraft, модели CPU и GPU.** Mojang не публикует моделей, только класс
  («4-ядерный», «Vulkan 1.3, от 2 ГБ VRAM»). Записанные ранее «Core i5-4690 / A10-7800» и
  «GeForce GTX 700 / RX 200» не опирались ни на что.

## Следствия

1. Тезис «рекомендуемая память — не измерение» (§5.1 документа по масштабу) **усилился,
   но по другой причине**. Я утверждал, что медиана отношения «рекомендуемо / минимум»
   равна ровно ×2.0 — на исправленных данных она **×1.5**, а у 8 игр из 19, публикующих
   обе ступени, рекомендуемая память **в точности равна минимальной** (различаются только
   процессор и видеокарта). Разброс ×4.0 у VALORANT, который я считал сильнейшим примером,
   вообще не существовал. Вывод тот же, но основание другое и более твёрдое: издатель
   часто не считает память регулируемым параметром — она одна на все ступени.
   При этом 9 игр по-прежнему публикуют ровно «16 ГБ»: шаблон никуда не делся.
2. Все измерения точности модели против этого эталона нужно повторить. Это сделано в
   `research/project-scale-integration-audit-2026-09-12.md`.
