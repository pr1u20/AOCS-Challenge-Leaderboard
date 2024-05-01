from django.shortcuts import render, redirect
from .forms import SubmissionForm
from .models import Submission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from pyaocs.simulation import digital_twin
from pyaocs import parameters as param
import numpy as np
import cloudpickle

@login_required
def submit_pickle(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            scores = process_pickle_file(request.FILES['file'])
            Submission.objects.create(user=request.user, 
                                      score_ideal=round(scores[0], 2),
                                      score_disturbances=round(scores[1], 2),
                                      score_noise=round(scores[2], 2))
            return redirect('leaderboard')  # Redirect to the leaderboard view
    else:
        form = SubmissionForm()
    return render(request, 'submissions/submit_csv.html', {'form': form})

def scoring(env):
    position_error = np.mean(np.abs((np.array(env.actual_positions) - np.array(env.target_positions))))
    orientation_error = 0
    firing_time = np.sum(np.array(env.F1s)) * 1 / param.sample_rate

    score = 400*position_error + orientation_error + firing_time

    print(f"Position error: {position_error} m")
    print(f"Firing time: {firing_time} s")
    print(f"Score: {score}")

    return score

def run_strategy_and_calculate_score(strategy_instance):

    print(strategy_instance)

    env, _, _ = digital_twin.run(strategy_instance,
                                 render = False,
                                 real_time=False,
                                 use_disturbances=False,
                                 noise=False,
                                 plot=False)
    
    # Calculate the score based on the environment state
    score_ideal = scoring(env)

    env, _, _ = digital_twin.run(strategy_instance,
                                 render = False,
                                 real_time=False,
                                 use_disturbances=True,
                                 noise=False,
                                 plot=False)
    
    # Calculate the score based on the environment state
    score_disturbances = scoring(env)

    env, _, _ = digital_twin.run(strategy_instance,
                                 render = False,
                                 real_time=False,
                                 use_disturbances=True,
                                 noise=True,
                                 plot=False)
    
    # Calculate the score based on the environment state
    score_noise = scoring(env)

    return [score_ideal, score_disturbances, score_noise]

def process_pickle_file(uploaded_file):
    # Optionally: validate the file's authenticity/contents as much as possible here

    # Load the pickle data from an in-memory file
    try:
        # Read the file into memory, and then use pickle.loads() to deserialize it.
        strategy_instance = cloudpickle.loads(uploaded_file.read())

        # Ensure execution of the strategy is done securely!
        score = run_strategy_and_calculate_score(strategy_instance)

        return score
    except (AttributeError, EOFError, ImportError, IndexError) as e:
        # Handle the exception for invalid pickle data
        return f"Error loading pickle file: {e}"
    except Exception as e:
        # Handle other exceptions
        return f"An error occurred: {str(e)}"

def get_leaderboard():
    leaderboard_submissions = []
    users = User.objects.all()

    # Get all users who have at least one submission
    users_with_submissions = User.objects.filter(submission__isnull=False).distinct()

    for user in users_with_submissions:
        # For each user, find their highest-scoring submission
        best_submission = user.submission_set.order_by('score_ideal', 'submission_time').first()

        # Find the latest submission by submission time
        latest_submission = user.submission_set.order_by('-submission_time').first()

        if best_submission:
            
            leaderboard_submissions.append({
                'user': user,
                'score_ideal': best_submission.score_ideal,
                'score_disturbances': best_submission.score_disturbances,
                'score_noise': best_submission.score_noise,
                'submission_time': best_submission.submission_time,
                'latest_submission_time': latest_submission.submission_time
            })
            

    # Sort the submissions by score and submission time
    #leaderboard_submissions.sort(key=lambda x: (x.score_ideal, x.submission_time))
    leaderboard_submissions.sort(key=lambda x: (x['score_ideal'], x['latest_submission_time']))

    return leaderboard_submissions

def leaderboard(request):
    
    leaderboard_submissions = get_leaderboard()

    return render(request, 'submissions/leaderboard.html', {'submissions': leaderboard_submissions})