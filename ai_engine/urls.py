"""
AI Engine URL Configuration
"""
from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('score/', views.score_risk, name='score-risk'),
]
