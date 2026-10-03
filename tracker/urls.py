from django.contrib import admin
from django.urls import path
from .views import delete_goal, delete_habit, delete_recurring_habit, habits, add_habits, habits_activity, logout_view, recurring_habits_activity, goals, add_goals, goal_activity, extend_deadline, dashboard, journal, add_journal, edit_journal, delete_journal, register, login_view

urlpatterns = [
    path('habits/', habits, name='habits'),
    path('add_habits/', add_habits, name='add_habits'),
    path('habits_activity/', habits_activity, name='habits_activity'),
    path('recurring_habits_activity/', recurring_habits_activity, name='recurring_habits_activity'),
    path('goals/', goals, name='goals'),
    path('add_goals/', add_goals, name='add_goals'),
    path('goal_activity/', goal_activity, name= 'goal_activity'),
    path('extend_deadline/', extend_deadline, name='extend_deadline'),
    path("goals/delete/<int:goal_id>/", delete_goal, name="delete_goal"),
    path('habits/delete/<int:habit_id>/', delete_habit, name='delete_habit'),
    path('recurring-habits/delete/<int:recurring_habit_id>/', delete_recurring_habit, name='delete_recurring_habit'),

    path('dashboard/', dashboard, name='dashboard'),
    path('journal/', journal, name='journal'),
    path('journal/add/', add_journal, name='add_journal'),
    path("journal/edit/<int:journal_id>/", edit_journal, name="edit_journal"),
    path("journal/delete/<int:journal_id>/", delete_journal, name="delete_journal"),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]