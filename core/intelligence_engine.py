from typing import Dict, List, Optional


FEATURE_NAMES = (
    "Reasoning DNA Profile",
    "Socratic Challenge Mode",
    "Explain My AI Decision",
    "Counterexample Laboratory",
    "Confidence vs Accuracy",
    "AI Dependency Detector",
    "Knowledge Transfer Challenge",
)


def build_reasoning_dna(analyses: List[Dict]) -> Dict[str, float]:
    if not analyses:
        return {
            "Analytical thinking": 0,
            "Logical reasoning": 0,
            "Critical evaluation": 0,
            "Evidence-based thinking": 0,
        }
    keys = (
        "Analytical thinking",
        "Logical reasoning",
        "Critical evaluation",
        "Evidence-based thinking",
    )
    return {
        key: round(sum(float(item.get("dna", {}).get(key, 0)) for item in analyses) / len(analyses), 1)
        for key in keys
    }


def explain_assistance_level(score: float, weakest_dimension: str) -> Dict:
    if score < 40:
        level = 2
        reasons = [
            "The reasoning-quality score is below 40.",
            f"The weakest measured dimension is {weakest_dimension}.",
            "Guided questions may help reveal the missing step without giving the answer.",
        ]
    elif score < 70:
        level = 2
        reasons = [
            "The reasoning-quality score is between 40 and 69.",
            f"The weakest measured dimension is {weakest_dimension}.",
            "A guided question provides enough support while preserving productive struggle.",
        ]
    else:
        level = 1
        reasons = [
            "The reasoning-quality score is 70 or above.",
            f"The strongest independent performance also suggests a low dependency risk.",
            "A minimal hint is sufficient because the response already shows useful structure.",
        ]

    names = {1: "Minimal Hint", 2: "Guided Question", 3: "Structured Explanation"}
    return {"level": level, "name": names[level], "reasons": reasons}


def calculate_calibration(confidence_rating: Optional[float], reasoning_score: float) -> Dict:
    if confidence_rating is None:
        return {"gap": None, "label": "Not calibrated yet"}
    gap = round(confidence_rating - reasoning_score, 1)
    if abs(gap) <= 10:
        label = "Well calibrated"
    elif gap > 10:
        label = "Overconfident"
    else:
        label = "Underconfident"
    return {"gap": gap, "label": label}


def analyze_dependency(events: List[Dict], attempts: List[Dict]) -> Dict:
    hints = sum(1 for event in events if event.get("event_type") == "hint_used")
    independent_attempts = sum(
        1 for attempt in attempts
        if attempt.get("is_challenge") == 1 or attempt.get("is_independent")
    )
    recent_scores = [float(attempt["reasoning_score"] or 0) for attempt in attempts[-5:]]
    average = round(sum(recent_scores) / len(recent_scores), 1) if recent_scores else 0

    if not attempts:
        dependency = "No evidence yet"
        status = "Submit an attempt to establish a baseline."
    elif hints == 0:
        dependency = "Low dependence"
        status = "You have used no recorded hints. Continue independent reassessment."
    elif hints >= 3 and independent_attempts == 0:
        dependency = "High dependence"
        status = "Try an independent challenge before requesting another hint."
    elif average >= 70:
        dependency = "Developing independence"
        status = "Your recent scores are strong; reduce hint use in the next challenge."
    else:
        dependency = "Moderate dependence"
        status = "Use hints only after documenting your first attempt."

    return {
        "hint_count": hints,
        "independent_attempts": independent_attempts,
        "recent_average": average,
        "dependency": dependency,
        "status": status,
    }


def build_cycle_status(attempt_count: int, hint_count: int) -> str:
    if attempt_count == 0:
        return "Start with Independent Thinking"
    if hint_count:
        return "Reasoning Analysis → Adaptive Assistance → Socratic Challenge"
    return "Independent Thinking → Reassessment → Knowledge Transfer"
