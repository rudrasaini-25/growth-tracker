from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# types of goals and habit
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name






# status model
    




#dashboard
class Profile(models.Model):
    user = models.OneToOneField(User ,on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    age = models.IntegerField()
    mobile = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='profile_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='profile_updated')

    def __str__(self):
        return str(self.user)
    

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='todo_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='todo_updated')

    def __str__(self):
        return f"{self.user},{self.title}"





#HABIT
class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=3)
    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='habit_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='habit_updated')


    def __str__(self):
        return f"{self.user},{self.title}"

class RecurringHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=3)
    start_date = models.DateField()
    end_date = models.DateField()

    REPETITION_CHOICES = [
    ('daily', 'Daily'),
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
    ]
    repetition = models.CharField(max_length=50, choices=REPETITION_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recurring_habit_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recurring_habit_updated')


    def __str__(self):
        return f"{self.user},{self.title}"

class DailyCheckIn(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.habit},{self.is_completed}"





# GOALS
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    target_date = models.DateField()
    target_hours = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='goal_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='goal_updated')


    def __str__(self):
        return f"{self.user},{self.title}"





# JOURNAL
class Journal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='journal_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='journal_updated')

    def __str__(self):
        return f"{self.user},{self.title}"

    



#pomodoro timer model
class ActivityTimeCalculate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work_duration = models.IntegerField()
    rest_duration = models.IntegerField()
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE , null=True, blank=True)
    recurring_habit = models.ForeignKey(RecurringHabit, on_delete=models.CASCADE , null=True, blank=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='timer_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='timer_updated')


    def __str__(self):
        return f"{self.user},{self.work_duration}"