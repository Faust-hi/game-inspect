"""Формирование итогового HTML-отчёта по прогону игр партий 01-11 через DSS."""

from __future__ import annotations

import itertools
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")

ROWS = json.loads((HERE / "compare.json").read_text(encoding="utf-8"))
RES = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
BY_ID = {r["id"]: r for r in RES}
OUT = HERE / "party_report.html"

TECH_RX = re.compile(
    r"render|shader|gpu|cpu|physic|stream|lod|cull|memory|ram|vram|netcode|tick|"
    r"pathfind|light|shadow|texture|terrain|draw|thread|anim|audio|save|compress|bake|"
    r"occlus|reflection|water|particle|destruct|loading|fps|frame|vulkan|dx1|directx|"
    r"mesh|vertex|fill|bandwidth|cache|pool|instanc|simulat|collision|ray|rt|ssd|hdd|"
    r"resolution|upscal|denois|probe|gi_|voxel|nav|job|thread"
)


def esc(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def bar(value, vmax, color="#2563eb"):
    w = 0 if not vmax else max(2, round(100 * float(value) / float(vmax)))
    return f'<div class="bar"><span style="width:{w}%;background:{color}"></span></div>'


def fmt(v, nd=3, dash="—"):
    return dash if v is None else f"{v:.{nd}f}"


def main() -> None:
    n_games = len(ROWS)
    n_dec = sum(r["n_decisions"] for r in ROWS)
    n_match_dec = sum(r["n_decisions_matched"] for r in ROWS)
    coverage = 100.0 * n_match_dec / n_dec
    dev = [r["gpu_deviation"] for r in ROWS if r["gpu_deviation"] is not None]
    mean_dev = sum(dev) / len(dev)
    over = sum(1 for d in dev if d > 0.05)
    same = sum(1 for d in dev if abs(d) <= 0.05)
    under = sum(1 for d in dev if d < -0.05)
    cpu_main = sum(1 for r in ROWS if "главный поток" in (r["bottleneck"] or ""))

    by_party = defaultdict(list)
    for r in ROWS:
        by_party[r["party"]].append(r)

    unmatched = Counter()
    for r in RES:
        for code in r["unmatched"]:
            unmatched[code] += 1
    tech_candidates = [c for c in unmatched if TECH_RX.search(c)]
    tech_candidates.sort(key=lambda c: (-unmatched[c], c))

    gpu_max = max(r["gpu_index"] or 0 for r in ROWS)
    cov_max = 100.0

    # ---------- таблица «железо» ----------
    hw_rows = sorted(ROWS, key=lambda r: -(r["gpu_index"] or 0))
    hw_html = []
    for r in hw_rows:
        d = r["gpu_deviation"]
        cls = "ok" if d is not None and abs(d) <= 0.05 else ("over" if (d or 0) > 0 else "under")
        hw_html.append(
            f"<tr>"
            f"<td class='name'>{esc(r['title'])}<div class='sub'>{r['party']:02d} · {r['year']} · "
            f"{esc(r['engine_raw'])[:44]}</div></td>"
            f"<td class='sub2'>{esc(r['world'])} / {esc(r['scale'])}<br>{esc(r['target'])} · {esc(r['api'])}</td>"
            f"<td>{esc(r['cpu_ref'])}<div class='sub'>класс {r['cpu_class']}</div></td>"
            f"<td>{esc(r['gpu_ref'] or 'вне каталога')}<div class='sub'>индекс "
            f"{fmt(r['gpu_index'], 3)}"
            f"{'' if r['gpu_ref'] else ' — превышает каталог'}"
            f"</div>{bar(min(r['gpu_index'] or 0, gpu_max), gpu_max)}</td>"
            f"<td class='num'>{fmt(r['ram_gb'], 1)}<div class='sub'>VRAM {fmt(r['vram_gb'], 1)}</div></td>"
            f"<td>{esc(r['bottleneck'])}<div class='sub'>доверие: {esc(r['confidence'])}</div></td>"
            f"<td>{esc(r['real_gpu'] or 'нет в каталоге')}</td>"
            f"<td class='num {cls}'>{fmt(d, 3)}</td>"
            f"</tr>"
        )

    # ---------- таблица «инженерные решения» ----------
    eng_rows = sorted(ROWS, key=lambda r: -r["coverage"])
    eng_html = []
    for r in eng_rows:
        rj = BY_ID[r["id"]]
        rb = rj["recommendations_base"]
        ra = rj.get("recommendations_arch") or {}
        top = [x for x in (rb.get("recommendations") or [])[:5]]
        top_txt = "<br>".join(
            f"{i+1}. {esc(x['method_name'])} <span class='sub'>({esc(x['method_code'])})</span>"
            for i, x in enumerate(top)
        )
        arch = (ra.get("recommendations") or [])[:3]
        arch_txt = "<br>".join(f"— {esc(x['method_name'])}" for x in arch) or "—"
        risks = rj["recommendations_base"].get("risks") or []
        risk_txt = "<br>".join(
            f"• {esc(x.get('title'))} <span class='sub'>[{esc(x.get('severity'))}]</span>"
            for x in risks[:3]
        ) or "—"
        eng_html.append(
            f"<tr>"
            f"<td class='name'>{esc(r['title'])}<div class='sub'>партия {r['party']:02d}</div></td>"
            f"<td class='num'>{r['n_decisions']}<div class='sub'>в партии</div></td>"
            f"<td class='num'>{r['n_decisions_matched']}"
            f"<div class='sub'>{r['coverage']:.0f}%</div>"
            f"{bar(r['coverage'], cov_max, '#0d9488')}</td>"
            f"<td class='num'>{r['basket_size']}<div class='sub'>методов DSS</div></td>"
            f"<td class='num'>{fmt(r['d_cpu_index'], 3)}<div class='sub'>GPU {fmt(r['d_gpu_index'], 3)}</div></td>"
            f"<td class='num'>{fmt(r['d_ram_gb'], 1)}<div class='sub'>VRAM {fmt(r['d_vram_gb'], 1)}</div></td>"
            f"<td class='num'>{r['top10_hit']}/10<div class='sub'>совпало с топ-10</div></td>"
            f"<td class='sub2'>{top_txt}</td>"
            f"<td class='sub2'>{arch_txt}</td>"
            f"<td class='sub2'>{risk_txt}</td>"
            f"</tr>"
        )

    # ---------- расхождения ----------
    diverg = sorted(
        [r for r in ROWS if r["gpu_deviation"] is not None],
        key=lambda r: -abs(r["gpu_deviation"]),
    )[:12]
    div_html = "\n".join(
        f"<tr><td class='name'>{esc(r['title'])}</td>"
        f"<td class='num'>{fmt(r['gpu_index'])}</td>"
        f"<td>{esc(r['real_gpu'])}</td>"
        f"<td class='num'>{fmt(r['real_gpu_score'])}</td>"
        f"<td class='num {'over' if r['gpu_deviation'] > 0 else 'under'}'>{r['gpu_deviation']:+.3f}</td>"
        f"<td class='sub2'>{esc((r['real_gpu_src'] or '')[:90])}</td></tr>"
        for r in diverg
    )

    # ---------- покрытие по партиям ----------
    party_html = []
    for p in sorted(by_party):
        rs = by_party[p]
        c = sum(x["coverage"] for x in rs) / len(rs)
        names = ", ".join(x["title"].split("(")[0].strip()[:22] for x in rs)
        party_html.append(
            f"<tr><td class='num'>{p:02d}</td><td class='num'>{len(rs)}</td>"
            f"<td class='num'>{c:.0f}%{bar(c, 100, '#0d9488')}</td>"
            f"<td class='sub2'>{esc(names)}</td></tr>"
        )

    # ---------- дифференциация рекомендаций ----------
    tops = [
        [x["method_code"] for x in ((r.get("recommendations_base") or {}).get("recommendations") or [])[:10]]
        for r in RES
    ]
    top_counter = Counter()
    for t in tops:
        top_counter.update(t)
    jac = [
        len(set(a) & set(b)) / len(set(a) | set(b))
        for a, b in itertools.combinations(tops, 2)
    ]
    jac_mean = sum(jac) / len(jac)
    basket_counter = Counter()
    for r in RES:
        basket_counter.update(r["basket_resolved"])
    uniq_top, uniq_basket = len(top_counter), len(basket_counter)
    freq_html = "\n".join(
        f"<tr><td><code>{esc(code)}</code></td><td class='num'>{n} / {n_games}</td>"
        f"<td class='num'>{basket_counter.get(code, 0)} / {n_games}</td>"
        f"<td class='sub2'>{esc(name)}</td></tr>"
        for code, n in top_counter.most_common(13)
        for name in [
            next(
                (x["method_name"] for g in RES
                 for x in ((g.get("recommendations_base") or {}).get("recommendations") or [])
                 if x["method_code"] == code),
                "",
            )
        ]
    )

    # ---------- пробелы каталога ----------
    gap_html = "\n".join(
        f"<li><code>{esc(c)}</code></li>" for c in tech_candidates[:40]
    )

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Игры партий 01–11 в DSS: железо и инженерные решения</title>
<style>
  :root {{ --bg:#ffffff; --fg:#111827; --muted:#6b7280; --line:#e5e7eb; --soft:#f9fafb;
          --blue:#2563eb; --teal:#0d9488; --red:#dc2626; --amber:#d97706; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:32px 40px 64px; background:var(--bg); color:var(--fg);
         font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif; }}
  h1 {{ font-size:26px; margin:0 0 6px; }}
  h2 {{ font-size:19px; margin:40px 0 12px; padding-bottom:6px; border-bottom:1px solid var(--line); }}
  h3 {{ font-size:15px; margin:24px 0 8px; }}
  p {{ margin:8px 0; max-width:1050px; }}
  .lead {{ color:var(--muted); margin-top:0; }}
  .cards {{ display:flex; gap:14px; flex-wrap:wrap; margin:18px 0 4px; }}
  .card {{ border:1px solid var(--line); border-radius:10px; padding:12px 16px; min-width:150px; background:var(--soft); }}
  .card b {{ display:block; font-size:22px; line-height:1.2; }}
  .card span {{ color:var(--muted); font-size:12px; }}
  table {{ border-collapse:collapse; width:100%; margin-top:10px; font-size:12.5px; }}
  th, td {{ border:1px solid var(--line); padding:6px 8px; vertical-align:top; text-align:left; }}
  th {{ background:var(--soft); font-weight:600; position:sticky; top:0; }}
  td.num {{ text-align:right; white-space:nowrap; }}
  td.name {{ min-width:230px; }}
  .sub {{ color:var(--muted); font-size:11px; font-weight:400; }}
  .sub2 {{ font-size:11.5px; color:#374151; }}
  .bar {{ background:#eef2f7; border-radius:3px; height:5px; margin-top:4px; overflow:hidden; }}
  .bar span {{ display:block; height:100%; }}
  .over {{ color:var(--red); }} .under {{ color:var(--amber); }} .ok {{ color:var(--teal); }}
  code {{ background:var(--soft); padding:1px 4px; border-radius:3px; font-size:12px; }}
  ul.gap {{ columns:2; column-gap:26px; font-size:12px; }}
  .note {{ border-left:3px solid var(--amber); background:#fffbeb; padding:10px 14px; margin:14px 0;
           border-radius:0 6px 6px 0; max-width:1050px; }}
  .wrap {{ overflow-x:auto; }}
</style>
</head>
<body>
<h1>Игры из партий 01–11 в расчёте DSS</h1>
<p class="lead">Все 58 игр из реестров партий преобразованы в профили <code>ProjectProfile</code> и прогнаны
через расчётное ядро проекта: аппаратную оценку и подбор инженерных методов. Дополнительно
выполнена сверка с реальными «Rec HW» из инженерных паспортов партий.</p>

<div class="cards">
  <div class="card"><b>{n_games}</b><span>игр прогнано</span></div>
  <div class="card"><b>{n_dec}</b><span>инженерных решений в партиях</span></div>
  <div class="card"><b>{coverage:.1f}%</b><span>решений представимо в каталоге</span></div>
  <div class="card"><b>{len(dev)}</b><span>игр сверено с Rec HW</span></div>
  <div class="card"><b>{mean_dev:+.3f}</b><span>среднее отклонение по GPU</span></div>
  <div class="card"><b>{cpu_main}</b><span>из {n_games} — упор в главный поток CPU</span></div>
  <div class="card"><b>{uniq_top}</b><span>методов встречается в топ-10 (из 111)</span></div>
  <div class="card"><b>{jac_mean:.2f}</b><span>похожесть топ-10 между играми</span></div>
</div>

<h2>Как считалось</h2>
<p>Партии 01–11 разобраны автоматически: из карточки игры извлечены движок, тип мира, масштаб,
уровни объектов и NPC, мультиплеер, кадровая цель и API; из раздела «Инженерные решения» —
список методов с реализацией. Каждое решение сопоставлялось с 111 методами каталога по
ключевым словам кода и описания; совпадения образовали корзину (<code>basket</code>) — то, что игра
реально реализовала в терминах DSS. Затем для каждой игры вызывались
<code>estimate_hardware</code> (базовая оценка профиля и оценка с корзиной),
<code>aggregate_load</code> и <code>build_recommendations</code>. Все игры заданы на стадии
<code>release</code> (это свершившиеся проекты), поэтому первый срез рекомендаций ограничен
поздними правками; чтобы увидеть и архитектурные советы, сделан второй срез с той же корзиной,
но на стадии <code>prototype</code>.</p>
<div class="note"><b>Ограничения.</b> Движки партий, которых нет в каталоге (RAGE, REDengine, AnvilNext,
Creation, id Tech, Frostbite, 4A, Northlight, Real Virtuality и др.), сведены в <code>custom</code> —
поэтому движковые инструменты и версионные ограничения для них не работают. Каталог оборудования
содержит 79 современных GPU, поэтому старые паспорта (GTX 660, HD 7850, R9 290X) сверить нельзя:
сверка выполнена для {len(dev)} игр из {n_games}. Расчёт всегда ориентировочный — в отчёте
сохранены <code>confidence</code> и <code>caveats</code> из ответа сервиса.</div>

<h2>1. Аппаратная оценка: рейтинг по требованию к GPU</h2>
<p>Сортировка по требуемому индексу GPU (шкала каталога: 0 — минимальный класс, 1 — верх каталога).
Значение выше 1 означает, что профиль выходит за пределы каталога.</p>
<div class="wrap">
<table>
<thead><tr>
  <th>Игра</th><th>Профиль</th><th>CPU (референс)</th><th>GPU (референс)</th>
  <th>RAM / VRAM, ГБ</th><th>Узкое место</th><th>Rec GPU из паспорта</th><th>Отклонение</th>
</tr></thead>
<tbody>
{''.join(hw_html)}
</tbody></table>
</div>

<h2>2. Инженерные решения: что DSS видит в реализации</h2>
<p>«Представимо» — доля решений игры, для которых в каталоге нашёлся метод-аналог.
«Δ» — как реализованные решения изменили требуемые ресурсы относительно голого профиля
(положительное значение = решения добавили нагрузку). «Совпало с топ-10» — сколько методов
из первой десятки рекомендаций DSS игра фактически реализовала.</p>
<div class="wrap">
<table>
<thead><tr>
  <th>Игра</th><th>Решений</th><th>Представимо</th><th>В корзине</th>
  <th>Δ CPU / GPU</th><th>Δ RAM / VRAM</th><th>Совпало</th>
  <th>Рекомендации на стадии релиза (топ-5)</th>
  <th>Если бы проект начинался с нуля (топ-3)</th><th>Риски профиля</th>
</tr></thead>
<tbody>
{''.join(eng_html)}
</tbody></table>
</div>

<h2>3. Сверка с реальным «Rec HW»</h2>
<p>GPU из инженерного паспорта партии ищется в каталоге оборудования; его
<code>raster_score</code> сравнивается с требуемым индексом расчёта. Положительное отклонение —
DSS требует больше реального, отрицательное — оценил мягче, чем заявлял разработчик.</p>
<p>Итог по {len(dev)} играм: <b class="over">{over}</b> — расчёт строже паспорта,
<b class="ok">{same}</b> — совпало в пределах ±0.05,
<b class="under">{under}</b> — расчёт мягче паспорта.</p>
<div class="wrap">
<table>
<thead><tr><th>Игра</th><th>Индекс DSS</th><th>Rec GPU</th><th>Его индекс</th>
<th>Отклонение</th><th>Источник строки</th></tr></thead>
<tbody>
{div_html}
</tbody></table>
</div>

<h2>4. Насколько рекомендации зависят от профиля</h2>
<p>Сравнение первых десяток рекомендаций по всем 58 играм: в топ-10 встречается всего
<b>{uniq_top} различных методов</b> из 111, {sum(1 for c, n in top_counter.items() if n == n_games)} из них
попадают в десятку <b>у всех игр подряд</b>, средняя похожесть Жаккара между десятками двух игр —
<b>{jac_mean:.2f}</b>. Для сравнения: корзины реально реализованных решений используют
{uniq_basket} различных методов — разнообразие на порядок выше.</p>
<p>Причина в модели: у_methods примерно равный экспертный балл, и TOPSIS выдаёт группу
«равнозначных» решений, внутри которой порядок определяется не профилем, а обходом каталога.
То есть верх рекомендаций почти не несёт информации о проекте — это дефект ранжирования,
а не совпадение.</p>
<div class="wrap">
<table>
<thead><tr><th>Метод</th><th>Попал в топ-10</th><th>Реально реализован</th><th>Название</th></tr></thead>
<tbody>
{freq_html}
</tbody></table>
</div>

<h2>5. Покрытие каталога по партиям</h2>
<div class="wrap">
<table>
<thead><tr><th>Партия</th><th>Игр</th><th>Среднее покрытие</th><th>Состав</th></tr></thead>
<tbody>{''.join(party_html)}</tbody>
</table>
</div>

<h2>6. Пробелы каталога</h2>
<p>Из {n_dec} решений партий {n_dec - n_match_dec} ({(100 - coverage):.1f}%) не имеют аналога среди
111 методов каталога. Это не ошибка: значительная часть таблиц партий — геймплейные,
контентные и издательские решения (концовки, DLC, споры вокруг монетизации), которые DSS
по своей предметной области описывать не должен. Ниже — технические формулировки без аналога;
это кандидаты на расширение каталога ({len(tech_candidates)} из {len(unmatched)} уникальных).</p>
<ul class="gap">
{gap_html}
</ul>

<h2>7. Что это значит для проекта</h2>
<p><b>Железо.</b> Расчёт адекватно различает весовые категории: Alan Wake 2 (4K/60 + path tracing)
уходит за пределы каталога, Cyberpunk 2077 требует RX&nbsp;6700&nbsp;XT-уровня, а Portal и CS:S
остаются на RX&nbsp;580. Среднее отклонение от паспортного Rec HW — {mean_dev:+.3f} по шкале
каталога, то есть системной ошибки в одну сторону нет. Основная точка роста — обработка
профилей, у которых комбинация «4K + полная трассировка + 60 fps» даёт индекс &gt; 1:
сейчас это «вне каталога», а нужно честно показывать «достижимо только с апскейлингом /
генерацией кадров».</p>
<p><b>Инженерные решения.</b> Каталог покрывает примерно треть записанных решений, но покрытие
сильно зависит от партии: 11% у FromSoftware (таблицы там в основном геймплейные) против
66% у партии 11 и 62% у партии 1. Упор в главный поток CPU у 53 игр из 58 — расчёт
последовательно считает главный поток главным риском, и это совпадает с содержанием партий
(Arma 3, Crysis, Skyrim, BF2042 — все CPU-bound по факту).</p>
<p><b>Главный дефект, который вскрыл прогон.</b> Рекомендации почти не зависят от профиля:
{top_counter.most_common(1)[0][1]} игр из {n_games} получают в топ-10 один и тот же метод
<code>{top_counter.most_common(1)[0][0]}</code>, а средняя похожесть десяток — {jac_mean:.2f}.
Значит, верх списка формируется не профилем проекта, а равенством экспертных баллов и порядком
обхода каталога. Пока это не исправлено (нужен либо разброс баллов, либо привязка весов
TOPSIS к профилю, либо явная группировка «равнозначных» без искусственного ранга),
сравнивать игры по рекомендациям нельзя — можно сравнивать только по аппаратной оценке
и по корзине.</p>
<p><b>Практический вывод.</b> Методика «сверка расчёта с реальными играми», которая сейчас
заглушена в <code>practice_check</code>, может быть наполнена этими 58 профилями: у каждой игры
есть паспортный Rec HW, кадровый бюджет и список реализованных решений. Это даст
калибровочную выборку, а не только экспертные коэффициенты.</p>

<p class="sub">Отчёт сформирован скриптами <code>validation/parties/</code>:
<code>build_games.py</code> → <code>build_profiles.py</code> → <code>run_dss.py</code> →
<code>compare.py</code> → <code>report.py</code>. Данные: <code>games_raw.json</code>,
<code>profiles.json</code>, <code>results.json</code>, <code>compare.json</code>.</p>
</body>
</html>"""

    OUT.write_text(html, encoding="utf-8")
    print(f"отчёт: {OUT} ({len(html)} символов)")
    print(f"игр {n_games}, решений {n_dec}, покрытие {coverage:.1f}%, сверок GPU {len(dev)}")


if __name__ == "__main__":
    main()
