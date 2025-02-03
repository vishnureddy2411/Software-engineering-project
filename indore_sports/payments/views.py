from django.shortcuts import render,redirect

def payments(request):
    if request.method == 'POST':
        # Logic for user registration (will add later)
        pass
    return render(request, 'payments.html')

# Create your views here.
