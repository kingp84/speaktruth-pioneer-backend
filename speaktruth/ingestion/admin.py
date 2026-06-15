from django.contrib import admin
from .models import AssignmentUpload, DirectoryUpload, RolesUpload
from speaktruth.parsers.pdf_parser import parse_assignment_pdfs
from speaktruth.parsers.directory_parser import parse_directory_excel
from speaktruth.parsers.roles_parser import parse_roles_excel

@admin.action(description="Process selected assignment PDFs")
def process_assignments(modeladmin, request, queryset):
    for upload in queryset:
        parse_assignment_pdfs(upload.file.path)
        upload.processed = True
        upload.save()

@admin.action(description="Process selected directory files")
def process_directory(modeladmin, request, queryset):
    for upload in queryset:
        parse_directory_excel(upload.file.path)
        upload.processed = True
        upload.save()
    print("DIRECTORY ACTION FIRED:", upload.file.path)

@admin.action(description="Process selected roles files")
def process_roles(modeladmin, request, queryset):
    for upload in queryset:
        parse_roles_excel(upload.file.path)
        upload.processed = True
        upload.save()

@admin.register(AssignmentUpload)
class AssignmentUploadAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at", "processed")
    actions = [process_assignments]

@admin.register(DirectoryUpload)
class DirectoryUploadAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at", "processed")
    actions = [process_directory]

@admin.register(RolesUpload)
class RolesUploadAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at", "processed")
    actions = [process_roles]
