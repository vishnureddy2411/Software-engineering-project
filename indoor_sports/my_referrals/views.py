from django.shortcuts import render

def referral_list(request):
    # Your view logic here
    return render(request, 'referrals/referral_list.html')
