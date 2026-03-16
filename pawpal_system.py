"""PawPal+ backend logic layer

This module defines the core domain classes for paw care scheduling:
- Owner
- Pet
- Task
- Schedule
- Scheduler
- Constraints

Method implementations are stubs for now; behavior will be added iteratively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Dict, Tuple, Any
from uuid import UUID, uuid4

HIGH_ENERGY_CATEGORIES = {"walk", "exercise", "play", "run", "training"}


@dataclass
class Task:
    id: UUID = field(default_factory=uuid4)
    due_date: Optional[date] = None
    description: str = ""
    completed: bool = False
    category: str = ""
    duration: Optional[timedelta] = None
    priority: int = 0
    frequency: Optional[str] = None  # e.g., 'daily', 'weekly', 'once'
    start_time: Optional[time] = None  # assigned start time once scheduled

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh Task for the next scheduled occurrence of this recurring task.

        For daily tasks the new due date is tomorrow; for weekly tasks it is seven
        days from the current due date (or today if due_date is unset).  Returns
        None for one-time tasks so callers know no follow-up is needed.
        """
        if self.frequency == "daily":
            next_due = (self.due_date or date.today()) + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = (self.due_date or date.today()) + timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_due,
        )

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and return the next occurrence if recurring.

        Marks the task done, then calls next_occurrence() so the caller can
        immediately re-queue a fresh copy for the next day or week.  Returns
        None when the task is a one-time event and no follow-up is required.
        """
        self.completed = True
        return self.next_occurrence()

    def is_due(self, on_date: Optional[date] = None) -> bool:
        """Return True if this task is due on the given date, respecting frequency."""
        if on_date is None:
            on_date = date.today()
        if self.frequency == "daily":
            return True
        if self.frequency == "weekly":
            if self.due_date is None:
                return True
            return on_date.weekday() == self.due_date.weekday()
        # 'once' or None — fall back to due_date comparison
        if self.due_date is None:
            return True
        return self.due_date <= on_date

    def update(self, **kwargs: Any) -> None:
        """Update task fields by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this task to a plain dictionary."""
        return {
            "id": self.id,
            "due_date": self.due_date,
            "description": self.description,
            "completed": self.completed,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
            "frequency": self.frequency,
            "start_time": self.start_time,
        }


@dataclass
class Schedule:
    id: UUID = field(default_factory=uuid4)
    date: date = field(default_factory=date.today)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this schedule if not already present."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task_id: UUID) -> None:
        """Remove the task with the given ID from this schedule."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Return the task matching the given ID, or None."""
        return next((t for t in self.tasks if t.id == task_id), None)

    def get_tasks(self) -> List[Task]:
        """Return all tasks in this schedule."""
        return self.tasks

    def get_total_duration(self) -> timedelta:
        """Return the sum of durations for all tasks in this schedule."""
        total = timedelta()
        for task in self.tasks:
            if task.duration:
                total += task.duration
        return total


@dataclass
class Pet:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    breed: str = ""
    weight: float = 0.0
    favorite_food: str = ""
    energy_level: float = 0.0
    tasks: List[Task] = field(default_factory=list)
    schedule: Optional[Schedule] = None

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: UUID) -> None:
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Return the pet's task matching the given ID, or None."""
        return next((task for task in self.tasks if task.id == task_id), None)

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return all completed tasks for this pet."""
        return [task for task in self.tasks if task.completed]

    def tasks_due_on(self, target_date: date) -> List[Task]:
        """Return tasks due on or before the given date."""
        return [task for task in self.tasks if task.is_due(target_date)]

    def set_favorite_food(self, food: str) -> None:
        """Set the pet's favorite food."""
        self.favorite_food = food

    def update_energy(self, level: float) -> None:
        """Update the pet's energy level."""
        self.energy_level = level

    def assign_schedule(self, schedule: Schedule) -> None:
        """Assign a Schedule to this pet."""
        self.schedule = schedule

    def get_assigned_tasks(self) -> List[Task]:
        """Return tasks from the pet's assigned schedule, or empty list."""
        if self.schedule:
            return self.schedule.get_tasks()
        return []


