import streamlit as st
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Schedule, Scheduler, Constraints

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A daily care planner for your pets — sorted, filtered, and conflict-checked automatically.")

st.divider()

# ── Owner & Pet Setup ────────────────────────────────────────────────────────
st.subheader("Owner & Pet Setup")

col_owner, col_pet = st.columns(2)
with col_owner:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")

energy_level = st.slider(
    "Pet energy level",
    0.0, 1.0, 0.5, 0.1,
    help="Above 0.6: walks and exercise go first. Below 0.4: gentler tasks (feeding, grooming) go first.",
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

if "pet" not in st.session_state:
    new_pet = Pet(name=pet_name)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.pet = new_pet

# Keep energy level in sync on every rerun
st.session_state.pet.energy_level = energy_level

# ── Add Tasks ────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    task_category = st.text_input("Category (walk, feed, groom, …)", value="")
with col5:
    task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

priority_map = {"low": 1, "medium": 2, "high": 3}

if st.button("Add task", type="primary"):
    task = Task(
        description=task_title,
        duration=timedelta(minutes=int(duration)),
        priority=priority_map[priority_label],
        category=task_category,
        frequency=task_frequency,
        due_date=date.today(),
    )
    st.session_state.pet.add_task(task)
    st.success(f"Added: {task_title}")

# ── Task list with filtering and sorting ─────────────────────────────────────
_scheduler = Scheduler()
all_tasks = st.session_state.pet.tasks if "pet" in st.session_state else []

col_filter, col_spacer = st.columns([1, 2])
with col_filter:
    status_filter = st.selectbox("Show", ["all", "pending", "completed"], index=0)

filtered_tasks = _scheduler.filter_tasks(
    all_tasks,
    status=None if status_filter == "all" else status_filter,
)

# Sort using the same logic the scheduler uses so the list matches the schedule
sorted_display = _scheduler.sort_tasks(filtered_tasks, pet=st.session_state.pet)

if sorted_display:
    st.caption(f"{len(sorted_display)} task(s) — sorted by overdue status, energy fit, then priority")
    st.table([
        {
            "description": t.description,
            "category": t.category or "—",
            "frequency": t.frequency or "once",
            "duration (min)": int(t.duration.total_seconds() // 60) if t.duration else 0,
            "priority": t.priority,
            "done": "yes" if t.completed else "no",
        }
        for t in sorted_display
    ])
else:
    st.info("No tasks yet — add one above.")

# ── Schedule Builder ──────────────────────────────────────────────────────────
st.divider()
st.subheader("Build Today's Schedule")
st.caption("Generates one schedule per pet using sort order, energy level, and your time window.")

col6, col7 = st.columns(2)
with col6:
    start_hour = st.number_input("Window start (hour, 0–23)", 0, 23, 8)
with col7:
    end_hour = st.number_input("Window end (hour, 0–23)", 0, 23, 20)

if st.button("Generate schedule", type="primary"):
    constraints = Constraints(
        available_hours={"start": time(int(start_hour), 0), "end": time(int(end_hour), 0)},
    )
    scheduler = Scheduler()
    owner = st.session_state.owner
    plans = scheduler.generate_all_pets_plans(owner, date.today(), constraints)

    if not plans:
        st.info("No pets set up yet.")
    else:
        # Cross-pet conflict warnings go at the top so they're hard to miss
        cross_warnings = scheduler.conflict_warnings(plans, owner)
        if cross_warnings:
            for w in cross_warnings:
                st.warning(w)
        else:
            st.success("No cross-pet scheduling conflicts.")

        st.divider()

        for pet in owner.pets:
            plan = plans.get(pet.id)
            if plan is None:
                continue

            scheduled_tasks = plan.get_tasks()
            total_min = int(plan.get_total_duration().total_seconds() // 60)

            # Per-pet summary metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Pet", pet.name)
            m2.metric("Tasks scheduled", len(scheduled_tasks))
            m3.metric("Total time", f"{total_min} min")

            if scheduled_tasks:
                # Sort by assigned start time for display
                sorted_sched = sorted(
                    scheduled_tasks,
                    key=lambda t: t.start_time.strftime("%H:%M") if t.start_time else "99:99"
                )
                st.table([
                    {
                        "start": t.start_time.strftime("%H:%M") if t.start_time else "—",
                        "description": t.description,
                        "category": t.category or "—",
                        "duration (min)": int(t.duration.total_seconds() // 60) if t.duration else 0,
                        "priority": t.priority,
                        "repeats": t.frequency or "once",
                    }
                    for t in sorted_sched
                ])

                # Per-pet same-pet conflict check
                same_pet_conflicts = scheduler.detect_conflicts(plan)
                if same_pet_conflicts:
                    st.warning(f"{len(same_pet_conflicts)} overlap(s) within {pet.name}'s schedule:")
                    for a, b in same_pet_conflicts:
                        st.write(f"  - **{a.description}** overlaps **{b.description}**")
                else:
                    st.success(f"{pet.name}'s schedule has no internal conflicts.")
            else:
                st.info(f"No tasks due today for {pet.name}.")

            st.divider()
