#!/usr/bin/env tsx
/**
 * ═══════════════════════════════════════════════════════════════════
 * Create Recipe — The Apothecary
 * ═══════════════════════════════════════════════════════════════════
 *
 * Creates a new recipe's JSON metadata and Markdown scaffold.
 *
 * Usage:
 *   npx tsx create-recipe.ts <path-to-input.json>
 *   npx tsx create-recipe.ts --stdin < input.json
 *
 * The input JSON must conform to the Recipe interface in schema.ts.
 * The script validates all fields (including that referenced ingredient
 * IDs actually exist), then writes:
 *   - Recipes/json/{slug}.json
 *   - Recipes/{slug}.md
 *
 * ── FOR LLMs ─────────────────────────────────────────────────────
 *
 * To create a new recipe, produce a JSON object matching this
 * exact structure (see schema.ts Recipe interface for full docs):
 *
 * {
 *   "id":                  "toothpaste",                  // short memorable key
 *   "name":                "Remineralizing Clay Toothpaste",
 *   "slug":                "remineralizing-clay-toothpaste", // lowercase-hyphenated filename
 *   "description":         "One sentence, max ~200ch",
 *   "category":            "oral",                        // one of: oral|skin|hair|cleaning|laundry|kitchen|health|garden
 *   "replaces":            "Commercial toothpaste ($4-8/tube)",
 *   "costPerUse":          "~$0.03",
 *   "shelfLife":           "1-2 months sealed glass jar",
 *   "effectiveness":       8,                             // integer 1-10, be honest
 *   "effectivenessNote":   "Why this score — strengths AND weaknesses",
 *   "difficulty":          "Easy",                        // "Easy" | "Moderate" | "Advanced"
 *   "coreIngredients":     ["bentonite-clay", "coconut-oil"],      // ingredient IDs (must exist)
 *   "optionalIngredients": ["baking-soda", "xylitol"],             // ingredient IDs (must exist)
 *   "warnings":            ["Warning 1", "Warning 2"],
 *   "scienceNote":         "One paragraph: WHY this works at a chemical level"
 * }
 *
 * Then either:
 *   A) Save as a .json file and run: npx tsx create-recipe.ts input.json
 *   B) Write the JSON + MD files directly following the schema
 *   C) Pipe to stdin: echo '{ ... }' | npx tsx create-recipe.ts --stdin
 *
 * The script validates everything — including that all ingredient IDs
 * reference existing ingredient JSON files — and generates both files.
 * ═══════════════════════════════════════════════════════════════════
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import {
  type Recipe,
  type ValidationError,
  validateRecipe,
  generateRecipeMarkdown,
} from "./schema.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

// ── Parse input ─────────────────────────────────────────────────────

function readInput(): Record<string, unknown> {
  const args = process.argv.slice(2);

  if (args.includes("--stdin") || args.includes("-")) {
    const input = readFileSync(0, "utf-8");
    return JSON.parse(input);
  }

  const filePath = args.find(a => !a.startsWith("-"));
  if (!filePath) {
    console.error(`
Usage:
  npx tsx create-recipe.ts <path-to-input.json>
  npx tsx create-recipe.ts --stdin < input.json

See the comment block at the top of this file for the expected JSON structure.
`);
    process.exit(1);
  }

  const resolved = resolve(filePath);
  if (!existsSync(resolved)) {
    console.error(`File not found: ${resolved}`);
    process.exit(1);
  }

  return JSON.parse(readFileSync(resolved, "utf-8"));
}

// ── Load existing ingredient IDs ────────────────────────────────────

function loadIngredientIds(): Map<string, string> {
  /** Returns Map<id, name> for all existing ingredients. */
  const ids = new Map<string, string>();
  const jsonDir = resolve(ROOT, "Ingredients", "json");

  if (!existsSync(jsonDir)) return ids;

  for (const file of readdirSync(jsonDir)) {
    if (!file.endsWith(".json")) continue;
    try {
      const data = JSON.parse(readFileSync(resolve(jsonDir, file), "utf-8"));
      if (data.id && data.name) {
        ids.set(data.id, data.name);
      }
    } catch {
      // skip malformed files
    }
  }

  return ids;
}

// ── Main ────────────────────────────────────────────────────────────

function main() {
  const data = readInput();

  // Validate schema
  const errors: ValidationError[] = validateRecipe(data);

  // Validate ingredient references against actual files
  const existingIngredients = loadIngredientIds();
  const allRefs = [
    ...((data.coreIngredients as string[]) || []),
    ...((data.optionalIngredients as string[]) || []),
  ];

  for (const id of allRefs) {
    if (!existingIngredients.has(id)) {
      errors.push({
        field: "coreIngredients/optionalIngredients",
        message: `Ingredient "${id}" not found. Create it first with create-ingredient.ts. Existing IDs: ${[...existingIngredients.keys()].sort().join(", ")}`,
      });
    }
  }

  if (errors.length > 0) {
    console.error("\nValidation failed:\n");
    for (const err of errors) {
      console.error(`  [${err.field}] ${err.message}`);
    }
    console.error(`\n${errors.length} error(s). Fix the input and try again.\n`);
    process.exit(1);
  }

  const recipe = data as unknown as Recipe;
  const slug = recipe.slug;

  // Check for existing files
  const jsonPath = resolve(ROOT, "Recipes", "json", `${slug}.json`);
  const mdPath = resolve(ROOT, "Recipes", `${slug}.md`);

  if (existsSync(jsonPath)) {
    console.error(`\nJSON already exists: ${jsonPath}`);
    console.error("Delete it first if you want to regenerate.\n");
    process.exit(1);
  }

  if (existsSync(mdPath)) {
    console.error(`\nMarkdown already exists: ${mdPath}`);
    console.error("Delete it first if you want to regenerate.\n");
    process.exit(1);
  }

  // Ensure directories exist
  const jsonDir = dirname(jsonPath);
  if (!existsSync(jsonDir)) mkdirSync(jsonDir, { recursive: true });

  // Build ingredient name lookup for MD generation
  const ingredientNames: Record<string, string> = {};
  for (const [id, name] of existingIngredients) {
    ingredientNames[id] = name;
  }

  // Write JSON
  const jsonContent = JSON.stringify(recipe, null, 2) + "\n";
  writeFileSync(jsonPath, jsonContent, "utf-8");
  console.log(`  Created: Recipes/json/${slug}.json`);

  // Write Markdown scaffold
  const mdContent = generateRecipeMarkdown(recipe, ingredientNames);
  writeFileSync(mdPath, mdContent, "utf-8");
  console.log(`  Created: Recipes/${slug}.md`);

  // Summary
  console.log(`\n  Recipe: ${recipe.name}`);
  console.log(`  Category: ${recipe.category}`);
  console.log(`  Effectiveness: ${recipe.effectiveness}/10`);
  console.log(`  Core ingredients: ${recipe.coreIngredients.map(id => existingIngredients.get(id) || id).join(", ")}`);

  if (recipe.optionalIngredients.length > 0) {
    console.log(`  Optional: ${recipe.optionalIngredients.map(id => existingIngredients.get(id) || id).join(", ")}`);
  }

  console.log(`\nDone! Now fill in the TODO sections in Recipes/${slug}.md`);
}

main();
