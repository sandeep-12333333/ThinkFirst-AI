import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.intelligence_engine import (
    analyze_dependency,
    build_reasoning_dna,
    calculate_calibration,
    explain_assistance_level,
)
from core.llm_service import (
    get_counterexample,
    get_socratic_question,
    get_transfer_challenge,
    is_api_configured,
)
from core.reasoning_engine import analyze_reasoning
from database.db_manager import get_attempts, get_events, save_attempt, save_event


def _latest_attempt(student_name: str):
    attempts = get_attempts(student_name)
    return attempts[-1] if attempts else None


def render_thinking_intelligence_lab(student_name: str) -> None:
    lab_header, lab_visual = st.columns([3, 2], vertical_alignment="center")
    with lab_header:
        st.title("Thinking Intelligence Lab", icon=":material/psychology_alt:")
        st.caption("A learning cycle designed to strengthen independent reasoning.")
    with lab_visual:
        st.image(
            "assets/thinknode.svg",
            alt="Neon progression from thinking through knowledge transfer",
            width="stretch",
        )
        st.markdown("""
        <div class="progress-track"><div class="progress-fill" style="width: 86%;"></div></div>
        """, unsafe_allow_html=True)

    attempts = get_attempts(student_name)
    events = get_events(student_name)

    st.markdown("**Learning cycle:** Independent Thinking → Reasoning Analysis → Adaptive Assistance → Socratic Challenge → Counterexample Testing → Independent Reassessment → Knowledge Transfer")

    tabs = st.tabs([
        "Reasoning DNA",
        "Socratic Challenge",
        "AI Decision",
        "Counterexample Lab",
        "Confidence Calibration",
        "Dependency Detector",
        "Knowledge Transfer",
    ])

    latest = _latest_attempt(student_name)
    analyses = [analyze_reasoning(row["question"], row["reasoning"]) for row in attempts]

    with tabs[0]:
        st.subheader("Reasoning DNA Profile")
        dna = build_reasoning_dna(analyses)
        categories = list(dna)
        values = list(dna.values())

        figure = go.Figure()
        figure.add_trace(go.Scatterpolar(
            r=values + values[:1],
            theta=categories + categories[:1],
            fill="toself",
            name="Current profile",
            line={"color": "#8b5cf6"},
        ))
        figure.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 100]}},
            showlegend=False,
            height=390,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(figure, width="stretch", alt="Radar chart of four reasoning dimensions")

        if len(analyses) > 1:
            trend_rows = [{"Attempt": index, "Reasoning quality": item["score"]} for index, item in enumerate(analyses, 1)]
            st.line_chart(pd.DataFrame(trend_rows), x="Attempt", y="Reasoning quality", alt="Reasoning quality improvement trend")
        else:
            st.info("Complete another assessed attempt to begin your improvement trend.")

    with tabs[1]:
        st.subheader("Socratic Challenge Mode")
        if not latest:
            st.info("Submit an attempt in Think First to begin.")
        else:
            prompt = get_socratic_question(latest["topic"], latest["question"], latest["reasoning"])
            st.warning(prompt)
            response = st.text_area("Defend or revise your explanation", key="socratic_response", height=150)
            if st.button("Submit Socratic response", key="submit_socratic"):
                if response.strip():
                    analysis = analyze_reasoning(latest["question"], response)
                    save_attempt(
                        student_name, latest["topic"], latest["question"], response,
                        analysis["score"], analysis["confidence"], is_challenge=True,
                    )
                    save_event(student_name, "socratic_response", "Student answered a Socratic follow-up", analysis["score"])
                    st.success(f"Response recorded — reasoning quality: {analysis['score']:.0f}/100")
                else:
                    st.warning("Write a response before submitting.")

    with tabs[2]:
        st.subheader("Explain My AI Decision")
        if not latest:
            st.info("Submit an attempt to receive an assistance decision.")
        else:
            analysis = analyze_reasoning(latest["question"], latest["reasoning"])
            explanation = explain_assistance_level(analysis["score"], analysis["weakest_dimension"])
            st.metric("Selected assistance", f"Level {explanation['level']} — {explanation['name']}")
            for reason in explanation["reasons"]:
                st.write(f"• {reason}")

    with tabs[3]:
        st.subheader("Counterexample Laboratory")
        if not latest:
            st.info("Submit an attempt to generate a counterexample.")
        else:
            counterexample = get_counterexample(latest["topic"], latest["question"], latest["reasoning"])
            st.info(counterexample)
            revised = st.text_area("Defend or revise your explanation", key="counterexample_response", height=150)
            if st.button("Submit revised reasoning", key="submit_counterexample"):
                if revised.strip():
                    analysis = analyze_reasoning(latest["question"], revised)
                    save_attempt(
                        student_name, latest["topic"], latest["question"], revised,
                        analysis["score"], analysis["confidence"], is_challenge=True,
                    )
                    save_event(student_name, "counterexample_response", counterexample, analysis["score"])
                    st.success(f"Revised reasoning recorded — {analysis['score']:.0f}/100")
                else:
                    st.warning("Write a revised explanation before submitting.")

    with tabs[4]:
        st.subheader("Confidence vs Accuracy")
        st.caption("Accuracy is shown as a clearly labelled reasoning-quality proxy, not a claim of factual correctness.")
        confidence = st.slider("My confidence", 0, 100, 50, 5, key="confidence_rating")
        if st.button("Record confidence", key="record_confidence"):
            if latest:
                analysis = analyze_reasoning(latest["question"], latest["reasoning"])
                save_attempt(
                    student_name, latest["topic"], latest["question"], latest["reasoning"],
                    analysis["score"], analysis["confidence"], confidence_rating=float(confidence),
                )
                calibration = calculate_calibration(float(confidence), analysis["score"])
                save_event(student_name, "confidence_recorded", calibration["label"], analysis["score"])
                st.success(f"{calibration['label']} — confidence: {confidence}%, reasoning proxy: {analysis['score']:.0f}%")
            else:
                st.warning("Submit a reasoning attempt before recording confidence.")

        calibration_rows = []
        for index, row in enumerate(attempts, 1):
            if row.get("confidence_rating") is not None:
                score = float(row["reasoning_score"] or 0)
                confidence_value = float(row["confidence_rating"])
                calibration_rows.append({
                    "Attempt": index,
                    "Confidence": confidence_value,
                    "Reasoning-quality proxy": score,
                })
        if calibration_rows:
            st.line_chart(pd.DataFrame(calibration_rows), x="Attempt", y=["Confidence", "Reasoning-quality proxy"])
        else:
            st.info("No confidence records are available yet.")

    with tabs[5]:
        st.subheader("AI Dependency Detector")
        dependency = analyze_dependency(events, attempts)
        st.metric("Current profile", dependency["dependency"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Recorded hints", dependency["hint_count"])
        col2.metric("Independent attempts", dependency["independent_attempts"])
        col3.metric("Recent score", dependency["recent_average"])
        st.info(dependency["status"])

        hint = st.button("Record hint used", key="record_hint")
        if hint:
            save_event(student_name, "hint_used", "Student requested assistance", None)
            st.success("Hint usage recorded. Use the next challenge without AI support.")

    with tabs[6]:
        st.subheader("Knowledge Transfer Challenge")
        topic = latest["topic"] if latest else "General University Learning"
        challenge = get_transfer_challenge(topic)
        st.info(challenge)
        answer = st.text_area("Apply the concept independently", key="transfer_answer", height=180)
        if st.button("Submit transfer challenge", key="submit_transfer"):
            if answer.strip():
                analysis = analyze_reasoning(challenge, answer)
                save_attempt(
                    student_name, topic, challenge, answer,
                    analysis["score"], analysis["confidence"], is_challenge=True,
                )
                save_event(student_name, "knowledge_transfer", topic, analysis["score"])
                st.success(f"Knowledge-transfer response recorded — {analysis['score']:.0f}/100")
            else:
                st.warning("Write your independent response before submitting.")

    st.caption("OpenAI is enabled." if is_api_configured() else "Local fallback mode is active. Set OPENAI_API_KEY for optional AI-generated prompts.")
