"""Tests for ticket reporting."""

import unittest

from campusflow.reports import generate_report


class GenerateReportTests(unittest.TestCase):
    def test_report_counts_statuses_and_priorities(self):
        tickets = [
            {"status": "open", "priority": "critical"},
            {"status": "in_progress", "priority": "high"},
            {"status": "resolved", "priority": "high"},
            {"status": "open", "priority": "low"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 4)
        self.assertEqual(
            report["by_status"],
            {"open": 2, "in_progress": 1, "resolved": 1},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 1, "high": 2, "medium": 0, "low": 1},
        )

    def test_empty_report_includes_all_zero_counts(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)
        self.assertEqual(
            report["by_status"],
            {"open": 0, "in_progress": 0, "resolved": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )

    def test_resolution_percentage(self):
        four_tickets = [
            {"status": "resolved", "priority": "high"},
            {"status": "resolved", "priority": "medium"},
            {"status": "open", "priority": "low"},
            {"status": "in_progress", "priority": "low"},
        ]
        ten_tickets = four_tickets + [
            {"status": "open", "priority": "low"},
            {"status": "open", "priority": "low"},
            {"status": "open", "priority": "low"},
            {"status": "open", "priority": "low"},
            {"status": "open", "priority": "low"},
            {"status": "open", "priority": "low"},
        ]

        self.assertEqual(generate_report(four_tickets)["resolution_percentage"], 50.0)
        self.assertEqual(generate_report(ten_tickets)["resolution_percentage"], 20.0)

    def test_unknown_status_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_report([{"status": "closed", "priority": "low"}])

    def test_unknown_priority_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_report([{"status": "open", "priority": "urgent"}])


if __name__ == "__main__":
    unittest.main()
