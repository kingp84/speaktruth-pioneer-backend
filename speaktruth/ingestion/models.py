from django.db import models


class AssignmentUpload(models.Model):
    file = models.FileField(upload_to="uploads/assignments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Assignment Sheet: {self.file.name}"


class DirectoryUpload(models.Model):
    file = models.FileField(upload_to="uploads/directory/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Directory Sheet: {self.file.name}"


class RolesUpload(models.Model):
    file = models.FileField(upload_to="uploads/roles/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Roles Sheet: {self.file.name}"
