from django.shortcuts import render, redirect
from .forms import SubmissionForm
from .models import Submission
import csv
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.contrib.auth.models import User

@login_required
def submit_csv(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            score = process_csv(request.FILES['file'])
            Submission.objects.create(user=request.user, score=score)
            return redirect('leaderboard')  # Redirect to the leaderboard view
    else:
        form = SubmissionForm()
    return render(request, 'submissions/submit_csv.html', {'form': form})

def process_csv(file):
    # Process the CSV file and return a score
    # Placeholder for your scoring logic
    return 10.0  # Example score

def get_leaderboard():
    leaderboard_submissions = []

    # Get all users who have at least one submission
    users_with_submissions = User.objects.filter(submission__isnull=False).distinct()

    for user in users_with_submissions:
        # For each user, find their highest-scoring submission
        best_submission = user.submission_set.order_by('-score', '-submission_time').first()
        if best_submission:
            leaderboard_submissions.append(best_submission)

    # Sort the submissions by score and submission time
    leaderboard_submissions.sort(key=lambda x: (-x.score, x.submission_time))

    return leaderboard_submissions

def leaderboard(request):
    
    leaderboard_submissions = get_leaderboard()

    return render(request, 'submissions/leaderboard.html', {'submissions': leaderboard_submissions})