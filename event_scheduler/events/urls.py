from django.urls import path
from .views import EventListView, EventDetailView

urlpatterns = [
    path('events/', EventListView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    
]
