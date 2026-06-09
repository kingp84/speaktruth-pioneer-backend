from django.db import models
from directory.models import DirectoryEntry, Role

class Assignment(models.Model):
    SERVICE_TYPES = [
        ('MONTHLY', 'Monthly Assignment'),
        ('SUN_AM', 'Sunday Morning'),
        ('SUN_PM', 'Sunday Evening'),
        ('WED_PM', 'Wednesday Evening'),
    ]

    date = models.DateField()
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPES)
    notes = models.TextField(blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    person = models.ForeignKey(DirectoryEntry, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - {self.get_service_type_display()} - {self.role.name} - {self.person}"
