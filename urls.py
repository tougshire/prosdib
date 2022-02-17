from django.urls import path
from . import views

app_name = 'prosdib'

urlpatterns = [
    path('project/create/', views.ProjectCreate.as_view(), name='project-create'),
    path('project/<int:pk>/update/', views.ProjectUpdate.as_view(), name='project-update'),
    path('project/<int:pk>/detail/', views.ProjectDetail.as_view(), name='project-detail'),
    path('project/<int:pk>/delete/', views.ProjectSoftDelete.as_view(), name='project-delete'),
    path('project/list/', views.ProjectList.as_view(), name='project-list'),
    path('project/<int:projectpk>/projectnote/create', views.ProjectProjectNoteCreate.as_view(), name='projectprojectnote-create'),
]
