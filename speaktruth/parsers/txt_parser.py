import re
from datetime import datetime
from directory.models import DirectoryEntry, Role
from assignments.models import Assignment

print("### USING NEW TXT PARSER ###")

# -----------------------------
# HELPERS
# -----------------------------

def find_person(name):
    if not name:
        return None
    name = name.strip()
    if name.lower() == "singing night":
        return None
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

# -----------------------------
# MAIN PARSER
# -----------------------------

def parse_assignment_txt(path):
    print("TXT ASSIGNMENT PARSER STARTED:", path)

    filename = path.lower()
    is_sunday = "sunday" in filename
    is_wednesday = "wednesday" in filename

    # Read text file
    with open(path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Extract month + year from header line
    month_line = None
    for line in lines:
        if re.search(r"[A-Za-z]+\s+\d{4}", line):
            month_line = line
            break

    if not month_line:
        print("ERROR: Could not find month/year in file.")
        return

    month_name, year = month_line.split()
    year = int(year)

    # -----------------------------
    # SUNDAY MONTHLY ASSIGNMENTS
    # -----------------------------
    if is_sunday:
        monthly_section = False
        for line in lines:

            if "MONTHLY ASSIGNMENTS" in line.upper():
                monthly_section = True
                continue

            if monthly_section:
                if ":" not in line:
                    monthly_section = False
                    continue

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
    # SUNDAY WEEKLY ASSIGNMENTS
    # -----------------------------
    if is_sunday:
        i = 0
        while i < len(lines):
            line = lines[i]

            if "Sunday Morning" in line and "Sunday Evening" in line:
                date_obj = parse_date(line, year)
                if not date_obj:
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
                    evening_person = find_person(evening_name)

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

            i += 1

    # -----------------------------
    # WEDNESDAY ASSIGNMENTS
    # -----------------------------
    if is_wednesday:
        i = 0
        while i < len(lines):
            line = lines[i]

            # Detect table header: starts with "Assignment"
            if line.startswith("Assignment"):
                parts = line.split()

                # Extract dates
                # Example: ["Assignment", "June", "3rd", "June", "10th"]
                date1 = parse_date(" ".join(parts[1:3]), year)

                date2 = None
                if len(parts) >= 5:
                    date2 = parse_date(" ".join(parts[3:5]), year)

                print("WEDNESDAY TABLE:", date1, date2)

                # Next 5 rows are role rows
                for j in range(1, 6):
                    if i + j >= len(lines):
                        break

                    row = lines[i + j]
                    if ":" not in row:
                        continue

                    # Split role from the two columns
                    role_name, rest = row.split(":", 1)
                    parts = rest.strip().split()

                    # Column 1 person
                    col1 = " ".join(parts[0:2]) if len(parts) >= 2 else None
                    # Column 2 person (optional)
                    col2 = " ".join(parts[2:4]) if len(parts) >= 4 else None

                    role = find_role(role_name)
                    p1 = find_person(col1)
                    p2 = find_person(col2)

                    # Save first date
                    if role and p1 and date1:
                        Assignment.objects.update_or_create(
                            date=date1,
                            service_type="WEDNESDAY EVENING",
                            role=role,
                            defaults={"person": p1},
                        )
                        print(date1, "| WEDNESDAY |", role_name, "→", col1)

                    # Save second date (if exists)
                    if role and p2 and date2:
                        Assignment.objects.update_or_create(
                            date=date2,
                            service_type="WEDNESDAY EVENING",
                            role=role,
                            defaults={"person": p2},
                        )
                        print(date2, "| WEDNESDAY |", role_name, "→", col2)

                i += 6
                continue

            i += 1

