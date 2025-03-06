from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Referral
from accounts.models import User  # Ensure the correct User model is imported

@login_required
def referral_list(request):
    user = request.user
    if not isinstance(user, User):
        print(f"request.user is not a User instance: {type(user)}")  # Debugging information
        return redirect('login')
    referrals_given = Referral.objects.filter(referrer_user=user)
    referrals_received = Referral.objects.filter(referred_user=user)
    return render(request, 'my_referrals/referral_list.html', {
        'referrals_given': referrals_given,
        'referrals_received': referrals_received
    })
