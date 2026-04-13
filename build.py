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
SITE_URL = "https://ncwardell.github.io/LifeApothecary"

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
<title>{e(name)} — The Apothecary</title>
<meta name="description" content="{e(desc)} Effectiveness: {effectiveness}/10 vs commercial. Cost: {e(recipe.get('costPerUse', 'varies'))}/use.">
<meta property="og:title" content="{e(name)} — The Apothecary">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="The Apothecary">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{e(name)} — The Apothecary">
<meta name="twitter:description" content="{e(desc)} {effectiveness}/10 vs commercial.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script type="application/ld+json">{schemas_json}</script>
<script type="application/ld+json">{faq_json}</script>
<script type="application/ld+json">{breadcrumb_json}</script>
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

    # Cost
    cost_html = ""
    if ingredient.get("costNote"):
        cost_html = f"""
        <div class="meta-item" style="display:inline-block;margin-bottom:20px">
          <div class="meta-label">Typical Cost</div>
          <div class="meta-value">{e(ingredient["costNote"])}</div>
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
<title>{e(name)} — DIY Ingredient Profile — The Apothecary</title>
<meta name="description" content="{e(name)}: {e(desc)} Chemical properties, safety data, DIY uses, and sourcing information.">
<meta property="og:title" content="{e(name)} — The Apothecary">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="The Apothecary">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{e(name)} — The Apothecary">
<meta name="twitter:description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script type="application/ld+json">{substance_json}</script>
<script type="application/ld+json">{faq_json}</script>
<script type="application/ld+json">{breadcrumb_json}</script>
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

  {meta_html}
  {chem_html}
  {warnings_html}
  {cost_html}

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


def main():
    # Clean and create output directory
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    print("Copying source files to _site/...")
    # Copy static files
    for f in ["index.html", ".nojekyll", "robots.txt", "llms.txt"]:
        src = ROOT / f
        if src.exists():
            shutil.copy2(src, OUT / f)

    # Copy Ingredients and Recipes directories (MD + JSON needed by index.html at runtime)
    for d in ["Ingredients", "Recipes"]:
        src = ROOT / d
        if src.exists():
            shutil.copytree(src, OUT / d)

    print("Loading data...")
    recipes = load_json_files("Recipes")
    ingredients_list = load_json_files("Ingredients")

    # Build lookup by id
    ingredients_db = {}
    for ing in ingredients_list:
        ingredients_db[ing["id"]] = ing

    print(f"  {len(recipes)} recipes, {len(ingredients_list)} ingredients")

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

    # Generate sitemap
    print("Generating sitemap.xml...")
    sitemap = build_sitemap(recipes, ingredients_list)
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    total = len(recipes) + len(ingredients_list)
    print(f"\nDone! Generated {total} pages + sitemap.xml in _site/")


if __name__ == "__main__":
    main()
