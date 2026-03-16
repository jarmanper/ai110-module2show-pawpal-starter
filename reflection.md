# PawPal+ Project Reflection

## 3 core actions:
Add a pet, create a feeding schedule, and be able to produce a daily plan.
## 1. System Design

**a. Initial design**

The initial plan had 5 domain classes: `Owner`, `Pet`, `Task`, `Schedule`, and `Scheduler`.

- `Owner`: holds basic owner info (`name`, `location`) and pet relationships (`pets` list). Provides methods to add/remove pets, retrieve a pet, and assign schedules.
- `Pet`: holds pet profile fields (`name`, `breed`, `weight`, `favorite_food`, `energy_level`) and a `schedule`; provides methods to change favorite food, update energy, assign/get schedule/tasks.
- `Task`: represents care work (`due_date`, `description`, `completed`, `category`, `duration`, `priority`) with stubs for create/read/update/delete/mark_complete.
- `Schedule`: day-level plan container (`date`, `tasks`) with task list management methods and total duration.
- `Scheduler`: orchestration class containing tasks with methods to add/remove/update tasks, query pending/completed, and generate a daily plan.

I also added `Constraints` to encapsulate planning rules (`max_available_time`, `preferred_categories`, `available_hours`, `min_priority`).

**b. Design changes**

- At this stage, no structural design changes were made after initial skeleton creation; the implementation follows the original design.
- Pending Copilot feedback, I may add an explicit `TaskRepository` or `OwnerManager` layer if the review flags single-class responsibility issues.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One tradeoff the scheduler makes is packing tasks back-to-back with no buffer time between them. As soon as one task ends, the next one starts at exactly that minute. In practice a pet owner probably needs a few minutes between walking the dog and feeding the cat — they have to walk back inside, wash their hands, grab the food bowl, etc. The scheduler ignores all of that.

The reason this is still a reasonable starting point is that adding buffer time would require another field on each task (or a global gap setting in `Constraints`), and it still wouldn't be accurate unless we also knew the owner's physical location for each task. For a basic planning tool, getting the order and rough time windows right matters more than modeling transition time to the minute. If the app grows, a `buffer_minutes` field in `Constraints` would be a natural next step.

A second, smaller tradeoff: conflict detection only flags tasks that genuinely overlap in duration — it does not warn when two tasks are scheduled back-to-back with zero gap. That means the schedule can look tight on paper even when no formal "conflict" is reported. Again, this is acceptable for now because the alternative (requiring a minimum gap between every pair of tasks) would make the packing algorithm significantly harder to reason about.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
