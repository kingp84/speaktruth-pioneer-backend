import pandas as pd

from directory.models import Role
from speaktruth.parsers.normalize import normalize_role_name


def parse_roles_excel(path: str) -> None:
    print("ROLES PARSER STARTED:", path)
    df = pd.read_excel(path, sheet_name=0)

    df.columns = [str(c).strip().upper() for c in df.columns]

    for _, row in df.iterrows():
        raw_role = str(row.get("ROLE", "")).strip()
        if not raw_role:
            continue

        name = normalize_role_name(raw_role)

        gender_col = str(row.get("ASSIGNED TO: MALE, FEMALE, FAMILY", "")).strip().upper()
        if "FAMILY" in gender_col:
            gender_restriction = "FAMILY"
        elif "MALE" in gender_col or "MEN" in gender_col:
            gender_restriction = "MEN"
        elif "FEMALE" in gender_col or "WOMEN" in gender_col:
            gender_restriction = "WOMEN"
        else:
            gender_restriction = "ANY"

        role, _ = Role.objects.update_or_create(
            name=name,
            defaults={
                "gender_restriction": gender_restriction,
            },
        )


