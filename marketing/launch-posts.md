# Launch posts — pre-drafted

Copy/paste templates for seeding the site in different communities. **Don't fire them all on the same day.** Rule of thumb: one post per week, different community, different framing. Read each subreddit's rules before posting; some require flair or a "self-promo" tag.

---

## Reddit — r/ZeroWaste

**Title:** I built a free, ad-free site with science-backed DIY replacements for everyday products — honest 1–10 effectiveness ratings vs commercial

**Body:**

Hey r/ZeroWaste — I got tired of "natural is always better" DIY blogs that hand-wave the chemistry, so I built [theapothecary.diy](https://www.theapothecary.diy) as a counter to that. It's a static site, no ads, no email gate.

Every recipe has:

- An honest 1–10 effectiveness score vs the commercial product it replaces (some DIY versions are genuinely worse — the site says so)
- The actual chemistry / mechanism, not "X cleans"
- Cost per use vs the commercial alternative
- Bulk ingredient sourcing

A few examples of where DIY actually wins:
- Sodium percarbonate ≈ OxiClean main ingredient, ~1/4 the price
- Tallow + jojoba moisturizer → ~$4 worth of ingredients makes ~$40 of "luxury" face cream
- White vinegar + water surface cleaner ≈ as good as most $12 sprays

And where it doesn't:
- DIY toothpaste lacks fluoride — flagged as a -2 if you're cavity-prone
- DIY deodorant is hit-or-miss for heavy sweating
- Commercial laundry detergent for hard water often still wins

I'm the sole author. Affiliate links exist on ingredient pages but the site works fine without clicking any. Suggestions / corrections welcome.

---

## Reddit — r/Frugal

**Title:** Free site I built: most $12–40 personal care products are 15 cents of bulk ingredients with markup — recipes + chemistry

**Body:**

Built [theapothecary.diy](https://www.theapothecary.diy) after one too many "$40 face cream is $4 of jojoba and tallow" realizations. It's a public, ad-free recipe + ingredient database — every recipe shows what commercial product it replaces and the cost-per-use comparison.

Some highlights for r/Frugal:

- $25 OxiClean tub ≈ pure sodium percarbonate (~$10/lb in bulk, lasts 6+ months)
- $4–8 toothpaste tube → ~$0.03 per brush with bentonite + coconut oil
- $12 surface cleaner → ~$0.05 per spray with white vinegar + water
- $40 face cream → ~$0.40 per use whipped tallow balm

Every recipe has an honest 1–10 effectiveness score vs commercial; a few DIY versions are genuinely worse and the site says so out loud (e.g., DIY laundry on hard water).

No newsletter. No paywall. Affiliate links on ingredient pages but they're optional — you can take any recipe to a local bulk store and ignore me entirely.

---

## Reddit — r/Cleaningtips

**Title:** I made a free database of cleaning recipes with the actual chemistry and an honest effectiveness rating vs commercial — sharing in case it's useful

**Body:**

Hey r/Cleaningtips — sharing [theapothecary.diy](https://www.theapothecary.diy) in case it's useful. It's a free site (no ads) with a bunch of cleaning recipes, each one rated honestly 1–10 vs the commercial product it replaces.

The thing I wanted that didn't exist anywhere: every recipe explains *why* it works at a chemistry level, not just "vinegar cleans." Acetic acid in vinegar (5%) protonates lime/scale to a soluble salt — that's why it works on hard water but not on grease. Hydrogen peroxide (3%) breaks down to water + free oxygen radical, which is why it whitens but degrades fast in light. Etc.

Some recipes are honestly equal to commercial (all-purpose vinegar spray, sodium percarbonate as oxygen bleach), others are genuinely worse (DIY laundry struggles in hard water — site flags it).

I'm the only author. If anything's wrong or missing a citation, let me know.

---

## Hacker News — Show HN

**Title:** Show HN: theapothecary.diy – Science-backed DIY replacements with honest effectiveness ratings

**Body:**

I built this after noticing that the DIY/zero-waste blogosphere has a credibility problem: every recipe is presented as obviously superior to the commercial version, the chemistry is hand-wavy, and there's no acknowledgment that some commercial products are genuinely better.

So I made the opposite. Every recipe at theapothecary.diy includes:

- A 1–10 effectiveness score vs the specific commercial product it replaces, with explicit reasoning for the score
- The chemical mechanism (specific reactions, not "it works")
- Cost-per-use comparison
- Cases where DIY is worse, called out in the warnings

The ingredient database has 35 entries with full chemistry profiles (formula, CAS, mechanism of action, regulatory status). 27 recipes covering oral care, skin, hair, cleaning, laundry, kitchen, health, and garden.

Static site, no JS framework, no ads, no analytics. Source is on GitHub, deploys via GitHub Actions.

Tech stack worth mentioning: TS-typed schema as the single source of truth, JSON+Markdown content files, Python build script that emits HTML + JSON-LD (HowTo, FAQPage, Product+Offer schemas) + an llms.txt for AI search engines. The schema doubles as documentation for an LLM-driven content authoring flow — I'm using a Claude Code skill that reads the schema, researches a new ingredient, and emits validated JSON+MD.

Affiliate links exist on ingredient pages (Amazon Associates) — disclosed and easy to ignore.

---

## Lobsters

**Title:** Show: A static-site DIY recipe database with honest effectiveness ratings and an LLM-driven content authoring pipeline

**Body:**

Live: theapothecary.diy
Source: github.com/ncwardell/TheApothecary

What it is: a small public-domain knowledge base of DIY replacements for commercial products, with honest 1–10 effectiveness ratings vs the commercial version (something missing from most DIY blogs — they all assume DIY wins).

What's interesting technically:

- TypeScript-typed canonical schema (`scripts/schema.ts`) is the single source of truth for both validation and LLM scaffolding.
- Static-site build is plain Python — emits 60+ pages, JSON-LD (HowTo, FAQPage, Product+Offer), llms.txt, sitemap, IndexNow notification.
- Pinterest pin SVGs auto-generated per recipe at build time.
- Two Claude Code skills (`/add-ingredient`, `/add-recipe`) drive a research-and-author flow; the LLM reads `schema.ts` as the spec, web-researches the topic, drafts validated JSON + a fully-written markdown body, and pauses for hybrid affiliate-link entry.
- CI validates schema + cross-references before deploy; bad data can't ship.

Tagged: practices, web

---

## Pinterest description (per pin)

Use this template per recipe pin (replace `{NAME}` and `{REPLACES}`):

> Homemade {NAME} — a science-backed replacement for {REPLACES}. Real chemistry, honest effectiveness rating vs commercial, bulk ingredient sourcing. Free recipe at theapothecary.diy.

Hashtags (rotate 3–5 per pin):
`#diy #zerowaste #homemade #naturalliving #frugalliving #sustainableliving #cleanliving #diyhomemade #naturalskincare #greenclean #ecofriendly`

---

## When to post

- Reddit posts: spread out one per week, different sub. **Read each sub's rules first** — many require user flair, posting cadence, or a `[Self-Promo]` tag.
- Show HN: Tuesday or Wednesday morning ET (8–10 am). Post once. Don't repost if it dies. Don't ask for upvotes anywhere.
- Lobsters: needs an invite — only post if you have one.
- Pinterest: bulk pin once on launch (use the gallery at /pins/), then one new pin per new recipe.

## What to avoid

- Posting in 5+ subreddits the same day → shadowban.
- Asking for upvotes anywhere.
- Editing the post to add "EDIT: thanks for the gold!!!" type fluff.
- Buying any kind of "boost."
