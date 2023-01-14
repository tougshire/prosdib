from django.db import models
from django.conf import settings
from datetime import datetime
from django.apps import apps
from libtekin.models import Item, Location
from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Q, Subquery


def get_default_status():
    try:
        return Status.objects.filter(is_default=True).first().pk
    except AttributeError:
        return None

class Status(models.Model):
    name = models.CharField(
        'name',
        max_length=50,
        blank=True,
        help_text='The name of the technician'
    )
    list_position = models.IntegerField(
        'list position',
        default = 10000,
        help_text = 'The position of this status in a list, not sorted by other fields'
    )
    is_active = models.BooleanField(
        'is active',
        default=True,
        help_text='If this status means the project is active '
    )
    is_default = models.BooleanField(
        'default',
        default=False,
        help_text='If this status is the default for new projects.  Only one should be chosen'
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering=('list_position', 'name',)


class Technician(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='user',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='prosdib_technician',
        help_text='The user account associated with this technician'
    )
    name = models.CharField(
        'name',
        max_length=50,
        blank=True,
        help_text='The name of the technician'
    )
    is_current = models.BooleanField(
        'current',
        default=True,
        help_text='If this technician is current (should receive emails from projects, etc)'
    )

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def user_is_tech(cls, user):
        return user in [ technician.user for technician in Technician.objects.all() ]

class ProjectManager(models.Manager):

    def get_queryset(self):
        
        return super().get_queryset(). \
            annotate(latest_update_when=Subquery(ProjectNote.objects.filter(project=OuterRef('pk')).filter(is_current=True).order_by('-when').values('when')[:1])). \
            annotate(qty_current_notes=Count('projectnote', filter=Q(projectnote__is_current=True))). \
            order_by('latest_update_when')

class Project(models.Model):
    PRIORITY_CHOICES = (
            (1, '1) Solve a Safety Hazard or Work Stoppage'),
            (2, '2) Fix a Major Problem or Implement a Major Improvement'),
            (3, '3) Fix a Highly Important Issue or Implement an Important Solution'),
            (4, '4) Fix a Moderately Important Issue or Implement a Moderately Importent Solution'),
            (5, '5) Fix a Minor Issue or implement a minor improvement')
    )

    title = models.CharField(
        'title',
        max_length=75,
        help_text='A short description of the project',
    )
    description = models.TextField(
        'description',
        blank=True,
        help_text='Details about the project'
    )
    priority = models.IntegerField(
        'priority',
        choices=PRIORITY_CHOICES,
        default=4,
        help_text='The priority, on a scale of 1 to 5, where 1 is the highest priority'
    )
    begin = models.DateTimeField(
        default=datetime.now,
        help_text='The date and time the project was submitted'
    )
    technician = models.ForeignKey(
        Technician,
        verbose_name='technician',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='project_responsibility',
        help_text='The technician primarily responsible for executing this project'
    )
    created_by = models.ForeignKey(
        Technician,
        verbose_name='created by',
        null=True,
        on_delete=models.SET_NULL,
        related_name='project_created',
        help_text='The technician who created this project'
    )
    status = models.ForeignKey(
        Status,
        verbose_name = 'status',
        on_delete = models.SET_NULL,
        null=True,
        default = get_default_status,
        help_text = 'The status of this project'
    )
    completion_notes = models.TextField(
        'resolution notes',
        blank=True,
        help_text='How the problem was resolved'
    )
    recipient_emails = models.TextField(
        'recipient emails',
        blank=True,
        help_text='The comma-separated list of emails of those who should get updates on this project.  By default, emails are sent for changes in notes and resolution status'
    )
    time_spent = models.DecimalField(
        'time spent',
        default=0,
        decimal_places=2,
        max_digits=6,
        help_text='The amount of time to be added to the project in addition to time spent logged in notes.  Use decimal notation (ex 1.25, not 1:15)'
    )

    def __str__(self):
        return self.title

    def user_is_editor(self, user):
        return user == self.created_by or user.has_perm('prosdib.change_project')

    def get_current_notes(self):
        current_notes=[]
        if self.completion_notes:
            current_notes.append('final:{}'.format(self.completion_notes))

        for note in self.projectnote_set.filter(is_current=True):
            current_notes.append('{}: {}'.format(note.when.strftime('%Y-%m-%d'), note.maintext))

        return current_notes

    def total_time_spent(self):
        time_spent = self.time_spent
        for note in self.projectnote_set.all():
            time_spent = time_spent + note.time_spent

        return time_spent

    objects = ProjectManager()

    class Meta:
        ordering=['status', 'priority']


class ProjectNote(models.Model):

    project=models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        help_text='The project to which this note applies',
    )
    maintext = models.CharField(
        'text',
        blank=True,
        max_length=255,
        help_text='The text of the note'
    )
    details = models.TextField(
        'details',
        blank=True,
        help_text='The details of the note if the main text is not sufficient'
    )
    submitted_by = models.ForeignKey(
        Technician,
        verbose_name='submitted by',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The technician who submitted this note'
    )
    when = models.DateTimeField(
        'when',
        default=datetime.now,
        help_text='The date that the note was submitted'
    )
    time_spent = models.DecimalField(
        'time spent',
        default=0,
        decimal_places=2,
        max_digits=6,
        help_text='The amount of time to be added to the project as per this note.  Use decimal notation (ex 1.25, not 1:15)'
    )
    is_current = models.BooleanField(
        'is current status',
        default=False,
        help_text='If this note is diplayed by default in the project detail view.  If not, it will be displayed when "Show All" is selected'
    )

    class Meta:
        ordering = ['-when',]

    def __str__(self):
        return self.maintext

class History(models.Model):

    when = models.DateTimeField(
        'when',
        auto_now_add=True,
        help_text='The date this change was made'
    )
    modelname = models.CharField(
        'model',
        max_length=50,
        help_text='The model to which this change applies'
    )
    objectid = models.BigIntegerField(
        'object id',
        null=True,
        blank=True,
        help_text='The id of the record that was changed'
    )
    fieldname = models.CharField(
        'field',
        max_length=50,
        help_text='The that was changed',
    )
    old_value = models.TextField(
        'old value',
        blank=True,
        null=True,
        help_text='The value of the field before the change'
    )
    new_value = models.TextField(
        'new value',
        blank=True,
        help_text='The value of the field after the change'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='prosdib_history',
        null=True,
        help_text='The user who made this change'
    )

    class Meta:
        ordering = ('-when', 'modelname', 'objectid')

    def __str__(self):

        new_value_trunc = self.new_value[:17:]+'...' if len(self.new_value) > 20 else self.new_value

        try:
            model = apps.get_model('prosdib', self.modelname)
            object = model.objects.get(pk=self.objectid)
            return f'{self.when.strftime("%Y-%m-%d")}: {self.modelname}: [{object}] [{self.fieldname}] changed to "{new_value_trunc}"'

        except Exception as e:
            print (e)

        return f'{"mdy".format(self.when.strftime("%Y-%m-%d"))}: {self.modelname}: {self.objectid} [{self.fieldname}] changed to "{new_value_trunc}"'


