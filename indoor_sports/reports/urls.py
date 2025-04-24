# from django.urls import path
# from . import views

# urlpatterns = [
#     path("weekly-report/", views.weekly_report, name="weekly_report"),
#     path("monthly-report/", views.monthly_report, name="monthly_report"),
#     path("yearly-report/", views.yearly_report, name="yearly_report"),

#     # Optional: unified page that displays all charts and table in one with tab switching
#     path("report-dashboard/", views.yearly_report, name="report_dashboard"),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('report/<str:period>/', views.report_view, name='report_view'),  # Unified reporting view
]
