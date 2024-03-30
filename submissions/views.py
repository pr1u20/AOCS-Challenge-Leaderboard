from django.shortcuts import render, redirect
from .forms import SubmissionForm
from .models import Submission
import os
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.contrib.auth.models import User
import pickle
from django.conf import settings
from pyaocs.simulation import digital_twin
from pyaocs import parameters as param
from pyaocs.control.example import SimpleTestControl
import numpy as np
import sys

sys.modules['__main__'].SimpleTestControl = SimpleTestControl

@login_required
def submit_pickle(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            score = process_pickle_file(request.FILES['file'])
            Submission.objects.create(user=request.user, score=score)
            return redirect('leaderboard')  # Redirect to the leaderboard view
    else:
        form = SubmissionForm()
    return render(request, 'submissions/submit_csv.html', {'form': form})

def scoring(env):
    position_error = np.mean(np.abs((np.array(env.actual_positions) - np.array(env.target_positions))))
    orientation_error = 0
    firing_time = np.sum(env.F1s) * 1 / param.sample_rate

    score = 400*position_error + orientation_error + firing_time

    print(f"Position error: {position_error} m")
    print(f"Firing time: {firing_time} s")
    print(f"Score: {score}")

    return score

def run_strategy_and_calculate_score(strategy_instance):

    env, _, _ = digital_twin.run(strategy_instance,
                                 render = False,
                                 real_time=False,
                                 use_disturbances=False,
                                 noise=False,
                                 plot=False)
    
    # Calculate the score based on the environment state
    score = scoring(env)

    return score

def process_pickle_file(uploaded_file):
    # Optionally: validate the file's authenticity/contents as much as possible here

    # Load the pickle data from an in-memory file
    try:
        # Read the file into memory, and then use pickle.loads() to deserialize it.
        uploaded_file.seek(0)  # Move the file pointer to the start of the file
        file_content = uploaded_file.read()
        strategy_instance = pickle.loads(file_content)
        #strategy_instance = pickle.loads(pickle_data)

        # Ensure execution of the strategy is done securely!
        score = run_strategy_and_calculate_score(strategy_instance)

        return score
    except (pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError) as e:
        # Handle the exception for invalid pickle data
        return f"Error loading pickle file: {e}"
    except Exception as e:
        # Handle other exceptions
        return f"An error occurred: {str(e)}"

def get_leaderboard():
    leaderboard_submissions = []

    # Get all users who have at least one submission
    users_with_submissions = User.objects.filter(submission__isnull=False).distinct()

    for user in users_with_submissions:
        # For each user, find their highest-scoring submission
        best_submission = user.submission_set.order_by('score', 'submission_time').first()
        if best_submission:
            leaderboard_submissions.append(best_submission)

    # Sort the submissions by score and submission time
    leaderboard_submissions.sort(key=lambda x: (x.score, x.submission_time))

    return leaderboard_submissions

def leaderboard(request):
    
    leaderboard_submissions = get_leaderboard()

    return render(request, 'submissions/leaderboard.html', {'submissions': leaderboard_submissions})