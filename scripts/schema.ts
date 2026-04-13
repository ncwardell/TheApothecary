/**
 * ═══════════════════════════════════════════════════════════════════
 * The Apothecary — Canonical Schema Definitions
 * ═══════════════════════════════════════════════════════════════════
 *
 * This file is the SINGLE SOURCE OF TRUTH for all ingredient and
 * recipe data structures. Both the JSON metadata files and the
 * Markdown content files must conform to these definitions.
 *
 * AN LLM CREATING NEW CONTENT SHOULD READ THIS FILE FIRST.
 * The types, validation rules, and template generators define
 * exactly what is required and how it should be structured.
 * ═══════════════════════════════════════════════════════════════════
 */

// ── Valid Categories ────────────────────────────────────────────────

export const CATEGORIES = [
  "oral",
  "skin",
  "hair",
  "cleaning",
  "laundry",
  "kitchen",
  "health",
  "garden",
] as const;

export type Category = (typeof CATEGORIES)[number];

export const CATEGORY_LABELS: Record<Category, string> = {
  oral: "Oral Care",
  skin: "Skin & Body",
  hair: "Hair",
  cleaning: "Cleaning",
  laundry: "Laundry",
  kitchen: "Kitchen & Food",
  health: "Health",
  garden: "Garden & Home",
};

// ── Valid Difficulty Levels ──────────────────────────────────────────

export const DIFFICULTIES = ["Easy", "Moderate", "Advanced"] as const;
export type Difficulty = (typeof DIFFICULTIES)[number];

// ── Ingredient Schema ───────────────────────────────────────────────

export interface Ingredient {
  /**
   * Unique identifier. Used as the key in recipe coreIngredients/optionalIngredients arrays.
   * Usually matches `slug`, but legacy exceptions exist (e.g., "acv" for apple-cider-vinegar).
   * NEW ingredients should always use slug as id.
   */
  id: string;

  /** Human-readable name, including common alternate name in parentheses if applicable. */
  name: string;

  /**
   * URL-safe identifier. MUST match the .md and .json filename (without extension).
   * Lowercase, hyphen-separated, no special characters.
   * Example: "baking-soda" -> Ingredients/baking-soda.md, Ingredients/json/baking-soda.json
   */
  slug: string;

  /** One-sentence summary of what this ingredient does and why it matters. Max ~200 chars. */
  description: string;

  /** IUPAC or common chemical name. Example: "Sodium hydrogen carbonate" */
  chemicalName: string;

  /**
   * Chemical formula using Unicode subscripts where appropriate.
   * Example: "NaHCO\u2083" (NaHCO₃)
   * Use "N/A" for complex mixtures without a single formula (e.g., tallow, castile soap).
   */
  formula: string;

  /**
   * Chemical Abstracts Service registry number.
   * Example: "144-55-8"
   * Use "N/A" for mixtures or substances without a CAS number.
   */
  casNumber: string;

  /**
   * Molecular weight with units.
   * Example: "84.007 g/mol"
   * Use "Varies" for mixtures.
   */
  molecularWeight: string;

  /** Physical appearance description. Example: "White crystalline powder; odorless" */
  appearance: string;

  /**
   * pH value or range in typical solution.
   * Example: "8.3-8.6"
   * Use "Not applicable" for non-aqueous substances.
   */
  pH: string;

  /**
   * Solubility in water and other relevant solvents.
   * Example: "96 g/L in water at 20°C; insoluble in ethanol"
   */
  solubility: string;

  /**
   * Condensed chemistry/mechanism summary for card/tooltip display.
   * Should explain HOW the ingredient works at a molecular level.
   * Target: 1-3 sentences, ~100-300 chars.
   */
  chemistry: string;

  /**
   * Key safety warnings for card/tooltip display.
   * Concise but specific. Example: "Can irritate sensitive skin at high concentrations."
   */
  warnings: string;

  /**
   * Cost with quantity and USD range.
   * Example: "$3-5 for 5 lb bag"
   */
  costNote: string;

  /**
   * How long the ingredient lasts when properly stored.
   * Example: "Indefinite when stored dry"
   */
  shelfLife: string;

  /**
   * Which recipe categories this ingredient is used in.
   * Must be valid Category values. At least one required.
   */
  categories: Category[];

  /**
   * Array of slug values pointing to related ingredient files.
   * Ingredients that complement, compete with, or can substitute for this one.
   * Each value must correspond to an existing Ingredients/json/{slug}.json file.
   */
  relatedIngredients: string[];
}

// ── Recipe Schema ───────────────────────────────────────────────────

