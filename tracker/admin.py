from django.contrib import admin
from .models import ActivityTimeCalculate, Profile, Todo, Habit, RecurringHabit, DailyCheckIn, Goal, Journal, Category

# Register your models here.
admin.site.register(Category)
admin.site.register(ActivityTimeCalculate)
admin.site.register(Profile)
admin.site.register(Todo)
admin.site.register(Habit)
admin.site.register(RecurringHabit)
admin.site.register(DailyCheckIn)
admin.site.register(Goal)
admin.site.register(Journal)

