from django.db import models


class ServiceNotes(models.Model):
    song_leader_note = models.TextField(
        default="Song Leader is responsible for any opening announcements."
    )
    preacher_note = models.TextField(
        default="Selected speaker is to select the Scripture Reading and give it to the reader."
    )

    def __str__(self):
        return "Service Notes"


class Role(models.Model):
    name = models.CharField(max_length=100)

    # Who is allowed to perform this role
    gender_restriction = models.CharField(
        max_length=10,
        choices=[
            ("MEN", "Male"),
            ("WOMEN", "Female"),
            ("FAMILY", "Family"),
        ],
        default="MEN",
    )

    # Permanent assignments (Steve, Gwen)
    permanently_assigned_to = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "If this role is always done by one person "
            "(e.g., Steve Hickman), enter their name here."
        ),
    )

    def __str__(self):
        return self.name


class DirectoryEntry(models.Model):
    # Basic identity
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    # Contact info
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)

    # Member status
    MEMBER_STATUS = [
        ("ACTIVE", "Active Member"),
        ("INACTIVE", "Inactive Member"),
    ]
    status = models.CharField(max_length=10, choices=MEMBER_STATUS, default="ACTIVE")

    # Roles they are willing to do
    roles = models.ManyToManyField(Role, blank=True)

    # Notes (for special instructions)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
