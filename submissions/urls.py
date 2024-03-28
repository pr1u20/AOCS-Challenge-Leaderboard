from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('submit', views.submit_csv, name='submit'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
]