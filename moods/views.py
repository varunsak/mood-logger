from urllib import request

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MoodEntry
from django.db.models import Avg, Count
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
import json
from django.utils.timezone import now
import datetime
from django.db.models.functions import TruncDate

#New User Entering

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('register')


#Registering a new user

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
        print("Something went wrong")

    return render(request, 'register.html', {'form': form})




#Dashboard view showing mood entries and stats
@login_required
def dashboard(request):
    entries = MoodEntry.objects.filter(user=request.user).order_by('-created_at')

    last_week = timezone.now() - timedelta(days=7)
    weekly_entries = entries.filter(created_at__gte=last_week)

    avg_stress = weekly_entries.aggregate(Avg('stress_level'))['stress_level__avg']
    avg_stress = round(avg_stress, 2) if avg_stress is not None else None
    avg_sleep = weekly_entries.aggregate(Avg('sleep_hours'))['sleep_hours__avg']
    avg_sleep = round(avg_sleep, 2) if avg_sleep is not None else None
    most_common_mood_data = weekly_entries.values('mood').annotate(count=Count('mood')).order_by('-count').first()
    most_common_mood = most_common_mood_data['mood'] if most_common_mood_data else None

    context = {
        'entries': entries,
        'avg_stress': avg_stress,
        'avg_sleep': avg_sleep,
        'most_common_mood': most_common_mood,
    }

    return render(request, 'dashboard.html', context)


#View to add new mood entry
@login_required
def add_mood(request):
    if request.method == 'POST':
        MoodEntry.objects.create(
            user=request.user,
            mood=request.POST['mood'],
            stress_level=request.POST['stress_level'],
            sleep_hours=request.POST['sleep_hours'],
            note=request.POST.get('note', ''), 
            productivity=request.POST.get('productivity', None),
        )
        return redirect('dashboard')

    return render(request, 'add_mood.html')

@login_required
def update_mood(request, entry_id):
    entry = MoodEntry.objects.get(id=entry_id, user=request.user)

    if request.method == 'POST':
        entry.mood = request.POST['mood']
        entry.stress_level = request.POST['stress_level']
        entry.sleep_hours = request.POST['sleep_hours']
        entry.note = request.POST.get('note', '')
        entry.productivity = request.POST.get('productivity', None)
        entry.save()
        return redirect('dashboard')

    return render(request, 'update_mood.html', {'entry': entry})


@login_required
def graphs(request):
    
    mood_counts = (
        MoodEntry.objects
        .filter(user=request.user)
        .values('mood')
        .annotate(count=Count('mood'))
    )
    entries = (
    MoodEntry.objects
    .filter(user=request.user)
    .annotate(date=TruncDate('created_at'))
    .values('date')
    .annotate(
        avg_sleep=Avg('sleep_hours'),
        avg_stress=Avg('stress_level'),
        avg_productivity=Avg('productivity'),
    )
    .order_by('date')
)
    
    data = {
        'dates': [
    entry['date'].strftime('%Y-%m-%d')
    for entry in entries
],
        'moods': [entry['mood'] for entry in mood_counts],
        'moodCounts': [entry['count'] for entry in mood_counts],
        'stressData': [entry['avg_stress'] for entry in entries],
        'sleepData': [entry['avg_sleep'] for entry in entries],
        'productivityData': [entry['avg_productivity'] for entry in entries],
    }

    return render(request, 'graphs.html', {'data': json.dumps(data)})


@login_required
def delete_entry(request, entry_id):
    deleting_entry = MoodEntry.objects.get(id=entry_id, user=request.user)
    if request.method == 'POST':
        deleting_entry.delete()
        return redirect('dashboard')
    MoodEntry.objects.get(id=entry_id, user=request.user).delete()
    
    