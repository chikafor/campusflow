"""Tests for ticket assignment, lifecycle transitions, and queue ordering."""

import unittest

from campusflow.tickets import add_note

from campusflow.workflow import (
    assign_ticket,
    change_status,
    get_open_queue,
    reopen_ticket,
)


def make_ticket(
    ticket_id, *, priority="medium", status="open", assigned_to=None
):
    return {
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "category": "Software",
        "urgency": "medium",
        "affected_users": 3,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class AssignmentTests(unittest.TestCase):
    def setUp(self):
        self.tickets = [make_ticket(1)]

    def test_assign_trims_staff_name(self):
        result = assign_ticket(self.tickets, 1, "  Alex Doe  ")
        self.assertEqual(result["assigned_to"], "Alex Doe")

    def test_blank_staff_name_is_rejected_without_mutation(self):
        before = self.tickets[0].copy()
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, 1, "   ")
        self.assertEqual(self.tickets[0], before)

    def test_unknown_ticket_id_raises_key_error(self):
        with self.assertRaises(KeyError):
            assign_ticket(self.tickets, 999, "Alex")

    def test_resolved_ticket_cannot_be_reassigned(self):
        self.tickets[0]["status"] = "resolved"
        before = self.tickets[0].copy()
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, 1, "Alex")
        self.assertEqual(self.tickets[0], before)


class WorkflowTransitionTests(unittest.TestCase):
    def setUp(self):
        self.tickets = [make_ticket(1)]

    def test_unassigned_ticket_cannot_enter_progress(self):
        before = self.tickets[0].copy()
        with self.assertRaises(ValueError):
            change_status(self.tickets, 1, "in_progress")
        self.assertEqual(self.tickets[0], before)

    def test_assigned_ticket_can_move_to_in_progress(self):
        assign_ticket(self.tickets, 1, "Alex")
        result = change_status(self.tickets, 1, "in_progress")
        self.assertEqual(result["status"], "in_progress")

    def test_in_progress_ticket_can_be_resolved(self):
        self.tickets[0]["assigned_to"] = "Alex"
        self.tickets[0]["status"] = "in_progress"
        result = change_status(self.tickets, 1, "resolved")
        self.assertEqual(result["status"], "resolved")

    def test_skipping_a_status_is_rejected(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, 1, "resolved")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_resolved_ticket_requires_explicit_reopen_before_mutation(self):
        self.tickets[0]["status"] = "resolved"
        before = self.tickets[0].copy()
        with self.assertRaises(ValueError):
            change_status(self.tickets, 1, "open")
        self.assertEqual(self.tickets[0], before)

    def test_only_resolved_tickets_can_be_reopened(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, 1)

    def test_reopen_changes_resolved_ticket_to_open(self):
        self.tickets[0]["status"] = "resolved"
        result = reopen_ticket(self.tickets, 1)
        self.assertEqual(result["status"], "open")
    
    def test_notes_survive_resolution_and_reopening(self):
        ticket = self.tickets[0]
        ticket["assigned_to"] = "Alex"

        note = add_note(
            self.tickets,
            ticket["id"],
            "Chika",
            "Investigating the reported issue.",
        )

        change_status(self.tickets, ticket["id"], "in_progress")
        change_status(self.tickets, ticket["id"], "resolved")
        reopen_ticket(self.tickets, ticket["id"])

        self.assertEqual(ticket["status"], "open")
        self.assertEqual(ticket["notes"], [note])


class QueueTests(unittest.TestCase):
    def test_queue_filters_and_sorts_without_reordering_input(self):
        tickets = [
            make_ticket(4, priority="low"),
            make_ticket(3, priority="critical"),
            make_ticket(2, priority="high"),
            make_ticket(1, priority="critical"),
            make_ticket(5, priority="high", status="in_progress"),
            make_ticket(6, priority="critical", status="resolved"),
        ]
        original_ids = [ticket["id"] for ticket in tickets]

        queue = get_open_queue(tickets)

        self.assertEqual([ticket["id"] for ticket in queue], [1, 3, 2, 4])
        self.assertEqual([ticket["id"] for ticket in tickets], original_ids)
        self.assertIsNot(queue, tickets)


    def test_queue_rejects_nonpositive_ticket_id(self):
        with self.assertRaises(ValueError):
            get_open_queue([make_ticket(0, priority="critical")])

    def test_empty_queue_is_empty(self):
        self.assertEqual(get_open_queue([]), [])


if __name__ == "__main__":
    unittest.main()
