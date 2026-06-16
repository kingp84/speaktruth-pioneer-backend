from django.contrib import admin, messages
from .models import AssignmentUpload, DirectoryUpload, RolesUpload

from speaktruth.parsers.txt_parser import parse_assignment_txt
from speaktruth.parsers.directory_parser import parse_directory_excel
from speaktruth.parsers.roles_parser import parse_roles_excel


# -----------------------------
# ASSIGNMENTS INGESTION
# -----------------------------
@admin.action(description="Process selected assignment files")
def process_assignment_files(modeladmin, request, queryset):
    for upload in queryset:
        file_path = upload.file.path

        if not file_path.lower().endswith(".txt"):
            messages.error(request, f"{upload.file.name} is not a .txt file.")
            continue

        try:
            parse_assignment_txt(file_path)
            upload.processed = True
            upload.save()
            messages.success(request, f"Successfully processed {upload.file.name}")
        except Exception as e:
            messages.error(request, f"Error processing {upload.file.name}: {e}")

class AssignmentUploadAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at", "processed")
    actions = [process_assignment_files]

admin.site.register(AssignmentUpload, AssignmentUploadAdmin)


# -----------------------------
# DIRECTORY INGESTION
# -----------------------------
@admin.action(description="Process selected directory files")
def process_directory(modeladmin, request, queryset):
    for upload in queryset:
        print("DIRECTORY ACTION FIRED:", upload.file.path)
        parse_directory_excel(upload.file.path)
        upload.processed = True
        upload.save()


@admin.register(DirectoryUpload)
class DirectoryUploadAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at", "processed")
    actions = [process_directory]


# -----------------------------
# ROLES INGESTION
# -----------------------------
@admin.action(description="Process selected roles files")
def process_roles(modeladmin, request, queryset):
    for upload in queryset:
        print("ROLES ACTION FIRED:", upload.file.path)
        parse_roles_excel(upload.file.path)
        upload.processed = True
        upload.save()


@admin.register(RolesUpload)
class RolesUploadAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at", "processed")
    actions = [process_roles]
