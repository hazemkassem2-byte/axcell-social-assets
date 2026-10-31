# Axcell social assets

Public image hosting for Axcell's scheduled social posts (Instagram needs a public JPEG URL). Contains no confidential data.

- `render_card.py`: renders a 1080x1350 brand card from a post's hook (navy, one red accent, Tajawal/Inter, footer).
- `brand/`: fonts (SIL Open Font License, from Google Fonts) and the white Axcell wordmark.
- `cards/YYYY-MM/<date>-<lang>.jpg`: one card per post. Raw URL pattern:
  `https://raw.githubusercontent.com/hazemkassem2-byte/axcell-social-assets/main/cards/YYYY-MM/<file>.jpg`

## Claude skills installed in this repo (`.claude/`)

Loaded automatically by Claude sessions and scheduled tasks that check out this repo.

| Source | Licence | What's included |
|---|---|---|
| [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | MIT | `seo` + 25 `seo-*` sub-skills, 19 sub-agents in `.claude/agents/`. Hooks and paid extensions (DataForSEO, Banana) **not** installed. Python deps: `pip install -r .claude/skills/seo/requirements.txt` |
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | MIT | 19 selected skills: product-marketing, ai-seo, copywriting, copy-editing, content-strategy, social, lead-magnets, offers, marketing-psychology, marketing-loops, customer-research, competitor-profiling, prospecting, cold-email, emails, link-building, site-architecture, free-tools, marketing-plan |
| [inhouseseo/superseo-skills](https://github.com/inhouseseo/superseo-skills) | Apache-2.0 | All 11 (markdown only): page-audit, content-brief, write-content, improve-content, keyword-deep-dive, semantic-gap-analysis, eeat-audit, topic-cluster-planning, featured-snippet-optimizer, linkbuilding, expert-interview |

Axcell context for all marketing skills: `.agents/product-marketing.md`. Licences: `.claude/skills/_licenses/`.
Installed 31 Oct 2026 from each repo's default branch; reviewed for outbound calls (only documented Google/SEO APIs, all optional).
