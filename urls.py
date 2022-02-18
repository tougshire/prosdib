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
    path('technician/create/', views.TechnicianCreate.as_view(), name='technician-create'),
    path('technician/<int:pk>/update/', views.TechnicianUpdate.as_view(), name='technician-update'),
    path('technician/<int:pk>/detail/', views.TechnicianDetail.as_view(), name='technician-detail'),
    path('technician/<int:pk>/delete/', views.TechnicianDelete.as_view(), name='technician-delete'),
    path('technician/list/', views.TechnicianList.as_view(), name='technician-list'),
    path('technician/<int:pk>/close/', views.TechnicianClose.as_view(), name="technician-close"),

]
