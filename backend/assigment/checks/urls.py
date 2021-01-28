from django.urls import path
from . import views

app_name = 'checks'

urlpatterns = [
    path("new_checks/", views.new_checks, name='new_checks'),
    path("create_checks/", views.create_checks, name='create_checks'),
    path("check/", views.check, name='check')

]