@dataclass
class Owner:
    name: str
    location: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: UUID) -> None:
        """Remove the pet with the given ID from this owner's list."""
        self.pets = [pet for pet in self.pets if pet.id != pet_id]

    def get_pet(self, pet_id: UUID) -> Optional[Pet]:
        """Return the pet matching the given ID, or None."""
        return next((p for p in self.pets if p.id == pet_id), None)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across every pet owned."""
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def get_all_pending(self) -> List[Task]:
        """Return all incomplete tasks across every pet owned."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def get_all_completed(self) -> List[Task]:
        """Return all completed tasks across every pet owned."""
        return [task for task in self.get_all_tasks() if task.completed]

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the pet with the given name (case-insensitive)."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.tasks
        return []

    def set_pet_schedule(self, pet_id: UUID, schedule: Schedule) -> None:
        """Assign a schedule to the pet with the given ID."""
        pet = self.get_pet(pet_id)
        if pet:
            pet.assign_schedule(schedule)


@dataclass
class Constraints:
    max_available_time: Optional[timedelta] = None
    preferred_categories: List[str] = field(default_factory=list)
    available_hours: Optional[Dict[str, time]] = None
    min_priority: Optional[int] = None


class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: UUID) -> None:
        """Remove the task with the given ID from the scheduler."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def update_task(self, task_id: UUID, **kwargs: Any) -> None:
        """Update fields on the task matching the given ID."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            task.update(**kwargs)

    def get_pending_tasks(self, owner: Optional[Owner] = None) -> List[Task]:
        """Return pending tasks from the owner (or internal list if no owner given)."""
        source = owner.get_all_pending() if owner else self.tasks
        return [t for t in source if not t.completed]

    def get_completed_tasks(self, owner: Optional[Owner] = None) -> List[Task]:
        """Return completed tasks from the owner (or internal list if no owner given)."""
        source = owner.get_all_completed() if owner else self.tasks
        return [t for t in source if t.completed]

    def filter_tasks(
        self,
        tasks: List[Task],
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by status ('pending'/'completed') and/or category string."""
        result = tasks
        if status == "pending":
            result = [t for t in result if not t.completed]
        elif status == "completed":
            result = [t for t in result if t.completed]
        if category:
            result = [t for t in result if t.category.lower() == category.lower()]
        return result

    def detect_conflicts(self, schedule: "Schedule") -> List[Tuple[Task, Task]]:
        """Return pairs of tasks whose scheduled time windows overlap.

        Only tasks that have both a start_time and a duration are considered.
        Two tasks conflict when their intervals overlap — i.e., one starts
        before the other ends.  Tasks with no assigned time are silently skipped
        rather than raising an error.
        """
        conflicts: List[Tuple[Task, Task]] = []
        timed = [t for t in schedule.get_tasks() if t.start_time and t.duration]
        for i, a in enumerate(timed):
            a_start = datetime.combine(schedule.date, a.start_time)
            a_end = a_start + a.duration
            for b in timed[i + 1:]:
                b_start = datetime.combine(schedule.date, b.start_time)
                b_end = b_start + b.duration
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts

    def conflict_warnings(
        self,
        plans: Dict[UUID, "Schedule"],
        owner: "Owner",
    ) -> List[str]:
        """Return human-readable warning strings for scheduling conflicts across all pets.

        Collects every timed task from every pet's schedule into a single list,
        then checks all pairs for overlapping time windows.  A warning is issued
        whether the clash is between two tasks for the same pet (the owner can't
        do both at once) or two different pets (same problem, different animals).
        Returns an empty list when no conflicts exist so callers can check with
        a simple ``if warnings`` guard instead of catching exceptions.
        """
        warnings: List[str] = []

        # Build a flat list of (task, pet_name, start_dt, end_dt)
        entries = []
        for pet in owner.pets:
            plan = plans.get(pet.id)
            if not plan:
                continue
            for t in plan.get_tasks():
                if t.start_time and t.duration:
                    start_dt = datetime.combine(plan.date, t.start_time)
                    end_dt = start_dt + t.duration
                    entries.append((t, pet.name, start_dt, end_dt))

        for i, (a, a_pet, a_start, a_end) in enumerate(entries):
            for b, b_pet, b_start, b_end in entries[i + 1:]:
                if a_start < b_end and b_start < a_end:
                    fmt = "%H:%M"
                    span_a = f"{a_start.strftime(fmt)}-{a_end.strftime(fmt)}"
                    span_b = f"{b_start.strftime(fmt)}-{b_end.strftime(fmt)}"
                    if a_pet == b_pet:
                        msg = (
                            f"WARNING [{a_pet}]: '{a.description}' ({span_a}) "
                            f"overlaps '{b.description}' ({span_b})"
                        )
                    else:
                        msg = (
                            f"WARNING [cross-pet]: '{a.description}' for {a_pet} ({span_a}) "
                            f"overlaps '{b.description}' for {b_pet} ({span_b})"
                        )
                    warnings.append(msg)

        return warnings

    def _build_schedule_for_tasks(
        self,
        pet: "Pet",
        candidates: List[Task],
        target_date: date,
        constraints: Optional["Constraints"] = None,
    ) -> "Schedule":
        """Assign sequential start times within the available window and build a Schedule."""
        plan = Schedule(date=target_date)

        if constraints and constraints.available_hours:
            window_start = constraints.available_hours.get("start", time(8, 0))
            window_end = constraints.available_hours.get("end", time(20, 0))
        else:
            window_start = time(8, 0)
            window_end = time(20, 0)

        cursor = datetime.combine(target_date, window_start)
        window_end_dt = datetime.combine(target_date, window_end)
        remaining_time = constraints.max_available_time if constraints else None

        for task in self.sort_tasks(candidates, pet=pet):
            if task.duration:
                if remaining_time is not None and task.duration > remaining_time:
                    continue
                task_end = cursor + task.duration
                if task_end > window_end_dt:
                    continue
                task.start_time = cursor.time()
                cursor = task_end
                if remaining_time is not None:
                    remaining_time -= task.duration
            plan.add_task(task)

        return plan

    def sort_tasks(self, tasks: List[Task], pet: Optional["Pet"] = None) -> List[Task]:
        """Sort tasks: overdue first, energy-aware by pet level, then due date and priority."""
        today = date.today()

        def key(t: Task) -> tuple:
            overdue_order = 0 if (t.due_date and t.due_date < today) else 1
            energy_order = 0
            if pet is not None:
                is_high_energy = t.category.lower() in HIGH_ENERGY_CATEGORIES
                if pet.energy_level > 0.6:
                    # energetic pet: schedule demanding tasks first
                    energy_order = 0 if is_high_energy else 1
                elif pet.energy_level < 0.4:
                    # low-energy pet: schedule gentle tasks first
                    energy_order = 1 if is_high_energy else 0
            return (t.completed, overdue_order, energy_order, t.due_date or date.max, -t.priority)

        return sorted(tasks, key=key)

    def generate_daily_plan(
        self,
        owner: Owner,
        target_date: date,
        constraints: Optional[Constraints] = None,
    ) -> Schedule:
        """Build a combined Schedule of due tasks for all of the owner's pets on the target date."""
        all_tasks: List[Task] = []
        for pet in owner.pets:
            all_tasks.extend(t for t in pet.get_pending_tasks() if t.is_due(target_date))

        if constraints and constraints.min_priority is not None:
            all_tasks = [t for t in all_tasks if t.priority >= constraints.min_priority]

        if constraints and constraints.preferred_categories:
            preferred = [t for t in all_tasks if t.category in constraints.preferred_categories]
            if preferred:
                all_tasks = preferred

        first_pet = owner.pets[0] if owner.pets else Pet()
        return self._build_schedule_for_tasks(first_pet, all_tasks, target_date, constraints)

    def generate_all_pets_plans(
        self,
        owner: Owner,
        target_date: date,
        constraints: Optional[Constraints] = None,
    ) -> Dict[UUID, Schedule]:
        """Generate a separate Schedule for each pet, respecting time windows and energy level."""
        plans: Dict[UUID, Schedule] = {}
        for pet in owner.pets:
            candidates = [t for t in pet.get_pending_tasks() if t.is_due(target_date)]

            if constraints and constraints.min_priority is not None:
                candidates = [t for t in candidates if t.priority >= constraints.min_priority]

            if constraints and constraints.preferred_categories:
                preferred = [t for t in candidates if t.category in constraints.preferred_categories]
                if preferred:
                    candidates = preferred

            plans[pet.id] = self._build_schedule_for_tasks(pet, candidates, target_date, constraints)
        return plans

    def apply_daily_plan(self, owner: Owner, pet_id: UUID, plan: Schedule) -> None:
        """Assign the generated daily plan to the specified pet."""
        pet = owner.get_pet(pet_id)
        if pet:
            pet.assign_schedule(plan)

