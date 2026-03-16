"""Tests for PawPal+ scheduling logic.

Covers three areas:
  - Sorting correctness: tasks come back in chronological order by start_time
  - Recurrence logic: mark_complete() spawns the right next-occurrence task
  - Conflict detection: the scheduler catches duplicate and overlapping times
"""

import pytest
from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Task, Schedule, Scheduler, Constraints


# ── helpers ─────────────────────────────────────────────────────────────────

def make_task(description, start_time=None, duration_min=30, priority=1,
              frequency=None, due_date=None, category=""):
    t = Task(
        description=description,
        start_time=start_time,
        duration=timedelta(minutes=duration_min),
        priority=priority,
        frequency=frequency,
        due_date=due_date or date.today(),
        category=category,
    )
    return t


def make_schedule_with_tasks(*tasks):
    """Create a Schedule and add the given tasks directly (bypassing the scheduler)."""
    s = Schedule(date=date.today())
    for t in tasks:
        s.add_task(t)
    return s


# ── sorting correctness ──────────────────────────────────────────────────────

class TestSortingCorrectness:

    def test_tasks_sorted_chronologically(self):
        """Tasks added out of order should come back sorted earliest to latest."""
        scheduler = Scheduler()
        t1 = make_task("Evening feed",    start_time=time(18, 0))
        t2 = make_task("Morning walk",    start_time=time(8, 0))
        t3 = make_task("Afternoon groom", start_time=time(14, 0))

        # Sort by HH:MM string the same way main.py does
        result = sorted(
            [t1, t2, t3],
            key=lambda t: t.start_time.strftime("%H:%M") if t.start_time else "99:99"
        )

        assert [r.description for r in result] == [
            "Morning walk", "Afternoon groom", "Evening feed"
        ]

    def test_tasks_without_start_time_go_last(self):
        """A task with no start_time should sort after all timed tasks."""
        t_timed   = make_task("Morning walk", start_time=time(8, 0))
        t_untimed = make_task("Brushing",     start_time=None)

        result = sorted(
            [t_untimed, t_timed],
            key=lambda t: t.start_time.strftime("%H:%M") if t.start_time else "99:99"
        )

        assert result[0].description == "Morning walk"
        assert result[1].description == "Brushing"

    def test_empty_task_list_returns_empty(self):
        """Sorting an empty list should not crash and should return an empty list."""
        result = sorted([], key=lambda t: t.start_time.strftime("%H:%M") if t.start_time else "99:99")
        assert result == []

    def test_scheduler_sort_tasks_respects_priority_when_times_equal(self):
        """When two tasks have the same due date, higher priority comes first."""
        scheduler = Scheduler()
        low  = make_task("Low priority",  priority=1, frequency="daily")
        high = make_task("High priority", priority=3, frequency="daily")

        result = scheduler.sort_tasks([low, high])

        assert result[0].description == "High priority"

    def test_scheduler_places_overdue_task_before_due_today(self):
        """An overdue task should sort before a task that is simply due today."""
        scheduler = Scheduler()
        today     = date.today()
        yesterday = today - timedelta(days=1)

        overdue   = make_task("Overdue medication", due_date=yesterday, frequency="once")
        due_today = make_task("Today's walk",       due_date=today,     frequency="once")

        result = scheduler.sort_tasks([due_today, overdue])

        assert result[0].description == "Overdue medication"

    def test_generate_all_pets_plans_assigns_sequential_start_times(self):
        """Tasks in a generated schedule should have start_times that do not overlap."""
        owner = Owner(name="Jordan")
        pet   = Pet(name="Mochi", energy_level=0.5)
        owner.add_pet(pet)

        pet.add_task(make_task("Walk",  duration_min=30, priority=3, frequency="daily"))
        pet.add_task(make_task("Feed",  duration_min=10, priority=2, frequency="daily"))
        pet.add_task(make_task("Brush", duration_min=15, priority=1, frequency="daily"))

        scheduler = Scheduler()
        constraints = Constraints(available_hours={"start": time(8, 0), "end": time(20, 0)})
        plans = scheduler.generate_all_pets_plans(owner, date.today(), constraints)

        tasks = plans[pet.id].get_tasks()
        assert len(tasks) == 3

        times = [t.start_time for t in tasks if t.start_time]
        assert len(times) == 3
        # Each start_time should be strictly later than the previous one
        for i in range(1, len(times)):
            assert times[i] > times[i - 1]


