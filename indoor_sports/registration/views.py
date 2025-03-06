from django.shortcuts import render,redirect
from django.core.checks import register
def registerpage(request):
    if request.method == 'POST':
        # Logic for user registration (will add later)
        pass
    return render(request, 'registerpage.html')