export interface Recipe {
  /**
   * Unique recipe identifier. Used as the key in shopping list and UI state.
   * Should be a short, memorable name (e.g., "toothpaste", "deodorant").
   * For new recipes, prefer the slug unless a shorter name is clearly better.
   */
  id: string;

  /** Full human-readable recipe name. Example: "Remineralizing Clay Toothpaste" */
  name: string;

  /**
   * URL-safe identifier. MUST match the .md and .json filename (without extension).
   * Lowercase, hyphen-separated, no special characters.
   * Example: "remineralizing-clay-toothpaste"
   */
  slug: string;

  /** One-sentence summary. Should convey what this makes and its key benefit. Max ~200 chars. */
  description: string;

  /** Single category this recipe belongs to. */
  category: Category;

  /**
   * What commercial product(s) this replaces, including typical price range.
   * Example: "Commercial toothpaste ($4-8/tube)"
   */
  replaces: string;

  /**
   * Approximate cost per use/application of the DIY version.
   * Example: "~$0.03"
   * Must include the ~ prefix if approximate.
   */
  costPerUse: string;

  /**
   * How long the finished product lasts.
   * Example: "1-2 months sealed glass jar"
   */
  shelfLife: string;

  /**
   * Effectiveness score from 1-10 compared to the commercial product it replaces.
   * Must be an integer. Be honest — this is not marketing.
   *
   * Guidelines:
   *   9-10: Equal or superior to commercial in all practical ways
   *   7-8:  Very effective, minor trade-offs
   *   5-6:  Decent but notable limitations
   *   3-4:  Works but significantly inferior
   *   1-2:  Barely functional, mostly educational
   */
  effectiveness: number;

  /**
   * Transparent reasoning for the effectiveness score.
   * MUST explain both strengths AND specific weaknesses.
   * Example: "Matches commercial for cleaning and whitening. -2 because fluoride
   *           paste has stronger cavity-prevention evidence for high-risk individuals."
   */
  effectivenessNote: string;

  /** How hard this is to make. */
  difficulty: Difficulty;

  /**
   * Array of ingredient IDs (not slugs) that are required for the recipe.
   * Each must correspond to an Ingredients/json/*.json file's `id` field.
   * Order: list most important / distinctive ingredients first.
   */
  coreIngredients: string[];

  /**
   * Array of ingredient IDs for optional/substitute ingredients.
   * These enhance but aren't required. Same ID rules as coreIngredients.
   */
  optionalIngredients: string[];

  /**
   * Safety warnings and important limitations. Array of strings.
   * Each string should be one specific, actionable warning.
   * Example: ["No fluoride — consider fluoride rinse if cavity-prone",
   *           "Must use non-metal utensils with bentonite clay"]
   */
  warnings: string[];

  /**
   * One-paragraph explanation of WHY this recipe works at a chemical level.
   * Not "baking soda cleans" — explain the actual mechanism.
   * This appears in the science box on the recipe card and in structured data.
   */
  scienceNote: string;
}

// ── Validation ──────────────────────────────────────────────────────

export interface ValidationError {
  field: string;
  message: string;
}

const SLUG_REGEX = /^[a-z0-9]+(-[a-z0-9]+)*$/;

function validateSlug(slug: string, field: string): ValidationError[] {
  if (!SLUG_REGEX.test(slug)) {
    return [{ field, message: `Invalid slug "${slug}". Must be lowercase, hyphen-separated, no special characters.` }];
  }
  return [];
}

function validateNonEmpty(value: string, field: string): ValidationError[] {
  if (!value || value.trim().length === 0) {
    return [{ field, message: `${field} is required and cannot be empty.` }];
  }
  return [];
}

function validateCategories(categories: string[], field: string): ValidationError[] {
  const errors: ValidationError[] = [];
  if (categories.length === 0) {
    errors.push({ field, message: "At least one category is required." });
  }
  for (const cat of categories) {
    if (!CATEGORIES.includes(cat as Category)) {
      errors.push({ field, message: `Invalid category "${cat}". Valid: ${CATEGORIES.join(", ")}` });
    }
  }
  return errors;
}

