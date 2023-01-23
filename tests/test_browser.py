from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver


from selenium.webdriver.common.keys import Keys

import time

# from selenium.webdriver.firefox.service import Service as FirefoxService
# from webdriver_manager.firefox import GeckoDriverManager
from django.contrib.auth import get_user_model

from ..models import Technician

# class NewProjectWithNotesTests(StaticLiveServerTestCase):

#     fixtures = ['prosdib_test_data.json']

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.selenium = WebDriver()
#         cls.selenium.implicitly_wait(10)

    
#     @classmethod
#     def tearDownClass(cls):
#         time.sleep(3)

#         cls.selenium.quit()
#         super().tearDownClass()

#     def test_create_project_with_note(self):
 
#         user = get_user_model().objects.first()
#         tech = Technician.objects.create(user=user, name="Alpha")

#         self.selenium.get(self.live_server_url  + '/prosdib/project/create/')
#         el_username = self.selenium.find_element(By.ID, 'id_username')
#         el_password = self.selenium.find_element(By.ID, 'id_password')
#         el_form = self.selenium.find_elements(By.TAG_NAME, 'form')[0]
#         el_username.send_keys(user.username)
#         el_password.send_keys(user.username)

#         el_form.submit()

#         el_title = self.selenium.find_element(By.ID, 'id_title')
#         project_title = 'Test Project'
#         el_title.send_keys(project_title)

#         el_addprojectnote = self.selenium.find_element(By.ID, 'button_addprojectnote')
#         el_addprojectnote.click()

#         el_projectnote_maintext = self.selenium.find_element(By.ID, 'id_projectnote_set-0-maintext')
#         projectnote_maintext = ('First Test Note for Test Project')
#         el_projectnote_maintext.send_keys(projectnote_maintext)


#         el_form = self.selenium.find_elements(By.TAG_NAME, 'form')[0]
#         el_form.submit()

#         time.sleep(3)

#         el_page = self.selenium.page_source

#         self.assertIn(project_title, el_page)

#         self.assertIn(projectnote_maintext, el_page)
