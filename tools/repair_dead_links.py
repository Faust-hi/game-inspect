#!/usr/bin/env python3
"""Repair unreachable sources in the research packs - without inventing evidence.

The orchestrator's ground truth is HTTP reachability. A source that returns
404/410 no longer supports the claims that cite it, so this tool does one of
two honest things and never a third:

  1. REPLACE  - when a verified (HTTP 200) replacement URL is known, rewrite
                the URL and say in `applicability_note` that it was replaced.
  2. DECLARE  - when no replacement exists, mark the source
                `unreachable_at_verification`, downgrade the citing claims to
                verification_state='source_unreachable' / evidence_level='low',
                and leave the original statement text untouched.

What it never does: silently delete a claim, silently keep a dead link, or
invent a new URL. Under the study's rules, an unreachable source is a
*weakness of evidence*, not a proof of absence and not a fabrication.

Sources that only failed with a network/proxy error (502 tunnel, TLS timeout)
are NOT marked dead - they are annotated as
"previously fetched; not re-verified on this run", which is the honest
description of a network failure rather than of a broken citation.

По умолчанию выполняется сухой прогон: паки не изменяются, печатается, что
было бы сделано. Запись выполняется только с явным флагом ``--apply``.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKS = ROOT / "research" / "packs"
VERIFY_DATE = "2026-09-11"

# Verified replacements (old URL -> what the replacement actually is).
#
# Замена описывает ЗАМЕНУ, а не только её URL. Раньше здесь лежала одна строка
# URL, и запись источника сохраняла прежние `title`, `author_or_publisher`,
# `source_type` и `locator` («n/a - server returned '404 Not Found'») при новом
# адресе. Получалось ровно то противоречие «название против URL», которое
# ловит собственный детектор проекта: Digital Foundry-разбор со ссылкой на
# статью Википедии и `availability='verified_fetched'` при локаторе с 404.
# Каждый `url` HTTP-проверен на 2xx перед записью.
REPLACEMENTS: dict[str, dict[str, str]] = {
    "https://www.digitalfoundry.net/articles/digitalfoundry-2021-it-takes-two-tech-analysis": {
        "url": "https://en.wikipedia.org/wiki/It_Takes_Two_(video_game)",
        "title": "It Takes Two (encyclopedia article)",
        "author_or_publisher": "Wikipedia contributors",
        "source_type": "encyclopedia",
        "locator": "article lead and development section",
    },
}

# URLs that failed only because of the local network/proxy on this run.
NETWORK_NOISE_HINTS = ("tunnel connection failed", "handshake operation timed out",
                       "bad gateway", "timed out", "connection aborted")


def load_report() -> dict | None:
    p = ROOT / "research" / "verification_report.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Заменить недоступные источники в паках или объявить их недоступными")
    parser.add_argument(
        "--apply", action="store_true",
        help="записать изменения в паки; без флага выполняется только сухой прогон")
    args = parser.parse_args()

    report = load_report()
    if not report:
        print("no verification_report.json - run tools/verify_sources.py first", file=sys.stderr)
        return 1

    url_results = report.get("packs", {}).get("url_results", {})
    dead = {u for u, r in url_results.items() if r.get("status") == "dead"}
    neterr = {u for u, r in url_results.items()
              if r.get("status") == "error"
              and any(h in (r.get("note") or "").lower() for h in NETWORK_NOISE_HINTS)}

    replaced = declared = annotated = claims_downgraded = 0

    for path in sorted(PACKS.glob("pack_*.json")):
        pack = json.loads(path.read_text(encoding="utf-8"))
        changed = False

        for s in pack.get("sources", []):
            url = (s.get("url") or "").strip()
            if not url:
                continue
            key = url.lower()

            if key in {d.lower() for d in dead}:
                if url in REPLACEMENTS:
                    replacement = REPLACEMENTS[url]
                    s["url"] = replacement["url"]
                    # Замена описывается целиком: адрес, название, издатель, тип
                    # и локатор. Иначе запись противоречит сама себе.
                    s["title"] = replacement["title"]
                    s["author_or_publisher"] = replacement["author_or_publisher"]
                    s["source_type"] = replacement["source_type"]
                    s["locator"] = replacement["locator"]
                    s["availability"] = "verified_fetched"
                    s["applicability_note"] = (
                        (s.get("applicability_note") or "").rstrip()
                        + f" [ORCHESTRATOR {VERIFY_DATE}: original URL returned HTTP 404 and was "
                          f"replaced with a verified alternative; the original citation is no "
                          f"longer reachable.]"
                    ).strip()
                    replaced += 1
                    changed = True
                else:
                    s["availability"] = f"unreachable_at_verification (HTTP 404 on {VERIFY_DATE})"
                    s["applicability_note"] = (
                        (s.get("applicability_note") or "").rstrip()
                        + f" [ORCHESTRATOR {VERIFY_DATE}: this URL returned HTTP 404 and could not be "
                          f"replaced. Claims citing it were downgraded to "
                          f"verification_state='source_unreachable', evidence_level='low'. The "
                          f"statement is retained but is no longer independently verifiable.]"
                    ).strip()
                    declared += 1
                    changed = True
                continue

            if key in {d.lower() for d in neterr}:
                if "not re-verified" not in (s.get("applicability_note") or ""):
                    s["applicability_note"] = (
                        (s.get("applicability_note") or "").rstrip()
                        + f" [ORCHESTRATOR {VERIFY_DATE}: could not be re-verified from this network "
                          f"(proxy/TLS failure, not an HTTP error). Reachability is unconfirmed on "
                          f"this run; the citation is not asserted to be dead.]"
                    ).strip()
                    annotated += 1
                    changed = True

        # downgrade claims whose source was declared unreachable
        unreachable = {
            (s.get("code") or ""): True
            for s in pack.get("sources", [])
            if (s.get("availability") or "").startswith("unreachable_at_verification")
        }
        if unreachable:
            for _section, block in pack.items():
                if not isinstance(block, dict):
                    continue
                for _ecode, edata in block.items():
                    if not isinstance(edata, dict):
                        continue
                    for c in edata.get("claims", []):
                        if c.get("source") in unreachable:
                            c["verification_state"] = "source_unreachable"
                            c["evidence_level"] = "low"
                            c["context"] = (
                                (c.get("context") or "").rstrip()
                                + f" [ORCHESTRATOR {VERIFY_DATE}: cited source returned HTTP 404; "
                                  f"statement retained but not independently verifiable.]"
                            ).strip()
                            claims_downgraded += 1
                            changed = True

        if changed:
            if args.apply:
                path.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"updated {path.name}")
            else:
                print(f"would update {path.name}")

    print(f"\nreplaced={replaced} declared_unreachable={declared} "
          f"network_annotated={annotated} claims_downgraded={claims_downgraded}")
    if not args.apply and (replaced or declared or annotated or claims_downgraded):
        print("сухой прогон: паки не изменены. Повторите с --apply, чтобы записать.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
