import streamlit as st
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Schedule, Scheduler, Constraints

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
energy_level = st.slider(
    "Pet energy level", 0.0, 1.0, 0.5, 0.1,
    help="High (>0.6): demanding tasks scheduled first. Low (<0.4): gentle tasks first.",
)

# Create Owner in session state if it doesn't exist yet
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

# Create Pet in session state if it doesn't exist yet
if "pet" not in st.session_state:
    new_pet = Pet(name=pet_name)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.pet = new_pet

# Sync energy level on every rerun
st.session_state.pet.energy_level = energy_level

st.markdown("### Tasks")
st.caption("Add a task below — it will be attached to your pet using pet.add_task().")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    task_category = st.text_input("Category (e.g. walk, feed, groom)", value="")
with col5:
    task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

priority_map = {"low": 1, "medium": 2, "high": 3}

if st.button("Add task"):
    task = Task(
        description=task_title,
        duration=timedelta(minutes=int(duration)),
        priority=priority_map[priority_label],
        category=task_category,
        frequency=task_frequency,
    )
    st.session_state.pet.add_task(task)

# Task filter
status_filter = st.selectbox("Show tasks", ["all", "pending", "completed"], index=0)

_scheduler = Scheduler()
all_tasks = st.session_state.pet.tasks if "pet" in st.session_state else []
filtered_tasks = _scheduler.filter_tasks(
    all_tasks,
    status=None if status_filter == "all" else status_filter,
)

if filtered_tasks:
    st.write(f"Tasks ({status_filter}):")
    st.table([
        {
            "description": t.description,
            "category": t.category,
            "frequency": t.frequency or "once",
            "duration (min)": int(t.duration.total_seconds() // 60) if t.duration else 0,
            "priority": t.priority,
            "completed": t.completed,
        }
        for t in filtered_tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Calls Scheduler.generate_all_pets_plans() — one schedule per pet.")

col6, col7 = st.columns(2)
with col6:
    start_hour = st.number_input("Schedule window start (hour)", 0, 23, 8)
with col7:
    end_hour = st.number_input("Schedule window end (hour)", 0, 23, 20)

if st.button("Generate schedule"):
    constraints = Constraints(
        available_hours={"start": time(int(start_hour), 0), "end": time(int(end_hour), 0)},
    )
    scheduler = Scheduler()
    plans = scheduler.generate_all_pets_plans(st.session_state.owner, date.today(), constraints)

    if not plans:
        st.info("No pets found.")
    else:
        for pet in st.session_state.owner.pets:
            plan = plans.get(pet.id)
            if plan is None:
                continue
            scheduled_tasks = plan.get_tasks()
            st.markdown(f"**{pet.name}** (energy: {pet.energy_level:.1f}) — {len(scheduled_tasks)} task(s)")
            if scheduled_tasks:
                st.table([
                    {
                        "description": t.description,
                        "category": t.category,
                        "start time": t.start_time.strftime("%H:%M") if t.start_time else "—",
                        "duration (min)": int(t.duration.total_seconds() // 60) if t.duration else 0,
                        "priority": t.priority,
                        "frequency": t.frequency or "once",
                    }
                    for t in scheduled_tasks
                ])
                conflicts = scheduler.detect_conflicts(plan)
                if conflicts:
                    st.warning(f"{len(conflicts)} conflict(s) detected:")
                    for a, b in conflicts:
                        st.write(f"- **{a.description}** overlaps with **{b.description}**")
                else:
                    st.success("No scheduling conflicts.")
            else:
                st.info(f"No tasks due today for {pet.name}.")
