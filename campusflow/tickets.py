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
        "assigned_to": None
    }

    tickets.append(ticket)
    return ticket

def search_tickets(
    tickets,
    query="",
    status=None,
    priority=None,
    category=None,
):
    """Search tickets using text and optional filters."""

    if not isinstance(query, str):
        raise ValueError("Search query must be a string")

    query = query.strip().casefold()

    filters = {
        "status": status,
        "priority": priority,
        "category": category,
    }

    for field, value in filters.items():
        if value is not None:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field.title()} filter must be a non-empty string"
                )
            filters[field] = value.strip().casefold()

    results = []

    for ticket in tickets:
        searchable_text = " ".join(
            str(ticket.get(field) or "")
            for field in (
                "id",
                "title",
                "category",
                "urgency",
                "priority",
                "status",
                "assigned_to",
            )
        ).casefold()

        if query and query not in searchable_text:
            continue

        if any(
            value is not None
            and str(ticket.get(field) or "").casefold() != value
            for field, value in filters.items()
        ):
            continue

        results.append(ticket)

    return results