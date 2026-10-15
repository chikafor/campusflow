
import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.directory = Path(self.temp_dir.name)
        self.file_path = self.directory / "tickets.json"

        self.tickets = []
        create_ticket(
            self.tickets, "Wi-Fi outage", "Network", "high", 12
        )
        create_ticket(
            self.tickets, "Broken keyboard", "Hardware", "low", 1
        )

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.file_path), [])

    def test_save_and_load_preserves_ticket_data(self):
        save_tickets(self.file_path, self.tickets)

        loaded = load_tickets(self.file_path)

        self.assertEqual(loaded, self.tickets)

    def test_saved_file_contains_valid_json(self):
        save_tickets(self.file_path, self.tickets)

        with self.file_path.open(encoding="utf-8") as file:
            loaded_json = json.load(file)

        self.assertEqual(loaded_json, self.tickets)

    def test_malformed_json_raises_storage_error(self):
        self.file_path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(StorageError):
            load_tickets(self.file_path)

        # The invalid file must not be silently replaced.
        self.assertEqual(
            self.file_path.read_text(encoding="utf-8"), "{invalid json"
        )

    def test_non_list_json_raises_storage_error(self):
        self.file_path.write_text(
            '{"id": 1}', encoding="utf-8"
        )

        with self.assertRaises(StorageError):
            load_tickets(self.file_path)

    def test_duplicate_ids_raise_storage_error(self):
        duplicate_tickets = [self.tickets[0], self.tickets[0]]

        self.file_path.write_text(
            json.dumps(duplicate_tickets), encoding="utf-8"
        )

        with self.assertRaises(StorageError):
            load_tickets(self.file_path)

    def test_invalid_priority_raises_storage_error(self):
        invalid_tickets = [dict(self.tickets[0])]
        invalid_tickets[0]["priority"] = "low"
        self.file_path.write_text(
            json.dumps(invalid_tickets), encoding="utf-8"
        )

        with self.assertRaises(StorageError):
            load_tickets(self.file_path)

    def test_invalid_data_is_not_saved(self):
        invalid_tickets = [dict(self.tickets[0])]
        invalid_tickets[0]["affected_users"] = 0

        with self.assertRaises(StorageError):
            save_tickets(self.file_path, invalid_tickets)

        self.assertFalse(self.file_path.exists())

    def test_save_failure_raises_storage_error(self):
        destination_is_directory = self.directory / "existing-directory"
        destination_is_directory.mkdir()

        with self.assertRaises(StorageError):
            save_tickets(destination_is_directory, self.tickets)

    def test_ids_remain_available_after_reload(self):
        save_tickets(self.file_path, self.tickets)
        loaded = load_tickets(self.file_path)

        next_id = max(ticket["id"] for ticket in loaded) + 1
        self.assertEqual(next_id, 3)


    def test_notes_persist_after_reload(self):
        ticket = dict(self.tickets[0])
        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "Chika",
                "message": "Network issue investigated",
            }
        ]

        save_tickets(self.file_path, [ticket])
        loaded = load_tickets(self.file_path)

        self.assertEqual(loaded[0]["notes"], ticket["notes"])
    
    def test_legacy_ticket_without_notes_loads(self):
        ticket = dict(self.tickets[0])
        ticket.pop("notes", None)

        self.file_path.write_text(
            json.dumps([ticket]),
            encoding="utf-8",
        )

        loaded = load_tickets(self.file_path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], ticket["id"])
        self.assertNotIn("notes", loaded[0])

    def test_invalid_note_raises_storage_error(self):
        ticket = dict(self.tickets[0])
        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "   ",
                "message": "Network issue investigated",
            }
        ]

        with self.assertRaises(StorageError):
            save_tickets(self.file_path, [ticket])

        self.assertFalse(self.file_path.exists())

    def test_duplicate_note_ids_raise_storage_error(self):
        ticket = dict(self.tickets[0])
        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "Chika",
                "message": "Network issue investigated",
            },
            {
                "note_id": "N001",
                "author": "Alex",
                "message": "Another network issue",
            },
        ]

        with self.assertRaises(StorageError):
            save_tickets(self.file_path, [ticket])

        self.assertFalse(self.file_path.exists())

    def test_note_ids_continue_after_reload(self):
        from campusflow.tickets import add_note

        ticket = dict(self.tickets[0])
        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "Chika",
                "message": "Network issue investigated",
            }
        ]

        save_tickets(self.file_path, [ticket])
        loaded = load_tickets(self.file_path)

        new_note = add_note(
            loaded,
            loaded[0]["id"],
            "Alex",
            "Network issue resolved",
        )

        self.assertEqual(new_note["note_id"], "N002")
    
    def test_ticket_ids_continue_after_reload(self):
        save_tickets(self.file_path, self.tickets)

        loaded = load_tickets(self.file_path)

        new_ticket = create_ticket(
            loaded,
            "Printer unavailable",
            "Hardware",
            "medium",
            5,
        )

        self.assertEqual(new_ticket["id"], 3)
        self.assertEqual(
        [ticket["id"] for ticket in loaded],
        [1, 2, 3],
    )
if __name__ == "__main__":
    unittest.main()
