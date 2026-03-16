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

    def create(self) -> None:
        """Persist or register task (stub)."""
        pass

    def read(self) -> Dict[str, Any]:
        """Return this task's data (stub)."""
        return {
            "id": self.id,
            "due_date": self.due_date,
            "description": self.description,
            "completed": self.completed,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
        }

    def update(self, **kwargs: Any) -> None:
        """Update task fields (stub)."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def delete(self) -> None:
        """Destroy or deregister this task (stub)."""
        pass

    def mark_complete(self) -> None:
        """Mark the task complete."""
        self.completed = True


@dataclass
class Schedule:
    id: UUID = field(default_factory=uuid4)
    date: date = field(default_factory=date.today)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: UUID) -> None:
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_task(self, task_id: UUID) -> Optional[Task]:
        return next((t for t in self.tasks if t.id == task_id), None)

    def get_tasks(self) -> List[Task]:
        return self.tasks

    def get_total_duration(self) -> timedelta:
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
    schedule: Optional[Schedule] = None

    def set_favorite_food(self, food: str) -> None:
        self.favorite_food = food

    def update_energy(self, level: float) -> None:
        self.energy_level = level

    def assign_schedule(self, schedule: Schedule) -> None:
        self.schedule = schedule

    def get_tasks(self) -> List[Task]:
        if self.schedule:
            return self.schedule.get_tasks()
        return []


@dataclass
class Owner:
    name: str
    location: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: UUID) -> None:
        self.pets = [pet for pet in self.pets if pet.id != pet_id]

    def get_pet(self, pet_id: UUID) -> Optional[Pet]:
        return next((p for p in self.pets if p.id == pet_id), None)

    def get_all_tasks(self) -> List[Task]:
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def set_pet_schedule(self, pet_id: UUID, schedule: Schedule) -> None:
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
        self.tasks.append(task)

    def remove_task(self, task_id: UUID) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def update_task(self, task_id: UUID, **kwargs: Any) -> None:
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            task.update(**kwargs)

    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.completed]

    def generate_daily_plan(
        self,
        owner: Owner,
        target_date: date,
        constraints: Optional[Constraints] = None,
    ) -> Schedule:
        """Generate a schedule plan (stub)."""
        schedule = Schedule(date=target_date)
        return schedule
