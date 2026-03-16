from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler, Constraints


def print_tasks(label: str, tasks: list) -> None:
    print(f"\n{label}")
    print("-" * len(label))
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        time_str = t.start_time.strftime("%H:%M") if t.start_time else "--:--"
        status = "[x]" if t.completed else "[ ]"
        print(f"  {status} [{time_str}] {t.description} (priority={t.priority}, freq={t.frequency})")


def main():
    owner = Owner(name="Jordan", location="Home")

    dog = Pet(name="Mochi", breed="Shiba Inu", weight=14.5, energy_level=0.8)
    cat = Pet(name="Nala", breed="Siamese", weight=8.2, energy_level=0.3)
    owner.add_pet(dog)
    owner.add_pet(cat)

    today = date.today()

    # Tasks added intentionally out of priority/time order to exercise sorting
    dog.add_task(Task(description="Evening walk",   category="walk",     duration=timedelta(minutes=20), priority=2, frequency="daily",  due_date=today))
    dog.add_task(Task(description="Feed breakfast", category="feed",     duration=timedelta(minutes=10), priority=3, frequency="daily",  due_date=today))
    dog.add_task(Task(description="Brush teeth",    category="groom",    duration=timedelta(minutes=5),  priority=1, frequency="weekly", due_date=today))
    dog.add_task(Task(description="Morning walk",   category="walk",     duration=timedelta(minutes=30), priority=3, frequency="daily",  due_date=today))

    cat.add_task(Task(description="Feed breakfast", category="feed",     duration=timedelta(minutes=10), priority=3, frequency="daily",  due_date=today))
    cat.add_task(Task(description="Vet medication", category="medication",duration=timedelta(minutes=5),  priority=2, frequency="once",   due_date=today))
    cat.add_task(Task(description="Litter box",     category="hygiene",  duration=timedelta(minutes=10), priority=3, frequency="daily",  due_date=today))

    # ── 1. Generate per-pet schedules ───────────────────────────────────────
    scheduler = Scheduler()
    constraints = Constraints(
        available_hours={"start": time(8, 0), "end": time(20, 0)},
    )
    plans = scheduler.generate_all_pets_plans(owner, today, constraints)

    # Sort by start_time using a lambda on "HH:MM" strings
    for pet in owner.pets:
        sorted_by_time = sorted(
            plans[pet.id].get_tasks(),
            key=lambda t: t.start_time.strftime("%H:%M") if t.start_time else "99:99"
        )
        print_tasks(f"{pet.name}'s schedule (sorted by time)", sorted_by_time)

    # ── 2. Filter by completion status and pet name ─────────────────────────
    pending   = scheduler.filter_tasks(owner.get_tasks_for_pet("Mochi"), status="pending")
    completed = scheduler.filter_tasks(owner.get_tasks_for_pet("Mochi"), status="completed")
    print_tasks("Mochi - pending tasks",   pending)
    print_tasks("Mochi - completed tasks", completed)
    print_tasks("All of Nala's tasks",     owner.get_tasks_for_pet("Nala"))

    # ── 3. mark_complete auto-spawns next occurrence ────────────────────────
    print("\nRecurring task auto-spawn")
    print("-------------------------")
    walk = dog.tasks[3]  # Morning walk (daily)
    next_task = walk.mark_complete()
    if next_task:
        dog.add_task(next_task)
        print(f"  Completed: '{walk.description}' (due {walk.due_date})")
        print(f"  Spawned:   '{next_task.description}' (due {next_task.due_date})")
    else:
        print(f"  '{walk.description}' marked complete — no recurrence")

    groom = dog.tasks[2]  # Brush teeth (weekly)
    next_groom = groom.mark_complete()
    if next_groom:
        dog.add_task(next_groom)
        print(f"  Completed: '{groom.description}' (due {groom.due_date})")
        print(f"  Spawned:   '{next_groom.description}' (due {next_groom.due_date})")

    vet = cat.tasks[1]  # Vet medication (once)
    next_vet = vet.mark_complete()
    print(f"  Completed: '{vet.description}' (once) -> next_occurrence returned: {next_vet}")

    # ── 4. Cross-pet conflict detection ─────────────────────────────────────
    # Both pets have tasks starting at 08:00 — the owner can't do both at once.
    # Rebuild plans so we can check cross-pet overlaps.
    plans = scheduler.generate_all_pets_plans(owner, today, constraints)
    warnings = scheduler.conflict_warnings(plans, owner)

    print("\nCross-pet conflict check")
    print("------------------------")
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  No conflicts found.")

    # ── 5. Force a same-pet conflict to verify detection ───────────────────
    # Manually set two of Mochi's tasks to the same start time.
    dog_tasks = plans[dog.id].get_tasks()
    if len(dog_tasks) >= 2:
        dog_tasks[0].start_time = time(9, 0)
        dog_tasks[1].start_time = time(9, 0)   # deliberate clash

    same_pet_conflicts = scheduler.detect_conflicts(plans[dog.id])
    print("\nForced same-pet conflict check (Mochi)")
    print("---------------------------------------")
    if same_pet_conflicts:
        for a, b in same_pet_conflicts:
            print(f"  WARNING: '{a.description}' and '{b.description}' both start at 09:00")
    else:
        print("  No conflicts found.")


if __name__ == "__main__":
    main()
