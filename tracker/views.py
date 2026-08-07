import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Habit, RecurringHabit, ActivityTimeCalculate, Goal
from .forms import HabitForm, RecurringHabitForm, GoalForm
from django.utils import timezone
from datetime import date

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
    today = datetime.date.today()

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