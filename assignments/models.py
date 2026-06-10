from django.db import models
from directory.models import DirectoryEntry, Role


class Assignment(models.Model):
    SERVICE_TYPES = [
        ('MONTHLY', 'Monthly Assignment'),
        ('Sunday Morning', 'Sunday Morning'),
        ('Sunday Evening', 'Sunday Evening'),
        ('Wednesday Evening', 'Wednesday Evening'),
    ]

    date = models.DateField()
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPES)
    notes = models.TextField(blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    person = models.ForeignKey(DirectoryEntry, on_delete=models.CASCADE)

    class Meta:
        ordering = ["date", "service_type", "role"]
        unique_together = ("date", "service_type", "role")
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return f"{self.date} - {self.get_service_type_display()} - {self.role.name} - {self.person}"

    @property
    def is_sunday(self):
        return self.service_type in ["Sunday Morning", "Sunday Evening"]

    @property
    def is_wednesday(self):
        return self.service_type == "Wednesday Evening"

    @property
    def is_monthly(self):
        return self.service_type == "MONTHLY"
