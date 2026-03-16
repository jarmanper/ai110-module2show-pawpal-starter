from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler, Constraints


def main():
    owner = Owner(name="Jordan", location="Home")

    # Create pets
    dog = Pet(name="Mochi", breed="Shiba Inu", weight=14.5, favorite_food="Salmon", energy_level=0.8)
    cat = Pet(name="Nala", breed="Siamese", weight=8.2, favorite_food="Tuna", energy_level=0.6)

    owner.add_pet(dog)
    owner.add_pet(cat)

    # Create tasks
    today = date.today()
    walk_task = Task(
        due_date=today,
        description="Morning walk",
        category="walk",
        duration=timedelta(minutes=30),
        priority=3,
        frequency="daily",
    )
    feed_task = Task(
        due_date=today,
        description="Feed breakfast",
        category="feeding",
        duration=timedelta(minutes=15),
        priority=2,
        frequency="daily",
    )
    vet_task = Task(
        due_date=today + timedelta(days=1),
        description="Vet medication",
        category="medication",
        duration=timedelta(minutes=10),
        priority=1,
        frequency="once",
    )

    # Assign tasks to pets
    dog.add_task(walk_task)
    dog.add_task(feed_task)
    cat.add_task(feed_task)
    cat.add_task(vet_task)

    scheduler = Scheduler()
    scheduler.add_task(walk_task)
    scheduler.add_task(feed_task)
    scheduler.add_task(vet_task)

    constraints = Constraints(max_available_time=timedelta(hours=2), min_priority=1)
    plan = scheduler.generate_daily_plan(owner=owner, target_date=today, constraints=constraints)

    print("Today's Schedule")
    print("---------------")
    print(f"Date: {plan.date}")
    for i, task in enumerate(plan.tasks, start=1):
        print(f"{i}. {task.description} ({task.category}) - due: {task.due_date} - duration: {task.duration} - priority: {task.priority}")

    print("\nOwner Tasks Summary")
    print("-------------------")
    print(f"Total tasks: {len(owner.get_all_tasks())}")
    print(f"Pending tasks: {len(owner.get_all_pending())}")
    print(f"Completed tasks: {len(owner.get_all_completed())}")


if __name__ == "__main__":
    main()
