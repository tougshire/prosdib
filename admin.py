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
        'completion_notes',
        'recipient_emails'
    )

admin.site.register(Project, ProjectAdmin)

class TechnicianAdmin(admin.ModelAdmin):
    list_display=('name', 'user')

admin.site.register(Technician, TechnicianAdmin)

admin.site.register(ProjectNote)

admin.site.register(Status)
