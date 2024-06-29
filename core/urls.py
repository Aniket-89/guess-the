from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index_view, name='home'),
    path('check-guess/', views.check_guess, name='check_guess'),
]