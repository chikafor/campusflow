import tempfile
import unittest
from pathlib import Path

from campusflow.understanding_check import (
    QUESTION_BANK,
    run_understanding_check,
    score_answers,
)


class UnderstandingCheckTests(unittest.TestCase):
    def test_question_bank_has_six_questions(self):
        self.assertEqual(len(QUESTION_BANK), 6)

    def test_all_correct_answers_score_six(self):
        answers = {
            "Q1": "B", "Q2": "C", "Q3": "B",
            "Q4": "C", "Q5": "C", "Q6": "B",
        }
        self.assertEqual(score_answers(answers), 6)

    def test_wrong_and_missing_answers_do_not_score(self):
        self.assertEqual(score_answers({"Q1": "A", "Q2": "C"}), 1)

    def test_invalid_answer_retries_and_quiz_scores(self):
        responses = iter([
            "X", "B", "C", "B", "C", "C", "B",
            "The unassigned ticket must stay unchanged.",
            "Zero tickets means zero percent.",
        ])
        output = []

        with tempfile.TemporaryDirectory() as temp_dir:
            note_path = Path(temp_dir) / "reflections.md"
            score = run_understanding_check(
                input_fn=lambda prompt: next(responses),
                output_fn=output.append,
                learning_note_path=note_path,
            )

            self.assertEqual(score, 6)
            self.assertTrue(any("Invalid answer" in line for line in output))
            self.assertIn("6/6", "\n".join(output))
            self.assertTrue(note_path.exists())
            saved_notes = note_path.read_text(encoding="utf-8")
            self.assertIn("Q1 answer: B", saved_notes)
            self.assertIn("Q2 answer: C", saved_notes)


if __name__ == "__main__":
    unittest.main()
