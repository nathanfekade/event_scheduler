from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    user = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='events'
            )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    recurrence_rule = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
