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
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4


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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_due(self, on_date: Optional[date] = None) -> bool:
        """Return True if this task is due on or before the given date."""
        if self.due_date is None:
            return True
        if on_date is None:
            on_date = date.today()
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

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by completion status, due date, then priority descending."""
        return sorted(
            tasks,
            key=lambda t: (
                t.completed,
                t.due_date or date.max,
                -t.priority,
            ),
        )

    def generate_daily_plan(
        self,
        owner: Owner,
        target_date: date,
        constraints: Optional[Constraints] = None,
    ) -> Schedule:
        """Build a Schedule of due tasks for the owner on the target date, respecting constraints."""
        plan = Schedule(date=target_date)
        candidates = [task for task in owner.get_all_pending() if task.is_due(target_date)]

        if constraints and constraints.min_priority is not None:
            candidates = [t for t in candidates if t.priority >= constraints.min_priority]

        if constraints and constraints.preferred_categories:
            preferred = [t for t in candidates if t.category in constraints.preferred_categories]
            if preferred:
                candidates = preferred

        sorted_candidates = self.sort_tasks(candidates)

        remaining_time = constraints.max_available_time if constraints else None

        for task in sorted_candidates:
            if task.duration and remaining_time is not None:
                if task.duration > remaining_time:
                    continue
                remaining_time -= task.duration

            plan.add_task(task)

        return plan

    def apply_daily_plan(self, owner: Owner, pet_id: UUID, plan: Schedule) -> None:
        """Assign the generated daily plan to the specified pet."""
        pet = owner.get_pet(pet_id)
        if pet:
            pet.assign_schedule(plan)

