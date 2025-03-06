from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def manage_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        profile.location = request.POST.get('location')
        profile.save()
        return redirect('manage_profile')
    return render(request, 'manage_profile.html', {'profile': profile})


