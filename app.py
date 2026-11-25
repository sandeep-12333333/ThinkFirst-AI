import base64
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

with open("assets/styles.css", "r", encoding="utf-8") as _styles:
    st.markdown(f"<style>{_styles.read()}</style>", unsafe_allow_html=True)

from core.adaptive_engine import build_assistance, get_next_challenge
from core.misconception_detector import detect_misconceptions
from core.reasoning_engine import analyze_reasoning
from database.db_manager import (
    ensure_student,
    get_attempts,
    get_events,
    init_database,
    save_attempt,
    save_event,
)
from ui.thinking_lab import render_thinking_intelligence_lab

st.set_page_config(
    page_title="ThinkFirst AI",
    page_icon=":material/lightbulb_circle:",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_database()

# ---------- SESSION STATE ----------
if "attempts" not in st.session_state:
    st.session_state.attempts = []

if "student_name" not in st.session_state:
    st.session_state.student_name = "Student"

ensure_student(st.session_state.student_name)

if not st.session_state.attempts:
    persisted_attempts = get_attempts(st.session_state.student_name)
    st.session_state.attempts = [
        {
            "topic": row["topic"],
            "question": row["question"],
            "reasoning": row["reasoning"],
            "challenge": bool(row["is_challenge"]),
        }
        for row in persisted_attempts
    ]

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# Initialize SQLite-backed student state
if "student_id" not in st.session_state:
    import uuid
    st.session_state.student_id = str(uuid.uuid4())

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0b1020;
    color: #f8fafc;
}

[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263248;
}

