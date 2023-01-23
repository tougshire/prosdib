from django.test import TestCase
from ..models import Project
from django.contrib.auth import get_user_model

class ProjectTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_one = get_user_model().objects.create(
            username="userone"
        )
        cls.project_one = Project.objects.create(
            title="project one"
        )

    def test_project_str_is_name(self):
        self.assertEqual(self.project_one.__str__(), self.project_one.title)