# ── recurrence logic ─────────────────────────────────────────────────────────

class TestRecurrenceLogic:

    def test_daily_task_spawns_next_day(self):
        """Completing a daily task should return a new task due tomorrow."""
        today    = date.today()
        tomorrow = today + timedelta(days=1)
        task = make_task("Morning walk", frequency="daily", due_date=today)

        next_task = task.mark_complete()

        assert task.completed is True
        assert next_task is not None
        assert next_task.due_date == tomorrow
        assert next_task.description == "Morning walk"
        assert next_task.completed is False

    def test_weekly_task_spawns_seven_days_later(self):
        """Completing a weekly task should return a new task due exactly one week later."""
        today       = date.today()
        next_week   = today + timedelta(weeks=1)
        task = make_task("Grooming", frequency="weekly", due_date=today)

        next_task = task.mark_complete()

        assert next_task is not None
        assert next_task.due_date == next_week

    def test_once_task_returns_none(self):
        """A one-time task should return None from mark_complete — no follow-up needed."""
        task = make_task("Vet appointment", frequency="once", due_date=date.today())

        next_task = task.mark_complete()

        assert task.completed is True
        assert next_task is None

    def test_task_with_no_frequency_returns_none(self):
        """A task with frequency=None should also return None from mark_complete."""
        task = make_task("One-off errand", frequency=None, due_date=date.today())

        next_task = task.mark_complete()

        assert next_task is None

    def test_next_occurrence_inherits_category_and_duration(self):
        """The spawned task should carry over category, duration, and priority."""
        task = make_task("Feed breakfast", frequency="daily", duration_min=10,
                         priority=3, category="feed", due_date=date.today())

        next_task = task.next_occurrence()

        assert next_task.category == "feed"
        assert next_task.duration == timedelta(minutes=10)
        assert next_task.priority == 3

    def test_next_occurrence_has_new_uuid(self):
        """Each spawned task should be a genuinely new object, not the same one."""
        task = make_task("Daily walk", frequency="daily", due_date=date.today())

        next_task = task.next_occurrence()

        assert next_task.id != task.id

    def test_daily_task_without_due_date_uses_today_as_base(self):
        """A daily task with no due_date should treat today as the base for the next occurrence."""
        today    = date.today()
        tomorrow = today + timedelta(days=1)
        task = Task(description="No-date daily", frequency="daily", duration=timedelta(minutes=5))

        next_task = task.next_occurrence()

        assert next_task.due_date == tomorrow

    def test_pet_with_no_tasks_generates_empty_schedule(self):
        """A pet that has no tasks assigned should produce an empty schedule without crashing."""
        owner = Owner(name="Jordan")
        pet   = Pet(name="Ghost")
        owner.add_pet(pet)

        scheduler = Scheduler()
        plans = scheduler.generate_all_pets_plans(owner, date.today())

        assert len(plans[pet.id].get_tasks()) == 0


# ── conflict detection ────────────────────────────────────────────────────────

