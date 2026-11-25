from typing import Dict


HINT_LEVELS = {
    1: "Hint: Restate the goal and identify which information is already known.",
    2: "Guided question: What assumption are you making, and what evidence supports it?",
    3: "Explanation: Organize the solution as claim, evidence, reasoning, and conclusion.",
}


def select_assistance_level(reasoning_score: float, hint_count: int = 0) -> int:
    """Choose the least supportive level that matches the learner's need."""
    if reasoning_score < 40 or hint_count >= 3:
        return 3
    if reasoning_score < 70:
        return 2
    return 1


def build_assistance(reasoning_score: float, topic: str, hint_count: int = 0) -> Dict:
    level = select_assistance_level(reasoning_score, hint_count)
    level_names = {
        1: "Minimal Hint",
        2: "Guided Question",
        3: "Structured Explanation",
    }
    return {
        "level": level,
        "name": level_names[level],
        "prompt": HINT_LEVELS[level],
        "topic": topic,
    }


def get_next_challenge(topic: str, confidence: str) -> str:
    if confidence == "uncertain":
        return f"Solve a familiar {topic} problem by stating one assumption before your final answer."
    if confidence == "developing":
        return f"Create a similar {topic} problem and explain why a plausible alternative answer is wrong."
    return f"Defend a {topic} solution, then construct a counterexample that tests it."
