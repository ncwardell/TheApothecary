# LifeApothecary

A rigorous, science-based repository of DIY replacements for everyday commercial products. Every recipe is grounded in real chemistry, cites actual mechanisms of action, and honestly rates its effectiveness against the commercial product it replaces.

The premise is simple: most commercial products are combinations of 15-20 bulk ingredients repackaged with branding, fragrance, and markup. A $12 bottle of surface cleaner is vinegar and water. A $40 face cream is tallow and jojoba oil. A $25 tub of OxiClean is sodium percarbonate. This repository documents the chemistry, provides tested recipes, and points you to the bulk ingredients.

## What This Is

- **35 ingredient profiles** with full chemistry, mechanisms of action, safety data, sourcing, and regulatory status
- **26 recipes** spanning oral care, skin, hair, cleaning, laundry, kitchen, health, and garden
- **Structured JSON metadata** for every ingredient and recipe, designed for programmatic use (website, RAG chatbot, affiliate integration)
- **Honest effectiveness scores** (1-10 vs commercial) with transparent reasoning about where DIY falls short

## What This Is Not

- Not "natural is always better" ideology. Some commercial products are genuinely superior (enzyme-based laundry detergents, fluoride toothpaste for high-risk individuals). We say so.
- Not folk remedies or wellness trends. Every claim links to a mechanism. If the evidence is weak, we say that too (see: magnesium spray, 6/10).
- Not a substitute for medical advice. Saline solution is saline solution. But serious wounds, severe burns, and acute illness need a doctor.

## Project Structure

```
LifeApothecary/
|
|-- README.md                          # This file
|-- diy-essentials.html                # Static HTML page (recipe cards + filter bar + shopping list)
|-- diy-essentials-repository.jsx      # React component (detailed recipes + ingredient DB + effectiveness scores)
|
|-- Ingredients/
|   |-- baking-soda.md                 # Full ingredient reference (chemistry, safety, sourcing, research)
|   |-- coconut-oil.md
|   |-- zinc-oxide.md
|   |-- ... (35 total)
|   |
|   |-- json/
|       |-- baking-soda.json           # Structured metadata for programmatic use
|       |-- coconut-oil.json
|       |-- zinc-oxide.json
|       |-- ... (35 total, filenames match their .md counterpart)
|
|-- Recipes/
    |-- remineralizing-clay-toothpaste.md   # Full recipe reference (method, science, variations, honest downsides)
    |-- natural-deodorant.md
    |-- complete-laundry-system.md
    |-- ... (26 total)
    |
    |-- json/
        |-- remineralizing-clay-toothpaste.json   # Structured metadata for programmatic use
        |-- natural-deodorant.json
        |-- complete-laundry-system.json
        |-- ... (26 total, filenames match their .md counterpart)
```

## Ingredients

### Markdown Files (`Ingredients/*.md`)

Each ingredient gets a comprehensive reference document. These are the deep-dive profiles — everything you'd want to know before putting something on your skin, in your mouth, or on your laundry. Think of them as the package insert that consumer products should have but don't.

**Required sections (in order):**

| Section | What It Covers |
|---|---|
| **Title + Blockquote** | Name and one-sentence summary of what this ingredient does and why it matters |
| **Quick Reference** | Table: common names, chemical name/IUPAC, formula, CAS number, molecular weight, appearance, pH, solubility |
| **Overview** | What this ingredient is, what gap it fills in a DIY system, why it matters chemically |
| **Chemical Composition & Structure** | Crystal structure, active compounds, relevant physical properties, mechanism tables |
| **How It Is Produced / How to Make It from Scratch** | Industrial process, whether home production is feasible, and if not, why not |
| **Mechanism of Action** | Exactly how it works at the molecular level for each application |
| **Applications & Uses** | DIY recipes and formulations, concentrations, methods. Also medical/industrial uses if relevant |
| **Efficacy & Research** | Specific studies with authors, journals, and findings. Not "studies show" — which study, what it found |
| **Safety, Warnings & Contraindications** | Toxicity, incompatibilities, handling precautions, who should avoid it |
| **Pros & Cons** | Honest assessment, including where the ingredient falls short |
| **Storage & Shelf Life** | How to store, how long it lasts, signs of degradation |
| **Cost & Sourcing** | Price table (quantity + USD range), where to buy, quality indicators to look for |
| **Regulatory Status** | FDA, EU, TGA, USP status. What's it approved for and at what concentrations |
| **Related Ingredients** | Cross-references to ingredients that complement, compete with, or replace this one |
| **References & Further Reading** | Numbered citations with full author, year, journal, title |

### JSON Files (`Ingredients/json/*.json`)

Structured metadata for each ingredient, used by the website, the RAG chatbot, and affiliate link integration. The filename matches the corresponding `.md` file (e.g., `baking-soda.md` -> `baking-soda.json`).

**Schema:**

