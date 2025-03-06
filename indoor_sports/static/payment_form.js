// payment_form.js

document.addEventListener('DOMContentLoaded', () => {
    const paymentMethodSelect = document.getElementById('payment_method');
    const cardPaymentDetails = document.getElementById('card-payment-details');

    paymentMethodSelect.addEventListener('change', (event) => {
        if (event.target.value === 'credit_card') {
            cardPaymentDetails.classList.remove('hidden');
        } else {
            cardPaymentDetails.classList.add('hidden');
        }
