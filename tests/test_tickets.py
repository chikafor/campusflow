import unittest

from campusflow.tickets import (
    calculate_priority,
    create_ticket,
    find_ticket,
    get_next_ticket_id,
    add_note,
)

class TicketTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
    
    def make_ticket(self):
        return create_ticket(
            self.tickets,
            title="Network connection issue",
            category="Network",
            urgency="high",
            affected_users=10,
        )

    def test_create_using_expected_defaults(self):
        ticket = create_ticket(
            self.tickets, "Wi-Fi outage", "Network", "high", 2
        )

        self.assertEqual(ticket["id"], 1)
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(ticket["priority"], "high")

    def test_creation_normalizes_category_and_urgency(self):
        ticket = create_ticket(
            self.tickets, "  Broken laptop  ", " HARDWARE ", " LOW ", 1
        )

        self.assertEqual(ticket["title"], "Broken laptop")
        self.assertEqual(ticket["category"], "Hardware")
        self.assertEqual(ticket["urgency"], "low")

    def test_blank_title_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "  ", "Other", "low", 1)
        self.assertEqual(self.tickets, [])

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Issue", "Electricity", "low", 1)

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Issue", "Other", "urgent", 1)

    def test_invalid_affected_users_are_rejected(self):
        for value in (0, -1, 2.5, "3", True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    create_ticket(
                        self.tickets, "Issue", "Other", "low", value
                    )
        self.assertEqual(self.tickets, [])

    def test_priority_boundaries(self):
        self.assertEqual(calculate_priority("low", 2), "low")
        self.assertEqual(calculate_priority("low", 3), "medium")
        self.assertEqual(calculate_priority("low", 9), "medium")
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("high", 2), "high")
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("medium", 10), "high")

    def test_ticket_ids_increase(self):
        create_ticket(self.tickets, "First", "Other", "low", 1)
        create_ticket(self.tickets, "Second", "Other", "low", 1)

        self.assertEqual(
            [ticket["id"] for ticket in self.tickets], [1, 2]
        )
        self.assertEqual(get_next_ticket_id(self.tickets), 3)

    def test_find_ticket_returns_matching_record(self):
        created = create_ticket(
            self.tickets, "Issue", "Software", "medium", 3
        )

        self.assertIs(find_ticket(self.tickets, 1), created)

    def test_find_unknown_ticket_raises_key_error(self):
        with self.assertRaises(KeyError):
            find_ticket(self.tickets, 99)
    

    def test_add_note_to_open_ticket(self):
        ticket = self.make_ticket()

        note = add_note(
        self.tickets,
        ticket["id"],
        " Chika ",
        " Investigating the network issue. ",
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Chika")
        self.assertEqual(
        note["message"],
        "Investigating the network issue.",
        )
        self.assertEqual(ticket["notes"], [note])


    def test_add_note_rejects_blank_author(self):
        ticket = self.make_ticket()

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                ticket["id"],
                "   ",
                "Investigating the network issue.",
            )

        self.assertEqual(ticket["notes"], [])


    def test_add_note_rejects_short_message(self):
        ticket = self.make_ticket()

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                ticket["id"],
                "Chika",
                "Test",
            )

        self.assertEqual(ticket["notes"], [])


    def test_add_note_rejects_long_message(self):
        ticket = self.make_ticket()

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                ticket["id"],
                "Chika",
                "A" * 301,
            )

        self.assertEqual(ticket["notes"], [])


    def test_note_ids_increase(self):
        ticket = self.make_ticket()

        first = add_note(
            self.tickets,
            ticket["id"],
            "Chika",
            "First investigation update.",
        )

        second = add_note(
            self.tickets,
            ticket["id"],
            "Chika",
            "Second investigation update.",
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")


    def test_add_note_rejects_resolved_ticket(self):
        ticket = self.make_ticket()
        ticket["status"] = "resolved"

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                ticket["id"],
                "Chika",
                "Investigation completed successfully.",
            )

        self.assertEqual(ticket["notes"], [])

if __name__ == "__main__":
    unittest.main()