.hero {
    padding: 32px;
    border-radius: 20px;
    background: linear-gradient(120deg, #172554, #312e81, #164e63);
    border: 1px solid #3b4a78;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 38px;
    color: white;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero p {
    color: #cbd5e1;
    font-size: 16px;
}

.metric-card {
    background: #151e31;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #29364c;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #a5b4fc;
}

.metric-label {
    color: #94a3b8;
    font-size: 13px;
}

.section-title {
    font-size: 23px;
    font-weight: 700;
    color: #f8fafc;
    margin-top: 22px;
}

.info-card {
    background: #151e31;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #29364c;
    min-height: 150px;
}

.info-card h3 {
    color: #c4b5fd;
    font-size: 17px;
}

.info-card p {
    color: #cbd5e1;
    font-size: 14px;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

.card-visual {
    width: 100%;
    height: auto;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


def embedded_asset(relative_path):
    with open(relative_path, "rb") as asset:
        encoded = base64.b64encode(asset.read()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


# ---------- SIDEBAR ----------
# Apply queued navigation before the keyed radio widget is instantiated.
pending_workspace = st.session_state.pop("pending_workspace", None)
if pending_workspace:
    st.session_state.workspace_menu = pending_workspace

with st.sidebar:

    st.image("assets/thinkfirst-mark.svg", width=52, alt="ThinkFirst prism compass logo")
    st.markdown("### ThinkFirst AI")
    student_name = st.text_input("Student name", value=st.session_state.student_name, key="student_name_input")
    if student_name.strip() and student_name.strip() != st.session_state.student_name:
        st.session_state.student_name = student_name.strip()
        ensure_student(st.session_state.student_name)

    st.divider()

    selected = st.radio(
        "WORKSPACE",
        [
            "Dashboard",
            "Think First",
            "Reasoning Lab",
            "Adaptive Tutor",
            "Independent Challenge",
            "Learning Journey",
            "Thinking Intelligence Lab"
        ],
        index=0,
        key="workspace_menu",
    )

    st.divider()

    st.caption("YOUR LEARNING SPACE")
    st.write("🎓 University Learning")
    st.write("⚡ Reasoning-First Mode")

    st.divider()
    st.caption("Developed as an Intelligent Interactive System")


# ---------- DASHBOARD ----------
if selected == "Dashboard":

    hero_left, hero_right = st.columns([3, 2], vertical_alignment="center")
    with hero_left:
        st.markdown("""
        <div class="hero">
            <h1>Think before you ask AI.</h1>
            <p>
            An intelligent learning environment that analyses your
            reasoning and adapts its assistance to support independent thinking.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with hero_right:
        st.image(
            "assets/thinknode.svg",
            alt="Interactive-style progression from thinking to knowledge transfer",
            width="stretch",
        )
        st.markdown("""
        <div class="progress-track"><div class="progress-fill" style="width: 78%;"></div></div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.attempts)}</div>
            <div class="metric-label">Learning Attempts</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3</div>
            <div class="metric-label">Adaptive Assistance Levels</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">AI</div>
            <div class="metric-label">Reasoning-Aware Learning</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Your Learning Workspace</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    mark_asset = embedded_asset("assets/thinkfirst-mark.svg")
    journey_asset = embedded_asset("assets/learning-journey.svg")

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h3>💡 Think First</h3>
            <p>Attempt a question and explain your thinking before receiving AI assistance.</p>
            <img class="card-visual" src="{mark_asset}" alt="Think First visual">
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card">
            <h3>🧠 Reasoning Lab</h3>
            <p>Explore your reasoning, misconceptions and areas requiring deeper understanding.</p>
            <img class="card-visual" src="{journey_asset}" alt="Reasoning Lab visual">
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            <h3>🎯 Independent Challenge</h3>
            <p>Test your understanding without relying on AI-generated hints.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h3>🤖 Adaptive Tutor</h3>
            <p>Receive assistance based on your demonstrated understanding and learning needs.</p>
            <img class="card-visual" src="{mark_asset}" alt="Adaptive Tutor visual">
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card">
            <h3>📈 Learning Journey</h3>
            <p>Explore attempts, reflections and learning progress.</p>
            <img class="card-visual" src="{journey_asset}" alt="Learning Journey visual">
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "Your learning principle: Attempt first. "
        "Understand better. Use AI intelligently."
    )


# ---------- THINK FIRST ----------
elif selected == "Think First":

    think_header, think_visual = st.columns([3, 2], vertical_alignment="center")
    with think_header:
        st.title("💡 Think First Workspace")
        st.write("Start with your own thinking before requesting AI support.")
    with think_visual:
        topic_asset = embedded_asset("assets/topic-learning.svg")
        st.markdown(f"<img src='{topic_asset}' alt='Independent learning topic illustration' style='width:100%; border-radius:16px;'>", unsafe_allow_html=True)

    topic = st.selectbox(
        "Choose your learning area",
        [
            "Artificial Intelligence",
            "Computer Science",
            "Data Science",
            "Mathematics",
            "Research and Academic Writing",
            "General University Learning"
        ]
    )

    question = st.text_area(
        "Learning question",
        placeholder="Enter a question or learning problem...",
        height=110
    )

    reasoning = st.text_area(
        "What do you already think?",
        placeholder="Explain your current understanding, approach or attempt...",
        height=180
    )

    if st.button("Submit My Thinking", type="primary"):

        if not question.strip() or not reasoning.strip():
            st.warning("Please enter both the question and your own reasoning.")

        else:
            st.session_state.current_question = question

            st.session_state.attempts.append({
                "topic": topic,
                "question": question,
                "reasoning": reasoning
            })
            analysis = analyze_reasoning(question, reasoning)
            save_attempt(
                st.session_state.student_name,
                topic,
                question,
                reasoning,
                analysis["score"],
                analysis["confidence"],
                is_challenge=False,
            )
            save_event(
                st.session_state.student_name,
                "initial_attempt",
                topic,
                analysis["score"],
            )

            st.success("Your initial attempt has been recorded!")

            st.info(
                "Next step: Analyse your reasoning in the Reasoning Lab."
            )


# ---------- REASONING LAB ----------
elif selected == "Reasoning Lab":

    st.title("🧠 Reasoning Lab")

    if not st.session_state.attempts:
        st.info("Submit your first attempt in Think First Workspace.")
    else:
        attempt = st.session_state.attempts[-1]

        st.subheader("Your latest attempt")
        st.write("**Question:**", attempt["question"])
        st.write("**Your reasoning:**", attempt["reasoning"])

        analysis = analyze_reasoning(attempt["question"], attempt["reasoning"])
        misconceptions = detect_misconceptions(attempt["reasoning"])

        metric_col, details_col = st.columns([1, 2])
        with metric_col:
            st.metric("Reasoning quality", f'{analysis["score"]:.0f}/100')
            st.caption(f'Confidence signal: {analysis["confidence"]}')

        with details_col:
            for dimension, value in analysis["dimensions"].items():
                st.progress(value / 100, text=f"{dimension}: {value}%")

        strength_col, improvement_col = st.columns(2)
        with strength_col:
            st.markdown("### Strengths")
            for item in analysis["strengths"]:
                st.success(item)

        with improvement_col:
            st.markdown("### Improve the reasoning")
            for item in analysis["improvements"]:
                st.warning(item)

        st.markdown("### Misconception watch")
        for item in misconceptions:
            st.info(item)

        if st.button("Open Adaptive Tutor", type="primary", key="open_adaptive_tutor"):
            st.session_state.pending_workspace = "Adaptive Tutor"
            save_event(
                st.session_state.student_name,
                "adaptive_support_requested",
                "Opened Adaptive Tutor from Reasoning Lab",
                analysis["score"],
            )
            st.rerun()


# ---------- ADAPTIVE TUTOR ----------
elif selected == "Adaptive Tutor":

    st.title("🤖 Adaptive Tutor")

    st.write(
        "Receive progressive assistance instead of immediately "
        "getting a complete answer."
    )

    if not st.session_state.attempts:
        st.info("Submit your first attempt in Think First before requesting adaptive help.")
    else:
        attempt = st.session_state.attempts[-1]
        analysis = analyze_reasoning(attempt["question"], attempt["reasoning"])
        events = get_events(st.session_state.student_name)
        hint_count = sum(1 for event in events if event["event_type"] == "hint_used")
        assistance = build_assistance(analysis["score"], attempt["topic"], hint_count)

        st.markdown(f"### Recommended: Level {assistance['level']} – {assistance['name']}")
        st.info(assistance["prompt"])

        level = st.segmented_control(
            "Override assistance level",
            options=["Level 1", "Level 2", "Level 3"],
            default=f"Level {assistance['level']}",
            key="assistance_level",
        )

        level_details = {
            "Level 1": (
                "Minimal Hint — prompts the student to inspect known and missing information.",
                "Identify one known fact and one missing fact.",
            ),
            "Level 2": (
                "Guided Question — asks the student to make and test an assumption.",
                "Explain one assumption, then use it to make the next step.",
            ),
            "Level 3": (
                "Structured Support — reveals a reasoning structure after repeated difficulty.",
                "Build a complete response using claim, evidence, reasoning, and conclusion.",
            ),
        }

        with st.container(border=True):
            st.markdown(f"**{level_details[level][0]}**")
            st.write(level_details[level][1])

        if st.button("Record this assistance and reveal support", key="adaptive_hint_used"):
            save_event(
                st.session_state.student_name,
                "hint_used",
                f"{level} — {level_details[level][1]}",
                analysis["score"],
            )
            st.success(f"{level} support recorded. Your next independent attempt should use fewer hints.")


# ---------- INDEPENDENT CHALLENGE ----------
elif selected == "Independent Challenge":

    st.title("🎯 Independent Challenge")

    st.write(
        "Apply your understanding to a new problem without AI hints."
    )

    if not st.session_state.attempts:
        st.info("Submit a learning attempt first, then use this challenge.")
    else:
        attempt = st.session_state.attempts[-1]
        analysis = analyze_reasoning(attempt["question"], attempt["reasoning"])
        challenge = get_next_challenge(attempt["topic"], analysis["confidence"])

        st.markdown("### Your independent challenge")
        st.warning(challenge)

        answer = st.text_area(
            "Write your answer without AI hints",
            key="independent_answer",
            height=180,
        )

        if st.button("Submit independent answer", type="primary"):
            if not answer.strip():
                st.warning("Write an answer before submitting.")
            else:
                answer_analysis = analyze_reasoning(challenge, answer)
                st.session_state.attempts.append({
                    "topic": attempt["topic"],
                    "question": challenge,
                    "reasoning": answer,
                    "challenge": True,
                })
                save_attempt(
                    st.session_state.student_name,
                    attempt["topic"],
                    challenge,
                    answer,
                    answer_analysis["score"],
                    answer_analysis["confidence"],
                    is_challenge=True,
                )
                save_event(
                    st.session_state.student_name,
                    "independent_attempt",
                    challenge,
                    answer_analysis["score"],
                )
                st.success(
                    f'Independent response recorded — reasoning quality: '
                    f'{answer_analysis["score"]:.0f}/100'
                )


# ---------- LEARNING JOURNEY ----------
elif selected == "Learning Journey":

    st.title("📈 Learning Journey")

    st.metric(
        "Total Attempts",
        len(st.session_state.attempts)
    )

    if st.session_state.attempts:
        journey_rows = []
        for index, attempt in enumerate(st.session_state.attempts, start=1):
            analysis = analyze_reasoning(attempt["question"], attempt["reasoning"])
            journey_rows.append({
                "Attempt": index,
                "Reasoning score": analysis["score"],
                "Confidence": analysis["confidence"].title(),
                "Topic": attempt["topic"],
            })

        st.subheader("Reasoning progress")
        st.line_chart(
            journey_rows,
            x="Attempt",
            y="Reasoning score",
            alt="Reasoning quality across learning attempts",
        )

        st.subheader("Previous Learning Attempts")

        for index, attempt in enumerate(
            reversed(st.session_state.attempts), 1
        ):
            analysis = analyze_reasoning(attempt["question"], attempt["reasoning"])
            with st.expander(f"Attempt {index}: {attempt['topic']} — {analysis['score']:.0f}/100"):
                st.write("**Question:**", attempt["question"])
                st.write("**Reasoning:**", attempt["reasoning"])

    else:
        st.info("Your learning history will appear here.")

# ---------- THINKING INTELLIGENCE LAB ----------
elif selected == "Thinking Intelligence Lab":

    render_thinking_intelligence_lab(st.session_state.student_name)
