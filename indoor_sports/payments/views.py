from django.shortcuts import render, redirect
from django.http import HttpResponse

def user_details(request):
    # Example data
    user_id = 12345
    amount = 100.00
    date = '2025-02-08T14:08:42'
    method = 'Credit Card'
    context = {
        'user_id': user_id,
        'amount': amount,
        'date': date,
        'method': method,
    }
    return render(request, 'user_details.html', context)

def payment_form(request):
    user_id = request.GET.get('user_id')
    amount = request.GET.get('amount')
    date = request.GET.get('date')
    method = request.GET.get('method')
    context = {
        'user_id': user_id,
        'amount': amount,
        'date': date,
        'method': method,
    }
    return render(request, 'payment_form.html', context)

def process_payment(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        amount = request.POST['amount']
        date = request.POST['date']
        method = request.POST['method']
        payment_method = request.POST['payment_method']
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Validate card details
        if payment_method == 'credit_card':
            if not (validate_card_number(card_number) and validate_expiry_date(expiry_date) and validate_cvv(cvv)):
                return HttpResponse("Invalid card details.")

        # Simulate payment processing
        return redirect('success')

    return HttpResponse("Invalid request method.")

def validate_card_number(card_number):
    return len(card_number) == 16 and card_number.isdigit()

def validate_expiry_date(expiry_date):
    # Add proper validation logic
    return len(expiry_date) == 5 and expiry_date[2] == '/'

def validate_cvv(cvv):
    return len(cvv) == 3 and cvv.isdigit()

def success(request):
    return render(request, 'success.html')
