import pandas as pd
from directory.models import DirectoryEntry


def parse_directory_excel(path: str) -> None:
    print("DIRECTORY PARSER STARTED:", path)

    df = pd.read_excel(path)

    # Normalize column names
    df.columns = [str(c).strip().upper() for c in df.columns]
    print("DIRECTORY COLUMNS:", df.columns)

    for _, row in df.iterrows():
        last_name = str(row.get("LAST NAME", "")).strip()
        first_name = str(row.get("FIRST NAME", "")).strip()

        if not first_name or not last_name:
            continue

        address = str(row.get("ADDRESS", "")).strip()
        phone = str(row.get("PHONE", "")).strip()
        email = str(row.get("EMAIL", "")).strip()
        notes = str(row.get("NOTES", "")).strip()
        raw_roles = str(row.get("ROLE", "")).strip()

        # Convert STATUS column ("Yes" / "Inactive") into ACTIVE/INACTIVE
        status_raw = str(row.get("STATUS", "")).strip().lower()
        status = "ACTIVE" if status_raw == "yes" else "INACTIVE"

        # Try to find an existing entry
        entry = DirectoryEntry.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name
        ).first()

        if entry is None:
            entry = DirectoryEntry(
                first_name=first_name,
                last_name=last_name
            )
            created = True
        else:
            created = False

        # Update fields
        entry.address = address
        entry.phone = phone
        entry.email = email
        entry.status = status
        entry.notes = notes
        entry.raw_roles = raw_roles

        entry.save()

        print(
            f"{'CREATED' if created else 'UPDATED'} DIRECTORY ENTRY:",
            first_name,
            last_name
        )
