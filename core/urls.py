from django.urls import path
from .views import ActivityCreateView, ActivityUpdateView, ActivityDetailView, ActivityFeedView, LogCreateView, ActivityDeleteView
from .views import ActivityStartWorkflowView

urlpatterns = [
    path("atividades/nova/", ActivityCreateView.as_view(), name="activity_create"),
    path("atividades/<int:numero>/editar/", ActivityUpdateView.as_view(), name="activity_update"),
    path("atividades/<int:numero>/", ActivityDetailView.as_view(), name="activity_detail"),
    path("atividades/feed/", ActivityFeedView.as_view(), name="activity_feed"),
    path("atividades/<int:numero>/apontar/", LogCreateView.as_view(), name="log_create"),
    path("activity/<int:numero>/delete/", ActivityDeleteView.as_view(), name="activity_delete"),  
    path("activity/<int:numero>/start-workflow/", ActivityStartWorkflowView.as_view(), name="activity_start_workflow"),
]
