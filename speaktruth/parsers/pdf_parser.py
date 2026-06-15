import pdfplumber
import re
from datetime import datetime
from directory.models import DirectoryEntry, Role
from assignments.models import Assignment


def find_person(name):
    name = name.strip()
    parts = name.split()
    if len(parts) < 2:
        return None
    first, last = parts[0], parts[-1]
    return DirectoryEntry.objects.filter(
        first_name__iexact=first,
        last_name__iexact=last
    ).first()


def find_role(role_name):
    return Role.objects.filter(name__iexact=role_name.strip()).first()


def parse_date(text, year):
    match = re.search(r"([A-Za-z]+)\s+(\d+)(?:st|nd|rd|th)", text)
    if not match:
        return None
    month = match.group(1)
    day = int(match.group(2))
    return datetime.strptime(f"{month} {day} {year}", "%B %d %Y").date()


def parse_assignment_pdfs(path):
    print("ASSIGNMENT PARSER STARTED:", path)

    filename = path.lower()
    is_sunday = "sunday" in filename
    is_wednesday = "wednesday" in filename

    # Extract month + year from filename
    match = re.search(r"([A-Za-z]+)\s+(\d{4})", filename)
    if not match:
        print("ERROR: Could not extract month/year from filename.")
        return

    month_name = match.group(1).capitalize()
    year = int(match.group(2))

    # Extract text
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # -----------------------------
    # MONTHLY ASSIGNMENTS (Sunday PDF only)
    # -----------------------------
    if is_sunday:
        for line in lines:
            if ":" in line and "June" not in line and "Sunday" not in line:
                role_name, person_name = line.split(":", 1)
                role = find_role(role_name)
                person = find_person(person_name)
                if role and person:
                    Assignment.objects.update_or_create(
                        date=datetime.strptime(f"{month_name} 1 {year}", "%B %d %Y").date(),
                        service_type="MONTHLY",
                        role=role,
                        defaults={"person": person},
                    )
                    print("MONTHLY:", role_name, "→", person_name)

    # -----------------------------
    # WEEKLY ASSIGNMENTS
    # -----------------------------
    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect date header
        if re.search(r"[A-Za-z]+\s+\d+(?:st|nd|rd|th)", line):
            date_obj = parse_date(line, year)
            if not date_obj:
                i += 1
                continue

            if is_sunday:
                # Expect: "June 7th Sunday Morning Sunday Evening"
                if "Sunday Morning" not in line or "Sunday Evening" not in line:
                    i += 1
                    continue

                # Next 5 rows are role rows
                for j in range(1, 6):
                    if i + j >= len(lines):
                        break

                    row = lines[i + j]
                    if ":" not in row:
                        continue

                    role_name, rest = row.split(":", 1)
                    parts = rest.strip().split()

                    if len(parts) < 2:
                        continue

                    morning_name = " ".join(parts[0:2])
                    evening_name = " ".join(parts[2:4]) if len(parts) >= 4 else None

                    role = find_role(role_name)
                    morning_person = find_person(morning_name)
                    evening_person = find_person(evening_name) if evening_name else None

                    if role and morning_person:
                        Assignment.objects.update_or_create(
                            date=date_obj,
                            service_type="SUNDAY MORNING",
                            role=role,
                            defaults={"person": morning_person},
                        )
                        print(date_obj, "| SUNDAY MORNING |", role_name, "→", morning_name)

                    if role and evening_person:
                        Assignment.objects.update_or_create(
                            date=date_obj,
                            service_type="SUNDAY EVENING",
                            role=role,
                            defaults={"person": evening_person},
                        )
                        print(date_obj, "| SUNDAY EVENING |", role_name, "→", evening_name)

                i += 6
                continue

            # -----------------------------
            # WEDNESDAY
            # -----------------------------
            if is_wednesday:
                # Next 5 rows are role rows
                for j in range(1, 6):
                    if i + j >= len(lines):
                        break

                    row = lines[i + j]
                    if ":" not in row:
                        continue

                    role_name, person_name = row.split(":", 1)
                    role = find_role(role_name)
                    person = find_person(person_name)

                    if role and person:
                        Assignment.objects.update_or_create(
                            date=date_obj,
                            service_type="WEDNESDAY EVENING",
                            role=role,
                            defaults={"person": person},
                        )
                        print(date_obj, "| WEDNESDAY EVENING |", role_name, "→", person_name)

                i += 6
                continue

        i += 1
