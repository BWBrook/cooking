# Cooking Notebook

> **Status:** developed in the open as a working record. This is work in progress: contents may change, and nothing here is peer-reviewed unless stated.

This repository is a versioned home-cooking notebook for pantry inventory,
recipe discovery, weekly cooking plans, shopping decisions, and kitchen
outcomes.

The repo is not primarily a software project. It is a practical working system
for:

- tracking durable pantry, fridge, and baking-crossover ingredients,
- turning pantry strengths into interesting recipes,
- separating stock ingredients from on-demand weekly purchases,
- recording what was actually cooked and how it worked,
- keeping concise research and adaptation notes,
- building a stable set of house recipes over time.

## Working Model

This repo assumes a simple division of labor:

- the human cook supplies preferences, constraints, observations, and final
  judgement,
- Codex helps structure inventories, propose recipe directions, build shopping
  lists, and convert rough notes into durable files,
- the repository serves as the memory between cooking weeks.

The pantry is the starting point, not the whole meal. Fresh meats, herbs,
vegetables, and other short-life ingredients are usually bought on demand for
the recipes chosen that week.

## Ingredient Model

Ingredients are tracked in three practical layers:

- **Stock items**: durable pantry, fridge, freezer, and baking-crossover items
  that are normally kept around.
- **On-demand perishables**: fresh herbs, vegetables, meats, fish, dairy, and
  similar ingredients bought for a particular week.
- **Recipe-specific non-perishables**: specialty pantry goods bought for one
  recipe or cuisine experiment, and only promoted to stock if they prove useful
  repeatedly.

## Repository Layout

- `inventory/`
  Current pantry, fridge, baking-crossover, wishlist, and on-demand ingredient
  records.
- `recipes/`
  Stable recipes, trial recipes, weekly candidates, and reusable templates.
- `cook_logs/`
  Dated records of actual cooking sessions and human judgement.
- `plans/`
  Weekly cooking plans that connect recipes to timing and shopping needs.
- `shopping/`
  Working shopping lists derived from weekly plans.
- `research/`
  Concise research, orientation, and adaptation notes.
- `techniques/`
  Reusable method and planning notes not tied to one recipe.
- `input/`
  Raw intake and provenance files that still need, or have recently undergone,
  promotion into durable repo structure.

## Current Direction

The starting pantry is strongest around:

- pulses, grains, oats, rice, and barley,
- canned fish and shelf-stable savoury proteins,
- Japanese and East Asian umami condiments,
- Eastern Mediterranean and Middle Eastern flavours,
- North African tomato-legume-fruit stews,
- Indian-adjacent dal and pulse cookery,
- historical-modern grain and pulse cooking,
- baking crossover from the companion baking notebook.

## Typical Workflow

1. Update `inventory/` when ingredients arrive or run out.
2. Capture rough ideas in `recipes/ingest.md`.
3. Promote promising ideas to `recipes/weekly-candidates/` or a proper recipe
   file.
4. Build a weekly plan in `plans/`.
5. Create a segmented shopping list in `shopping/`.
6. Cook, then record the result in `cook_logs/`.
7. Update the recipe only after the log captures what actually happened.

## Kindle and EPUB

Recipes and research notes can be built as Kindle-friendly `EPUB` files.

Useful commands:

```bash
make kindle-list
make epub FILE=recipes/historical/medieval-pease-pottage-slow-cooker.md
make epub FILE=recipes/historical/medieval-pease-pottage-slow-cooker.md INCLUDE_RESEARCH=1
make kindle-init-config
make kindle-preflight FILE=recipes/historical/medieval-pease-pottage-slow-cooker.md
make kindle FILE=recipes/historical/medieval-pease-pottage-slow-cooker.md
```

Generated files land under `build/kindle/` and are not tracked in git. Kindle
delivery uses a local-only config at `.cooking.local.yml`, seeded from the
existing creative-writer Kindle config when available. SMTP passwords are read
from the environment or macOS Keychain; they are not stored in this repo.

## Related Repository

The companion baking notebook lives at `/Users/bwbrook/git/baking`. Its flour,
baking support, and equipment inventories are summarized here only where they
matter for general cooking.

## Licence

Code is released under the [MIT Licence](LICENSE). Text, figures and data created for this project are released under [CC BY-SA 4.0](LICENSE-CONTENT). Third-party material keeps its own terms where stated.
