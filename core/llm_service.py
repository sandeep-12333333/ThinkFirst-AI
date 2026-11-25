import os


FALLBACK_SOCRATIC = (
    "What assumption is most important to your explanation, and what evidence would support or weaken it?"
)

FALLBACK_COUNTEREXAMPLE = (
    "Consider a scenario where one condition you assumed is false or reversed. "
    "Would your conclusion still hold?"
)

FALLBACK_TRANSFER = (
    "In a real-world setting with incomplete information, apply the same concept: identify the constraint, "
    "make one justified assumption, and explain how you would test your conclusion."
)


def is_api_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_ENV"))


def generate_text(prompt: str, fallback: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.responses.create(
            model=model,
            input=(
                "You are a Socratic learning assistant. Never give the final answer first. "
                "Challenge assumptions, ask concise follow-up questions, and encourage independent reasoning.\n\n"
                f"{prompt}"
            ),
            temperature=0.4,
        )
        text = getattr(response, "output_text", None)
        return text.strip() if text else fallback
    except Exception:
        return fallback


def get_socratic_question(topic: str, question: str, reasoning: str) -> str:
    prompt = (
        f"Topic: {topic}\nLearning problem: {question}\nStudent explanation: {reasoning}\n"
        "Ask one specific follow-up question that exposes an assumption or missing justification."
    )
    return generate_text(prompt, FALLBACK_SOCRATIC)


def get_counterexample(topic: str, question: str, reasoning: str) -> str:
    prompt = (
        f"Topic: {topic}\nLearning problem: {question}\nStudent explanation: {reasoning}\n"
        "Create a concise alternative scenario that could contradict or stress-test the student's assumption."
    )
    return generate_text(prompt, FALLBACK_COUNTEREXAMPLE)


def get_transfer_challenge(topic: str) -> str:
    prompt = (
        f"Create an unfamiliar real-world problem that requires the student to transfer knowledge from {topic}. "
        "Do not reveal the solution or use a copy of the original problem."
    )
    return generate_text(prompt, FALLBACK_TRANSFER)
