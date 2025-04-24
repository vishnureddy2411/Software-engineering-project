import matplotlib
matplotlib.use('Agg')  # For server-side rendering
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count
from bookings.models import BookingReport
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def generate_graphs(data):
    """
    Generate graphs and return them as a list of (image, description) tuples.
    """
    graphs = []

    # Graph 1: Bookings by Sport
    sport_counts = data.values('sport').annotate(total=Count('sport'))
    plt.figure(figsize=(6, 4))
    plt.bar([item['sport'] for item in sport_counts], [item['total'] for item in sport_counts], color=['#2a9d8f', '#e76f51', '#f4a261'])
    plt.title('Bookings by Sport')
    plt.xlabel('Sport')
    plt.ylabel('Total Bookings')
    plt.xticks(rotation=45)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings for each sport.'))
    buffer.close()
    plt.close()

    # Graph 2: Bookings by Location
    location_counts = data.values('location').annotate(total=Count('location'))
    plt.figure(figsize=(6, 4))
    plt.bar([item['location'] for item in location_counts], [item['total'] for item in location_counts], color=['#8ecae6', '#219ebc', '#023047', '#ffb703', '#fb8500'])
    plt.title('Bookings by Location')
    plt.xlabel('Location')
    plt.ylabel('Total Bookings')
    plt.xticks(rotation=45)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings for each location.'))
    buffer.close()
    plt.close()

    # Graph 3: Bookings by Gender
    gender_counts = data.values('gender').annotate(total=Count('gender'))
    plt.figure(figsize=(6, 4))
    plt.bar([item['gender'] for item in gender_counts], [item['total'] for item in gender_counts], color=['#457b9d', '#1d3557', '#a8dadc'])
    plt.title('Bookings by Gender')
    plt.xlabel('Gender')
    plt.ylabel('Total Bookings')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings by gender.'))
    buffer.close()
    plt.close()

    # Graph 4: Booking Status (Donut Chart)
    status_counts = data.values('status').annotate(total=Count('status'))
    labels = [item['status'] for item in status_counts]
    sizes = [item['total'] for item in status_counts]
    plt.figure(figsize=(6, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#2a9d8f', '#e76f51', '#f4a261'], wedgeprops={'width': 0.4})
    plt.title('Booking Status Distribution')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Distribution of booking status (donut chart).'))
    buffer.close()
    plt.close()

    return graphs

def report_view(request, period):
    """
    Unified view for displaying reports: weekly, monthly, yearly.
    """
    now = timezone.now()
    title = "Report"

    # Get data based on the requested period
    if period == 'weekly':
        data = BookingReport.objects.filter(date__week=now.isocalendar()[1])
        title = "Weekly Report"
    elif period == 'monthly':
        data = BookingReport.objects.filter(date__month=now.month)
        title = "Monthly Report"
    elif period == 'yearly':
        data = BookingReport.objects.filter(date__year=now.year)
        title = "Yearly Report"
    elif period == 'all':  # Fix: Explicit condition for all bookings
        data = BookingReport.objects.all()
        title = "All Bookings"
    else:
        messages.error(request, "Invalid report period requested.")
        return redirect("home")

    # Generate graphs based on retrieved data
    graphs = generate_graphs(data)

    context = {
        'title': title,
        'graphs': graphs,
        'bookings': data,  # Include bookings in context to display in the table
    }
    return render(request, 'common_report.html', context)

# import matplotlib
# matplotlib.use('Agg')
# from django.shortcuts import render, redirect
# from django.utils import timezone
# from django.db.models import Count
# from bookings.models import BookingReport
# import matplotlib.pyplot as plt
# import base64
# from io import BytesIO
# from django.contrib import messages
# from accounts.models import User  # Ensure compatibility with User model
# from django.contrib.auth.decorators import login_required


# def generate_graphs(data):
#     """
#     Generate graphs based on booking data using Matplotlib.
#     Encodes graphs as Base64 strings to render in templates.
#     """
#     graphs = []

#     # Custom colors
#     sport_colors = ['#2a9d8f', '#e76f51', '#f4a261', '#264653']
#     location_colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703', '#fb8500']
#     gender_colors = ['#457b9d', '#1d3557', '#a8dadc']

#     # Graph 1: Bookings by Sport
#     sport_counts = data.values('sport').annotate(total=Count('sport'))
#     plt.figure(figsize=(6, 4))
#     plt.bar([item['sport'] for item in sport_counts], [item['total'] for item in sport_counts], color=sport_colors)
#     plt.title('Bookings by Sport', fontsize=14, color='#264653')
#     plt.xlabel('Sport', fontsize=12)
#     plt.ylabel('Total Bookings', fontsize=12)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     buffer = BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings for each sport.'))
#     buffer.close()
#     plt.close()

#     # Graph 2: Bookings by Location
#     location_counts = data.values('location').annotate(total=Count('location'))
#     plt.figure(figsize=(6, 4))
#     plt.bar([item['location'] for item in location_counts], [item['total'] for item in location_counts], color=location_colors)
#     plt.title('Bookings by Location', fontsize=14, color='#264653')
#     plt.xlabel('Location', fontsize=12)
#     plt.ylabel('Total Bookings', fontsize=12)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     buffer = BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings for each location.'))
#     buffer.close()
#     plt.close()

#     # Graph 3: Bookings by Gender
#     gender_counts = data.values('gender').annotate(total=Count('gender'))
#     plt.figure(figsize=(6, 4))
#     plt.bar([item['gender'] for item in gender_counts], [item['total'] for item in gender_counts], color=gender_colors)
#     plt.title('Bookings by Gender', fontsize=14, color='#264653')
#     plt.xlabel('Gender', fontsize=12)
#     plt.ylabel('Total Bookings', fontsize=12)
#     plt.tight_layout()
#     buffer = BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Number of bookings by gender.'))
#     buffer.close()
#     plt.close()

#     # Graph 4: Booking Status Donut Chart (Confirmed vs Cancelled vs Pending)
#     status_counts = data.values('status').annotate(total=Count('status'))
#     labels = [item['status'] for item in status_counts]
#     sizes = [item['total'] for item in status_counts]
#     plt.figure(figsize=(6, 4))
#     plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#2a9d8f', '#e76f51', '#f4a261'], wedgeprops={'width': 0.4})
#     plt.title('Booking Status Distribution')
#     plt.tight_layout()
#     buffer = BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     graphs.append((base64.b64encode(buffer.getvalue()).decode('utf-8'), 'Distribution of booking status (donut chart).'))
#     buffer.close()
#     plt.close()

#     return graphs


# @login_required
# def weekly_report(request):
#     """
#     Generate and display the weekly booking report.
#     Requires a logged-in user (admin or normal user).
#     """
#     week_number = timezone.now().isocalendar()[1]
#     bookings = BookingReport.objects.filter(date__week=week_number)

#     # Check if the user has appropriate permissions (if applicable)
#     if not request.user.is_staff and not request.user.is_authenticated:
#         messages.error(request, "You are not authorized to access this report.")
#         return redirect("loginpage")

#     graphs = generate_graphs(bookings)
#     context = {
#         'report_title': 'Weekly Booking Report',
#         'report_heading': '📅 Weekly Booking Report',
#         'table_heading': '📋 Booking Details (Week)',
#         'bookings': bookings,
#         'graphs': graphs
#     }
#     return render(request, 'common_report.html', context)


# @login_required
# def monthly_report(request):
#     """
#     Generate and display the monthly booking report.
#     Requires a logged-in user (admin or normal user).
#     """
#     month = timezone.now().month
#     bookings = BookingReport.objects.filter(date__month=month)

#     # Ensure user is authenticated to view the report
#     if not request.user.is_staff and not request.user.is_authenticated:
#         messages.error(request, "You are not authorized to access this report.")
#         return redirect("loginpage")

#     graphs = generate_graphs(bookings)
#     context = {
#         'report_title': 'Monthly Booking Report',
#         'report_heading': '🗓️ Monthly Booking Report',
#         'table_heading': '📋 Booking Details (Month)',
#         'bookings': bookings,
#         'graphs': graphs
#     }
#     return render(request, 'common_report.html', context)


# @login_required
# def yearly_report(request):
#     """
#     Generate and display the yearly booking report.
#     Requires a logged-in user (admin or normal user).
#     """
#     year = timezone.now().year
#     bookings = BookingReport.objects.filter(date__year=year)

#     # Ensure user is authenticated to view the report
#     if not request.user.is_staff and not request.user.is_authenticated:
#         messages.error(request, "You are not authorized to access this report.")
#         return redirect("loginpage")

#     graphs = generate_graphs(bookings)
#     context = {
#         'report_title': 'Yearly Booking Report',
#         'report_heading': '📆 Yearly Booking Report',
#         'table_heading': '📋 Booking Details (Year)',
#         'bookings': bookings,
#         'graphs': graphs
#     }
#     return render(request, 'common_report.html', context)
