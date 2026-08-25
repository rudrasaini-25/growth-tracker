from django.contrib import admin
from django.urls import path
from .views import habits, add_habits, habits_activity, recurring_habits_activity, goals, add_goals, goal_activity, extend_deadline, dashboard

urlpatterns = [
    path('habits/', habits, name='habits'),
    path('add_habits/', add_habits, name='add_habits'),
    path('habits_activity/', habits_activity, name='habits_activity'),
    path('recurring_habits_activity/', recurring_habits_activity, name='recurring_habits_activity'),
    path('goals/', goals, name='goals'),
    path('add_goals/', add_goals, name='add_goals'),
    path('goal_activity/', goal_activity, name= 'goal_activity'),
    path('extend_deadline/', extend_deadline, name='extend_deadline'),
    path('dashboard/', dashboard, name='dashboard'),

]