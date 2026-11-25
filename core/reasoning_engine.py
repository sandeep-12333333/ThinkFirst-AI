import re
from typing import Dict, List


_REASONING_MARKERS = (
    "because", "since", "therefore", "thus", "if", "so", "however",
    "first", "then", "next", "assume", "compared", "example", "support",
    "evidence", "proof", "reason",
)

_STEP_MARKERS = (
    "first", "second", "third", "then", "next", "finally", "step",
    "1", "2", "3",
)

_UNCERTAINTY_MARKERS = (
    "not sure", "uncertain", "may", "might", "possibly", "could",
    "i think", "perhaps", "depends",
)


def analyze_reasoning(question: str, reasoning: str) -> Dict:
    """Return transparent, non-AI reasoning signals for an initial attempt."""
    text = reasoning.lower()
    words = re.findall(r"\b[a-z0-9][a-z0-9'-]*\b", text)

    evidence_count = sum(text.count(marker) for marker in _REASONING_MARKERS)
    step_count = sum(text.count(marker) for marker in _STEP_MARKERS)
    uncertainty_count = sum(text.count(marker) for marker in _UNCERTAINTY_MARKERS)

    question_terms = set(re.findall(r"\b[a-zA-Z]{4,}\b", question.lower()))
    answer_terms = set(re.findall(r"\b[a-zA-Z]{4,}\b", text))
    stop_words = {"with", "what", "when", "where", "which", "that", "this", "have", "from", "your", "about"}
    topical_overlap = len((question_terms - stop_words) & (answer_terms - stop_words))

    length_score = min(len(words) / 45, 1.0)
    evidence_score = min(evidence_count / 3, 1.0)
    structure_score = min(step_count / 3, 1.0)
    relevance_score = min(topical_overlap / 3, 1.0)

    analytical_score = round(100 * (0.55 * length_score + 0.45 * relevance_score))
    logical_score = round(100 * (0.60 * structure_score + 0.40 * evidence_score))
    critical_score = round(100 * (0.50 * evidence_score + 0.50 * min(
        sum(text.count(marker) for marker in ("however", "but", "alternative", "counterexample", "assume")) / 3,
        1.0,
    )))
    evidence_based_score = round(100 * evidence_score)

    dna = {
        "Analytical thinking": analytical_score,
        "Logical reasoning": logical_score,
        "Critical evaluation": critical_score,
        "Evidence-based thinking": evidence_based_score,
    }

    overall = round(
        100 * (0.30 * length_score + 0.30 * evidence_score
               + 0.20 * structure_score + 0.20 * relevance_score),
        1,
    )

    strengths: List[str] = []
    improvements: List[str] = []

    if evidence_count:
        strengths.append("You used reasoning language or justification.")
    else:
        improvements.append("Explain why your answer follows from the information given.")

    if step_count:
        strengths.append("Your response shows some step-by-step structure.")
    else:
        improvements.append("Break the solution into numbered steps or stages.")

    if relevance_score >= 0.67:
        strengths.append("Your explanation refers to ideas from the question.")
    else:
        improvements.append("Connect the explanation more directly to the question.")

    if uncertainty_count:
        strengths.append("You identified uncertainty, which creates a useful learning target.")

    if len(words) < 20:
        improvements.append("Add more detail so another learner can follow your reasoning.")

    if not strengths:
        strengths.append("You made an initial attempt before using assistance.")

    confidence = "uncertain" if uncertainty_count else ("developing" if overall < 70 else "confident")

    weakest_dimension = min(dna, key=dna.get)

    return {
        "score": overall,
        "confidence": confidence,
        "word_count": len(words),
        "strengths": strengths,
        "improvements": improvements,
        "dimensions": {
            "Depth": round(length_score * 100),
            "Justification": round(evidence_score * 100),
            "Structure": round(structure_score * 100),
            "Relevance": round(relevance_score * 100),
        },
        "dna": dna,
        "weakest_dimension": weakest_dimension,
        "calibration_gap": 0,
    }
