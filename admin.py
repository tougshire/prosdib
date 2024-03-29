from django.contrib import admin
from .models import Project, Technician, ProjectNote, Status

class ProjectAdmin(admin.ModelAdmin):
    list_display=('title', 'technician', 'status',)
    fields=(
        'title',
        'description',
        'priority',
        'technician',
        'created_by',
        'begin',
        'status',
        'recipient_emails'
    )

admin.site.register(Project, ProjectAdmin)

class TechnicianAdmin(admin.ModelAdmin):
    list_display=('name', 'user')

admin.site.register(Technician, TechnicianAdmin)

admin.site.register(ProjectNote)

class StatusAdmin(admin.ModelAdmin):
    list_display=('name', 'is_active', 'is_default',)

admin.site.register(Status, StatusAdmin)
