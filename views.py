import sys
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.http import QueryDict
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from libtekin.models import Item, Location, Mmodel
from tougshire_vistas.models import Vista
from tougshire_vistas.views import (delete_vista, default_vista, get_global_vista,
                                    get_latest_vista, make_vista,
                                    retrieve_vista)

from .forms import (ProjectForm, ProjectProjectNoteForm,
                    ProjectProjectNoteFormset, TechnicianForm)
from .models import History, Project, ProjectNote, Technician


def update_history(form, modelname, object, user):
    for fieldname in form.changed_data:
        try:
            old_value = str(form.initial[fieldname]),
        except KeyError:
            old_value = None

        history = History.objects.create(
            user=user,
            modelname=modelname,
            objectid=object.pk,
            fieldname=fieldname,
            old_value=old_value,
            new_value=str(form.cleaned_data[fieldname])
        )

        history.save()


def send_project_mail(project, request, is_new=False):
    """Send an email

    Args:
        project: The project about which the email is being sent.  Usually self.object or self.object.project
        request: A request object.  Usually self.request
        is_new: If this mail is about the creation of a new project.  If not then it's an update

    """

    # if it has no @ sign, assume no emails should be sent
    if not project.recipient_emails.find('@') > 0:
        return

    project_url = request.build_absolute_uri(
        reverse('prosdib:project-detail', kwargs={'pk': project.pk}))

    mail_subject_action = "Submitted" if is_new else "Updated"
    mail_subject = f"Tech Project { mail_subject_action }: { project.title }"

    mail_from = settings.PROSDIB_EMAIL_FROM if hasattr(
        settings, 'PROSDIB_FROM_EMAIL') else settings.DEFAULT_FROM_EMAIL

    mail_message = "\n".join(
        [
            f"Title: { project.title }",
            f"Urgency: { project.get_priority_display() }",
            f"Description: { project.description }",
            f"Project URL: { project_url }",
        ]
    )
    if project.projectnote_set.all().exists:
        mail_message = mail_message + "\nNotes:\n" + "\n".join([str(note.when) + ': ' + note.text + ' -- ' + str(note.submitted_by) for note in project.projectnote_set.all()])

    mail_html_message = "<br>\n".join(
        [
            f"Title: { project.title }",
            f"Urgency: { project.get_priority_display() }",
            f"Description: { project.description }",
            f"Project URL: <a href=\"{ project_url }\">{ project_url }</a>"
        ]
    )
    if project.projectnote_set.all().exists:
        mail_html_message = mail_html_message + "<br>Notes:<br>\n" + "<br>\n".join([str(note.when) + ': ' + note.text + ' --' + str(note.submitted_by) for note in project.projectnote_set.all()])


    mail_recipients = [email.strip() for email in project.recipient_emails.split(',')]

    try:
        send_mail(
            mail_subject,
            mail_message,
            mail_from,
            mail_recipients,
            html_message=mail_html_message,
            fail_silently=False,
        )
    except Exception as e:
        messages.add_message(request, messages.WARNING, 'There was an error sending emails.')
        messages.add_message(request, messages.WARNING, e)

        print(e, ' at ', sys.exc_info()[2].tb_lineno)

class ProjectCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'prosdib.add_project'
    model = Project
    form_class = ProjectForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['projectnotes'] = ProjectProjectNoteFormset(self.request.POST)
        else:
            context_data['projectnotes'] = ProjectProjectNoteFormset(initial=[
            {
                'submitted_by': self.request.user
            }
        ])

        return context_data

    def get_initial(self):
        tech_emails = [tech.user.email for tech in Technician.objects.filter(is_current=True).filter(user__isnull=False)]
        all_recipient_emails = ( tech_emails + [ self.request.user.email ] ) if self.request.user.email not in tech_emails else tech_emails

        return {
            'recipient_emails': ",\n".join(all_recipient_emails)
        }

    def form_valid(self, form):

        response = super().form_valid(form)

        self.object = form.save(commit=False)
        technician, created = Technician.objects.get_or_create(
            user=self.request.user,
            defaults={'name': self.request.user.__str__()},
        )
        self.object.submitted_by = technician

        if not 'recipient_emails' in self.request.POST:
            self.object.recipient_emails = self.get_initial()['recipient_emails']


        self.object.save()

        projectnotes = ProjectProjectNoteFormset(self.request.POST, instance=self.object)

        if(projectnotes).is_valid():
            for form in projectnotes.forms:
                projectnote = form.save(commit=False)
                if projectnote.submitted_by is None:
                    projectnote.submitted_by = technician
            projectnotes.save()
        else:
            return self.form_invalid(form)


        if not 'donot_send' in self.request.POST:
            send_project_mail(self.object, self.request, is_new=True)

        return response

    def get_success_url(self):
        return reverse_lazy('prosdib:project-detail', kwargs={'pk': self.object.pk})


class ProjectUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'prosdib.change_project'

    model = Project
    form_class = ProjectForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['projectnotes'] = ProjectProjectNoteFormset(self.request.POST, instance=self.object)
        else:
            context_data['projectnotes'] = ProjectProjectNoteFormset(instance=self.object, initial=[{'submitted_by':self.request.user}])

        return context_data


    def form_valid(self, form):

        response = super().form_valid(form)

        self.object = form.save()

        technician, created = Technician.objects.get_or_create(
            user=self.request.user,
            defaults={'name': self.request.user.__str__()},
        )

        projectnotes = ProjectProjectNoteFormset(self.request.POST, instance=self.object, initial=[
            {
                'submitted_by': technician
            }
        ])

        if(projectnotes).is_valid():
            for form in projectnotes.forms:
                projectnote = form.save(commit=False)
                if projectnote.submitted_by is None:
                    projectnote.submitted_by = technician
            projectnotes.save()
        else:
            print('tp m2if36', projectnotes.errors)
            return self.form_invalid(form)

        if not 'donot_send' in self.request.POST:
            send_project_mail(self.object, self.request, is_new=False)

        return response

    def get_success_url(self):

        return reverse_lazy('prosdib:project-detail', kwargs={'pk': self.object.pk})

class ProjectDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'prosdib.view_project'
    model = Project

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['project_labels'] = {field.name: field.verbose_name.title(
        ) for field in Project._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        context_data['projectnote_labels'] = {field.name: field.verbose_name.title(
        ) for field in ProjectNote._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        return context_data


class ProjectDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'prosdib.delete_project'
    model = Project
    success_url = reverse_lazy('prosdib:project-list')


class ProjectSoftDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'prosdib.delete_project'
    model = Project
    template_name = 'prosdib/item_confirm_delete.html'
    success_url = reverse_lazy('prosdib:project-list')
    fields = ['is_deleted']

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['current_notes'] = self.object.projectnote_set.all().filter(
            is_current_status=True)
        context_data['project_labels'] = {field.name: field.verbose_name.title(
        ) for field in Project._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        context_data['projectnote_labels'] = {field.name: field.verbose_name.title(
        ) for field in ProjectNote._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}

        return context_data

class ProjectList(PermissionRequiredMixin, ListView):
    permission_required = 'prosdib.view_project'
    model = Project
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'text_fields_available':[],
            'filter_fields_available':{},
            'order_by_fields_available':[],
            'columns_available':[]
        }

        self.vista_settings['text_fields_available']=[
            'title',
            'description',
            'completion_notes',
        ]

        self.vista_settings['filter_fields_available'] = [
            'title',
            'description',
            'priority',
            'begin',
            'technician',
            'created_by',
            'status',
            'completion_notes',
        ]

        for fieldname in [
            'title',
            'priority',
            'begin',
            'technician',
            'created_by',
            'status',
        ]:
            self.vista_settings['order_by_fields_available'].append(fieldname)
            self.vista_settings['order_by_fields_available'].append('-' + fieldname)

        for fieldname in [
            'title',
            'description',
            'priority',
            'begin',
            'technician',
            'created_by',
            'status',
            'completion_notes',
            'recipient_emails',
        ]:
            self.vista_settings['columns_available'].append(fieldname)

        self.vista_settings['field_types'] = {
            'begin':'date',
        }

        self.vista_defaults = {
            'order_by': Project._meta.ordering,
            'filterop__status':'in',
            'filterfield__status': (1,2,3),
            'paginate_by':self.paginate_by
        }

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'vista_query_submitted' in self.request.POST:

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'libtekin.item',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp m38830', urllib.parse.urlencode(self.vista_defaults))
            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                QueryDict(urllib.parse.urlencode(self.vista_defaults)),
                self.vista_settings
            )


        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        context_data['mmodels'] = Mmodel.objects.all()
        context_data['items'] = Item.objects.all()
        context_data['technicians'] = Technician.objects.all()
        context_data['priorities'] = Project.PRIORITY_CHOICES
        context_data['statuses'] = Project.STATUS_CHOICES

        context_data['order_by_fields_available'] = []
        for fieldname in self.vista_settings['order_by_fields_available']:
            if fieldname > '' and fieldname[0] == '-':
                context_data['order_by_fields_available'].append({ 'name':fieldname, 'label':Project._meta.get_field(fieldname[1:]).verbose_name.title() + ' [Reverse]'})
            else:
                context_data['order_by_fields_available'].append({ 'name':fieldname, 'label':Project._meta.get_field(fieldname).verbose_name.title()})

        context_data['columns_available'] = [{ 'name':fieldname, 'label':Project._meta.get_field(fieldname).verbose_name.title() } for fieldname in self.vista_settings['columns_available']]

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='prosdib.project').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        vista_querydict = self.vistaobj['querydict']

        #putting the index before item name to make it easier for the template to iterate
        context_data['filter'] = []
        for indx in range( self.vista_settings['max_search_keys']):
            cdfilter = {}
            cdfilter['fieldname'] = vista_querydict.get('filter__fieldname__' + str(indx)) if 'filter__fieldname__' + str(indx) in vista_querydict else ''
            cdfilter['op'] = vista_querydict.get('filter__op__' + str(indx) ) if 'filter__op__' + str(indx) in vista_querydict else ''
            cdfilter['value'] = vista_querydict.get('filter__value__' + str(indx)) if 'filter__value__' + str(indx) in vista_querydict else ''
            if cdfilter['op'] in ['in']:
                cdfilter['value'] = vista_querydict.getlist('filter__value__' + str(indx)) if 'filter__value__'  + str(indx) in vista_querydict else []
            context_data['filter'].append(cdfilter)

        context_data['order_by'] = vista_querydict.getlist('order_by') if 'order_by' in vista_querydict else Item._meta.ordering

        context_data['combined_text_search'] = vista_querydict.get('combined_text_search') if 'combined_text_search' in vista_querydict else ''

        context_data['project_labels'] = { field.name: field.verbose_name.title() for field in Project._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class ProjectProjectNoteCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'prosdib.add_projectnote'
    model=ProjectNote
    form_class=ProjectProjectNoteForm
    template_name='prosdib/projectprojectnote_form.html'

    def form_valid(self, form):

        self.object=form.save(commit=False)
        self.object.project=Project.objects.get(pk=self.kwargs.get('projectpk'))
        technician, created = Technician.objects.get_or_create(
            user=self.request.user,
            defaults={'name': self.request.user.__str__()},
        )
        self.object.submitted_by = technician
        self.object.save()

        if not 'donot_send' in self.request.POST:
            send_project_mail(self.object.project, self.request, is_new=False)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('prosdib:project-detail', kwargs={'pk': self.object.project.pk})


class TechnicianCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'prosdib.add_technician'
    model = Technician
    form_class = TechnicianForm

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('prosdib:technician-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('prosdib:technician-detail', kwargs={'pk': self.object.pk})

        return response

class TechnicianUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'prosdib.change_technician'
    model = Technician
    form_class = TechnicianForm

    def get_success_url(self):
        return reverse_lazy('prosdib:technician-detail', kwargs={'pk': self.object.pk})


class TechnicianDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'prosdib.view_technician'
    model = Technician

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['technician_labels'] = { field.name: field.verbose_name.title() for field in Technician._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class TechnicianDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'prosdib.delete_technician'
    model = Technician
    success_url = reverse_lazy('prosdib:technician-list')

class TechnicianList(PermissionRequiredMixin, ListView):
    permission_required = 'prosdib.view_technician'
    model = Technician

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['technician_labels'] = { field.name: field.verbose_name.title() for field in Technician._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        return context_data

class TechnicianClose(PermissionRequiredMixin, DetailView):
    permission_required = 'prosdib.view_technician'
    model = Technician
    template_name = 'prosdib/technician_closer.html'

