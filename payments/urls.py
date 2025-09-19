from django.urls import path
from . import views

urlpatterns = [
    path('create_checkout/', views.create_checkout, name='create_checkout'),
    path('callback/success/', views.callback_success, name='callback_success'),
    path('callback/cancel/', views.callback_cancel, name='callback_cancel'),
    path('callback/general/', views.callback_general, name='callback_general'),
]