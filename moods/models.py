from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('Happy', 'Happy'),
        ('Neutral', 'Neutral'),
        ('Sad', 'Sad'),
        ('Anxious', 'Anxious'),
        ('Angry', 'Angry'),
        ('Excited', 'Excited'),
        ('Tired', 'Tired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, name='mood')
    stress_level = models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(0)], name='stress_level')
    sleep_hours = models.FloatField(validators=[MaxValueValidator(24.0), MinValueValidator(0.0)], name='sleep_hours')
    note = models.TextField(blank=True, name = 'note')
    productivity = models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(0)], name='productivity', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, name='created_at')

    def __str__(self):
        return f"{self.user.username} - {self.mood}"
