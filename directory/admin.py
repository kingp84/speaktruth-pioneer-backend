from django.contrib import admin
from .models import DirectoryEntry, Role

admin.site.register(Role)

@admin.register(DirectoryEntry)
class DirectoryEntryAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'status')
    list_filter = ("status",)
    search_fields = ('first_name', 'last_name', 'phone', 'email')
