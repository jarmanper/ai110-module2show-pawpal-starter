# PawPal+ Project Reflection

Screenshot of the streamlit app:


<a href="course_images/image.png" target="_blank"><img src='course_images\image.png' title='PawPal App' width='1000' alt='PawPal App' class='center-block' /></a>

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

The scheduler considers five constraints: the owner's available time window (`available_hours`), a maximum total time budget (`max_available_time`), a minimum priority threshold (`min_priority`), preferred task categories, and the pet's energy level (stored on the `Pet` object rather than in `Constraints`).

I decided time window and priority mattered most because they map directly to a real owner's daily situation. If someone is only home from 8am to 6pm, tasks outside that window simply can't happen — there's no point scheduling them. Priority is a close second because not all care tasks are equal: a medication that needs to be given today is more urgent than a grooming session that can slip to tomorrow. Energy level felt important but less urgent, so it affects ordering rather than inclusion — a low-energy pet still needs to eat even if walks should wait.

**b. Tradeoffs**

One tradeoff the scheduler makes is packing tasks back-to-back with no buffer time between them. As soon as one task ends, the next one starts at exactly that minute. In practice a pet owner probably needs a few minutes between walking the dog and feeding the cat — they have to walk back inside, wash their hands, grab the food bowl, etc. The scheduler ignores all of that.

The reason this is still a reasonable starting point is that adding buffer time would require another field on each task (or a global gap setting in `Constraints`), and it still wouldn't be accurate unless we also knew the owner's physical location for each task. For a basic planning tool, getting the order and rough time windows right matters more than modeling transition time to the minute. If the app grows, a `buffer_minutes` field in `Constraints` would be a natural next step.

A second, smaller tradeoff: conflict detection only flags tasks that genuinely overlap in duration — it does not warn when two tasks are scheduled back-to-back with zero gap. That means the schedule can look tight on paper even when no formal "conflict" is reported. Again, this is acceptable for now because the alternative (requiring a minimum gap between every pair of tasks) would make the packing algorithm significantly harder to reason about.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools at three distinct stages. During design, I asked open-ended questions like "what are the most important edge cases to test for a pet scheduler with sorting and recurring tasks?" — that kind of prompt was genuinely useful because it surfaced scenarios (a pet with zero tasks, two tasks at the exact same minute) I probably would have found eventually but might have missed early. During implementation, I used Copilot's inline suggestions mainly for boilerplate — dataclass field definitions, `__init__` stubs, repetitive list comprehensions. The suggestions were fast and usually right for that kind of work. During testing and documentation I used chat to help phrase docstrings and README sections, then rewrote them to sound less generated.

The most effective prompts were specific and gave context: "I have a `Task` dataclass with a `frequency` field set to 'daily' or 'weekly' — how should `mark_complete` return the next occurrence?" was far more useful than "how do I handle recurring tasks?" The more I described the actual design, the better the suggestions fit.

**b. Judgment and verification**

Early in the project, Copilot suggested adding a `TaskRepository` class as a layer between `Scheduler` and the task list — essentially a data access object pattern. The reasoning was solid for a larger system, but for a single-file project with five classes it would have added two layers of indirection without any real benefit. I skipped it. The way I evaluated it was simple: I asked whether adding it would help me test anything I couldn't already test, or prevent any class from getting too large. The answer was no on both counts, so it stayed out.

A second example: when I asked for help with conflict detection, the first suggestion checked only for exact start-time matches (same `start_time` value). That would have missed the more realistic case where one task starts partway through another. I caught it because the test I wrote for overlapping-but-not-same-start tasks failed. Fixing it meant switching from equality to an interval overlap check — a small change, but one the original suggestion missed.

---

## 4. Testing and Verification

**a. What you tested**

I tested three core behaviors: sorting correctness (tasks come back in the right order regardless of insertion order), recurrence logic (daily/weekly tasks spawn the right next occurrence, one-time tasks don't), and conflict detection (overlapping time windows are flagged, empty schedules don't crash, cross-pet conflicts are distinguished from same-pet ones).

These were the right things to test first because they're the behaviors the rest of the app depends on. If `sort_tasks` is wrong, every schedule is wrong. If `mark_complete` doesn't spawn the next occurrence correctly, recurring care routines silently disappear. If `detect_conflicts` crashes on edge cases, the UI breaks. Getting these right before worrying about the Streamlit layer meant I had a reliable foundation to build on.

**b. Confidence**

4 out of 5. The core algorithms — sorting, recurrence, conflict detection — pass 22 tests and I'm confident they handle the scenarios I've thought of. What I'm less confident about is coverage of longer time horizons (what happens after several weeks of recurring tasks piling up?), and the interaction between session state and the UI (Streamlit reruns introduce subtleties that are hard to test with pytest). If I had more time I'd add tests for: a daily task marked complete five days in a row to check dates keep advancing, an owner with no pets, and a constraints window that's too narrow to fit any tasks at all.

---

## 5. Reflection

**a. What went well**

The class design held up better than I expected. Starting with clean domain objects (`Owner`, `Pet`, `Task`, `Schedule`, `Scheduler`, `Constraints`) made every feature addition feel like extending the system rather than fighting it. When I needed to add energy-aware sorting, there was already a natural place for it — the `sort_tasks` method took a `pet` parameter and the logic slotted in without touching anything else. That kind of stability usually means the initial design was reasonable, which is satisfying to see in practice.

The test suite was also more useful than I anticipated. Writing tests before I was "done" with the logic twice caught real bugs — the overlapping-conflict case and a situation where tasks with no `start_time` were incorrectly sorted. Both would have been annoying to debug later from the UI.

**b. What you would improve**

Two things stand out. First, I'd add a `buffer_minutes` option to `Constraints` so the scheduler inserts a small gap between tasks rather than packing them wall-to-wall. Right now the schedule is technically correct but unrealistically tight. Second, I'd fix the session state issue in `app.py` where changing the owner or pet name in the text inputs doesn't actually update the stored objects — they're created once and never refreshed. That's a confusing experience for anyone trying the app live.

On the design side, I might pull the conflict logic into its own module once it grows larger. Right now `Scheduler` is doing a lot — sorting, filtering, building schedules, detecting conflicts. That's fine for this project but would start to feel crowded if more features were added.

**c. Key takeaway**

AI is genuinely good at accelerating the parts of software development that are repetitive or well-understood — generating field definitions, writing docstrings, suggesting test cases, filling in boilerplate. What it doesn't replace is judgment about what the system *should* do. The most important decisions in this project — what counts as a scheduling conflict, how recurring tasks should behave, what constraints actually matter — all required thinking through the real scenario rather than accepting the first suggestion.

The most useful framing I found was to treat AI as a fast junior collaborator: capable, quick, and usually directionally right, but not someone you'd trust to make architectural decisions without review. Being the "lead architect" meant staying clear on the design goals so I could evaluate suggestions against something concrete, not just accept whatever felt plausible. That took more upfront thinking than just asking "write me a scheduler," but it meant the code actually matched the problem instead of a generic version of it.
