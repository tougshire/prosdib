from django.test import  SimpleTestCase, TestCase, Client
from ..forms import ProjectForm
from ..models import Project
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
import time

class ViewTests(TestCase):

    late_fixtures=['prosdib_test_data.json']

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='alpha', password='alpha', is_superuser=True)
        call_command("loaddata", cls.late_fixtures)

    def test_project_list_view(self):
        client = Client()
        response = client.get('/prosdib/project/')
        self.assertEqual(response.url, '/prosdib/project/list/')

    def test_project_detail_view(self):
        client = Client()
        client.login(username='alpha', password='alpha')
        response = client.get('/prosdib/project/1/detail/')
        time.sleep(3)
        self.assertContains(response, 'Project Alpha')


    def test_get_project_create_view_no_auth(self):
        client = Client()
        response = client.get('/prosdib/project/create/')
        self.assertEqual(response.status_code, 302)

    def test_get_project_create_view(self):
        client = Client()
        client.login(username='alpha', password='alpha')
        response = client.get('/prosdib/project/create/')
        self.assertEqual(response.status_code, 200)


    def test_post_project_create_view_no_auth(self):
        client = Client()
        project_title = 'Project Bravo'
        response = client.post('/prosdib/project/create/', {'title': project_title, 'start': '1/1/2021'})
        project_count = Project.objects.filter(title=project_title).count()
        self.assertEqual(project_count, 0)

    def test_post_project_create_view(self):
        client = Client()
        client.login(username='alpha', password='alpha')
        project_title = 'Project Bravo'
        response = client.post('/prosdib/project/create/', {'title': project_title, 'begin': '1/1/2021', 'priority': 1, 'status': 1})
        project_count = Project.objects.filter(title=project_title).count()
        self.assertEqual(project_count, 1)

    def test_get_project_update_view_no_auth(self):
        client = Client()
        project = Project.objects.first()
        response = client.get(f'/prosdib/project/1/update/')
        self.assertEqual(response.status_code, 302)

    def test_get_project_update_view(self):
        client = Client()
        client.login(username='alpha', password='alpha')
        response = client.get(f'/prosdib/project/1/update/')
        self.assertEqual(response.status_code, 200)


    def test_post_project_update_view_no_auth(self):
        client = Client()
        project = Project.objects.create( title='Project before post' )
        ppk = project.pk
        response = client.post(f'/prosdib/project/{ ppk }/update/', {'name': 'Project after post', 'start': '1/2/2021'})
        project = Project.objects.get( pk=ppk )
        self.assertEqual(project.title, 'Project before post')

    def test_post_project_update_view_auth(self):
        client = Client()
        client.login(username='alpha', password='alpha')
        project = Project.objects.create( title='Project before post' )
        ppk = project.pk
        response = client.post(f'/prosdib/project/{ ppk }/update/', {'title': 'Project after post', 'begin': '1/2/2021', 'priority': 1, 'status': 1})
        project = Project.objects.get( pk=ppk )
        self.assertEqual(project.title, 'Project after post')

    def test_post_project_created_by(self):
        client = Client()
        client.login(username='alpha', password='alpha')
        response = client.post(f'/prosdib/project/create/', {'title': 'Project Bravo', 'start': '1/2/2021'})
        self.assertEqual(Project.objects.get(title='Project Bravo').created_by, get_user_model().objects.first() )

class ProjectCreateProjectNoteFormsetTests(TestCase):

    late_fixtures = ['prosdib_test_data.json']

    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_user(
            username = "alpha",
            password = "alpha",
            is_superuser = True
        )
        call_command('loaddata', cls.late_fixtures)
        cls.project_one = Project.objects.first()
        cls.projectnote_one = cls.project_one.projectnote_set.first()

    def test_project_post_with_projectnote_create_with_superuser(self):
        c = Client()
        c.login(username = "superone", password="TestSuper#1")
        response = c.post('/prosdib/project/create/', {
            'title':'Project Bravo',
            'begin':'1/1/2021',
            'status': 1,
            'priority': 1,
            'projectnote_set-TOTAL_FORMS':3,
            'projectnote_set-INITIAL_FORMS':0,
            'projectnote_set-MIN_NUM_FORMS':0,
            'projectnote_set-MAX_NUM_FORMS':0,
            'projectnote_set-0-when':'2021-11-19',
            'initial-projectnote_set-0-when':'2021-11-19',
            'projectnote_set-0-maintext':'Project Update One',
            'projectnote_set-1-when':'2021-11-19',
            'initial-projectnote_set-1-when':'2021-11-19',
            'projectnote_set-1-maintext':'',
            'projectnote_set-2-when':'2021-11-19',
            'initial-projectnote_set-2-when':'2021-11-19',
            'projectnote_set-2-maintext':'',
        })
        self.assertEqual(Project.objects.count(), 1)

class ProjectUpdateProjectNoteFormsetTests(TestCase):

    late_fixtures = ['prosdib_test_data.json']

    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_user(
            username = "alpha",
            password = "alpha",
            is_superuser = True
        )
        call_command('loaddata', cls.late_fixtures)
        cls.project_one = Project.objects.first()
        cls.projectnote_one = cls.project_one.projectnote_set.first()

    def test_project_post_with_projectnote_update_with_superuser(self):
        c = Client()
        c.login(username = "superone", password="TestSuper#1")
        response = c.post('/prosdib/project/' + str(self.project_one.pk) + '/update/', {
            'name':'Project One Updated',
            'start':'1/1/2001',
            'projectnote_set-TOTAL_FORMS':4,
            'projectnote_set-INITIAL_FORMS':1,
            'projectnote_set-MIN_NUM_FORMS':0,
            'projectnote_set-MAX_NUM_FORMS':0,
            'projectnote_set-0-id':self.projectnote_one.pk,
            'projectnote_set-0-project':self.project_one.pk,
            'projectnote_set-0-when':'2021-11-19',
            'initial-projectnote_set-0-when':'2021-11-19',
            'projectnote_set-0-maintext':'Project Note One Updated',

            'projectnote_set-1-Project':self.project_one.pk,
            'projectnote_set-1-when':'2021-11-19',
            'initial-projectnote_set-1-when':'2021-11-19',
            'projectnote_set-1-maintext':'Project Note Two',

            'projectnote_set-2-Project':self.project_one.pk,
            'projectnote_set-2-when':'2021-11-19',
            'initial-projectnote_set-2-when':'2021-11-19',
            'projectnote_set-2-maintext':'',
            'projectnote_set-3-when':'2021-11-19',
            'initial-projectnote_set-3-when':'2021-11-19',
            'projectnote_set-3-maintext':'',
        })
        self.assertEqual(Project.objects.count(), 1)
