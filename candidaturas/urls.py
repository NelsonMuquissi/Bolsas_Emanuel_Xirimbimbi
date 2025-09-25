from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/', views.apply, name='apply'),
    path('load-courses/', views.load_courses, name='load_courses'),
    path('bolsas/nacionais', views.nacionais, name='nacionais'),
    path('bolsas/internacionais', views.internacionais, name='internacionais'),
]