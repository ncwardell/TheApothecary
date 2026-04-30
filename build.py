#!/usr/bin/env python3
"""
Build script for LifeApothecary static site.
Generates individual HTML pages for each recipe and ingredient from JSON + MD files.
Also generates sitemap.xml.

Usage: python3 build.py
"""

import json
import os
import html
import shutil
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
SITE_URL = "https://www.theapothecary.diy"

CATEGORY_LABELS = {
    "oral": "Oral Care",
    "skin": "Skin &amp; Body",
    "hair": "Hair",
    "cleaning": "Cleaning",
    "laundry": "Laundry",
    "kitchen": "Kitchen",
    "health": "Health",
    "garden": "Garden &amp; Home",
}

# ── Shared HTML fragments ──────────────────────────────────────────────

HEAD_COMMON = """\
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Source+Sans+3:wght@300;400;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="canonical" href="{canonical}">"""

STYLES = """\
<style>
:root {
  --bg: #f4f1eb;
  --card: #ffffff;
  --text: #2c2416;
  --muted: #7a6f5f;
  --accent: #b8860b;
  --accent-light: #dcc07a;
  --divider: #e0d8c8;
  --tag-bg: #f0e9d8;
  --savings-bg: #e8f0e4;
  --savings-text: #3a6b2a;
  --warn-bg: #faf0ec;
  --warn-text: #993333;
  --warn-border: #d4a8a8;
  --shadow: 0 1px 3px rgba(44,36,22,0.06);
  --radius: 10px;
}
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Source Sans 3', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}
.page-container {
  max-width: 780px;
  margin: 0 auto;
  padding: 28px 20px 80px;
}

/* ── Nav ── */
.top-nav {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--divider);
}
.top-nav a {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.88em;
  border-bottom: 1px solid transparent;
  transition: border-color 0.15s;
}
.top-nav a:hover { border-bottom-color: var(--accent); }
.nav-sep { color: var(--divider); }
.nav-current { color: var(--muted); font-size: 0.88em; }

/* ── Page header ── */
.page-title {
  font-family: 'DM Serif Display', serif;
  font-size: 2em;
  color: var(--text);
  letter-spacing: -0.5px;
  margin-bottom: 6px;
}
.page-subtitle {
  color: var(--muted);
  font-size: 1em;
  font-weight: 300;
  margin-bottom: 20px;
  line-height: 1.55;
}

/* ── Meta grid ── */
.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  margin-bottom: 24px;
}
.meta-item {
  background: var(--card);
  border-radius: 8px;
  padding: 10px 13px;
  border: 1px solid var(--divider);
}
.meta-label {
  font-size: 0.65em;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 700;
}
.meta-value {
  font-size: 0.9em;
  color: var(--text);
  margin-top: 2px;
}

/* ── Badges ── */
.badge-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.badge {
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 0.78em;
  font-weight: 700;
  white-space: nowrap;
}
.badge-cost { background: var(--savings-bg); color: var(--savings-text); }
.badge-eff-high { background: #e4f0e4; color: #3a7d2a; }
.badge-eff-mid { background: #f0ede4; color: #8a7d2a; }
.badge-eff-low { background: #f0e8e4; color: #a05a2a; }
.badge-diff-easy { background: #e4f0e4; color: #3a7d2a; }
.badge-diff-moderate { background: #f0ede4; color: #8a7d2a; }
.badge-diff-advanced { background: #f0e8e4; color: #a05a2a; }
.cat-pill {
  background: var(--tag-bg);
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.72em;
  color: #8a7d6b;
  font-weight: 600;
  text-transform: uppercase;
}

/* ── Shop block (prominent affiliate CTA) ── */
.shop-block {
  background: linear-gradient(135deg, #f4ecd6 0%, #faf5e3 100%);
  border: 1px solid var(--accent-light);
  border-radius: var(--radius);
  padding: 18px 18px 14px;
  margin-bottom: 22px;
  box-shadow: 0 2px 8px rgba(184,134,11,0.08);
}
.shop-block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}
.shop-block-title {
  font-family: 'DM Serif Display', serif;
  font-size: 1.1em;
  color: var(--text);
  letter-spacing: -0.2px;
}
.shop-block-sub {
  font-size: 0.78em;
  color: var(--muted);
  font-weight: 600;
}
.shop-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 13px;
  background: var(--card);
  border: 1px solid var(--divider);
  border-radius: 8px;
  margin-bottom: 6px;
  text-decoration: none;
  color: var(--text);
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
}
.shop-row:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(184,134,11,0.12);
}
.shop-row-left { min-width: 0; flex: 1; }
.shop-row-name { font-weight: 700; font-size: 0.92em; color: var(--text); }
.shop-row-detail { font-size: 0.78em; color: var(--muted); margin-top: 2px; }
.shop-row-cta {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--accent);
  color: #fff !important;
  font-weight: 700;
  font-size: 0.82em;
  padding: 7px 14px;
  border-radius: 7px;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s;
}
.shop-row:hover .shop-row-cta { background: #9a7209; }
.shop-row-price { font-weight: 700; color: var(--savings-text); font-size: 0.82em; }
.shop-row.no-link { cursor: default; opacity: 0.85; }
.shop-row.no-link:hover { transform: none; box-shadow: none; border-color: var(--divider); }
.shop-row.no-link .shop-row-cta {
  background: transparent;
  color: var(--muted) !important;
  border: 1px solid var(--divider);
  font-weight: 600;
}
.shop-disclaimer {
  font-size: 0.7em;
  color: var(--muted);
  font-style: italic;
  margin-top: 8px;
  text-align: center;
}

/* ── Buy CTA (single big button, ingredient page) ── */
.buy-cta-block {
  background: linear-gradient(135deg, #f4ecd6 0%, #faf5e3 100%);
  border: 1px solid var(--accent-light);
  border-radius: var(--radius);
  padding: 16px 18px;
  margin-bottom: 22px;
  box-shadow: 0 2px 8px rgba(184,134,11,0.08);
}
.buy-cta-label {
  font-size: 0.7em;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 6px;
}
.buy-cta-cost { font-size: 0.95em; color: var(--text); margin-bottom: 10px; }
.buy-cta-cost strong { color: var(--accent); }
.buy-cta-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 16px;
  background: var(--accent);
  color: #fff !important;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 700;
  margin-bottom: 6px;
  transition: background 0.15s, transform 0.15s;
  font-size: 0.95em;
}
.buy-cta-btn:hover { background: #9a7209; transform: translateY(-1px); }
.buy-cta-btn-secondary {
  background: var(--card);
  color: var(--text) !important;
  border: 1.5px solid var(--accent);
  font-weight: 600;
  font-size: 0.88em;
}
.buy-cta-btn-secondary:hover { background: var(--tag-bg); }
.buy-cta-price { font-weight: 700; opacity: 0.95; }

/* ── Effectiveness bar ── */
.eff-wrap {
  background: var(--card);
  border-radius: var(--radius);
  padding: 16px 18px;
  border: 1px solid var(--divider);
  margin-bottom: 20px;
}
.eff-bar { display: flex; align-items: center; gap: 10px; }
.eff-bar-label {
  font-size: 0.75em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  min-width: 100px;
}
.eff-bar-track {
  flex: 1;
  height: 8px;
  background: #eae5d6;
  border-radius: 4px;
  overflow: hidden;
}
.eff-bar-fill { height: 100%; border-radius: 4px; }
.eff-bar-score { font-size: 0.9em; font-weight: 700; min-width: 35px; text-align: right; }
.eff-note {
  font-size: 0.85em;
  color: #6b5d4d;
  line-height: 1.5;
  font-style: italic;
  margin-top: 6px;
}

/* ── Ingredient links ── */
.ingredient-section { margin-bottom: 20px; }
.ingredient-section-title {
  font-size: 0.72em;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  margin-bottom: 8px;
}
.ingredient-section-title.core { color: var(--accent); }
.ingredient-section-title.optional { color: #8a7d6b; }
.ingredient-link {
  display: inline-block;
  background: none;
  border: 1px solid #c8bfa8;
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 0.85em;
  color: #6b5d4d;
  text-decoration: none;
  margin: 0 4px 6px 0;
  transition: all 0.15s;
}
.ingredient-link:hover {
  background: #f5eed8;
  border-color: var(--accent);
  color: var(--text);
}

/* ── Warning box ── */
.warnings-box { margin-bottom: 20px; }
.warning-item {
  font-size: 0.85em;
  line-height: 1.45;
  color: #6b4a3e;
  padding: 7px 12px;
  background: var(--warn-bg);
  border-radius: 6px;
  border-left: 3px solid var(--warn-border);
  margin-bottom: 5px;
}

/* ── Science box ── */
.science-box {
  background: #eae5d6;
  border-radius: var(--radius);
  padding: 16px 18px;
  border-left: 3px solid var(--accent);
  margin-bottom: 24px;
}
.science-box-title {
  font-size: 0.72em;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 6px;
}
.science-box p {
  font-size: 0.88em;
  line-height: 1.6;
  color: #4a3f30;
}

/* ── Related links ── */
.related-section { margin-top: 28px; padding-top: 20px; border-top: 1px solid var(--divider); }
.related-title {
  font-family: 'DM Serif Display', serif;
  font-size: 1.1em;
  margin-bottom: 10px;
}
.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}
.related-card {
  background: var(--card);
  border-radius: 8px;
  padding: 12px 14px;
  border: 1px solid var(--divider);
  text-decoration: none;
  color: var(--text);
  transition: border-color 0.15s, box-shadow 0.2s;
}
.related-card:hover { border-color: var(--accent); box-shadow: 0 3px 12px rgba(44,36,22,0.1); }
.related-card-name { font-weight: 600; font-size: 0.9em; }
.related-card-detail { font-size: 0.78em; color: var(--muted); margin-top: 2px; }

/* ── Markdown body ── */
.md-body { font-size: 0.92em; line-height: 1.7; color: #3a3225; margin-top: 20px; }
.md-body h1 {
  font-family: 'DM Serif Display', serif;
  font-size: 1.5em;
  margin: 28px 0 10px;
  color: var(--text);
  border-bottom: 2px solid var(--accent);
  padding-bottom: 6px;
}
.md-body h2 {
  font-family: 'DM Serif Display', serif;
  font-size: 1.2em;
  margin: 24px 0 10px;
  padding-left: 12px;
  border-left: 3px solid var(--accent);
  color: var(--text);
}
.md-body h3 { font-size: 1em; font-weight: 700; margin: 18px 0 6px; color: var(--text); }
.md-body h4 { font-size: 0.88em; font-weight: 700; margin: 14px 0 4px; color: var(--accent); }
.md-body p { margin: 8px 0; }
.md-body ul, .md-body ol { margin: 8px 0; padding-left: 24px; }
.md-body li { margin: 3px 0; }
.md-body blockquote {
  border-left: 3px solid var(--accent-light);
  margin: 12px 0;
  padding: 8px 16px;
  background: var(--tag-bg);
  border-radius: 0 8px 8px 0;
  font-style: italic;
  color: #5a4f3e;
}
.md-body table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 0.94em; }
.md-body th {
  background: var(--tag-bg);
  font-weight: 700;
  text-align: left;
  padding: 8px 10px;
  border-bottom: 2px solid var(--divider);
  font-size: 0.9em;
  color: var(--text);
}
.md-body td { padding: 6px 10px; border-bottom: 1px solid var(--divider); vertical-align: top; }
.md-body tr:last-child td { border-bottom: none; }
.md-body code { background: var(--tag-bg); padding: 1px 5px; border-radius: 4px; font-size: 0.9em; }
.md-body pre {
  background: #2c2416;
  color: #e8dcc8;
  padding: 14px 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  font-size: 0.85em;
  line-height: 1.5;
}
.md-body pre code { background: none; padding: 0; color: inherit; }
.md-body strong { color: var(--text); }
.md-body a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent-light); }
.md-body a:hover { border-bottom-color: var(--accent); }
.md-body hr { border: none; border-top: 1px solid var(--divider); margin: 16px 0; }

/* ── Responsive ── */
@media (max-width: 640px) {
  .page-title { font-size: 1.6em; }
  .page-container { padding: 16px 14px 60px; }
  .meta-grid { grid-template-columns: 1fr 1fr; }
  .related-grid { grid-template-columns: 1fr; }
}
</style>"""


