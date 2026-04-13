#!/usr/bin/env tsx
/**
 * ═══════════════════════════════════════════════════════════════════
 * Validate — The Apothecary
 * ═══════════════════════════════════════════════════════════════════
 *
 * Validates all existing ingredient and recipe JSON files against
 * the canonical schema. Also checks cross-references:
 *   - Recipe ingredient IDs must reference existing ingredients
 *   - Related ingredient slugs must reference existing ingredients
 *   - Every JSON file must have a corresponding .md file
 *
 * Usage:
 *   npx tsx validate.ts              # validate everything
 *   npx tsx validate.ts --fix-refs   # also add missing cross-references
 * ═══════════════════════════════════════════════════════════════════
 */

import { readFileSync, readdirSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { validateIngredient, validateRecipe, type ValidationError } from "./schema.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

interface FileReport {
  file: string;
  errors: ValidationError[];
}

function loadJsonDir(dir: string): { file: string; data: Record<string, unknown> }[] {
  const fullDir = resolve(ROOT, dir);
  if (!existsSync(fullDir)) return [];

  return readdirSync(fullDir)
    .filter(f => f.endsWith(".json"))
    .sort()
    .map(f => ({
      file: `${dir}/${f}`,
      data: JSON.parse(readFileSync(resolve(fullDir, f), "utf-8")),
    }));
}

function main() {
  let totalErrors = 0;
  const reports: FileReport[] = [];

  // ── Load all data ──────────────────────────────────────────────

  const ingredients = loadJsonDir("Ingredients/json");
  const recipes = loadJsonDir("Recipes/json");

  const ingredientIds = new Set(ingredients.map(i => i.data.id as string));
  const ingredientSlugs = new Set(ingredients.map(i => i.data.slug as string));

  console.log(`Validating ${ingredients.length} ingredients and ${recipes.length} recipes...\n`);

  // ── Validate ingredients ───────────────────────────────────────

  for (const { file, data } of ingredients) {
    const errors = validateIngredient(data);

    // Check .md file exists
    const slug = data.slug as string;
    if (slug && !existsSync(resolve(ROOT, "Ingredients", `${slug}.md`))) {
      errors.push({ field: "slug", message: `Missing markdown file: Ingredients/${slug}.md` });
    }

    // Check relatedIngredients reference valid slugs
    const related = (data.relatedIngredients || []) as string[];
    for (const ref of related) {
      if (!ingredientSlugs.has(ref) && !ingredientIds.has(ref)) {
        errors.push({
          field: "relatedIngredients",
          message: `References unknown ingredient "${ref}"`,
        });
      }
    }

    if (errors.length > 0) {
      reports.push({ file, errors });
      totalErrors += errors.length;
    }
  }

  // ── Validate recipes ───────────────────────────────────────────

  for (const { file, data } of recipes) {
    const errors = validateRecipe(data);

    // Check .md file exists
    const slug = data.slug as string;
    if (slug && !existsSync(resolve(ROOT, "Recipes", `${slug}.md`))) {
      errors.push({ field: "slug", message: `Missing markdown file: Recipes/${slug}.md` });
    }

    // Check ingredient references
    const allRefs = [
      ...((data.coreIngredients || []) as string[]),
      ...((data.optionalIngredients || []) as string[]),
    ];
    for (const ref of allRefs) {
      if (!ingredientIds.has(ref)) {
        errors.push({
          field: "coreIngredients/optionalIngredients",
          message: `References unknown ingredient ID "${ref}"`,
        });
      }
    }

    if (errors.length > 0) {
      reports.push({ file, errors });
      totalErrors += errors.length;
    }
  }

  // ── Check for orphaned files ───────────────────────────────────

  // MD files without corresponding JSON
  for (const dir of ["Ingredients", "Recipes"]) {
    const mdDir = resolve(ROOT, dir);
    if (!existsSync(mdDir)) continue;

    const jsonDir = dir === "Ingredients" ? "Ingredients/json" : "Recipes/json";
    const jsonSlugs = new Set(
      (dir === "Ingredients" ? ingredients : recipes).map(i => i.data.slug as string)
    );

    for (const f of readdirSync(mdDir)) {
      if (!f.endsWith(".md")) continue;
      const slug = f.replace(".md", "");
      if (!jsonSlugs.has(slug)) {
        reports.push({
          file: `${dir}/${f}`,
          errors: [{ field: "orphan", message: `Markdown file has no corresponding JSON in ${jsonDir}/` }],
        });
        totalErrors++;
      }
    }
  }

  // ── Report ─────────────────────────────────────────────────────

  if (totalErrors === 0) {
    console.log("All files valid. No errors found.");
    console.log(`  ${ingredients.length} ingredients`);
    console.log(`  ${recipes.length} recipes`);
    console.log(`  All cross-references OK`);
    process.exit(0);
  }

  for (const report of reports) {
    console.log(`${report.file}:`);
    for (const err of report.errors) {
      console.log(`  [${err.field}] ${err.message}`);
    }
    console.log();
  }

  console.log(`${totalErrors} error(s) in ${reports.length} file(s).`);
  process.exit(1);
}

main();
