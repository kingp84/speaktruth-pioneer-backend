import pdfplumber
import re
from datetime import datetime
from directory.models import DirectoryEntry, Role
from assignments.models import Assignment


# -----------------------------
# Helpers
# -----------------------------

def parse_date_from_header(text, year):
    """
    Extracts dates like 'June 7th' and returns a Python date.
    """
    match = re.search(r"([A-Za-z]+)\s+(\d+)(?:st|nd|rd|th)", text)
    if not match:
        return None

    month_name = match.group(1)
    day = int(match.group(2))

    try:
        return datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y").date()
    except:
        return None


def find_person(name):
    """
    Match a person in DirectoryEntry by first + last name.
    """
    parts = name.strip().split()
    if len(parts) < 2:
        return None

    first, last = parts[0], parts[-1]

    return DirectoryEntry.objects.filter(
        first_name__iexact=first,
        last_name__iexact=last
    ).first()


def find_role(role_name):
    """
    Match a Role object by exact name.
    """
    return Role.objects.filter(name__iexact=role_name.strip()).first()


# -----------------------------
# MAIN PARSER
# -----------------------------

def parse_assignment_pdfs(path):
    print("ASSIGNMENT PARSER STARTED:", path)

    # Determine if this is Sunday or Wednesday
    filename = path.lower()

    if "sunday" in filename:
        service_type_map = {
            "morning": "SUNDAY MORNING",
            "evening": "SUNDAY EVENING",
        }
        is_sunday = True
        is_wednesday = False

    elif "wednesday" in filename:
        service_type_map = {
            "evening": "WEDNESDAY EVENING",
        }
        is_sunday = False
        is_wednesday = True

    else:
        print("ERROR: Could not determine Sunday/Wednesday from filename.")
        return

    # Extract month + year from filename
    match = re.search(r"([A-Za-z]+)\s+(\d{4})", filename)
    if not match:
        print("ERROR: Could not extract month/year from filename.")
        return

    month_name = match.group(1).capitalize()
    year = int(match.group(2))

    # -----------------------------
    # Extract PDF text
    # -----------------------------
    with pdfplumber.open(path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # -----------------------------
    # Parse Monthly Assignments (Sunday PDF only)
    # -----------------------------
    if is_sunday:
        monthly_section = re.search(
            r"MONTHLY ASSIGNMENTS(.*?)# WEEKLY ASSIGNMENTS",
            full_text,
            re.DOTALL | re.IGNORECASE
        )

        if monthly_section:
            lines = monthly_section.group(1).split("\n")
            for line in lines:
                if ":" not in line:
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
    # Parse Weekly Assignments
    # -----------------------------
    # Find all date headers like "June 7th"
    date_headers = re.findall(r"([A-Za-z]+\s+\d+(?:st|nd|rd|th))", full_text)

    for header in date_headers:
        date_obj = parse_date_from_header(header, year)
        if not date_obj:
            continue

        # Extract the block of text for this date
        pattern = header + r"(.*?)(?:June|\Z)"
        block_match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)

        if not block_match:
            continue

        block = block_match.group(1)

        # Determine service types
        if is_sunday:
            services = {
                "morning": "SUNDAY MORNING",
                "evening": "SUNDAY EVENING",
            }
        else:
            services = {
                "evening": "WEDNESDAY EVENING",
            }

        # Parse role → person pairs
        pairs = re.findall(r"([A-Za-z ]+):\s*([A-Za-z ]+)", block)

        for role_name, person_name in pairs:
            role = find_role(role_name)
            person = find_person(person_name)

            if not role or not person:
                continue

            # Determine service type
            if is_sunday:
                # Sunday PDFs alternate Morning/Evening in order
                # We detect based on the order in the table
                # First half = morning, second half = evening
                # But simplest: check the block text
                if "Sunday Morning" in block:
                    service_type = "SUNDAY MORNING"
                elif "Sunday Evening" in block:
                    service_type = "SUNDAY EVENING"
                else:
                    # fallback: morning first
                    service_type = "SUNDAY MORNING"
            else:
                service_type = "WEDNESDAY EVENING"

            Assignment.objects.update_or_create(
                date=date_obj,
                service_type=service_type,
                role=role,
                defaults={"person": person},
            )

            print(f"{date_obj} | {service_type} | {role_name} → {person_name}")
