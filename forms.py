from django import forms
from django.forms import inlineformset_factory
from .models import Project, ProjectNote, Technician

class ItemSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            textforfilter = f'{name}|{value.instance.primary_id}'
            if value.instance.location is not None:
                option['attrs']['data-home'] = value.instance.home.pk
                textforfilter = textforfilter + f'|{value.instance.home.short_name}|{value.instance.home.full_name}'

            if value.instance.assignee is not None:
                textforfilter = textforfilter + f'|{value.instance.assignee.friendly_name}|{value.instance.assignee.full_name}'
                option['attrs']['data-textforfilter'] = textforfilter

        return option


class ProjectForm(forms.ModelForm):
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    class Meta:
        model = Project
        fields = [
            'title',
            'begin',
            'description',
            'priority',
            'technician',
            'status',
            'recipient_emails',
            'completion_notes',
        ]
        widgets = {
            'title':forms.TextInput(attrs={'class':'len75'}),
            'description':forms.Textarea(attrs={'class':'len75'}),
            'begin':forms.DateTimeInput(format='%Y-%m-%dT%H:%M:%S',  attrs={'type':'datetime-local'} ),

        }


class ProjectProjectNoteForm(forms.ModelForm):
    class Meta:
        model = ProjectNote
        fields = [
            'when',
            'text',
            'is_major',
            'time_spent',
        ]
        widgets={
            'when':forms.DateTimeInput(format='%Y-%m-%dT%H:%M:%S',  attrs={'type':'datetime-local'} ),
            'text':forms.TextInput(attrs={'class':'len100'})
        }

class TechnicianForm(forms.ModelForm):
    class Meta:
        model = Technician
        fields = [
            'user',
            'name',
            'is_current',
        ]



ProjectProjectNoteFormset = inlineformset_factory(Project, ProjectNote, form=ProjectProjectNoteForm, extra=10)
