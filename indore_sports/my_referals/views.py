from django.shortcuts import render,redirect

def myreferals(request):
    if request.method == 'POST':
        # Logic for user registration (will add later)
        pass
    return render(request, 'myreferals.html')

# Create your views here.

