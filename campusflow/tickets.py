#Tickets creation, validation, lookup and priority calculation.

CATEGORIES = {
    "network": "Network",
    "hardware": "Hardware",
    "software": "Software",
    "other": "Other",
}


URGENCIES = {"low", "medium", "high"}

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def _normalize_choice(value, allowed, field_name):
    #Normalize a string choice or reject an invalid value.
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    normalized = value.strip().casefold()

    if normalized not in allowed:
        choices = ", ".join(sorted(allowed.values()) if isinstance(
            allowed, dict
        ) else sorted(allowed))
        raise ValueError(
            f"Invalid {field_name}. Choose one of: {choices}."
        )
    return allowed[normalized] if isinstance(allowed, dict) else normalized


def _validate_affected_users(affected_users):
    #Require a positive whole-number count, excluding booleans
    if (
        isinstance(affected_users, bool)
        or not isinstance(affected_users, int)
        or affected_users <= 0
    ):
        raise ValueError("Affected users must be a positive whole number")


def calculate_priority(urgency, affected_users):
    #Calculate priority using the agreed rule precedence.
    _normalize_urgency = _normalize_choice(
        urgency, {value: value for value in URGENCIES}, "urgency"
    )
    _validate_affected_users(affected_users)

    if _normalize_urgency == "high" and affected_users >= 10:
        return "critical"

    if _normalize_urgency == "high" or affected_users >= 10:
        return "high"

    if _normalize_urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def get_next_ticket_id(tickets):
    #Return the next ID after the largest existing tickets Id
    existing_ids = [
        ticket["id"]
        for ticket in tickets
        if isinstance(ticket.get("id"), int)
        and not isinstance(ticket.get("id"), bool)
        and ticket["id"] > 0
    ]

    return max(existing_ids, default=0) + 1


def find_ticket(tickets, ticket_id):
    #Find a ticket by ID or raise KeyError
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise KeyError(f"Ticket")


def search_tickets(
    tickets,
    query="",
    status=None,
    priority=None,
    category=None,
):
    """Search tickets by text and optional AND-combined filters."""
    if not isinstance(query, str):
        raise ValueError("Search query must be text.")

    filters = {
        "status": status,
        "priority": priority,
        "category": category,
    }
    for name, value in filters.items():
        if value is not None and (
            not isinstance(value, str) or not value.strip()
        ):
            raise ValueError(f"{name.title()} filter must be nonblank text.")

    normalized_query = query.strip().casefold()
    results = []

    for ticket in tickets:
        searchable_text = " ".join(
            str(ticket.get(field, ""))
            for field in ("title", "category")
        ).casefold()

        if normalized_query and normalized_query not in searchable_text:
            continue
        if status is not None and str(ticket.get("status", "")).casefold() != status.strip().casefold():
            continue
        if priority is not None and str(ticket.get("priority", "")).casefold() != priority.strip().casefold():
            continue
        if category is not None and str(ticket.get("category", "")).casefold() != category.strip().casefold():
            continue

        results.append(ticket)

    return results

def create_ticket(tickets, title, category, urgency, affected_users):
    #Validate and  append a new ticket, rteturning the new record.
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Ticket title cannot be blank")

    _normalize_category = _normalize_choice(category, CATEGORIES, "category")

    _normalize_urgency = _normalize_choice(urgency, {value: value for value in URGENCIES}, "urgency")

    _validate_affected_users(affected_users)

    priority = calculate_priority(_normalize_urgency, affected_users)

    ticket = {
        "id": get_next_ticket_id(tickets),
        "title": title.strip(),
        "category": _normalize_category,
        "urgency": _normalize_urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": []
    }

    tickets.append(ticket)
    return ticket


def add_note(tickets, ticket_id, author, message):
    """Add a note to an open or in-progress ticket."""
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] not in ("open", "in_progress"):
        raise ValueError("Notes can only be added to open or in-progress tickets.")

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author cannot be blank.")

    if not isinstance(message, str):
        raise ValueError("Note message must be text.")

    author = author.strip()
    message = message.strip()

    if not 5 <= len(message) <= 300:
        raise ValueError("Note message must contain 5 to 300 characters.")

    notes = ticket.setdefault("notes", [])

    note_numbers = [
    int(note["note_id"][1:])
    for note in notes
    if isinstance(note.get("note_id"), str)
    and note["note_id"].startswith("N")
    and note["note_id"][1:].isdigit()
    ]

    note_id = f"N{max(note_numbers, default=0) + 1:03d}"

    note = {
        "note_id": note_id,
        "author": author,
        "message": message,
    }

    notes.append(note)
    return note