from django.contrib import admin
from .models import Project, Technician, ProjectNote

class ProjectAdmin(admin.ModelAdmin):
    list_display=('title', 'technician', 'is_complete')
    fields=(
        'title',
        'description',
        'priority',
        'technician',
        'begin',
        'is_complete',
        'completion_notes',
        'recipient_emails'
    )

admin.site.register(Project, ProjectAdmin)

class TechnicianAdmin(admin.ModelAdmin):
    list_display=('name', 'user')

admin.site.register(Technician, TechnicianAdmin)

admin.site.register(ProjectNote)