export function validateIngredient(data: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  // Required string fields
  const requiredStrings: (keyof Ingredient)[] = [
    "id", "name", "slug", "description", "chemicalName", "formula",
    "casNumber", "molecularWeight", "appearance", "pH", "solubility",
    "chemistry", "warnings", "costNote", "shelfLife",
  ];

  for (const field of requiredStrings) {
    errors.push(...validateNonEmpty(data[field] as string || "", field));
  }

  // Slug format
  if (data.slug) errors.push(...validateSlug(data.slug as string, "slug"));
  if (data.id) errors.push(...validateSlug(data.id as string, "id"));

  // id should match slug for new ingredients (legacy exceptions allowed)
  const LEGACY_ID_EXCEPTIONS: Record<string, string> = {
    "acv": "apple-cider-vinegar",
    "ammonia": "household-ammonia",
  };
  if (data.id && data.slug && data.id !== data.slug) {
    if (LEGACY_ID_EXCEPTIONS[data.id as string] !== data.slug) {
      errors.push({
        field: "id",
        message: `id "${data.id}" does not match slug "${data.slug}". New ingredients should use slug as id.`,
      });
    }
  }

  // Categories
  if (!Array.isArray(data.categories)) {
    errors.push({ field: "categories", message: "categories must be an array." });
  } else {
    errors.push(...validateCategories(data.categories as string[], "categories"));
  }

  // Related ingredients
  if (!Array.isArray(data.relatedIngredients)) {
    errors.push({ field: "relatedIngredients", message: "relatedIngredients must be an array." });
  }

  return errors;
}

export function validateRecipe(data: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  // Required string fields
  const requiredStrings: (keyof Recipe)[] = [
    "id", "name", "slug", "description", "category",
    "replaces", "costPerUse", "shelfLife", "effectivenessNote",
    "difficulty", "scienceNote",
  ];

  for (const field of requiredStrings) {
    errors.push(...validateNonEmpty(data[field] as string || "", field));
  }

  // Slug format
  if (data.slug) errors.push(...validateSlug(data.slug as string, "slug"));

  // Category
  if (data.category && !CATEGORIES.includes(data.category as Category)) {
    errors.push({ field: "category", message: `Invalid category "${data.category}". Valid: ${CATEGORIES.join(", ")}` });
  }

  // Difficulty
  if (data.difficulty && !DIFFICULTIES.includes(data.difficulty as Difficulty)) {
    errors.push({ field: "difficulty", message: `Invalid difficulty "${data.difficulty}". Valid: ${DIFFICULTIES.join(", ")}` });
  }

  // Effectiveness
  const eff = data.effectiveness;
  if (typeof eff !== "number" || !Number.isInteger(eff) || eff < 1 || eff > 10) {
    errors.push({ field: "effectiveness", message: "effectiveness must be an integer from 1 to 10." });
  }

  // Ingredient arrays (can be empty for standalone recipes like compost, herbal teas, etc.)
  if (!Array.isArray(data.coreIngredients)) {
    errors.push({ field: "coreIngredients", message: "coreIngredients must be an array." });
  }
  if (!Array.isArray(data.optionalIngredients)) {
    errors.push({ field: "optionalIngredients", message: "optionalIngredients must be an array (can be empty)." });
  }

  // Warnings
  if (!Array.isArray(data.warnings)) {
    errors.push({ field: "warnings", message: "warnings must be an array of strings." });
  }

  return errors;
}

// ── Markdown Templates ──────────────────────────────────────────────
//
// These generate the COMPLETE .md file scaffold with all required sections.
// Every section is mandatory. If information doesn't exist, state that
// explicitly rather than omitting the section.

export function generateIngredientMarkdown(ing: Ingredient): string {
  return `# ${ing.name}

> ${ing.description}

## Quick Reference

| Property | Value |
|---|---|
| **Common Names** | ${ing.name} |
| **Chemical Name / IUPAC** | ${ing.chemicalName} |
| **Chemical Formula** | ${ing.formula} |
| **CAS Number** | ${ing.casNumber} |
| **Molecular Weight** | ${ing.molecularWeight} |
| **Appearance** | ${ing.appearance} |
| **pH (in solution)** | ${ing.pH} |
| **Solubility** | ${ing.solubility} |

## Overview

<!-- What this ingredient is, what gap it fills in a DIY system, why it matters chemically.
     2-3 paragraphs. Lead with the practical value, then explain the chemistry. -->

TODO: Write overview.

## Chemical Composition & Structure

<!-- Crystal structure, active compounds, relevant physical properties, mechanism tables.
     Include molecular structure details relevant to how it works. -->

TODO: Write chemical composition details.

## How It Is Produced / How to Make It from Scratch

<!-- Industrial production process. Is home production feasible? If not, why not?
     Be specific about whether this is a "buy it" or "make it" ingredient. -->

TODO: Write production/sourcing details.

## Mechanism of Action

<!-- Exactly how it works at the molecular level for EACH application.
     Not "it cleans" — what chemical reaction or physical process is occurring?
     Use subheadings for different applications if applicable. -->

TODO: Write mechanism of action.

## Applications & Uses

<!-- DIY recipes and formulations this ingredient appears in.
     Include concentrations, methods, and specific formulation notes.
     Also note medical/industrial uses if relevant. -->

### DIY Formulations

TODO: List DIY applications with concentrations.

### Other Uses

TODO: List non-DIY uses if relevant.

## Efficacy & Research

<!-- Specific studies with authors, journals, and findings.
     Not "studies show" — WHICH study, WHAT it found, and any limitations.
     If research is limited, say so explicitly. -->

TODO: Cite specific research.

## Safety, Warnings & Contraindications

<!-- Toxicity data, incompatibilities, handling precautions, who should avoid it.
     Be specific: at what concentration does irritation occur? What reactions are dangerous? -->

TODO: Write safety data.

## Pros & Cons

**Pros:**
- TODO

**Cons:**
- TODO

## Storage & Shelf Life

<!-- How to store, how long it lasts, signs of degradation.
     Specify container type, temperature range, humidity requirements. -->

TODO: Write storage details.

## Cost & Sourcing

| Quantity | Price Range (USD) | Notes |
|---|---|---|
| TODO | TODO | TODO |

<!-- Where to buy, quality indicators to look for, bulk vs retail. -->

TODO: Write sourcing details.

## Regulatory Status

<!-- FDA, EU, TGA, USP status. What is it approved for and at what concentrations?
     Include GRAS status if applicable. -->

TODO: Write regulatory status.

## Related Ingredients

${ing.relatedIngredients.length > 0
    ? ing.relatedIngredients.map(slug => `- [${slug}](../Ingredients/${slug}.md)`).join("\n")
    : "- None specified"}

## References & Further Reading

<!-- Numbered citations with full author, year, journal, title.
     Minimum 3 references. Prefer peer-reviewed sources. -->

1. TODO: Add references
`;
}

