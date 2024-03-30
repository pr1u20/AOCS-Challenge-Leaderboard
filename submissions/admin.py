from django.contrib import admin
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'score_ideal', 'score_disturbances', 'score_noise', 'submission_time']
    search_fields = ['user__username']
    list_filter = ['submission_time']