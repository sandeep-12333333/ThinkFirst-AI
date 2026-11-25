import re
from typing import List


_COMMON_PATTERNS = (
    ("always", "Absolute language (\"always\" or \"never\") may hide important exceptions."),
    ("never", "Absolute language (\"always\" or \"never\") may hide important exceptions."),
    ("guess", "A guess can be useful, but should be followed by a check or supporting reason."),
    ("obviously", "Claimed obviousness may hide an unstated assumption; identify the missing step."),
    ("magic", "Explain the mechanism rather than relying on an unexplained shortcut."),
)


def detect_misconceptions(reasoning: str) -> List[str]:
    text = reasoning.lower()
    findings = []
    for marker, message in _COMMON_PATTERNS:
        if re.search(rf"\b{marker}\b", text):
            findings.append(message)

    if len(re.findall(r"\b(and|or)\b", text)) >= 5:
        findings.append("Multiple ideas appear without clear relationships; separate the claims and explain their links.")

    unique = list(dict.fromkeys(findings))
    return unique or ["No obvious misconception cue was detected. Validate the reasoning with a counterexample."]
