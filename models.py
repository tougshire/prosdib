from django.db import models
from django.conf import settings
from datetime import datetime
from django.apps import apps
from libtekin.models import Item, Location
from django.contrib.auth import get_user_model

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
        help_text='A short description of the issue',
    )
    description = models.TextField(
        'description',
        blank=True,
        help_text='The description of the problem if the short description isn\'t adequate'
    )
    priority = models.IntegerField(
        'priority',
        choices=PRIORITY_CHOICES,
        default=4,
        help_text='The urgency, on a scale of 1 to 5, where 1 is the most urgent'
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
        help_text='The technician responsible for responding to this project'
    )
    is_complete = models.BooleanField(
        'is resolved',
        blank=True,
        default=False,
        help_text = 'If the problem is resolved'

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

    def __str__(self):
        return self.short_description

    def user_is_editor(self, user):
        return user == self.submitted_by or user.has_perm('prosdib.change_project')

    class Meta:
        ordering=['is_complete', 'priority', 'begin']


class ProjectNote(models.Model):

    project=models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        help_text='The project to which this note applies',
    )
    text = models.CharField(
        'text',
        blank=True,
        max_length=255,
        help_text='The text of the note'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='submitted by',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The user who submitted this note'
    )
    when = models.DateTimeField(
        'when',
        default=datetime.now,
        help_text='The date that the note was submitted'
    )

    def __str__(self):
        return self.text

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