```json
{
  "id": "baking-soda",
  "name": "Baking Soda (Sodium Bicarbonate)",
  "slug": "baking-soda",
  "description": "One-sentence summary",
  "chemicalName": "Sodium hydrogen carbonate",
  "formula": "NaHCO₃",
  "casNumber": "144-55-8",
  "molecularWeight": "84.007 g/mol",
  "appearance": "White crystalline powder",
  "pH": "8.3–8.6",
  "solubility": "96 g/L in water at 20°C",
  "chemistry": "Concise mechanism summary for UI display",
  "warnings": "Key safety warnings for UI display",
  "costNote": "$3–5 for 5 lb bag",
  "shelfLife": "Indefinite when stored dry",
  "categories": ["oral", "cleaning", "laundry", "skin"],
  "relatedIngredients": ["washing-soda", "bentonite-clay"]
}
```

**Field notes:**

- `id` — Unique identifier used in code. Usually matches `slug`, but a few legacy exceptions exist: `"acv"` for apple-cider-vinegar, `"ammonia"` for household-ammonia. These match the JSX `INGREDIENTS_DB` keys.
- `slug` — Always matches the `.md` filename (without extension). Used for URL routing and file lookups.
- `categories` — Array of: `"oral"`, `"skin"`, `"hair"`, `"cleaning"`, `"laundry"`, `"health"`, `"garden"`, `"kitchen"`
- `relatedIngredients` — Array of `slug` values pointing to other ingredient files
- `chemistry` and `warnings` — Condensed versions of what's in the MD file, designed for card/tooltip display in the UI

## Recipes

### Markdown Files (`Recipes/*.md`)

Full recipe documents with method, science, variations, and honest downsides. These are written so someone with zero experience can follow them, but with enough chemistry that someone with a science background can understand *why* each step works.

**Required sections (in order):**

| Section | What It Covers |
|---|---|
| **Title + Blockquote** | Name and one-sentence summary |
| **Overview** | Table: category, what it replaces, cost per use, shelf life, effectiveness score, difficulty |
| **What This Replaces & Why** | What commercial product(s) this replaces, why the commercial version is overpriced or unnecessary, and where the DIY version is genuinely inferior |
| **Ingredients** | Core ingredients table (linked to Ingredient MD files) and optional ingredients table, each with amount and specific role |
| **Equipment Needed** | What you need and why (e.g., "non-metal spoon — bentonite reacts with metal") |
| **Method** | Step-by-step instructions, numbered, with enough detail that a first-timer can follow |
| **The Science Behind It** | Why this recipe works at the chemical level. Not "baking soda cleans" but "NaHCO₃ neutralizes lactic acid produced by S. mutans, raising oral pH above the 5.5 demineralization threshold" |
| **Variations** | Alternative formulations, substitutions, adaptations for different needs |
| **Effectiveness Assessment** | Score out of 10 vs commercial equivalent with transparent reasoning |
| **Pros** | Advantages over commercial |
| **Cons & Limitations** | Honest downsides — where the DIY version falls short |
| **Tips & Troubleshooting** | Common problems and how to solve them |
| **Safety Notes** | Anything that could go wrong and how to prevent it |
| **Related Recipes** | Cross-references to complementary recipes |

### JSON Files (`Recipes/json/*.json`)

Structured metadata for each recipe. Filename matches the `.md` file.

**Schema:**

```json
{
  "id": "toothpaste",
  "name": "Remineralizing Clay Toothpaste",
  "slug": "remineralizing-clay-toothpaste",
  "description": "One-sentence summary",
  "category": "oral",
  "replaces": "Commercial toothpaste ($4–8/tube)",
  "costPerUse": "~$0.03",
  "shelfLife": "1–2 months sealed glass jar",
  "effectiveness": 8,
  "effectivenessNote": "Transparent reasoning for the score",
  "difficulty": "Easy",
  "coreIngredients": ["bentonite-clay", "coconut-oil"],
  "optionalIngredients": ["baking-soda", "sea-salt", "xylitol"],
  "warnings": ["Warning 1", "Warning 2"],
  "scienceNote": "Why it works, in one paragraph"
}
```

**Field notes:**

- `id` — Unique recipe identifier. Matches the JSX `RECIPES` id where one exists.
- `slug` — Always matches the `.md` filename. Used for URL routing.
- `category` — Single string: `"oral"`, `"skin"`, `"hair"`, `"cleaning"`, `"laundry"`, `"health"`, `"garden"`, `"kitchen"`
- `effectiveness` — Integer 1-10. Honest comparison vs the commercial product it replaces.
- `coreIngredients` / `optionalIngredients` — Arrays of ingredient `id` values (not slugs). These create the link between recipes and ingredients.
- `difficulty` — `"Easy"`, `"Moderate"`, or `"Advanced"`

## Categories

| ID | Label | Covers |
|---|---|---|
| `oral` | Oral Care | Toothpaste, mouthwash, whitening, toothbrush alternatives |
| `skin` | Skin & Body | Moisturizer, deodorant, soap, lip balm, sunscreen |
| `hair` | Hair | Shampoo, conditioner, hair growth, scalp treatment |
| `cleaning` | Cleaning | Surface cleaners, glass, degreaser, descaler, disinfectant |
| `laundry` | Laundry | Detergent, softener, stain removal, whitening |
| `kitchen` | Kitchen & Food | Broth, fermentation, bread, spices |
| `health` | Health | Supplements, saline, herbal medicine, wound care, bath soaks |
| `garden` | Garden & Home | Pest control, fertilizer, wood stain |

