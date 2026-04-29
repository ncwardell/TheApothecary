---
name: add-recipe
description: Research and add a new recipe to The Apothecary. Use when the user types `/add-recipe <name>` or asks to add/create a new recipe. Researches mechanism/effectiveness via web, drafts schema-conformant JSON + filled-in markdown, ensures all referenced ingredients exist (creating any missing ones), then validates and writes the files.
---

# add-recipe

You are adding a new recipe to The Apothecary site (`/home/arnold/Work/Personal/LifeApothecary`). The full schema is defined in `scripts/schema.ts` — read it once before generating data; treat it as the source of truth.

## Inputs

- `$ARGUMENTS` — the recipe name (e.g. "homemade dish soap"). May include a target commercial product to replace, e.g. "homemade dish soap (Dawn)". If the user only provides a name, infer the most-replaced commercial equivalent and price range.

## Step 1 — Sanity check

1. Compute `slug` from the name: lowercase, hyphens, no special chars. Drop "homemade"/"DIY" prefixes.
2. Check `Recipes/json/{slug}.json` does NOT exist. Abort if it does.
3. Read `scripts/schema.ts` if you haven't this session.
4. Decide a short `id` (often the slug, but a shorter memorable key like `"toothpaste"` is fine if clearly better).

## Step 2 — Research

Use `WebSearch` to gather:

- **What it replaces** + price range, e.g. "Commercial dish soap ($3–6/bottle)".
- **Cost per use** of the DIY version, e.g. "~$0.05".
- **Effectiveness 1–10** vs commercial: be honest. 9–10 = equal/superior; 7–8 = very effective with minor trade-offs; 5–6 = decent but limited; 3–4 = significantly inferior; 1–2 = barely functional. Always include `effectivenessNote` explaining BOTH strengths AND specific weaknesses. No marketing.
- **Difficulty:** `Easy` | `Moderate` | `Advanced`.
- **Shelf life** of the finished product.
- **Category:** one of `oral|skin|hair|cleaning|laundry|kitchen|health|garden`.
- **Mechanism (`scienceNote`):** one paragraph explaining WHY this works at a chemical level. Specific reactions / properties, not "X cleans".
- **Warnings:** array of specific actionable safety items.
- **Ingredient list** — names, then map each to an existing ingredient `id`.

## Step 3 — Reconcile ingredients

For each ingredient referenced:

1. Check `Ingredients/json/*.json` for an existing record (look up by id and by name fuzzy-match).
2. If it exists, use its `id`.
3. If it does NOT exist, **invoke the `add-ingredient` flow inline** for each missing ingredient before continuing. Do not write the recipe with dangling references — `validate.ts` will reject it.

Split into `coreIngredients` (required) and `optionalIngredients` (substitutes / enhancers). Order core ingredients with the most distinctive / load-bearing one first.

## Step 4 — Draft the JSON

Construct a JSON object matching the `Recipe` interface in `scripts/schema.ts`. All fields required by the validator must be present and non-empty.

## Step 5 — Write the JSON file

Write to `Recipes/json/{slug}.json`, pretty-printed, trailing newline.

## Step 6 — Write the markdown

Generate the full markdown yourself (do NOT use `create-recipe.ts` — its output is a TODO scaffold). Follow the section structure in `scripts/schema.ts` `generateRecipeMarkdown`:

- `# {Name}` + blockquote description
- `## Overview` (property table)
- `## What This Replaces & Why` — including where DIY is genuinely inferior
- `## Ingredients` — Core + Optional tables with **Amount** and **Role** filled in for every row
- `## Equipment Needed` — list each item with WHY (e.g. "non-metal spoon — bentonite reacts with metal")
- `## Method` — numbered steps with timing, temperatures, visual/texture cues
- `## The Science Behind It` — expand on `scienceNote` with full chemistry
- `## Variations` — alternative formulations + when to prefer each
- `## Effectiveness Assessment` — what's better, what's worse, when to prefer commercial
- `## Pros`
- `## Cons & Limitations` — include the warnings
- `## Tips & Troubleshooting` — common failure modes + fixes
- `## Safety Notes`
- `## Related Recipes` — cross-references
- `## References` — numbered, real citations

Write to `Recipes/{slug}.md`.

## Step 7 — Validate, build, report

```bash
cd /home/arnold/Work/Personal/LifeApothecary/scripts && npx tsx validate.ts
nix-shell -p python3 --run "cd /home/arnold/Work/Personal/LifeApothecary && python3 build.py"
```

If validation fails (especially "ingredient X not found"), fix and retry — never skip.

The build auto-injects the new slug into `index.html`'s recipe list. No manual array edit needed.

Report to the user:
- Files created
- Any new ingredients created along the way
- Effectiveness score + reasoning (so they can sanity-check)
- Local preview URL: `https://www.theapothecary.diy/recipes/{slug}/` once deployed

## Style

Match the existing site voice: technical, honest, science-backed, not preachy. The brand promise is honest effectiveness ratings — under-promise where DIY is inferior, don't oversell. If commercial is genuinely better in ways that matter, say so in `effectivenessNote`.
