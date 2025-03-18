import matplotlib
matplotlib.use('Agg')
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count
from bookings.models import BookingReport
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from django.contrib import messages
from accounts.models import User  # Ensure compatibility with User model
from django.contrib.auth.decorators import login_required


def generate_graphs(data):
    """
    Generate graphs based on booking data using Matplotlib.
    Encodes graphs as Base64 strings to render in templates.
    """
    graphs = []

    # Custom colors
    sport_colors = ['#2a9d8f', '#e76f51', '#f4a261', '#264653']
    location_colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703', '#fb8500']
    gender_colors = ['#457b9d', '#1d3557', '#a8dadc']

    # Graph 1: Bookings by Sport
    sport_counts = data.values('sport').annotate(total=Count('sport'))
    plt.figure(figsize=(6, 4))
    plt.bar([item['sport'] for item in sport_counts], [item['total'] for item in sport_counts], color=sport_colors)
    plt.title('Bookings by Sport', fontsize=14, color='#264653')
    plt.xlabel('Sport', fontsize=12)
    plt.ylabel('Total Bookings', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings for each sport.'))
    buffer.close()
    plt.close()

    # Graph 2: Bookings by Location
    location_counts = data.values('location').annotate(total=Count('location'))
    plt.figure(figsize=(6, 4))
    plt.bar([item['location'] for item in location_counts], [item['total'] for item in location_counts], color=location_colors)
    plt.title('Bookings by Location', fontsize=14, color='#264653')
    plt.xlabel('Location', fontsize=12)
    plt.ylabel('Total Bookings', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings for each location.'))
    buffer.close()
    plt.close()

    # Graph 3: Bookings by Gender
    gender_counts = data.values('gender').annotate(total=Count('gender'))
    plt.figure(figsize=(6, 4))
    plt.bar([item['gender'] for item in gender_counts], [item['total'] for item in gender_counts], color=gender_colors)
    plt.title('Bookings by Gender', fontsize=14, color='#264653')
    plt.xlabel('Gender', fontsize=12)
    plt.ylabel('Total Bookings', fontsize=12)
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings by gender.'))
    buffer.close()
    plt.close()

    return graphs


@login_required
def weekly_report(request):
    """
    Generate and display the weekly booking report.
    Requires a logged-in user (admin or normal user).
    """
    week_number = timezone.now().isocalendar()[1]
    bookings = BookingReport.objects.filter(date__week=week_number)

    # Check if the user has appropriate permissions (if applicable)
    if not request.user.is_staff and not request.user.is_authenticated:
        messages.error(request, "You are not authorized to access this report.")
        return redirect("loginpage")

    graphs = generate_graphs(bookings)
    context = {
        'report_title': 'Weekly Booking Report',
        'report_heading': '📅 Weekly Booking Report',
        'table_heading': '📋 Booking Details (Week)',
        'bookings': bookings,
        'graphs': graphs
    }
    return render(request, 'common_report.html', context)


@login_required
def monthly_report(request):
    """
    Generate and display the monthly booking report.
    Requires a logged-in user (admin or normal user).
    """
    month = timezone.now().month
    bookings = BookingReport.objects.filter(date__month=month)

    # Ensure user is authenticated to view the report
    if not request.user.is_staff and not request.user.is_authenticated:
        messages.error(request, "You are not authorized to access this report.")
        return redirect("loginpage")

    graphs = generate_graphs(bookings)
    context = {
        'report_title': 'Monthly Booking Report',
        'report_heading': '🗓️ Monthly Booking Report',
        'table_heading': '📋 Booking Details (Month)',
        'bookings': bookings,
        'graphs': graphs
    }
    return render(request, 'common_report.html', context)


@login_required
def yearly_report(request):
    """
    Generate and display the yearly booking report.
    Requires a logged-in user (admin or normal user).
    """
    year = timezone.now().year
    bookings = BookingReport.objects.filter(date__year=year)

    # Ensure user is authenticated to view the report
    if not request.user.is_staff and not request.user.is_authenticated:
        messages.error(request, "You are not authorized to access this report.")
        return redirect("loginpage")

    graphs = generate_graphs(bookings)
    context = {
        'report_title': 'Yearly Booking Report',
        'report_heading': '📆 Yearly Booking Report',
        'table_heading': '📋 Booking Details (Year)',
        'bookings': bookings,
        'graphs': graphs
    }
    return render(request, 'common_report.html', context)
