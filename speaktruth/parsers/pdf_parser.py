import os
import pdfplumber

from assignments.models import Assignment
from speaktruth.parsers.normalize import (
    get_or_create_role,
    find_directory_entry,
    parse_date_from_string,
)


def parse_assignment_pdfs(path: str) -> None:
    filename = os.path.basename(path).lower()
    if "sunday" in filename:
        parse_sunday_pdf(path)
    elif "wednesday" in filename:
        parse_wednesday_pdf(path)
    else:
        # If you ever combine them, you can call both here
        parse_sunday_pdf(path)
        parse_wednesday_pdf(path)


def parse_sunday_pdf(path: str) -> None:
    """
    Expects a table like the one in '7a. July 2026 Sunday.pdf':
    - Columns: Date, Sunday Morning, Sunday Evening
    - Rows: Preaching, Scriptures, Song Leader, Opening Prayer, Closing Prayer
    """
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                _parse_sunday_table(table)


def _parse_sunday_table(table: list[list[str]]) -> None:
    """
    table is a list of rows; each row is a list of cell strings.
    We look for date rows like 'July 5th', then the following role rows.
    """
    current_date = parse_date_from_string(cells[0], default_year=2026)

    for row in table:
        cells = [c.strip() if isinstance(c, str) else "" for c in row]
        if not any(cells):
            continue

        # Date row: e.g. ['July 5th', 'Sunday Morning', 'Sunday Evening']
        if cells[0].lower().startswith("july"):
            current_date = parse_july_date(cells[0])
            continue

        if current_date is None:
            continue

        label = cells[0].rstrip(":")
        morning_name = cells[1] if len(cells) > 1 else ""
        evening_name = cells[2] if len(cells) > 2 else ""

        if not label:
            continue

        # Morning assignment
        if morning_name:
            _create_assignment(
                date=current_date,
                service_type="SUNDAY MORNING",
                role_label=label,
                person_name=morning_name,
            )

        # Evening assignment
        if evening_name:
            _create_assignment(
                date=current_date,
                service_type="SUNDAY EVENING",
                role_label=label,
                person_name=evening_name,
            )


def parse_wednesday_pdf(path: str) -> None:
    """
    Expects a table like '7b. July 2026 Wednesday.pdf':
    - First row: Assignment | July 1st | July 8th
    - First column: Bible Class, Song Leader, Opening Prayer, Invitation, Closing Prayer
    """
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                _parse_wednesday_table(table)


def _parse_wednesday_table(table: list[list[str]]) -> None:
    if not table:
        return

    header = [c.strip() if isinstance(c, str) else "" for c in table[0]]
    # header: ['Assignment', 'July 1st', 'July 8th', ...]
    date_cols = []
    for idx, col in enumerate(header):
        if col.lower().startswith("july"):
            date_cols.append((idx, parse_date_from_string(col, default_year=2026)))

    # For each subsequent row, first cell is role label, others are names
    for row in table[1:]:
        cells = [c.strip() if isinstance(c, str) else "" for c in row]
        if not any(cells):
            continue

        label = cells[0].rstrip(":")
        if not label or label.lower() == "assignment":
            continue

        for col_idx, date in date_cols:
            if col_idx >= len(cells):
                continue
            name = cells[col_idx]
            if not name or name.lower().startswith("singing night"):
                continue

            _create_assignment(
                date=date,
                service_type="WEDNESDAY EVENING",
                role_label=label,
                person_name=name,
            )


def _create_assignment(date, service_type, role_label, person_name) -> None:
    role = get_or_create_role(role_label)
    person = find_directory_entry(person_name)
    if person is None:
        # You might want to log this somewhere
        return

    Assignment.objects.update_or_create(
        date=date,
        service_type=service_type,
        role=role,
        defaults={
            "person": person,
        },
    )
