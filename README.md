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

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest test_pawpal.py -v
```

The tests are split into three groups:

**Sorting correctness** — checks that tasks come back in chronological order regardless of the order they were added, that tasks with no start time fall to the end of the list, and that the scheduler respects priority and overdue status when times are equal.

**Recurrence logic** — verifies that marking a daily task complete returns a new task due tomorrow, that a weekly task returns one due exactly seven days later, and that one-time tasks return `None` (no follow-up). Also confirms that the spawned task inherits category, duration, and priority correctly and gets a fresh UUID.

**Conflict detection** — makes sure the scheduler catches exact same-time clashes and overlapping windows, ignores tasks with no assigned time (instead of crashing), handles empty schedules gracefully, and correctly distinguishes between a same-pet conflict and a cross-pet conflict in the warning messages.

**Confidence level: 4 / 5 stars**

The core scheduling behaviors — sorting, recurrence, and conflict detection — are well covered and all 22 tests pass. I knocked off one star because the tests don't yet cover the Streamlit UI layer (session state, button interactions) and don't test multi-week recurring tasks over a longer time horizon. Those edge cases exist, they just aren't exercised yet.

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
