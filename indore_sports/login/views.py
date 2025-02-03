from django.shortcuts import render,redirect
from django.contrib.auth import login
def loginpage(request):
    if request.method == 'POST':
        # Logic for user registration (will add later)
        pass
    return render(request, 'loginpage.html')

# Create your views here.
