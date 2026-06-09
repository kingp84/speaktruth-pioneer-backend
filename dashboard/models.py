from django.db import models

class ServiceNotes(models.Model):
    song_leader_note = models.TextField(default="Song Leader gives announcements.")
    preacher_note = models.TextField(default="Sunday Preacher gives Scripture Reader the passage.")

    def __str__(self):
        return "Service Notes"
