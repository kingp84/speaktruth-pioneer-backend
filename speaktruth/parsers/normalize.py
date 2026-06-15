import datetime
from difflib import get_close_matches

from directory.models import DirectoryEntry, Role


ROLE_MAP = {
    "Song Learder": "Song Leader",
    "Song Leader": "Song Leader",
    "Invidation": "Invitation",
    "Invitation": "Invitation",
    "Scriptures": "Scripture Reading",
    "Scripture": "Scripture Reading",
    "Scripture Reading": "Scripture Reading",
    "Opening Prayer": "Opening Prayer",
    "Closing Prayer": "Closing Prayer",
    "Bible Class": "Bible Class",
    "Preaching": "Preaching",
}

NAME_FIXES = {
    "Charley Nutley": "Charlie Nutley",
}


def normalize_role_name(raw: str) -> str:
    raw = (raw or "").strip()
    return ROLE_MAP.get(raw, raw)


def normalize_person_name(raw: str) -> str:
    raw = (raw or "").strip()
    if raw in NAME_FIXES:
        return NAME_FIXES[raw]
    return raw


def get_or_create_role(raw_name: str) -> Role:
    name = normalize_role_name(raw_name)
    role, _ = Role.objects.get_or_create(name=name)
    return role


def find_directory_entry(full_name: str) -> DirectoryEntry | None:
    full_name = normalize_person_name(full_name)
    if not full_name:
        return None

    parts = full_name.split()
    if len(parts) == 1:
        first_name = parts[0]
        candidates = DirectoryEntry.objects.filter(first_name__iexact=first_name)
        return candidates.first() if candidates.exists() else None

    first_name = parts[0]
    last_name = parts[-1]

    qs = DirectoryEntry.objects.filter(
        first_name__iexact=first_name, last_name__iexact=last_name
    )
    if qs.exists():
        return qs.first()

    all_names = [
        (f"{d.first_name} {d.last_name}", d.id)
        for d in DirectoryEntry.objects.all()
    ]
    labels = [n for n, _ in all_names]
    matches = get_close_matches(full_name, labels, n=1, cutoff=0.8)
    if matches:
        match_label = matches[0]
        for label, pk in all_names:
            if label == match_label:
                return DirectoryEntry.objects.get(pk=pk)
    return None


import datetime
import re

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def parse_date_from_string(raw: str, default_year: int = None) -> datetime.date:
    """
    Parses dates like:
    - 'July 5th'
    - 'June 1'
    - 'Aug 12th'
    - 'September 3'
    - 'July 29th'
    - 'July 1st'

    If no year is present, uses default_year or current year.
    """

    if not raw:
        raise ValueError("Empty date string")

    raw = raw.strip().lower()

    # Extract month
    month = None
    for key, value in MONTH_MAP.items():
        if raw.startswith(key):
            month = value
            break

    if not month:
        raise ValueError(f"Could not parse month from: {raw}")

    # Extract day (strip st/nd/rd/th)
    match = re.search(r"(\d+)", raw)
    if not match:
        raise ValueError(f"Could not parse day from: {raw}")

    day = int(match.group(1))

    # Extract year if present
    match_year = re.search(r"(20\d{2})", raw)
    if match_year:
        year = int(match_year.group(1))
    else:
        year = default_year or datetime.date.today().year

    return datetime.date(year, month, day)

