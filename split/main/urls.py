from django.urls import path
from django.views.generic import RedirectView
from . import views



urlpatterns = [
    path('', RedirectView.as_view(url = 'dashboard')),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('group/<int:pk>/', views.GroupView.as_view(), name='group'),
] 
