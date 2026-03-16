# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

The scheduler has grown past a basic to-do list. Here's what it can do now:

**Recurring tasks** — when you call `task.mark_complete()`, it automatically returns a new copy of the task due the next day (for daily tasks) or the same weekday next week (for weekly tasks). You can pass that straight to `pet.add_task()` so the task reappears without any extra effort. One-time tasks just return `None`, so the pattern is the same either way.

**Energy-aware ordering** — the scheduler looks at a pet's `energy_level` before deciding what order to place tasks. A high-energy dog gets walks and play scheduled first thing in the morning. A low-energy or recovering cat gets gentler tasks (feeding, grooming) up front, with anything physically demanding pushed later.

**Time windows** — you can pass a `Constraints` object with `available_hours` to tell the scheduler when the owner is actually around. Tasks that would run past the end of the window are skipped rather than crammed in.

**Conflict detection** — there are two layers. `detect_conflicts(schedule)` checks a single pet's plan for tasks that overlap in duration. `conflict_warnings(plans, owner)` checks across all pets at once, which matters because an owner can't walk the dog and clean the litter box at the same time even if those are two separate schedules. Both methods return warning messages instead of crashing, so you can handle them however makes sense for your UI.

**Per-pet schedules** — `generate_all_pets_plans()` produces an independent schedule for each pet rather than one big combined list. That makes it easier to display, filter, and check for conflicts per animal.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