## How to Add a New Ingredient

1. **Research.** Read primary sources (peer-reviewed papers, FDA monographs, toxicology databases). Do not write from blog posts or hearsay.

2. **Create the MD file.** Add `Ingredients/your-ingredient.md` following the section template above. Every section is required. If information for a section doesn't exist (e.g., no relevant research), state that explicitly rather than omitting the section.

3. **Create the JSON file.** Add `Ingredients/json/your-ingredient.json` matching the schema above. The `slug` must match the MD filename. The `id` should match the slug unless there's a legacy reason not to.

4. **Cross-reference.** Add this ingredient to the `relatedIngredients` arrays of any existing ingredients it's related to (and add those to its own array).

5. **Update recipes.** If any existing recipes should reference this ingredient (as core or optional), update their JSON files' `coreIngredients` or `optionalIngredients` arrays.

6. **Verify.** Run a quick check: does the slug in the JSON match the filename? Does the `id` match what the JSX `INGREDIENTS_DB` uses (if it's referenced there)? Are the categories valid?

## How to Add a New Recipe

1. **Identify the gap.** What commercial product does this replace? Is the replacement grounded in chemistry, or is it wishful thinking? If you can't explain *why* it works at the molecular level, it doesn't belong here.

2. **Create the MD file.** Add `Recipes/your-recipe.md` following the section template above. Include an honest effectiveness score with reasoning. If the DIY version is inferior in specific ways, say so.

3. **Create the JSON file.** Add `Recipes/json/your-recipe.json` matching the schema above. The `slug` must match the MD filename. Reference ingredients by their `id` values.

4. **Verify ingredient references.** Every ingredient ID in `coreIngredients` and `optionalIngredients` must correspond to an existing `Ingredients/json/*.json` file. If the recipe uses an ingredient that doesn't have a profile yet, create the ingredient files first.

5. **Cross-reference.** Add this recipe to the "Related Recipes" section of any related recipe MD files.

## Naming Conventions

- **Filenames**: lowercase, hyphen-separated, no special characters. `sodium-percarbonate.md`, not `Sodium_Percarbonate.md`
- **JSON `slug`**: always matches the filename without extension
- **JSON `id`**: matches `slug` for new entries. Legacy exceptions (`acv`, `ammonia`) exist but should not be expanded
- **Ingredient links in MD files**: use relative paths: `[Baking Soda](../Ingredients/baking-soda.md)`

## Roadmap

### The Apothecary (RAG Chatbot)

The MD files and JSON metadata are structured to serve as a knowledge base for a retrieval-augmented generation chatbot. The intent:

- User asks: "What can I use instead of OxiClean?"
- RAG retrieves `sodium-percarbonate.md` and `complete-laundry-system.md`
- LLM synthesizes an answer grounded in the actual chemistry and recipe data
- Response includes the specific recipe, ingredient list, and honest effectiveness rating

The MD files provide depth (mechanisms, research, safety). The JSON files provide structure (categories, ingredient cross-references, effectiveness scores) for retrieval filtering and ranking.

### Affiliate Integration

Each ingredient JSON will gain an `affiliateLinks` field:

```json
{
  "affiliateLinks": [
    {
      "retailer": "amazon",
      "url": "https://www.amazon.com/dp/B00XXXX?tag=lifeapothecary-20",
      "productName": "Pure Sodium Bicarbonate, 5 lb",
      "quantity": "5 lb",
      "priceRange": "$3–5"
    }
  ]
}
```

The website and chatbot can then render a "Get the ingredients" list for any recipe, where each ingredient links to a verified product. The user clicks through a recipe, sees the ingredient list with one-click purchase links, and we earn affiliate commission on the products they'd buy anyway.

**Rules for affiliate links:**

- Only link products we'd actually recommend (correct grade, reputable brand, good value)
- Never let affiliate incentives influence which ingredients or recipes we recommend
- Always disclose affiliate relationship
- Prefer bulk sizes that represent the best value (the whole point is saving money)

### Website

The static HTML and React component are the current frontend. Future plans:

- Recipe pages generated from the MD files
- Ingredient profile pages with cross-referenced recipes
- "Build your shopping list" feature: select recipes, get a deduplicated ingredient list with affiliate links
- Cost calculator: input how many people, how often, see annual savings vs commercial

## Contributing

The bar for contributions is high. This repository prioritizes being correct over being comprehensive. Before adding an ingredient or recipe:

1. Can you explain the mechanism of action? Not "it works because it's natural" — what is the actual chemistry?
2. Is there peer-reviewed evidence, or at minimum a well-understood chemical mechanism?
3. Are you being honest about limitations? Every entry should have real downsides listed.
4. Would you use this yourself and recommend it to a friend?

If the answer to all four is yes, follow the steps above and submit a PR.

## License

TBD