def e(text):
    """HTML-escape a string."""
    return html.escape(str(text)) if text else ""


def eff_color(score):
    if score >= 8:
        return "#3a7d2a"
    elif score >= 6:
        return "#8a7d2a"
    return "#a05a2a"


def eff_badge_class(score):
    if score >= 8:
        return "badge-eff-high"
    elif score >= 6:
        return "badge-eff-mid"
    return "badge-eff-low"


def diff_badge_class(difficulty):
    if not difficulty:
        return "badge-diff-easy"
    d = difficulty.lower()
    if "advanced" in d or "hard" in d:
        return "badge-diff-advanced"
    if "moderate" in d or "medium" in d:
        return "badge-diff-moderate"
    return "badge-diff-easy"


def load_json_files(directory):
    """Load all JSON files from a directory, return list of dicts."""
    results = []
    json_dir = ROOT / directory / "json"
    if not json_dir.exists():
        return results
    for f in sorted(json_dir.glob("*.json")):
        with open(f) as fh:
            results.append(json.load(fh))
    return results


def read_md(directory, slug):
    """Read a markdown file, return contents or empty string."""
    md_path = ROOT / directory / f"{slug}.md"
    if md_path.exists():
        return md_path.read_text(encoding="utf-8")
    return ""


def build_recipe_page(recipe, ingredients_db, all_recipes):
    """Generate HTML for a single recipe page."""
    slug = recipe["slug"]
    name = recipe["name"]
    desc = recipe.get("description", "")
    category = recipe.get("category", "")
    cat_label = CATEGORY_LABELS.get(category, category)
    canonical = f"{SITE_URL}/recipes/{slug}/"
    effectiveness = recipe.get("effectiveness", 0)
    ec = eff_color(effectiveness)

    md_content = read_md("Recipes", slug)
    # Escape the markdown for embedding in a JS string
    md_js = json.dumps(md_content)

    # Build "Shop the Ingredients" block — prominent affiliate CTA
    shop_block_html = ""
    if recipe.get("coreIngredients"):
        rows = []
        with_links = 0
        for iid in recipe["coreIngredients"]:
            ing = ingredients_db.get(iid)
            if not ing:
                continue
            link = (ing.get("affiliateLinks") or [None])[0]
            if link:
                with_links += 1
                rows.append(f"""
              <a class="shop-row" href="{e(link['url'])}" target="_blank" rel="noopener sponsored" data-aff-ingredient="{e(ing['slug'])}">
                <div class="shop-row-left">
                  <div class="shop-row-name">{e(ing['name'])}</div>
                  <div class="shop-row-detail">{e(link.get('quantity', ''))} &middot; <span class="shop-row-price">{e(link.get('price', ''))}</span></div>
                </div>
                <span class="shop-row-cta">Buy on Amazon &rarr;</span>
              </a>""")
            else:
                rows.append(f"""
              <a class="shop-row no-link" href="../../ingredients/{e(ing['slug'])}/">
                <div class="shop-row-left">
                  <div class="shop-row-name">{e(ing['name'])}</div>
                  <div class="shop-row-detail">{e(ing.get('costNote', 'Source locally or in bulk'))}</div>
                </div>
                <span class="shop-row-cta">View &rarr;</span>
              </a>""")
        if rows:
            label = f"{with_links} of {len(rows)} on Amazon" if with_links else "Source guide"
            shop_block_html = f"""
        <section class="shop-block" aria-label="Shop ingredients">
          <div class="shop-block-header">
            <div class="shop-block-title">Shop the Ingredients</div>
            <div class="shop-block-sub">{label}</div>
          </div>
          {"".join(rows)}
          {'<div class="shop-disclaimer">Affiliate links — we may earn a commission at no extra cost to you.</div>' if with_links else ''}
        </section>"""

    # Build ingredient links
    core_html = ""
    if recipe.get("coreIngredients"):
        pills = []
        for iid in recipe["coreIngredients"]:
            ing = ingredients_db.get(iid)
            if ing:
                pills.append(f'<a class="ingredient-link" href="../../ingredients/{e(ing["slug"])}/">{e(ing["name"])}</a>')
            else:
                pills.append(f'<span class="ingredient-link">{e(iid)}</span>')
        core_html = f"""
        <div class="ingredient-section">
          <div class="ingredient-section-title core">Core Ingredients</div>
          {"".join(pills)}
        </div>"""

    optional_html = ""
    if recipe.get("optionalIngredients"):
        pills = []
        for iid in recipe["optionalIngredients"]:
            ing = ingredients_db.get(iid)
            if ing:
                pills.append(f'<a class="ingredient-link" href="../../ingredients/{e(ing["slug"])}/">{e(ing["name"])}</a>')
            else:
                pills.append(f'<span class="ingredient-link">{e(iid)}</span>')
        optional_html = f"""
        <div class="ingredient-section">
          <div class="ingredient-section-title optional">Optional Ingredients</div>
          {"".join(pills)}
        </div>"""

    # Warnings
    warnings_html = ""
    if recipe.get("warnings"):
        items = "".join(f'<div class="warning-item">{e(w)}</div>' for w in recipe["warnings"])
        warnings_html = f'<div class="warnings-box">{items}</div>'

    # Science
    science_html = ""
    if recipe.get("scienceNote"):
        science_html = f"""
        <div class="science-box">
          <div class="science-box-title">The Science</div>
          <p>{e(recipe["scienceNote"])}</p>
        </div>"""

    # Meta grid
    meta_items = []
    if recipe.get("costPerUse"):
        meta_items.append(("Cost per Use", recipe["costPerUse"]))
    if recipe.get("shelfLife"):
        meta_items.append(("Shelf Life", recipe["shelfLife"]))
    if recipe.get("difficulty"):
        meta_items.append(("Difficulty", recipe["difficulty"]))
    if recipe.get("replaces"):
        meta_items.append(("Replaces", recipe["replaces"]))
    meta_html = ""
    if meta_items:
        cells = "".join(
            f'<div class="meta-item"><div class="meta-label">{e(l)}</div><div class="meta-value">{e(v)}</div></div>'
            for l, v in meta_items
        )
        meta_html = f'<div class="meta-grid">{cells}</div>'

    # Related recipes (same category, excluding self)
    related_recipes = [r for r in all_recipes if r["category"] == category and r["slug"] != slug][:6]
    related_html = ""
    if related_recipes:
        cards = "".join(
            f'<a class="related-card" href="../{e(r["slug"])}/">'
            f'<div class="related-card-name">{e(r["name"])}</div>'
            f'<div class="related-card-detail">{e(r.get("costPerUse", ""))} &middot; {r.get("effectiveness", "")}/10</div>'
            f'</a>'
            for r in related_recipes
        )
        related_html = f"""
        <div class="related-section">
          <div class="related-title">More {cat_label} Recipes</div>
          <div class="related-grid">{cards}</div>
        </div>"""

    # Build JSON-LD Recipe schema
    ingredient_names = []
    for iid in recipe.get("coreIngredients", []):
        ing = ingredients_db.get(iid)
        ingredient_names.append(ing["name"] if ing else iid)
    for iid in recipe.get("optionalIngredients", []):
        ing = ingredients_db.get(iid)
        ingredient_names.append(f'{ing["name"] if ing else iid} (optional)')

    # Product/Offer schema for ingredients with affiliate links — helps Google show price/store
    offer_schemas = []
    for iid in recipe.get("coreIngredients", []) + recipe.get("optionalIngredients", []):
        ing = ingredients_db.get(iid)
        if not ing or not ing.get("affiliateLinks"):
            continue
        for link in ing["affiliateLinks"]:
            offer_schemas.append({
                "@context": "https://schema.org",
                "@type": "Product",
                "name": link.get("productName", ing["name"]),
                "description": ing.get("description", ""),
                "url": link["url"],
                "offers": {
                    "@type": "Offer",
                    "url": link["url"],
                    "priceCurrency": "USD",
                    "price": (link.get("price", "").replace("~", "").replace("$", "").split("-")[0].strip() or "0"),
                    "availability": "https://schema.org/InStock",
                    "seller": {"@type": "Organization", "name": link.get("retailer", "Amazon").title()}
                }
            })

    recipe_schema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": name,
        "description": desc,
        "url": canonical,
        "supply": [{"@type": "HowToSupply", "name": n} for n in ingredient_names],
        "totalTime": "PT15M" if recipe.get("difficulty") == "Easy" else "PT30M" if recipe.get("difficulty") == "Moderate" else "PT60M",
    }

    # FAQ schema for GEO (AI search engines extract Q&A)
    replaces_clean = (recipe.get("replaces", "") or "").split("(")[0].strip()
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"How do you make homemade {name.lower()}?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"{desc} The core ingredients are: {', '.join(ingredient_names[:5])}. {recipe.get('scienceNote', '')}"
                }
            },
            {
                "@type": "Question",
                "name": f"Is DIY {name.lower()} as good as {replaces_clean.lower()}?" if replaces_clean else f"How effective is {name.lower()}?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Effectiveness: {effectiveness}/10 compared to commercial. {recipe.get('effectivenessNote', '')} Cost per use: {recipe.get('costPerUse', 'varies')}."
                }
            }
        ]
    }

    # BreadcrumbList schema
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "The Apothecary", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Recipes", "item": SITE_URL + "/#recipes"},
            {"@type": "ListItem", "position": 3, "name": name, "item": canonical}
        ]
    }

    schemas_json = json.dumps(recipe_schema)
    faq_json = json.dumps(faq_schema)
    breadcrumb_json = json.dumps(breadcrumb_schema)
    offers_html = "".join(
        f'<script type="application/ld+json">{json.dumps(o)}</script>' for o in offer_schemas
    )

    # SEO-optimized title: lead with searchable intent
    cost_str = recipe.get("costPerUse", "")
    seo_title = f"Homemade {name} Recipe"
    if cost_str:
        seo_title += f" — {cost_str}/use"
    seo_title += " — The Apothecary"

    # SEO-optimized meta description (under ~160 chars)
    seo_desc = f"DIY {name.lower()} recipe with real chemistry."
    if replaces_clean:
        seo_desc = f"DIY {name.lower()} that replaces {replaces_clean.lower()}."
    seo_desc += f" {effectiveness}/10 effectiveness, {cost_str}/use."
    if recipe.get("difficulty"):
        seo_desc += f" {recipe['difficulty']}."

    # GEO: Static summary block visible to all crawlers
    geo_summary = f"""
  <aside class="geo-summary" style="margin-top:32px;padding:20px;background:#f8f5ed;border-radius:10px;border:1px solid #e0d8c8">
    <h2 style="font-family:'DM Serif Display',serif;font-size:1.1em;margin-bottom:8px">Quick Summary</h2>
    <p style="font-size:0.88em;color:#4a3f30;line-height:1.6;margin-bottom:8px"><strong>{e(name)}</strong> is a DIY replacement for {e(replaces_clean or 'commercial products')}. It costs approximately {e(recipe.get('costPerUse', 'varies'))} per use and scores <strong>{effectiveness}/10</strong> versus commercial alternatives.</p>
    <p style="font-size:0.88em;color:#4a3f30;line-height:1.6;margin-bottom:8px"><strong>Core ingredients:</strong> {', '.join(e(n) for n in ingredient_names if '(optional)' not in n)}</p>
    {f'<p style="font-size:0.88em;color:#4a3f30;line-height:1.6;margin-bottom:8px"><strong>How it works:</strong> {e(recipe.get("scienceNote", ""))}</p>' if recipe.get("scienceNote") else ""}
    {f'<p style="font-size:0.88em;color:#6b4a3e;line-height:1.6"><strong>Limitations:</strong> {e(recipe.get("effectivenessNote", ""))}</p>' if recipe.get("effectivenessNote") else ""}
  </aside>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON.format(canonical=canonical)}
<title>{e(seo_title)}</title>
<meta name="description" content="{e(seo_desc)}">
<meta property="og:title" content="{e(seo_title)}">
<meta property="og:description" content="{e(seo_desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="The Apothecary">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(seo_title)}">
<meta name="twitter:description" content="{e(seo_desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script type="application/ld+json">{schemas_json}</script>
<script type="application/ld+json">{faq_json}</script>
<script type="application/ld+json">{breadcrumb_json}</script>
{offers_html}
{STYLES}
</head>
<body>
<div class="page-container">
  <nav class="top-nav" aria-label="Breadcrumb">
    <a href="../../">The Apothecary</a>
    <span class="nav-sep">/</span>
    <a href="../../#recipes">Recipes</a>
    <span class="nav-sep">/</span>
    <span class="nav-current">{e(name)}</span>
  </nav>

  <article>
  <h1 class="page-title">{e(name)}</h1>
  <p class="page-subtitle">{e(desc)}</p>

  <div class="badge-row">
    <span class="cat-pill">{cat_label}</span>
    <span class="badge badge-cost">{e(recipe.get("costPerUse", ""))}</span>
    <span class="badge {eff_badge_class(effectiveness)}">{effectiveness}/10</span>
    {f'<span class="badge {diff_badge_class(recipe.get("difficulty"))}">{e(recipe.get("difficulty"))}</span>' if recipe.get("difficulty") else ""}
  </div>

  {shop_block_html}

  {meta_html}

  <div class="eff-wrap">
    <div class="eff-bar">
      <span class="eff-bar-label" style="color:{ec}">vs Commercial</span>
      <div class="eff-bar-track">
        <div class="eff-bar-fill" style="width:{effectiveness * 10}%;background:{ec}"></div>
      </div>
      <span class="eff-bar-score" style="color:{ec}">{effectiveness}/10</span>
    </div>
    {f'<div class="eff-note">{e(recipe.get("effectivenessNote", ""))}</div>' if recipe.get("effectivenessNote") else ""}
  </div>

  {core_html}
  {optional_html}
  {warnings_html}
  {science_html}

  <div class="md-body" id="md-content"></div>

  {geo_summary}
  </article>

  {related_html}
</div>

<script>
document.getElementById("md-content").innerHTML = marked.parse({md_js});
</script>
</body>
</html>"""


