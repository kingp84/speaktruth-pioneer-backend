from django.contrib import admin
from .models import DirectoryEntry, Role

admin.site.register(Role)

@admin.register(DirectoryEntry)
class DirectoryEntryAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'family_name', 'phone','email', 'address')
    list_filter = ("status",)
    search_fields = ('last_name', 'first_name', 'family_name', 'phone', 'email', 'address')
