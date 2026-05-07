# AGENTS.md

This repository is a home-cooking knowledge base and journal, not a conventional
software codebase. Treat it as a durable notebook for pantry inventory, recipe
selection, weekly planning, shopping decisions, and cooking outcomes.

## Purpose

Use this repo to help the user:

- maintain pantry, fridge, and baking-crossover inventories,
- distinguish stock items from on-demand recipe purchases,
- identify interesting recipes that fit the current larder,
- create practical weekly cooking plans and shopping lists,
- record actual cooking outcomes,
- store concise research and adaptation notes,
- refine recipes over time through evidence from the kitchen.

## Core Principles

- Human kitchen experience is the primary evidence.
- The inventory is a planning baseline, not a constraint that forbids buying
  fresh ingredients.
- Stable recipes, candidate ideas, shopping lists, and cook logs should not be
  mixed together.
- Record what happened before proposing what should change.
- Be explicit about uncertainty. Do not invent quantities, outcomes, or
  availability.
- Keep notes concise, practical, and useful in a home kitchen.
- Prefer interesting, flavourful, pantry-aware cooking over generic recipe
  accumulation.
- Treat baking crossover as important context, but keep detailed bread work in
  `/Users/bwbrook/git/baking` unless the user explicitly wants it here.

## Repository Expectations

- `inventory/` stores current durable ingredients, fridge staples, baking
  crossover, wishlists, and on-demand purchase conventions.
- `recipes/` stores working recipes, stable recipes, weekly candidates, and
  drafting templates.
- `recipes/ingest.md` is the temporary intake file for raw recipe notes,
  conversation dumps, and partial ideas.
- `cook_logs/` stores dated records of individual cooking sessions.
- `plans/` stores weekly cooking plans.
- `shopping/` stores working shopping lists derived from plans.
- `research/` stores sourced notes, orientation notes, and adaptation rationale.
- `techniques/` stores general method and planning notes that are not tied to
  one recipe.
- `input/` stores raw provenance files. Promote useful material out of it, but
  do not overwrite provenance files unless the user asks.

## Ingredient Model

Track ingredients in three layers:

- **Stock items**: durable pantry, fridge, freezer, and baking-crossover
  ingredients that are normally available.
- **On-demand perishables**: fresh herbs, vegetables, meat, fresh fish, and
  other short-life ingredients bought for a selected week.
- **Recipe-specific non-perishables**: specialty pantry items bought for one
  recipe or cuisine experiment. Promote them to stock only after repeated use
  or explicit user direction.

When proposing recipes, state which ingredients are already stock and which
need to be bought.

## Content Rules

- Prefer metric weights in grams and liquid measures in millilitres where
  precision matters.
- Preserve the difference between recipe, candidate, weekly plan, shopping
  list, cook log, research note, and technique note.
- If the user reports a meal verbally, convert it into a dated cook log before
  revising the recipe.
- When a recipe is updated after cooking, note what changed and why.
- When web research is done, store the date, question, short synthesis, and
  links to the sources used.
- When adapting historical or traditional recipes, separate original context
  from modern pantry and equipment choices.
- When `recipes/ingest.md` contains raw notes, process them into the proper
  destination files and then reset the intake file for reuse.
- Do not treat ordinary weekly perishables as stock inventory unless the user
  says they are normally kept on hand.

## Current Household Defaults

- Fresh herbs, fresh vegetables, meat, and most fresh seafood are on-demand
  weekly purchases, not stock.
- Greek yogurt is a normal staple.
- Free-range eggs are a normal stock strength because the user has active
  laying hens.
- Olive oil is the default cooking fat unless butter, sesame oil, or another
  fat is clearly better.
- Use gas stovetop cooking thoughtfully: avoid long continuous gas simmering
  and never assume unattended open-flame cooking.
- Avoid Teflon/nonstick-coated cookware because cockatiels are in the house;
  prefer stainless steel, cast iron, glass, oven, slow cooker, microwave, air
  fryer, or rice cooker methods.
- Default weekly planning shape is two mains plus support components for one
  person, with planned leftovers.
- The strongest current pantry axes are pulses/grains, canned fish, Japanese
  umami, Eastern Mediterranean/Middle Eastern, North African, Indian-adjacent,
  and historical-modern grain cookery.
- The companion baking repo remains the source of truth for detailed flour,
  bread, and bake-log work.

## Inventory Guidance

- Keep durable pantry inventory specific and up to date.
- Distinguish confirmed stock from uncertain stock with a note rather than
  silently resolving uncertainty.
- Update inventory files whenever the user mentions new pantry items, fridge
  staples, wishlist items, or tools.
- Keep raw input files as provenance when they seeded a baseline.

## Editing Style

- Keep markdown clean and easy to scan.
- Favor short sections, tables where useful, and direct practical language.
- Do not invent cooking outcomes, timings, or recipe performance.
- If a recommendation depends on assumptions, state them.
