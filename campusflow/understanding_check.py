"""Interactive Engineering Understanding Check for CampusFlow."""

from pathlib import Path
from typing import Callable

QUESTION_BANK = [
    {
        "id": "Q1",
        "question": "An open, unassigned T001 is moved to in_progress. What should happen?",
        "options": {
            "A": "Accept the change",
            "B": "Reject and preserve all data",
            "C": "Resolve automatically",
            "D": "Remove the ticket",
        },
        "correct": "B",
    },
    {
        "id": "Q2",
        "question": "What is the resolution percentage when there are zero tickets?",
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "correct": "C",
    },
    {
        "id": "Q3",
        "question": "Search uses title='wifi', category='Network', status='open'. Which tickets should match?",
        "options": {
            "A": "Any ticket matching at least one filter",
            "B": "Only tickets matching every supplied filter",
            "C": "Every Network ticket",
            "D": "Every open ticket",
        },
        "correct": "B",
    },
    {
        "id": "Q4",
        "question": "A resolved ticket receives an Add note request. What should happen?",
        "options": {
            "A": "Append the note",
            "B": "Delete old notes",
            "C": "Reject until the ticket is reopened",
            "D": "Silently change the status",
        },
        "correct": "C",
    },
    {
        "id": "Q5",
        "question": "A JSON file contains duplicate ticket IDs. What should loading do?",
        "options": {
            "A": "Keep both tickets",
            "B": "Replace memory with the duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "correct": "C",
    },
    {
        "id": "Q6",
        "question": "A PR changes validation but adds no negative-case tests. What is the best review action?",
        "options": {
            "A": "Approve because the code runs",
            "B": "Request focused tests and an explanation of the reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "correct": "B",
    },
]


def score_answers(answers: dict[str, str]) -> int:
    """Return the number of correct answers without handling user interaction."""
    return sum(
        answers.get(question["id"], "").strip().upper() == question["correct"]
        for question in QUESTION_BANK
    )


def run_understanding_check(
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
    learning_note_path: Path = Path("docs/understanding-check-reflections.md"),
) -> int:
    """Run the quiz, retry invalid choices, and save two learner explanations."""
    read = input if input_fn is None else input_fn
    write = print if output_fn is None else output_fn
    answers: dict[str, str] = {}

    write("\\n=== Engineering Understanding Check ===")
    write("Choose A, B, C, or D for each question.")

    for question in QUESTION_BANK:
        write(f"\\n{question['id']}. {question['question']}")
        for letter, option in question["options"].items():
            write(f"  {letter}. {option}")

        while True:
            answer = read("Your answer: ").strip().upper()
            if answer in question["options"]:
                answers[question["id"]] = answer
                break
            write("Invalid answer. Enter A, B, C, or D.")

    score = score_answers(answers)
    write(f"\\nYour score: {score}/6")

    explanations = []
    for question_id in ("Q1", "Q2"):
        explanation = read(
            f"In your own words, briefly explain why you chose "
            f"{answers[question_id]} for {question_id}: "
        ).strip()
        explanations.append((question_id, answers[question_id], explanation))

    learning_note_path.parent.mkdir(parents=True, exist_ok=True)
    with learning_note_path.open("a", encoding="utf-8") as note_file:
        note_file.write("\\n## Engineering Understanding Check\\n")
        note_file.write(f"Score: {score}/6\\n")
        for question_id, answer, explanation in explanations:
            note_file.write(f"- {question_id} answer: {answer}\\n")
            note_file.write(f"  Explanation: {explanation or '(not provided)'}\\n")

    write(f"Learning explanations saved to {learning_note_path}.")
    return score