export function generateRecipeMarkdown(recipe: Recipe, ingredientNames: Record<string, string>): string {
  const coreRows = recipe.coreIngredients
    .map(id => `| [${ingredientNames[id] || id}](../Ingredients/${id}.md) | TODO: amount | TODO: role |`)
    .join("\n");

  const optionalRows = recipe.optionalIngredients
    .map(id => `| [${ingredientNames[id] || id}](../Ingredients/${id}.md) | TODO: amount | TODO: role |`)
    .join("\n");

  return `# ${recipe.name}

> ${recipe.description}

## Overview

| Property | Value |
|---|---|
| **Category** | ${CATEGORY_LABELS[recipe.category]} |
| **Replaces** | ${recipe.replaces} |
| **Cost per Use** | ${recipe.costPerUse} |
| **Shelf Life** | ${recipe.shelfLife} |
| **Effectiveness** | ${recipe.effectiveness}/10 |
| **Difficulty** | ${recipe.difficulty} |

## What This Replaces & Why

<!-- What commercial product(s) this replaces.
     Why the commercial version is overpriced or unnecessary.
     Where the DIY version is GENUINELY INFERIOR — be honest. -->

TODO: Write replacement rationale.

## Ingredients

### Core Ingredients

| Ingredient | Amount | Role |
|---|---|---|
${coreRows}

### Optional Ingredients

| Ingredient | Amount | Role |
|---|---|---|
${optionalRows || "| None | — | — |"}

## Equipment Needed

<!-- What you need and WHY (e.g., "non-metal spoon — bentonite reacts with metal").
     Include container/storage requirements. -->

- TODO

## Method

<!-- Step-by-step numbered instructions.
     Detailed enough that a first-timer can follow.
     Include timing, temperatures, and visual/texture cues. -->

1. TODO

## The Science Behind It

<!-- Why this recipe works at the chemical level.
     Not "baking soda cleans" but explain the actual reaction/mechanism.
     Reference specific ingredients and their interactions. -->

${recipe.scienceNote}

TODO: Expand with full chemistry explanation.

## Variations

<!-- Alternative formulations, substitutions, adaptations for different needs.
     For each variation, explain what changes and why someone might prefer it. -->

TODO: Write variations.

## Effectiveness Assessment

**Score: ${recipe.effectiveness}/10** vs ${recipe.replaces}

${recipe.effectivenessNote}

<!-- Expand with specific comparisons:
     - What does the DIY version do BETTER?
     - What does the DIY version do WORSE?
     - Under what conditions might you prefer commercial? -->

TODO: Expand effectiveness assessment.

## Pros

- TODO

## Cons & Limitations

- TODO
${recipe.warnings.map(w => `- ${w}`).join("\n")}

## Tips & Troubleshooting

<!-- Common problems and how to solve them.
     What does it look/feel like when something goes wrong? -->

- TODO

## Safety Notes

${recipe.warnings.map(w => `- ${w}`).join("\n")}

<!-- Add any additional safety information not covered in warnings. -->

## Related Recipes

<!-- Cross-references to complementary recipes. -->

- TODO

## References

1. TODO: Add references
`;
}
