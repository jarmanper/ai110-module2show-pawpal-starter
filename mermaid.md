```mermaid
classDiagram
    class Owner {
        +String name
        +String location
        +List~Pet~ pets
        +addPet(pet: Pet)
        +removePet(petId: UUID)
        +getPet(petId: UUID)
        +getAllTasks()
        +setPetSchedule(petId: UUID, schedule: Schedule)
    }

    class Pet {
        +UUID id
        +String name
        +String breed
        +Float weight
        +String favoriteFood
        +Float energyLevel
        +Schedule schedule
        +setFavoriteFood(food: String)
        +updateEnergy(level: Float)
        +assignSchedule(schedule: Schedule)
        +getTasks()
    }

    class Task {
        +UUID id
        +Date dueDate
        +String description
        +Boolean completed
        +String category
        +Duration duration
        +Int priority
        +create()
        +read()
        +update(fields: Dict)
        +delete()
        +markComplete()
    }

    class Schedule {
        +UUID id
        +Date date
        +List~Task~ tasks
        +addTask(task: Task)
        +removeTask(taskId: UUID)
        +getTask(taskId: UUID)
        +getTasks()
        +getTotalDuration()
    }

    class Scheduler {
        +List~Task~ tasks
        +generateDailyPlan(owner: Owner, date: Date, constraints: Constraints)
        +addTask(task: Task)
        +removeTask(taskId: UUID)
        +updateTask(task: Task)
        +getPendingTasks()
        +getCompletedTasks()
    }

    class Constraints {
        +Duration maxAvailableTime
        +List~String~ preferredCategories
        +TimeRange availableHours
        +Int minPriority
    }

    Owner "1" --> "0..*" Pet
    Pet "1" --> "0..1" Schedule
    Schedule "1" --> "0..*" Task
    Scheduler "1" --> "0..*" Task

    style Owner fill:#f9f,stroke:#333,stroke-width:2px
    style Pet fill:#bbf,stroke:#333,stroke-width:2px
    style Task fill:#bfb,stroke:#333,stroke-width:2px
    style Schedule fill:#fbf,stroke:#333,stroke-width:2px