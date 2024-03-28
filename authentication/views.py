from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from submissions.views import get_leaderboard

# Create your views here.
def home(request):
    leaderboard_submissions = get_leaderboard()
    return render(request, 'index.html', {'submissions': leaderboard_submissions})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']

        if password != confirmPassword:
            messages.error(request, 'Passwords do not match!')
            return redirect('home')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken!')
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken!')
            return redirect('home')
    

        myuser = User.objects.create_user(username, email, password)
        #myuser.username = request.POST['username']
        myuser.save()

        messages.success(request, 'Your account has been created successfully!')

        return redirect('signin')
        

    return render(request, 'authentication/signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in!')
            return render(request, 'index.html')
        else:
            messages.error(request, 'Invalid credentials, please try again!')
            return redirect('home')
        
    return render(request, 'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out!')
    return redirect('home')













