# Output contract for research workers

Write ONE JSON file. Name it exactly the path given in your brief.
It is loaded by `backend/app/seed/pack_loader.py` (`pack_*.json` in `research/packs/`).

## Top level

```json
{
  "pack": "<pack_name>",
  "generated": "2026-09-10",
  "agent_scope": "<what this pack covers>",
  "sources": [ SOURCE, ... ],
  "<section>": { "<entity_code>": ENTITY, ... }
}
```

`<section>` is one of: `methods`, `functions`, `engines`, `engine_tools`,
`technology_nodes`, `cases`, `platforms`, `stage_budgets`, `network_modes`,
`target_metrics`, `load_profiles`, `risk_factors`.

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

## ENTITY

```json
{
  "claims": [ CLAIM, ... ],
  "game_examples": [ GAME_EXAMPLE, ... ]
}
```

## CLAIM

```json
{
  "field": "<the catalog field being evidenced>",
  "statement": "factual sentence, reproducible, specific",
  "unit": "ms | % | GiB | person-days | ... or empty",
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

## GAME_EXAMPLE

```json
{
  "game": "Game Title",
  "studio": "Studio",
  "year": 2019,
  "engine": "Unreal Engine 4.22",
  "world_type": "open_world|linear|arena|...",
  "network_mode": "single|coop|dedicated_server|p2p",
  "fact": "what is publicly confirmed to exist in this game",
  "locator": "GDC talk 00:12:40 / postmortem p.4",
  "source": "SRC-<PACK>-001",
  "relevance": "exact|strong|partial|weak",
  "non_transferable": "what must NOT be copied to another project"
}
```

## HARD RULES — violation means rejection

1. **Never invent a URL.** Every `url` must be one you actually opened with
   WebFetch or confirmed via search results. If you did not open it, you may not
   cite it.
2. `availability` must be honest: `verified_fetched` ONLY if you retrieved the
   content; `verified_url_only` if you only confirmed it resolves.
3. **Never claim a number the source does not contain.** If the source says
   "significantly faster", you write a qualitative `statement` with
   `value: null`, not an invented figure.
4. `basis=derived` REQUIRES `formula` AND `input_parameters`.
5. `basis=expert_estimate` must say in `context` that it is an estimate and why.
6. **Absence of a source is never compatibility.** If you cannot find evidence,
   emit a claim with `basis: "unknown"` and `statement` describing the gap.
   Do NOT silently omit, and do NOT fabricate.
7. Game examples must be **different games** from each other — two examples from
   the same title count as one.
8. `locator` must be precise and specific to the claim; "the docs" is rejected.
9. Do not restate the entity name as a claim. Claims must add information.
10. Prefer primary sources. Secondary sources only when primary is unavailable,
    and say so in `applicability_note`.
