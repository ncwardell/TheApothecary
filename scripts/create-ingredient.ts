#!/usr/bin/env tsx
/**
 * ═══════════════════════════════════════════════════════════════════
 * Create Ingredient — The Apothecary
 * ═══════════════════════════════════════════════════════════════════
 *
 * Creates a new ingredient's JSON metadata and Markdown scaffold.
 *
 * Usage:
 *   npx tsx create-ingredient.ts <path-to-input.json>
 *   npx tsx create-ingredient.ts --stdin < input.json
 *
 * The input JSON must conform to the Ingredient interface in schema.ts.
 * The script validates all fields, then writes:
 *   - Ingredients/json/{slug}.json
 *   - Ingredients/{slug}.md
 *
 * ── FOR LLMs ─────────────────────────────────────────────────────
 *
 * To create a new ingredient, produce a JSON object matching this
 * exact structure (see schema.ts Ingredient interface for full docs):
 *
 * {
 *   "id":                  "sodium-percarbonate",        // = slug for new ingredients
 *   "name":                "Sodium Percarbonate",        // human-readable, include alt names
 *   "slug":                "sodium-percarbonate",        // lowercase-hyphenated filename
 *   "description":         "One sentence, max ~200ch",   // what it does & why it matters
 *   "chemicalName":        "Sodium carbonate peroxyhydrate", // IUPAC or common chemical name
 *   "formula":             "2Na\u2082CO\u2083\u00B73H\u2082O\u2082",  // Unicode subscripts
 *   "casNumber":           "15630-89-4",                 // or "N/A" for mixtures
 *   "molecularWeight":     "314.02 g/mol",               // or "Varies" for mixtures
 *   "appearance":          "White granular powder",
 *   "pH":                  "10.4-10.6",                  // or "Not applicable"
 *   "solubility":          "140 g/L in water at 20°C",
 *   "chemistry":           "1-3 sentences: HOW it works at molecular level",
 *   "warnings":            "Key safety warnings, concise",
 *   "costNote":            "$X-Y for Z quantity",
 *   "shelfLife":           "Duration + storage condition",
 *   "categories":          ["cleaning", "laundry"],      // from: oral|skin|hair|cleaning|laundry|kitchen|health|garden
 *   "relatedIngredients":  ["hydrogen-peroxide", "washing-soda"]  // slugs of related ingredients
 * }
 *
 * Then either:
 *   A) Save as a .json file and run: npx tsx create-ingredient.ts input.json
 *   B) Write the JSON + MD files directly following the schema
 *   C) Pipe to stdin: echo '{ ... }' | npx tsx create-ingredient.ts --stdin
 *
 * The script validates everything and generates both files.
 * ═══════════════════════════════════════════════════════════════════
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import {
  type Ingredient,
  validateIngredient,
  generateIngredientMarkdown,
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
  npx tsx create-ingredient.ts <path-to-input.json>
  npx tsx create-ingredient.ts --stdin < input.json

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

// ── Main ────────────────────────────────────────────────────────────

function main() {
  const data = readInput();

  // Validate
  const errors = validateIngredient(data);
  if (errors.length > 0) {
    console.error("\nValidation failed:\n");
    for (const err of errors) {
      console.error(`  [${err.field}] ${err.message}`);
    }
    console.error(`\n${errors.length} error(s). Fix the input and try again.\n`);
    process.exit(1);
  }

  const ingredient = data as unknown as Ingredient;
  const slug = ingredient.slug;

  // Check for existing files
  const jsonPath = resolve(ROOT, "Ingredients", "json", `${slug}.json`);
  const mdPath = resolve(ROOT, "Ingredients", `${slug}.md`);

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

  // Write JSON (formatted for readability)
  const jsonContent = JSON.stringify(ingredient, null, 2) + "\n";
  writeFileSync(jsonPath, jsonContent, "utf-8");
  console.log(`  Created: Ingredients/json/${slug}.json`);

  // Write Markdown scaffold
  const mdContent = generateIngredientMarkdown(ingredient);
  writeFileSync(mdPath, mdContent, "utf-8");
  console.log(`  Created: Ingredients/${slug}.md`);

  // Cross-reference reminder
  if (ingredient.relatedIngredients.length > 0) {
    console.log("\nReminder — update relatedIngredients in these files:");
    for (const related of ingredient.relatedIngredients) {
      const relatedPath = `Ingredients/json/${related}.json`;
      const exists = existsSync(resolve(ROOT, relatedPath));
      console.log(`  ${exists ? "+" : "?"} ${relatedPath} — add "${slug}" to relatedIngredients`);
    }
  }

  console.log(`\nDone! Now fill in the TODO sections in Ingredients/${slug}.md`);
}

main();
