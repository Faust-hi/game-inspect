# Research worker brief — evidence packs for the gamedev DSS

You are a research worker. You produce **one JSON file** per assignment.
An orchestrator will independently re-check every URL you cite. A single
invented URL invalidates the whole pack, so honesty beats volume.

## Output file

Write exactly the path given in your assignment (under `research/packs/`).
It is consumed by `backend/app/seed/pack_loader.py` (`pack_*.json`).

## Top-level shape

```json
{
  "pack": "<pack_name>",
  "generated": "2026-09-10",
  "agent_scope": "one sentence",
  "sources": [ SOURCE, ... ],
  "<section>": { "<entity_code>": ENTITY, ... }
}
```

`<section>` ∈ {`methods`, `functions`, `engines`, `engine_tools`,
`technology_nodes`, `cases`, `platforms`, `stage_budgets`, `network_modes`,
`target_metrics`, `load_profiles`, `risk_factors`}.

Entity keys MUST be exactly the `code` values given in your assignment
(they already exist in the database). Do not invent new codes.

## SOURCE

```json
{
  "code": "SRC-<PACK>-001",
  "title": "Exact title of the real document",
  "author_or_publisher": "Author / studio / org",
  "source_type": "official_documentation|api_specification|academic_paper|conference_talk|postmortem|open_source|hardware_benchmark|interview|engineering_blog|book|vendor_press_release|standard|secondary",
  "published_date": "YYYY or YYYY-MM or YYYY-MM-DD",
  "verified_date": "2026-09-10",
  "url": "https://real-url-you-actually-opened",
  "engine_or_api_version": "UE 5.4 / Unity 6 / Vulkan 1.3 / ...",
  "platform": "Windows PC / Linux PC / cross-platform",
  "locator": "p.12 / §3.2 / 00:14:35 / section 'Virtual Shadow Maps'",
  "availability": "verified_fetched | verified_url_only | paywalled | not_accessible",
  "applicability_note": "what this source does and does NOT prove"
}
```

`locator` is mandatory and must be specific. `published_date` is mandatory —
use the real year of the document (a 2021 GDC talk is 2021, not the crawl date).

## ENTITY

```json
{ "claims": [ CLAIM, ... ], "game_examples": [ GAME_EXAMPLE, ... ] }
```

## CLAIM

```json
{
  "field": "<the catalog field being evidenced>",
  "statement": "factual sentence, reproducible, specific",
  "unit": "ms | % | GiB | person-days | ... or empty string",
  "value": 12.5,
  "value_range": [10.0, 15.0],
  "source": "SRC-<PACK>-001",
  "locator": "page/section/timestamp proving THIS claim",
  "basis": "measured|documented|derived|case_evidence|expert_estimate|unknown",
  "verification_state": "verified|unverified|contradicted",
  "evidence_level": "high|medium|low",
  "formula": "required when basis=derived",
  "input_parameters": {"k": "v"},
  "context": "scope conditions under which this holds"
}
```

Use `"value": null` when the source states something qualitatively. Never
convert "significantly faster" into a number.

## GAME_EXAMPLE

```json
{
  "game": "Game Title", "studio": "Studio", "year": 2019,
  "engine": "Unreal Engine 4.22", "world_type": "open_world|linear|arena",
  "network_mode": "single|coop|dedicated_server|p2p",
  "fact": "what is publicly confirmed to exist in this game",
  "locator": "GDC talk 00:12:40 / postmortem p.4",
  "source": "SRC-<PACK>-001",
  "relevance": "exact|strong|partial|weak",
  "non_transferable": "what must NOT be copied to another project"
}
```

Game examples within one entity must be **different games**.

## HARD RULES — violation means the pack is rejected

1. **Never invent a URL.** Open it (WebFetch) or confirm it in search results.
   If you did not open it, do not cite it.
2. `availability` honest: `verified_fetched` ONLY if you retrieved content.
3. **Never claim a number the source does not contain.**
4. `basis=derived` REQUIRES `formula` AND `input_parameters`.
5. `basis=expert_estimate` must state in `context` that it is an estimate and why.
6. **Absence of a source is never compatibility.** Emit `basis:"unknown"` and
   describe the gap. Do not omit, do not fabricate.
7. Distinct games per entity (two examples from the same title = one).
8. `locator` must be precise; "the docs" is rejected.
9. Claims must add information, not restate the entity name.
10. Prefer primary sources; mark secondary ones as `secondary` in
    `source_type` and say why in `applicability_note`.

## Quality bar the orchestrator will enforce

Per entity: **≥3 claims**, **≥2 distinct sources carrying a locator**,
**≥2 independent game examples** (game-proofs where the assignment asks for
them). Numeric claims must resolve to a real source. Sources whose URL does
not return HTTP 2xx will be dropped automatically.

## Working method that works here

- `research/_mp/get.py <url>` downloads + extracts text/PDF (cached in `_mp/dl`).
  `LIM=30000 python get.py <url>` for longer extracts. Use it for PDFs/PPTs.
- `WebSearch` to find the primary source, then `WebFetch`/`get.py` to confirm.
- Prefer official engine docs, SIGGRAPH/GDC talks, engine source on GitHub,
  academic papers, vendor engineering blogs. Books are acceptable sources.
- Budget your effort: breadth of *verified* sources beats depth on one topic.
