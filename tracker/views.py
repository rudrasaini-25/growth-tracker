from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Habit, RecurringHabit, ActivityTimeCalculate, Goal, Journal
from .forms import HabitForm, RecurringHabitForm, GoalForm, JournalForm
from django.utils import timezone
from datetime import date
from django.db.models import Q
from datetime import datetime, timedelta



def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists."
            })

        if password != confirm_password:
            return render(request, "register.html", {
                "error": "Passwords do not match."
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("dashboard")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "login.html")

@login_required
def habits(request):

    today = timezone.localdate()

    habits_list = Habit.objects.filter(
        user=request.user,
        start_date__lte=today,
        end_date__gte=today
    )

    for habit in habits_list:

        habit.checked_today = False

        timers = ActivityTimeCalculate.objects.filter(
            user=request.user,
            habit=habit
        )

        for timer in timers:

            timer_date = timezone.localtime(timer.created_at).date()

            if timer_date == today:
                habit.checked_today = True
                break

    
    today_name = today.strftime('%A').lower()

    recurring_list = RecurringHabit.objects.filter(
        user=request.user,
        start_date__lte=today,
        end_date__gte=today
    )

    visible_recurring = []

    for habit in recurring_list:

        if habit.repetition == 'daily' or habit.repetition == today_name:

            habit.checked_today = False

            timers = ActivityTimeCalculate.objects.filter(
                user=request.user,
                recurring_habit=habit
            )

            for timer in timers:

                timer_date = timezone.localtime(timer.created_at).date()

                if timer_date == today:
                    habit.checked_today = True
                    break

            visible_recurring.append(habit)
    

    context = {
        "habits": habits_list,
        "recurringhabits": visible_recurring,
    }
    
    return render(request, "habit.html", context)

@login_required
def add_habits(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "habit":

            habit_form = HabitForm(request.POST)

            if habit_form.is_valid():
                habit = habit_form.save(commit=False)

                habit.user = request.user
                habit.created_by = request.user
                habit.updated_by = request.user

                habit.save()

                return redirect("habits")

        elif form_type == "recurring":

            recurring_habit_form = RecurringHabitForm(request.POST)

            if recurring_habit_form.is_valid():

                recurring = recurring_habit_form.save(commit=False)

                recurring.user = request.user
                recurring.created_by = request.user
                recurring.updated_by = request.user

                recurring.save()

                return redirect("habits")
    else:

        habit_form = HabitForm()
        recurring_habit_form = RecurringHabitForm()


    return render (request, "add_habit.html",
                    {'habit_form': habit_form,'recurring_habit_form': recurring_habit_form,})

@require_POST
@login_required
def habits_activity(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=403)

    habit_id = request.POST.get('habit_id')
    work_duration = request.POST.get('work_duration')

    if not habit_id or not work_duration:
        return JsonResponse({'error': 'Missing habit_id or work_duration.'}, status=400)
    try:
        work_duration = int(work_duration)
    except ValueError:
        return JsonResponse({'error': 'work_duration must be an integer.'}, status=400)

    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    timer = ActivityTimeCalculate(
        user=request.user,
        work_duration=work_duration,
        rest_duration=0,
        habit=habit,
        goal=None,
        recurring_habit=None,
        created_by=request.user,
        updated_by=request.user,
    )
    today = timezone.localdate()

    already_done = ActivityTimeCalculate.objects.filter(
        user=request.user,
        habit=habit,
        created_at__date=today,
    ).exists()

    if already_done:
        return JsonResponse(
            {'error': 'Habit already completed today.'},
            status=400
    )

    timer.save()

    return JsonResponse({'success': True, 'timer_id': timer.id})


@require_POST
@login_required
def recurring_habits_activity(request):

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=403)

    recurring_habit_id = request.POST.get('recurring_habit_id')
    work_duration = request.POST.get('work_duration')

    if not recurring_habit_id or not work_duration:
        return JsonResponse({'error': 'Missing recurring_habit_id or work_duration.'}, status=400)
    try:
        work_duration = int(work_duration) 
    except ValueError:
        return JsonResponse({'error': 'work_duration must be an integer.'}, status=400)

    recurring_habit = get_object_or_404(RecurringHabit, id=recurring_habit_id, user=request.user)

    timer = ActivityTimeCalculate(
        user=request.user,
        work_duration=work_duration,
        rest_duration=0,
        habit=None,
        goal=None,
        recurring_habit=recurring_habit,
        created_by=request.user,
        updated_by=request.user,
    )
    today = timezone.localdate()

    already_done = ActivityTimeCalculate.objects.filter(
        user=request.user,
        recurring_habit=recurring_habit,
        created_at__date=today,
    ).exists()

    if already_done:
        return JsonResponse(
            {'error': 'Habit already completed today.'},
            status=400
    )

    timer.save()

    return JsonResponse({'success': True, 'timer_id': timer.id})


# ---------------------------------------------------------------------------

@login_required
def goals(request):

    today = timezone.localdate()

    goals_list = Goal.objects.filter(
        user=request.user
    )
 
    for goal in goals_list:

        activities = ActivityTimeCalculate.objects.filter(
            user=request.user,
            goal=goal 
        )

        total_minutes = 0

        for activity in activities:
            total_minutes = total_minutes + activity.work_duration

        goal.completed_hours = total_minutes / 60

        if goal.completed_hours >= goal.target_hours:
            goal.status = "COMPLETED"

        elif goal.completed_hours < goal.target_hours and today <= goal.target_date:
            goal.status = "ACTIVE"

        else:
            goal.status = "EXPIRED"

    context = {
        "goals": goals_list
    }

    return render(
        request,
        "goal.html",
        context
    )

@login_required
def add_goals(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "goal":

            goal_form = GoalForm(request.POST)

            if goal_form.is_valid():
                goal = goal_form.save(commit=False)

                goal.user = request.user
                goal.created_by = request.user
                goal.updated_by = request.user

                goal.save()

                return redirect("goals")
    else:

        goal_form = GoalForm()


    return render (request, "add_goal.html",
                    {'goal_form': goal_form})
                

@require_POST
@login_required
def goal_activity(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=403)

    goal_id = request.POST.get('goal_id')
    work_duration = request.POST.get('work_duration')

    if not goal_id or not work_duration:
        return JsonResponse({'error': 'Missing goal_id or work_duration.'}, status=400)
    try:
        work_duration = int(work_duration)
    except ValueError:
        return JsonResponse({'error': 'work_duration must be an integer.'}, status=400)

    goal = get_object_or_404(Goal, id=goal_id, user=request.user)

    timer = ActivityTimeCalculate(
    user=request.user,
    work_duration=work_duration,
    rest_duration=0,
    habit=None,
    goal=goal,
    recurring_habit=None,
    created_by=request.user,
    updated_by=request.user,
    )
    
    timer.save()

    total_minutes = 0

    activities = ActivityTimeCalculate.objects.filter(
        user=request.user,
        goal=goal
    )

    for activity in activities:
        total_minutes += activity.work_duration
    completed_hours = total_minutes / 60

    today = timezone.localdate()
    if completed_hours >= goal.target_hours:
            goal.status = "COMPLETED"

    elif completed_hours < goal.target_hours and today <= goal.target_date:
        goal.status = "ACTIVE"

    else:
        goal.status = "EXPIRED"

    return JsonResponse({'success': True, 'timer_id': timer.id, 'completed_hours': completed_hours, 'status': goal.status})




@require_POST
@login_required
def extend_deadline(request):

    if not request.user.is_authenticated: 
        return JsonResponse({'error': 'Authentication required.'}, status=403) 
    
    goal_id = request.POST.get('goal_id') 
    new_deadline = request.POST.get('new_deadline') 

    if not goal_id or not new_deadline:
            return JsonResponse({'error': 'Missing goal_id or new_deadline.'}, status=400)

    goal = get_object_or_404(Goal, id=goal_id, user=request.user) #this gets the goal object so that i can use goal.save , goal.target_date etc.

    new_deadline = date.fromisoformat(new_deadline)

    goal.target_date = new_deadline
    goal.save()
	
    total_minutes = 0
    activities = ActivityTimeCalculate.objects.filter(
        user=request.user,
        goal=goal
    )
    
    for activity in activities:
        total_minutes += activity.work_duration
    completed_hours = total_minutes / 60

    today = timezone.localdate()
	
    if completed_hours >= goal.target_hours:
        goal.status = "COMPLETED"

    elif completed_hours < goal.target_hours and today <= goal.target_date:
        goal.status = "ACTIVE"

    else:
        goal.status = "EXPIRED"

    return JsonResponse({'success': True, 'status': goal.status, 'new_target_date': goal.target_date})


@login_required
def dashboard(request):

    today = timezone.localdate()
# for active habits
    habits = Habit.objects.filter(
        user=request.user,
        start_date__lte=today,
        end_date__gte=today
    ) 
    active_habits = habits.count()


    today_weekday = today.strftime("%A").lower()

    recurring_habits = RecurringHabit.objects.filter(
        user=request.user,
        start_date__lte=today,
        end_date__gte=today
    ).filter( Q(repetition = "daily") | Q(repetition = today_weekday) )
    active_recurring_habits = recurring_habits.count()

    total_active_habits = active_habits + active_recurring_habits


# for active goals
    goals = Goal.objects.filter(
        user=request.user
    )
    active_goals = []
    total_active_goals = 0
    for goal in goals:
        total_minutes = 0
        activities = ActivityTimeCalculate.objects.filter(
            user=request.user,
            goal=goal
        )

        for activity in activities:
            total_minutes += activity.work_duration
        completed_hours = total_minutes / 60
        
        if completed_hours >= goal.target_hours:
            goal.status = "COMPLETED"
    
        elif completed_hours < goal.target_hours and today <= goal.target_date:
            goal.status = "ACTIVE"
            total_active_goals += 1
            goal_progress = (completed_hours / goal.target_hours) * 100 if goal.target_hours > 0 else 0

            active_goals.append({
                'title': goal.title,
                'progress': goal_progress
            })
    
        else:
            goal.status = "EXPIRED"

    total_completed_hours = 0
    total_target_hours = 0

    for goal in goals:
        activities = ActivityTimeCalculate.objects.filter(
            user=request.user,
            goal=goal
        )

        total_minutes = 0

        for activity in activities:
            total_minutes += activity.work_duration

        completed_hours = total_minutes / 60

        total_completed_hours += completed_hours
        total_target_hours += goal.target_hours

    if total_target_hours > 0:
        progress_percentage = (
            total_completed_hours / total_target_hours
        ) * 100
    else:
        progress_percentage = 0
        

# for todays activity in hours
    today_start = timezone.make_aware(
        datetime.combine(today, datetime.min.time())
    )

    tomorrow_start = today_start + timedelta(days=1)

    todays_activities = ActivityTimeCalculate.objects.filter(
        user=request.user,
        created_at__gte=today_start,
        created_at__lt=tomorrow_start
    )

    today_hours = sum( activity.work_duration for activity in todays_activities ) / 60

# for overall goal progress

    total_completed_hours = 0
    total_target_hours = 0

    for goal in goals:
        # calculate this goal's completed_hours
        total_minutes = 0
        activities = ActivityTimeCalculate.objects.filter(
            user=request.user,
            goal=goal
        )

        for activity in activities:
            total_minutes += activity.work_duration
            
        completed_hours = total_minutes / 60

        total_completed_hours += completed_hours
        total_target_hours += goal.target_hours

        progress_percentage = (total_completed_hours / total_target_hours * 100) if total_target_hours > 0 else 0

# for the habit ,done/pending
    # normal habits
    todays_habit_activities = ActivityTimeCalculate.objects.filter(
        user=request.user,
        habit__isnull=False,
        created_at__gte=today_start,
        created_at__lt=tomorrow_start
    )
    completed_habit_ids = set(
        activity.habit_id
        for activity in todays_habit_activities
    )
    habit_data = []
    for habit in habits:

        if habit.id in completed_habit_ids:
            status = "DONE"
        else:
            status = "PENDING"

        habit_data.append({
            'title': habit.title,
            'status': status
        })
        
    # recurring habits
    todays_recurring_habit_activities = ActivityTimeCalculate.objects.filter(
        user=request.user,
        recurring_habit__isnull=False,
        created_at__gte=today_start,
        created_at__lt=tomorrow_start
    )
    completed_recurring_habit_ids = set(
        activity.recurring_habit_id
        for activity in todays_recurring_habit_activities
    )
    recurring_habit_data = []

    for habit in recurring_habits:

        if habit.id in completed_recurring_habit_ids:
            status = "DONE"
        else:
            status = "PENDING"

        recurring_habit_data.append({
            'title': habit.title,
            'status': status
        })

    all_habits = habit_data + recurring_habit_data


    context = {
        'total_active_habits': total_active_habits,
        'total_active_goals': total_active_goals,
        'today_hours': today_hours,
        'active_goals': active_goals,
        'progress_percentage': progress_percentage,
        'all_habits': all_habits,
    }
    return render(request, "dashboard.html", context)

# retrive
@login_required
def journal(request):

    journals = Journal.objects.filter(
        user=request.user,
    )

    context = {
        'journals': journals,
    }

    return render(request, "journal.html", context)

# create
@login_required
def add_journal(request):

    if request.method == "POST":
        form = JournalForm(request.POST)

        if form.is_valid():
            journal = form.save(commit=False)

            journal.user = request.user
            journal.created_by = request.user
            journal.updated_by = request.user

            journal.save()

            return redirect("journal")

    form = JournalForm()

    context = {
        'form': form,
    }

    return render(request, "add_journal.html", context)

@login_required
def edit_journal(request, journal_id):

    journal = Journal.objects.get(id=journal_id, user=request.user)

    form = JournalForm(instance=journal)
    if request.method == "POST":
        form = JournalForm(request.POST, instance=journal)

        if form.is_valid():
            journal = form.save(commit=False)

            journal.updated_by = request.user
            journal.save()

            return redirect("journal")


    context = {
        'form': form,
    }

    return render(request, "edit_journal.html", context)


@login_required
def delete_journal(request, journal_id):

    journal = Journal.objects.get(id=journal_id, user=request.user)

    if request.method == "POST":

        journal.delete()

        return redirect("journal")



@login_required
def delete_habit(request, habit_id):

    habit = Habit.objects.get(id=habit_id, user=request.user)

    if request.method == "POST":

        habit.delete()

        return redirect("habits")

@login_required
def delete_recurring_habit(request, recurring_habit_id):

    recurring_habit = RecurringHabit.objects.get(id=recurring_habit_id, user=request.user)

    if request.method == "POST":

        recurring_habit.delete()

        return redirect("habits")
    
@login_required
def delete_goal(request, goal_id):

    goal = Goal.objects.get(id=goal_id, user=request.user)

    if request.method == "POST":

        goal.delete()

        return redirect("goals")    



@login_required
def logout_view(request):
    logout(request)
    return redirect("login")