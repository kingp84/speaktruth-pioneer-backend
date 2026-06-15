import pandas as pd

from directory.models import DirectoryEntry


def parse_directory_excel(path: str) -> None:
    print("DIRECTORY PARSER STARTED:", path)
    df = pd.read_excel(path)

    # Expect columns like: LAST NAME, FIRST NAME, ADDRESS, Home Phone, Cell Phone, ATTENDING, Active, GENDER, Role
    df.columns = [str(c).strip().upper() for c in df.columns]
    print("DIRECTORY COLUMNS:", df.columns)

    for _, row in df.iterrows():
        last_name = str(row.get("LAST NAME", "")).strip()
        first_name = str(row.get("FIRST NAME", "")).strip()
        if not first_name or not last_name:
            continue

        address = str(row.get("ADDRESS", "")).strip()
        home_phone = str(row.get("HOME PHONE", "")).strip()
        cell_phone = str(row.get("CELL PHONE", "")).strip()
        active = str(row.get("ACTIVE", "")).strip().lower()

        status = "ACTIVE" if active == "yes" else "INACTIVE"

        phone = cell_phone or home_phone

        entry, _ = DirectoryEntry.objects.update_or_create(
            first_name__iexact=first_name,
            last_name__iexact=last_name,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "phone": phone,
                "status": status,
                "notes": notes,
                "role": role,
            },
        )

