
#JSON persistence for CampusFlow tickets.

import json
import os
import tempfile
from pathlib import Path

from .tickets import calculate_priority


class StorageError(Exception):
    """Raised when ticket data cannot be safely loaded or saved."""


REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}

VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
VALID_URGENCIES = {"low", "medium", "high"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}
VALID_STATUSES = {"open", "in_progress", "resolved"}


def _validate_tickets(tickets):
    #Reject invalid records before loading or saving them.
    if not isinstance(tickets, list):
        raise StorageError("Ticket data must be a JSON list.")

    seen_ids = set()

    for index, ticket in enumerate(tickets):
        location = f"Ticket at index {index}"

        if not isinstance(ticket, dict):
            raise StorageError(f"{location} must be an object.")

        missing = REQUIRED_FIELDS - ticket.keys()
        if missing:
            fields = ", ".join(sorted(missing))
            raise StorageError(f"{location} is missing fields: {fields}.")

        ticket_id = ticket["id"]
        if (
            isinstance(ticket_id, bool)
            or not isinstance(ticket_id, int)
            or ticket_id <= 0
        ):
            raise StorageError(
                f"{location} has an invalid positive integer ID."
            )

        if ticket_id in seen_ids:
            raise StorageError(
                f"Duplicate ticket ID {ticket_id} in stored data."
            )
        seen_ids.add(ticket_id)

        if not isinstance(ticket["title"], str) or not ticket["title"].strip():
            raise StorageError(f"{location} has an invalid title.")

        if ticket["category"] not in VALID_CATEGORIES:
            raise StorageError(f"{location} has an invalid category.")

        if ticket["urgency"] not in VALID_URGENCIES:
            raise StorageError(f"{location} has an invalid urgency.")

        users = ticket["affected_users"]
        if (
            isinstance(users, bool)
            or not isinstance(users, int)
            or users <= 0
        ):
            raise StorageError(
                f"{location} has an invalid affected_users value."
            )

        if ticket["priority"] not in VALID_PRIORITIES:
            raise StorageError(f"{location} has an invalid priority.")

        expected_priority = calculate_priority(ticket["urgency"], users)
        if ticket["priority"] != expected_priority:
            raise StorageError(
                f"{location} has priority {ticket['priority']!r}; "
                f"expected {expected_priority!r}."
            )

        if ticket["status"] not in VALID_STATUSES:
            raise StorageError(f"{location} has an invalid status.")

        assigned_to = ticket["assigned_to"]
        if assigned_to is not None and (
            not isinstance(assigned_to, str) or not assigned_to.strip()
        ):
            raise StorageError(
                f"{location} has an invalid assigned_to value."
            )

            # Validate notes when present. Older tickets may not have this field.
        notes = ticket.get("notes", [])

        if not isinstance(notes, list):
            raise StorageError(
                f"{location} has an invalid notes field."
            )

        seen_note_ids = set()

        for note_index, note in enumerate(notes):
            note_location = (
                f"{location}, note at index {note_index}"
            )

            if not isinstance(note, dict):
                raise StorageError(
                    f"{note_location} must be an object."
                )

            required_note_fields = {"note_id", "author", "message"}
            missing_note_fields = required_note_fields - note.keys()

            if missing_note_fields:
                fields = ", ".join(sorted(missing_note_fields))
                raise StorageError(
                    f"{note_location} is missing fields: {fields}."
                )

            note_id = note["note_id"]

            if (
                not isinstance(note_id, str)
                or not note_id.startswith("N")
                or len(note_id[1:]) < 3
                or not note_id[1:].isdigit()
            ):
                raise StorageError(
                    f"{note_location} has an invalid note ID."
                )

            if note_id in seen_note_ids:
                raise StorageError(
                    f"Duplicate note ID {note_id} within ticket "
                    f"{ticket['id']}."
                )

            seen_note_ids.add(note_id)

            author = note["author"]

            if not isinstance(author, str) or not author.strip():
                raise StorageError(
                    f"{note_location} has an invalid author."
                )

            message = note["message"]

            if (
                not isinstance(message, str)
                or not 5 <= len(message.strip()) <= 300
            ):
                raise StorageError(
                    f"{note_location} has an invalid message. "
                    "Messages must contain 5 to 300 characters."
                )

def load_tickets(path):
    # Load and validate tickets; a missing file means a fresh start.
    file_path = Path(path)

    try:
        with file_path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise StorageError(
            f"Cannot read ticket data from {file_path}: invalid JSON."
        ) from exc
    except OSError as exc:
        raise StorageError(
            f"Cannot read ticket data from {file_path}: {exc}"
        ) from exc

    _validate_tickets(tickets)
    return tickets


def save_tickets(path, tickets):
    #Validate and atomically save tickets as JSON.
    _validate_tickets(tickets)
    file_path = Path(path)
    temporary_path = None

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(tickets, temporary_file, indent=2, ensure_ascii=False)
            temporary_file.write("\n")

        os.replace(temporary_path, file_path)
    except (OSError, TypeError, ValueError) as exc:
        raise StorageError(
            f"Cannot save ticket data to {file_path}: {exc}"
        ) from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
