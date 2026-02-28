from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_mood, name='add_mood'),
    path('register/', views.register, name='register'),
    path('update/<int:entry_id>/', views.update_mood, name='update_mood'),
    path('graphs/', views.graphs, name='graphs'),
]