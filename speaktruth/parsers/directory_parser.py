import pandas as pd
from directory.models import DirectoryEntry

def parse_directory_excel(path: str) -> None:
    print("DIRECTORY PARSER STARTED:", path)

    # Load Excel
    df = pd.read_excel(path)

    # Normalize column names
    df.columns = [str(c).strip().upper() for c in df.columns]
    print("DIRECTORY COLUMNS:", df.columns)

    # Expected columns based on your actual Pioneer Directory.xlsx
    # LAST NAME | FIRST NAME | ADDRESS | PHONE | EMAIL | STATUS | NOTES | ROLE

    for _, row in df.iterrows():
        last_name = str(row.get("LAST NAME", "")).strip()
        first_name = str(row.get("FIRST NAME", "")).strip()

        # Skip rows without names
        if not first_name or not last_name:
            continue

        address = str(row.get("ADDRESS", "")).strip()
        phone = str(row.get("PHONE", "")).strip()
        email = str(row.get("EMAIL", "")).strip()
        status = str(row.get("STATUS", "")).strip()
        notes = str(row.get("NOTES", "")).strip()
        role = str(row.get("ROLE", "")).strip()

        # Create or update DirectoryEntry
        entry, created = DirectoryEntry.objects.update_or_create(
            first_name__iexact=first_name,
            last_name__iexact=last_name,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "phone": phone,
                "email": email,
                "status": status,
                "notes": notes,
                "role": role,
            },
        )

        print(
            f"{'CREATED' if created else 'UPDATED'} DIRECTORY ENTRY:",
            first_name,
            last_name,
        )