def build_ingredient_page(ingredient, ingredients_db, all_recipes):
    """Generate HTML for a single ingredient page."""
    slug = ingredient["slug"]
    name = ingredient["name"]
    desc = ingredient.get("description", "")
    canonical = f"{SITE_URL}/ingredients/{slug}/"

    md_content = read_md("Ingredients", slug)
    md_js = json.dumps(md_content)

    # Properties grid
    props = [
        ("Chemical Name", ingredient.get("chemicalName")),
        ("Formula", ingredient.get("formula")),
        ("CAS Number", ingredient.get("casNumber")),
        ("Mol. Weight", ingredient.get("molecularWeight")),
        ("pH", ingredient.get("pH")),
        ("Appearance", ingredient.get("appearance")),
        ("Solubility", ingredient.get("solubility")),
        ("Shelf Life", ingredient.get("shelfLife")),
    ]
    props = [(l, v) for l, v in props if v and v != "Not applicable"]
    meta_html = ""
    if props:
        cells = "".join(
            f'<div class="meta-item"><div class="meta-label">{e(l)}</div><div class="meta-value">{e(v)}</div></div>'
            for l, v in props
        )
        meta_html = f'<div class="meta-grid">{cells}</div>'

    # Category pills
    cats = ingredient.get("categories", [])
    cat_pills = " ".join(f'<span class="cat-pill">{CATEGORY_LABELS.get(c, c)}</span>' for c in cats)

    # Chemistry
    chem_html = ""
    if ingredient.get("chemistry"):
        chem_html = f"""
        <div class="science-box">
          <div class="science-box-title">Chemistry &amp; Mechanism</div>
          <p>{e(ingredient["chemistry"])}</p>
        </div>"""

    # Warnings
    warnings_html = ""
    if ingredient.get("warnings"):
        warnings_html = f"""
        <div class="warnings-box">
          <div class="warning-item">{e(ingredient["warnings"])}</div>
        </div>"""

    # Cost + affiliate buy CTA — prominent, near top
    cost_html = ""
    aff_links = ingredient.get("affiliateLinks") or []
    if aff_links:
        buttons = []
        primary = True
        for link in aff_links:
            cls = "buy-cta-btn" if primary else "buy-cta-btn buy-cta-btn-secondary"
            buttons.append(f"""
            <a class="{cls}" href="{e(link['url'])}" target="_blank" rel="noopener sponsored" data-aff-ingredient="{e(slug)}">
              <span><strong>{'Buy on Amazon' if primary else 'Alternate option'} &rarr;</strong> {e(link.get('productName', ''))} ({e(link.get('quantity', ''))})</span>
              <span class="buy-cta-price">{e(link.get('price', ''))}</span>
            </a>""")
            primary = False
        cost_html = f"""
        <section class="buy-cta-block" aria-label="Buy {e(name)}">
          <div class="buy-cta-label">Get {e(name)} Delivered</div>
          <div class="buy-cta-cost">Typical price: <strong>{e(ingredient.get('costNote', 'varies'))}</strong></div>
          {"".join(buttons)}
          <div class="shop-disclaimer">Affiliate link — we may earn a commission at no extra cost to you.</div>
        </section>"""
    elif ingredient.get("costNote"):
        cost_html = f"""
        <div class="buy-cta-block">
          <div class="buy-cta-label">Typical Cost</div>
          <div class="buy-cta-cost"><strong>{e(ingredient["costNote"])}</strong></div>
          <p style="font-size:0.85em;color:var(--muted);margin:0">Source from local bulk stores or co-ops.</p>
        </div>"""

    # Used in recipes
    used_in = [r for r in all_recipes if
               ingredient["id"] in (r.get("coreIngredients", []) + r.get("optionalIngredients", []))]
    used_html = ""
    if used_in:
        cards = "".join(
            f'<a class="related-card" href="../../recipes/{e(r["slug"])}/">'
            f'<div class="related-card-name">{e(r["name"])}</div>'
            f'<div class="related-card-detail">{e(r.get("costPerUse", ""))} &middot; {r.get("effectiveness", "")}/10</div>'
            f'</a>'
            for r in used_in
        )
        used_html = f"""
        <div class="related-section">
          <div class="related-title">Used In Recipes</div>
          <div class="related-grid">{cards}</div>
        </div>"""

    # Related ingredients
    related = []
    for rid in ingredient.get("relatedIngredients", []):
        ri = ingredients_db.get(rid)
        if not ri:
            # Try slug lookup
            for ing in ingredients_db.values():
                if ing["slug"] == rid:
                    ri = ing
                    break
        if ri:
            related.append(ri)
    related_html = ""
    if related:
        cards = "".join(
            f'<a class="related-card" href="../{e(ri["slug"])}/">'
            f'<div class="related-card-name">{e(ri["name"])}</div>'
            f'<div class="related-card-detail">{e(ri.get("costNote", ""))}</div>'
            f'</a>'
            for ri in related
        )
        related_html = f"""
        <div class="related-section" style="{'margin-top:0;border-top:none;padding-top:0' if not used_in else ''}">
          <div class="related-title">Related Ingredients</div>
          <div class="related-grid">{cards}</div>
        </div>"""

    # Structured data: Chemical substance / product
    cat_labels = [CATEGORY_LABELS.get(c, c) for c in cats]
    substance_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": name,
        "description": desc,
        "url": canonical,
        "about": {
            "@type": "ChemicalSubstance",
            "name": name,
            "description": desc,
        },
        "author": {"@type": "Organization", "name": "The Apothecary"},
    }
    if ingredient.get("chemicalName"):
        substance_schema["about"]["alternateName"] = ingredient["chemicalName"]

    # FAQ schema for GEO
    faq_questions = [
        {
            "@type": "Question",
            "name": f"What is {name.lower()} used for in DIY products?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{desc} Categories: {', '.join(cat_labels)}. {ingredient.get('chemistry', '')}"
            }
        }
    ]
    if ingredient.get("warnings"):
        faq_questions.append({
            "@type": "Question",
            "name": f"Is {name.lower()} safe to use?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Safety considerations: {ingredient['warnings']} Always follow recommended concentrations and handling guidelines."
            }
        })
    if used_in:
        recipe_names = ", ".join(r["name"] for r in used_in[:5])
        faq_questions.append({
            "@type": "Question",
            "name": f"What DIY recipes use {name.lower()}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{name} is used in: {recipe_names}{'.' if len(used_in) <= 5 else f', and {len(used_in) - 5} more recipes.'}"
            }
        })

    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_questions}

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "The Apothecary", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Ingredients", "item": SITE_URL + "/#ingredients"},
            {"@type": "ListItem", "position": 3, "name": name, "item": canonical}
        ]
    }

    substance_json = json.dumps(substance_schema)
    faq_json = json.dumps(faq_schema)
    breadcrumb_json = json.dumps(breadcrumb_schema)

    # Product/Offer schemas for affiliate links
    offer_html_parts = []
    for link in (ingredient.get("affiliateLinks") or []):
        product_schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": link.get("productName", name),
            "description": desc,
            "url": link["url"],
            "category": (cat_labels[0] if cat_labels else "Bulk ingredient"),
            "offers": {
                "@type": "Offer",
                "url": link["url"],
                "priceCurrency": "USD",
                "price": (link.get("price", "").replace("~", "").replace("$", "").split("-")[0].strip() or "0"),
                "availability": "https://schema.org/InStock",
                "seller": {"@type": "Organization", "name": link.get("retailer", "Amazon").title()}
            }
        }
        offer_html_parts.append(f'<script type="application/ld+json">{json.dumps(product_schema)}</script>')
    offers_html = "".join(offer_html_parts)

    # SEO-optimized title
    seo_title_parts = [name]
    if ingredient.get("formula") and ingredient["formula"] != "N/A":
        seo_title_parts.append(f"({ingredient['formula']})")
    seo_title = f"{' '.join(seo_title_parts)} — Buy in Bulk, Uses, Chemistry — The Apothecary"
    seo_desc = f"{desc} {ingredient.get('costNote', '')}. Mechanism, safety data, DIY recipes."[:158]

    # GEO: Static summary
    recipe_list_text = ""
    if used_in:
        recipe_list_text = f'<p style="font-size:0.88em;color:#4a3f30;line-height:1.6;margin-bottom:8px"><strong>Used in:</strong> {", ".join(e(r["name"]) for r in used_in)}</p>'

    geo_summary = f"""
  <aside class="geo-summary" style="margin-top:32px;padding:20px;background:#f8f5ed;border-radius:10px;border:1px solid #e0d8c8">
    <h2 style="font-family:'DM Serif Display',serif;font-size:1.1em;margin-bottom:8px">Quick Summary</h2>
    <p style="font-size:0.88em;color:#4a3f30;line-height:1.6;margin-bottom:8px"><strong>{e(name)}</strong>{f' ({e(ingredient.get("formula", ""))})' if ingredient.get("formula") else ""}: {e(desc)}</p>
    {f'<p style="font-size:0.88em;color:#4a3f30;line-height:1.6;margin-bottom:8px"><strong>Mechanism:</strong> {e(ingredient.get("chemistry", ""))}</p>' if ingredient.get("chemistry") else ""}
    {f'<p style="font-size:0.88em;color:#4a3f30;line-height:1.6;margin-bottom:8px"><strong>Cost:</strong> {e(ingredient.get("costNote", ""))}</p>' if ingredient.get("costNote") else ""}
    {recipe_list_text}
    {f'<p style="font-size:0.88em;color:#6b4a3e;line-height:1.6"><strong>Safety:</strong> {e(ingredient.get("warnings", ""))}</p>' if ingredient.get("warnings") else ""}
  </aside>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON.format(canonical=canonical)}
<title>{e(seo_title)}</title>
<meta name="description" content="{e(seo_desc)}">
<meta property="og:title" content="{e(seo_title)}">
<meta property="og:description" content="{e(seo_desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="The Apothecary">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(seo_title)}">
<meta name="twitter:description" content="{e(seo_desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script type="application/ld+json">{substance_json}</script>
<script type="application/ld+json">{faq_json}</script>
<script type="application/ld+json">{breadcrumb_json}</script>
{offers_html}
{STYLES}
</head>
<body>
<div class="page-container">
  <nav class="top-nav" aria-label="Breadcrumb">
    <a href="../../">The Apothecary</a>
    <span class="nav-sep">/</span>
    <a href="../../#ingredients">Ingredients</a>
    <span class="nav-sep">/</span>
    <span class="nav-current">{e(name)}</span>
  </nav>

  <article>
  <h1 class="page-title">{e(name)}</h1>
  <p class="page-subtitle">{e(desc)}</p>

  <div class="badge-row">
    {cat_pills}
  </div>

  {cost_html}
  {meta_html}
  {chem_html}
  {warnings_html}

  <div class="md-body" id="md-content"></div>

  {geo_summary}
  </article>

  {used_html}
  {related_html}
</div>

<script>
document.getElementById("md-content").innerHTML = marked.parse({md_js});
</script>
</body>
</html>"""