class TestConflictDetection:

    def test_no_conflict_for_sequential_tasks(self):
        """Tasks that run back-to-back (not overlapping) should not be flagged."""
        scheduler = Scheduler()
        t1 = make_task("Walk",  start_time=time(8, 0),  duration_min=30)
        t2 = make_task("Feed",  start_time=time(8, 30), duration_min=10)
        schedule = make_schedule_with_tasks(t1, t2)

        conflicts = scheduler.detect_conflicts(schedule)

        assert conflicts == []

    def test_exact_same_start_time_is_a_conflict(self):
        """Two tasks at the exact same start time should be flagged as a conflict."""
        scheduler = Scheduler()
        t1 = make_task("Walk",  start_time=time(9, 0), duration_min=30)
        t2 = make_task("Feed",  start_time=time(9, 0), duration_min=10)
        schedule = make_schedule_with_tasks(t1, t2)

        conflicts = scheduler.detect_conflicts(schedule)

        assert len(conflicts) == 1
        descriptions = {t.description for pair in conflicts for t in pair}
        assert "Walk" in descriptions
        assert "Feed" in descriptions

    def test_overlapping_tasks_are_a_conflict(self):
        """A task that starts during another task's window should be flagged."""
        scheduler = Scheduler()
        t1 = make_task("Long walk", start_time=time(8, 0),  duration_min=60)
        t2 = make_task("Feed",      start_time=time(8, 30), duration_min=10)
        schedule = make_schedule_with_tasks(t1, t2)

        conflicts = scheduler.detect_conflicts(schedule)

        assert len(conflicts) == 1

    def test_tasks_without_start_time_are_not_flagged(self):
        """Tasks with no start_time should be silently skipped, not cause a false positive."""
        scheduler = Scheduler()
        t1 = make_task("Walk", start_time=None, duration_min=30)
        t2 = make_task("Feed", start_time=None, duration_min=10)
        schedule = make_schedule_with_tasks(t1, t2)

        conflicts = scheduler.detect_conflicts(schedule)

        assert conflicts == []

    def test_empty_schedule_has_no_conflicts(self):
        """An empty schedule should return an empty conflict list without crashing."""
        scheduler = Scheduler()
        schedule  = Schedule(date=date.today())

        conflicts = scheduler.detect_conflicts(schedule)

        assert conflicts == []

    def test_conflict_warnings_catches_cross_pet_overlap(self):
        """Two pets with tasks at the same time should produce a cross-pet warning."""
        owner = Owner(name="Jordan")
        dog   = Pet(name="Mochi")
        cat   = Pet(name="Nala")
        owner.add_pet(dog)
        owner.add_pet(cat)

        dog_task = make_task("Dog walk", start_time=time(8, 0), duration_min=30)
        cat_task = make_task("Cat feed", start_time=time(8, 0), duration_min=10)

        dog_plan = make_schedule_with_tasks(dog_task)
        cat_plan = make_schedule_with_tasks(cat_task)

        plans = {dog.id: dog_plan, cat.id: cat_plan}
        scheduler = Scheduler()
        warnings = scheduler.conflict_warnings(plans, owner)

        assert len(warnings) == 1
        assert "cross-pet" in warnings[0]
        assert "Mochi" in warnings[0]
        assert "Nala" in warnings[0]

    def test_conflict_warnings_returns_empty_when_no_overlap(self):
        """Non-overlapping cross-pet tasks should produce zero warnings."""
        owner = Owner(name="Jordan")
        dog   = Pet(name="Mochi")
        cat   = Pet(name="Nala")
        owner.add_pet(dog)
        owner.add_pet(cat)

        dog_task = make_task("Dog walk", start_time=time(8, 0),  duration_min=30)
        cat_task = make_task("Cat feed", start_time=time(9, 0),  duration_min=10)

        plans = {dog.id: make_schedule_with_tasks(dog_task),
                 cat.id: make_schedule_with_tasks(cat_task)}
        scheduler = Scheduler()
        warnings = scheduler.conflict_warnings(plans, owner)

        assert warnings == []

    def test_conflict_warnings_same_pet_overlap(self):
        """Two tasks for the same pet that overlap should produce a same-pet warning."""
        owner = Owner(name="Jordan")
        pet   = Pet(name="Mochi")
        owner.add_pet(pet)

        t1 = make_task("Walk",  start_time=time(8, 0), duration_min=60)
        t2 = make_task("Brush", start_time=time(8, 30), duration_min=20)

        plans = {pet.id: make_schedule_with_tasks(t1, t2)}
        scheduler = Scheduler()
        warnings = scheduler.conflict_warnings(plans, owner)

        assert len(warnings) == 1
        assert "cross-pet" not in warnings[0]
        assert "Mochi" in warnings[0]
