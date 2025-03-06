from django.shortcuts import render,redirect

def dashboards(request):
    if request.method == 'POST':
        # Logic for user registration (will add later)
        pass
    return render(request, 'dashboards.html')

# Create your views here.
