---
name: add-ingredient
description: Research and add a new ingredient to The Apothecary. Use when the user types `/add-ingredient <name>` or asks to add/create a new ingredient. Researches chemistry/safety/sourcing via web, drafts schema-conformant JSON + filled-in markdown, generates an Amazon search URL pre-tagged with the user's affiliate ID, pauses for the user to paste the SiteStripe `amzn.to/...` link, then validates and writes the files.
---

# add-ingredient

You are adding a new ingredient to The Apothecary site (`/home/arnold/Work/Personal/LifeApothecary`). The full schema is defined in `scripts/schema.ts` — read it once before generating data; treat it as the source of truth.

## Inputs

- `$ARGUMENTS` — the ingredient name (e.g. "potassium bicarbonate"). May include the target bulk size in parens, e.g. "potassium bicarbonate (5 lb)". If the user only provides a name, infer a sensible bulk target (typically 5 lb / 32 oz / 64 oz / 1 gal depending on the substance — favor the size that gives the best $/unit at typical bulk-DIY use).
- If the user has already shared an `amzn.to/...` link in their message, accept it and skip Step 4's search-URL prompt. Still ask for product name + quantity + price unless the user provided those too — Amazon blocks anonymous scraping, so you cannot derive them from the URL alone.

## Step 1 — Sanity check

1. Compute `slug` from the name: lowercase, hyphens, no special chars, no parens content.
2. Check `Ingredients/json/{slug}.json` does NOT exist. If it does, abort and tell the user — never overwrite.
3. Read `scripts/schema.ts` if you haven't this session.

## Step 2 — Research

Use `WebSearch` and `WebFetch` to gather:

- **Chemical identity:** chemical name (IUPAC), formula (Unicode subscripts: `NaHCO₃`, `H₂O₂`), CAS number, molecular weight, appearance, pH (in solution), solubility (in water + relevant solvents).
- **Mechanism:** 1–3 sentence summary of HOW it works at the molecular level for DIY applications. Specific. Not "it cleans" — what reaction or property is doing the work?
- **Safety:** key warnings, irritation thresholds, incompatibilities, handling.
- **Cost:** typical retail bulk price range, e.g. "$8–12 for 5 lb bag".
- **Storage:** shelf life when stored properly.
- **Categories:** which of `oral|skin|hair|cleaning|laundry|kitchen|health|garden` apply.
- **Related ingredients:** scan `Ingredients/json/*.json` for ingredients in the same category or with similar function — pick 3–5 slugs.

For mixtures without a single formula (tallow, castile soap), use `"N/A"` for `formula` and `casNumber` and `"Varies"` for `molecularWeight`.

## Step 3 — Draft the JSON

Construct a JSON object matching the `Ingredient` interface in `scripts/schema.ts`. `id` should equal `slug` (the legacy `acv` / `ammonia` exceptions don't apply to new ingredients). Leave `affiliateLinks` out for now — Step 5 fills it in.

## Step 4 — Generate the affiliate search URL

The Amazon Associates tag for this site is **`theapothec061-20`** (also stored in project memory). Build a search URL pre-filtered to the target bulk size:

```
https://www.amazon.com/s?k=<query>&tag=theapothec061-20
```

Example query for "potassium bicarbonate, 5 lb": `k=potassium+bicarbonate+5+lb+food+grade`. Pick keywords that bias toward the right grade (food-grade, USP, cosmetic-grade) and bulk size.

## Step 5 — Pause for the user

Print the search URL and these exact instructions, then stop and wait for the user to reply with the SiteStripe data:

```
Search Amazon and pick a product (highest reviews × rating, target qty, reasonable $/unit):
<the search URL>

Then paste back:
1. The SiteStripe `amzn.to/...` link from Site Stripe → "Get Link" → "Short Link"
2. Product name (e.g. "Pure Sodium Bicarbonate, 5 lb")
3. Quantity (e.g. "5 lb")
4. Price (e.g. "~$12.00")
```

If the user replies "skip" or "no good options", proceed to Step 6 with `affiliateLinks` omitted.

## Step 6 — Build affiliateLinks

When the user pastes the link details, append:

```json
"affiliateLinks": [
  {
    "retailer": "amazon",
    "url": "<their amzn.to link>",
    "productName": "<their product name>",
    "quantity": "<their quantity>",
    "price": "<their price>"
  }
]
```

## Step 7 — Write the files

Write the JSON to `Ingredients/json/{slug}.json` (pretty-printed, trailing newline).

Generate the markdown body yourself — do NOT use `create-ingredient.ts` because it produces a TODO scaffold and the goal is fully-researched content. Follow the section structure in `scripts/schema.ts` `generateIngredientMarkdown`:

- `# {Name}` + blockquote description
- `## Quick Reference` (the property table)
- `## Overview` — 2–3 paragraphs, lead with practical value, then chemistry
- `## Chemical Composition & Structure`
- `## How It Is Produced / How to Make It from Scratch` — say explicitly "buy it" or "make it"
- `## Mechanism of Action` — per application
- `## Applications & Uses` — DIY formulations + other uses
- `## Efficacy & Research` — cite specific studies if any
- `## Safety, Warnings & Contraindications`
- `## Pros & Cons`
- `## Storage & Shelf Life`
- `## Cost & Sourcing` — table + bulk vs retail notes
- `## Regulatory Status`
- `## Related Ingredients`
- `## References & Further Reading` — minimum 3 numbered references

Fill every section with researched content. No `TODO:` placeholders.

Write to `Ingredients/{slug}.md`.

## Step 8 — Cross-link

For each slug in `relatedIngredients`, open `Ingredients/json/{related}.json` and add the new ingredient's slug to its `relatedIngredients` array if not already present. This keeps the bidirectional graph consistent.

## Step 9 — Validate, build, report

Run, in order:

```bash
cd /home/arnold/Work/Personal/LifeApothecary/scripts && npx tsx validate.ts
nix-shell -p python3 --run "cd /home/arnold/Work/Personal/LifeApothecary && python3 build.py"
```

If validation fails, report errors and stop. The build auto-injects the new slug into `index.html`'s ingredient list — no manual array edit needed.

Report to the user:
- Files created (paths)
- Cross-links added (which sibling JSON files were updated)
- Local preview URL: `https://www.theapothecary.diy/ingredients/{slug}/` once deployed (or `_site/ingredients/{slug}/index.html` for local check)

## Style

Match the existing site voice: technical, honest, science-backed, not preachy. Cite real studies when claiming efficacy. If evidence is weak, say so explicitly — that's the whole brand.
