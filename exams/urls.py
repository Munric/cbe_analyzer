from django.urls import path

from .views import (
    class_entry,
    teacher_results,
    merit_list,
    merit_pdf,
    bulk_report_cards,
    analytics_dashboard,
    report_card
)

urlpatterns = [

    # =========================
    # CLASS ENTRY
    # =========================
    path(
        "class-entry/",
        class_entry,
        name="class_entry"
    ),

    # =========================
    # TEACHER RESULTS
    # =========================
    path(
        "results/",
        teacher_results,
        name="teacher_results"
    ),

    # =========================
    # MERIT LIST
    # =========================
    path(
        "merit/<int:exam_id>/<str:grade>/",
        merit_list,
        name="merit_list"
    ),

    path(
          "merit-pdf/<int:exam_id>/<str:grade>/",
          merit_pdf,
          name="merit_pdf"
    ),

    # =========================
    # ANALYTICS
    # =========================
    path(
        "analytics/",
        analytics_dashboard,
        name="analytics_dashboard"
    ),

    # =========================
    # REPORT CARD PDF
    # =========================
    path(
        "report/<int:learner_id>/<int:exam_id>/",
        report_card,
        name="report_card"
    ),

    path(
        "bulk-report/<int:exam_id>/",
        bulk_report_cards,
        name="bulk_report_cards"
    ),
]