# IndexNow key — random hex, also hosted at /{key}.txt for verification.
# This lets us notify Bing/Yandex of new URLs on every deploy.
INDEXNOW_KEY = "cba1e421f06894f7b383823881c9cae7"


def build_pin_svg(recipe):
    """Generate a 1000x1500 Pinterest-optimized SVG pin for a recipe."""
    name = recipe["name"]
    replaces = (recipe.get("replaces", "") or "").split("(")[0].strip() or "commercial products"
    cost = recipe.get("costPerUse", "").lstrip("~") or "—"
    eff = recipe.get("effectiveness", 0)
    cat_label = CATEGORY_LABELS.get(recipe.get("category", ""), "DIY").replace("&amp;", "&")

    # Wrap recipe name to fit (~14 chars per line at 84pt)
    words = name.split()
    lines = []
    cur = ""
    for w in words:
        candidate = (cur + " " + w).strip()
        if len(candidate) > 14 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = candidate
    if cur:
        lines.append(cur)
    lines = lines[:3]  # max 3 lines
    title_y_start = 580 - (len(lines) - 1) * 50
    title_lines = "\n  ".join(
        f'<text x="500" y="{title_y_start + i * 100}" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="84" fill="#2c2416" letter-spacing="-1">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1500" width="1000" height="1500">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f4ecd6"/>
      <stop offset="1" stop-color="#e8dfc6"/>
    </linearGradient>
    <linearGradient id="band" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#b8860b"/>
      <stop offset="1" stop-color="#dcc07a"/>
    </linearGradient>
  </defs>
  <rect width="1000" height="1500" fill="url(#bg)"/>
  <rect x="0" y="0" width="1000" height="14" fill="url(#band)"/>
  <rect x="0" y="1486" width="1000" height="14" fill="url(#band)"/>

  <!-- Top eyebrow -->
  <text x="500" y="220" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="32" font-weight="700" fill="#b8860b" letter-spacing="6">HOMEMADE · {html.escape(cat_label.upper())}</text>
  <line x1="380" y1="270" x2="620" y2="270" stroke="#b8860b" stroke-width="3"/>

  <!-- Recipe name -->
  {title_lines}

  <!-- Replaces -->
  <text x="500" y="780" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="34" font-weight="300" fill="#5a4f3e" font-style="italic">a science-backed replacement for</text>
  <text x="500" y="830" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="40" font-weight="600" fill="#2c2416">{html.escape(replaces)}</text>

  <!-- Stats panel -->
  <rect x="120" y="920" width="760" height="280" fill="#ffffff" stroke="#dcc07a" stroke-width="2" rx="20"/>
  <text x="320" y="1010" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="22" font-weight="700" fill="#7a6f5f" letter-spacing="3">COST PER USE</text>
  <text x="320" y="1100" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="92" fill="#b8860b">{html.escape(cost)}</text>
  <line x1="500" y1="980" x2="500" y2="1140" stroke="#e0d8c8" stroke-width="2"/>
  <text x="680" y="1010" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="22" font-weight="700" fill="#7a6f5f" letter-spacing="3">VS COMMERCIAL</text>
  <text x="680" y="1100" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="92" fill="#3a6b2a">{eff}/10</text>
  <text x="500" y="1170" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="20" fill="#7a6f5f" font-style="italic">honestly rated · real chemistry</text>

  <!-- Footer -->
  <text x="500" y="1320" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="56" fill="#2c2416">The Apothecary</text>
  <text x="500" y="1380" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="32" font-weight="700" fill="#b8860b" letter-spacing="6">THEAPOTHECARY.DIY</text>
  <text x="500" y="1430" text-anchor="middle" font-family="Source Sans 3, Helvetica, sans-serif" font-size="22" fill="#7a6f5f">Full recipe + ingredient sourcing</text>
</svg>
"""


def build_pin_gallery(recipes):
    """A simple HTML page listing every pin for easy bulk-download/pinning."""
    rows = []
    for r in recipes:
        slug = r["slug"]
        rows.append(f"""
    <li>
      <a href="{slug}.svg" target="_blank" download>
        <img src="{slug}.svg" alt="{e(r['name'])}" loading="lazy">
        <span class="pin-name">{e(r['name'])}</span>
        <span class="pin-meta">{slug}.svg</span>
      </a>
    </li>""")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Pinterest Pins — The Apothecary</title>
<style>
  body {{ font-family: system-ui, sans-serif; background: #f4f1eb; color: #2c2416; padding: 24px; max-width: 1280px; margin: 0 auto; }}
  h1 {{ font-family: 'DM Serif Display', Georgia, serif; font-weight: 400; }}
  p {{ color: #6b5d4d; margin-bottom: 24px; line-height: 1.5; }}
  ul {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; list-style: none; padding: 0; }}
  li a {{ display: block; background: #fff; border: 1px solid #e0d8c8; border-radius: 10px; padding: 10px; text-decoration: none; color: inherit; transition: border-color 0.15s, box-shadow 0.2s; }}
  li a:hover {{ border-color: #b8860b; box-shadow: 0 4px 16px rgba(184,134,11,0.15); }}
  img {{ width: 100%; height: auto; aspect-ratio: 2/3; object-fit: cover; border-radius: 6px; background: #eae5d6; }}
  .pin-name {{ display: block; font-weight: 700; margin-top: 8px; font-size: 0.92em; }}
  .pin-meta {{ display: block; font-size: 0.78em; color: #9a8e7a; font-family: ui-monospace, monospace; }}
</style>
</head>
<body>
<h1>Pinterest pins</h1>
<p>One 1000×1500 pin per recipe. Right-click → Save, or use Pinterest's bulk-pin tool. Each pin file is also reachable directly at <code>/pins/&lt;slug&gt;.svg</code>. This page is <code>noindex</code>.</p>
<ul>{"".join(rows)}
</ul>
</body>
</html>
"""


def build_sitemap(recipes, ingredients):
    """Generate sitemap.xml."""
    today = date.today().isoformat()
    urls = [f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>"""]

    for r in recipes:
        urls.append(f"""  <url>
    <loc>{SITE_URL}/recipes/{r['slug']}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")

    for ing in ingredients:
        urls.append(f"""  <url>
    <loc>{SITE_URL}/ingredients/{ing['slug']}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{chr(10).join(urls)}
</urlset>"""


def build_robots_txt():
    """Generate robots.txt."""
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""


def build_rss(recipes):
    """Generate an RSS 2.0 feed of all recipes, newest by mtime first.
    Helps with discoverability via feed readers and content syndication tools."""
    today = date.today()
    rfc822 = today.strftime("%a, %d %b %Y 00:00:00 +0000")

    # Sort by recipe slug for stable order; for "newest" semantics we'd need
    # a published-at field in the JSON. Until then, slug order is fine and
    # produces a deterministic feed.
    items = []
    for r in recipes:
        slug = r["slug"]
        url = f"{SITE_URL}/recipes/{slug}/"
        title = r["name"]
        desc = r.get("description", "")
        cat = CATEGORY_LABELS.get(r.get("category", ""), "DIY").replace("&amp;", "&")
        eff = r.get("effectiveness", 0)
        cost = r.get("costPerUse", "")
        full_desc = f"{desc} Effectiveness: {eff}/10 vs commercial. Cost: {cost}/use. Category: {cat}."
        items.append(f"""    <item>
      <title>{e(title)}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <description>{e(full_desc)}</description>
      <category>{e(cat)}</category>
      <pubDate>{rfc822}</pubDate>
    </item>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>The Apothecary</title>
    <link>{SITE_URL}/</link>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    <description>Science-backed DIY replacements for everyday commercial products. Real chemistry, honest effectiveness ratings, bulk ingredient sourcing.</description>
    <language>en-us</language>
    <lastBuildDate>{rfc822}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""


def build_llms_txt(recipes, ingredients):
    """Generate llms.txt dynamically from actual data."""
    # Group recipes by category
    by_cat = {}
    for r in recipes:
        cat = r.get("category", "other")
        by_cat.setdefault(cat, []).append(r)

    cat_lines = []
    for cat_id, cat_label in CATEGORY_LABELS.items():
        cat_recipes = by_cat.get(cat_id, [])
        if not cat_recipes:
            continue
        names = ", ".join(r["name"] for r in cat_recipes)
        # Unescape &amp; for plain text
        label = cat_label.replace("&amp;", "&")
        cat_lines.append(f"- **{label}:** {names}")

    # Top recipes by effectiveness
    top_recipes = sorted(recipes, key=lambda r: r.get("effectiveness", 0), reverse=True)[:8]
    example_lines = []
    for r in top_recipes:
        example_lines.append(
            f"- {r['name']} ({r.get('effectiveness', '?')}/10 vs commercial, {r.get('costPerUse', '?')}/use)"
        )

    # Top ingredients
    ingredient_names = []
    for ing in ingredients[:12]:
        formula = f" ({ing['formula']})" if ing.get("formula") else ""
        snippet = ing.get("description", "").split(".")[0]
        ingredient_names.append(f"- {ing['name']}{formula} — {snippet}")

    return f"""# The Apothecary

> Science-backed DIY replacements for everyday commercial products. Every recipe is grounded in real chemistry, cites actual mechanisms of action, and honestly rates its effectiveness against the commercial product it replaces.

## What This Site Offers

- {len(ingredients)} ingredient profiles with full chemistry, mechanisms of action, safety data, sourcing, and regulatory status
- {len(recipes)} DIY recipes spanning oral care, skin, hair, cleaning, laundry, kitchen, health, and garden
- Honest effectiveness scores (1-10 vs commercial) with transparent reasoning about where DIY falls short
- Structured JSON metadata for every ingredient and recipe

## Content Structure

### Recipe Pages
Each recipe at /recipes/{{slug}}/ includes:
- What commercial product it replaces and cost comparison
- Complete ingredient list with links to ingredient profiles
- Step-by-step method with chemistry explanations
- Effectiveness score vs commercial equivalent (1-10 with reasoning)
- Safety warnings and limitations
- Full markdown content with citations

### Ingredient Pages
Each ingredient at /ingredients/{{slug}}/ includes:
- Chemical properties (formula, CAS number, molecular weight, pH, solubility)
- Mechanism of action at the molecular level
- Safety data, warnings, and contraindications
- Cost and sourcing information
- Regulatory status (FDA, EU, TGA)
- Cross-references to recipes that use this ingredient

## Categories

{chr(10).join(cat_lines)}

## Key Principles

- Not "natural is always better" — some commercial products are genuinely superior, and this site says so
- Every claim links to a mechanism; if evidence is weak, that is stated explicitly
- Not a substitute for medical advice
- All effectiveness scores include transparent reasoning about limitations

## Useful URLs

- Homepage: {SITE_URL}/
- Sitemap: {SITE_URL}/sitemap.xml
- Recipe JSON data: {SITE_URL}/Recipes/json/{{slug}}.json
- Ingredient JSON data: {SITE_URL}/Ingredients/json/{{slug}}.json

## Top Recipes (by effectiveness)

{chr(10).join(example_lines)}

## Featured Ingredients

{chr(10).join(ingredient_names)}
"""


def build_index_html(source_html, recipes, ingredients):
    """Inject dynamic values into index.html — counts, URLs."""
    n_ing = len(ingredients)
    n_rec = len(recipes)

    # Group recipes by category for the noscript block
    by_cat = {}
    for r in recipes:
        cat = r.get("category", "other")
        by_cat.setdefault(cat, []).append(r)

    noscript_cats = []
    for cat_id, cat_label in CATEGORY_LABELS.items():
        cat_recipes = by_cat.get(cat_id, [])
        if not cat_recipes:
            continue
        label = cat_label.replace("&amp;", "&amp;")
        names = ", ".join(r["name"] for r in cat_recipes)
        noscript_cats.append(f"        <li><strong>{label}:</strong> {names}</li>")

    # Top ingredients for noscript
    top_ings = ingredients[:12]
    ing_desc = ", ".join(
        f'{ing["name"]}{" (" + ing["formula"] + ")" if ing.get("formula") else ""}'
        for ing in top_ings
    )

    noscript_block = f"""
    <section class="geo-static" style="max-width:780px;margin:40px auto;padding:0 20px">
      <h2>About The Apothecary</h2>
      <p>The Apothecary is a rigorous, science-based collection of {n_rec} DIY replacements for everyday commercial products, backed by {n_ing} detailed ingredient profiles. Most commercial products are combinations of 15-20 bulk ingredients repackaged with branding, fragrance, and markup. A $12 bottle of surface cleaner is vinegar and water. A $40 face cream is tallow and jojoba oil. A $25 tub of OxiClean is sodium percarbonate.</p>
      <p>This site documents the chemistry, provides tested recipes, and points you to the bulk ingredients. Every recipe includes an honest effectiveness score compared to the commercial product it replaces.</p>

      <h3>Recipe Categories</h3>
      <ul>
{chr(10).join(noscript_cats)}
      </ul>

      <h3>Key Ingredients</h3>
      <p>The ingredient database covers {n_ing} substances with full chemistry profiles: {ing_desc}, and more.</p>

      <h3>How It Works</h3>
      <p>Each recipe includes: what commercial product it replaces, cost per use comparison, step-by-step instructions, the chemistry behind why it works, an effectiveness score from 1-10 versus commercial, and honest limitations. Each ingredient includes: chemical properties, mechanism of action, safety data, regulatory status, and sourcing information.</p>
    </section>"""

    # Replace the static noscript content
    import re
    html = re.sub(
        r'<noscript>.*?</noscript>',
        f'<noscript>{noscript_block}\n  </noscript>',
        source_html,
        flags=re.DOTALL
    )

    # Replace hardcoded counts in meta description (any digits, future-proof)
    html = re.sub(
        r'\d+ ingredient profiles and \d+ recipes',
        f'{n_ing} ingredient profiles and {n_rec} recipes',
        html
    )
    html = re.sub(
        r'\d+ recipes across',
        f'{n_rec} recipes across',
        html
    )
    html = re.sub(
        r'\d+ DIY recipes',
        f'{n_rec} DIY recipes',
        html
    )

    # Auto-inject INGREDIENT_FILES and RECIPE_FILES arrays from actual disk state.
    # Without this, adding a new JSON file silently breaks the homepage until
    # the arrays are manually updated.
    ing_slugs = sorted(ing["slug"] for ing in ingredients)
    rec_slugs = sorted(r["slug"] for r in recipes)
    ing_array = ",\n  ".join(f'"{s}"' for s in ing_slugs)
    rec_array = ",\n  ".join(f'"{s}"' for s in rec_slugs)

    html = re.sub(
        r'const INGREDIENT_FILES = \[[^\]]*\];',
        f'const INGREDIENT_FILES = [\n  {ing_array}\n];',
        html
    )
    html = re.sub(
        r'const RECIPE_FILES = \[[^\]]*\];',
        f'const RECIPE_FILES = [\n  {rec_array}\n];',
        html
    )

    return html


def main():
    # Clean and create output directory
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    print("Loading data...")
    recipes = load_json_files("Recipes")
    ingredients_list = load_json_files("Ingredients")

    # Build lookup by id
    ingredients_db = {}
    for ing in ingredients_list:
        ingredients_db[ing["id"]] = ing

    print(f"  {len(recipes)} recipes, {len(ingredients_list)} ingredients")
    print(f"  Site URL: {SITE_URL}")

    # Copy source directories (MD + JSON needed by index.html at runtime)
    print("Copying source files to _site/...")
    for d in ["Ingredients", "Recipes"]:
        src = ROOT / d
        if src.exists():
            shutil.copytree(src, OUT / d)

    # Copy .nojekyll
    nojekyll = ROOT / ".nojekyll"
    if nojekyll.exists():
        shutil.copy2(nojekyll, OUT / ".nojekyll")

    # Emit CNAME so the custom domain is preserved across GitHub Pages deploys
    (OUT / "CNAME").write_text("www.theapothecary.diy\n", encoding="utf-8")

    # IndexNow verification key — a file at /<key>.txt containing the key.
    # Bing/Yandex fetch this when we POST to the IndexNow API to confirm we
    # own the domain.
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")

    # Copy static assets that live at the site root
    for asset in ["og-image.svg", "favicon.svg"]:
        src = ROOT / asset
        if src.exists():
            shutil.copy2(src, OUT / asset)

    # Process and write index.html (inject dynamic counts + noscript content)
    print("Building index.html...")
    source_html = (ROOT / "index.html").read_text(encoding="utf-8")
    index_html = build_index_html(source_html, recipes, ingredients_list)
    (OUT / "index.html").write_text(index_html, encoding="utf-8")

    # Generate recipe pages
    print("Generating recipe pages...")
    for recipe in recipes:
        slug = recipe["slug"]
        out_dir = OUT / "recipes" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        page_html = build_recipe_page(recipe, ingredients_db, recipes)
        (out_dir / "index.html").write_text(page_html, encoding="utf-8")
        print(f"  recipes/{slug}/index.html")

    # Generate ingredient pages
    print("Generating ingredient pages...")
    for ingredient in ingredients_list:
        slug = ingredient["slug"]
        out_dir = OUT / "ingredients" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        page_html = build_ingredient_page(ingredient, ingredients_db, recipes)
        (out_dir / "index.html").write_text(page_html, encoding="utf-8")
        print(f"  ingredients/{slug}/index.html")

    # Generate sitemap, robots.txt, llms.txt
    print("Generating sitemap.xml...")
    (OUT / "sitemap.xml").write_text(build_sitemap(recipes, ingredients_list), encoding="utf-8")

    print("Generating robots.txt...")
    (OUT / "robots.txt").write_text(build_robots_txt(), encoding="utf-8")

    print("Generating rss.xml...")
    (OUT / "rss.xml").write_text(build_rss(recipes), encoding="utf-8")

    print("Generating llms.txt...")
    (OUT / "llms.txt").write_text(build_llms_txt(recipes, ingredients_list), encoding="utf-8")

    # Pinterest pins — one SVG per recipe + a noindex gallery for bulk download
    print("Generating Pinterest pins...")
    pins_dir = OUT / "pins"
    pins_dir.mkdir(exist_ok=True)
    for recipe in recipes:
        (pins_dir / f"{recipe['slug']}.svg").write_text(build_pin_svg(recipe), encoding="utf-8")
    (pins_dir / "index.html").write_text(build_pin_gallery(recipes), encoding="utf-8")

    # urls.txt — flat list of every public URL, consumed by the IndexNow
    # workflow step to notify Bing/Yandex of new content on each deploy.
    all_urls = [f"{SITE_URL}/"]
    all_urls += [f"{SITE_URL}/recipes/{r['slug']}/" for r in recipes]
    all_urls += [f"{SITE_URL}/ingredients/{ing['slug']}/" for ing in ingredients_list]
    (OUT / "urls.txt").write_text("\n".join(all_urls) + "\n", encoding="utf-8")

    total = len(recipes) + len(ingredients_list)
    print(f"\nDone! Generated {total} pages + {len(recipes)} pins + sitemap/robots/llms in _site/")


if __name__ == "__main__":
    main()
