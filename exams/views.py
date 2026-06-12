from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Sum
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import getSampleStyleSheet
from learners.models import Learner
from .models import Subject, Exam, Result
from reportlab.lib.pagesizes import letter
from schools.utils import (
    get_current_school
)

from schools.utils import get_current_school

def school_context(request):

    return {
        "current_school": get_current_school(request)
    }
# ==========================================
# CBC GRADING SYSTEM
# ==========================================
def get_grade(marks):

    if marks >= 90:
        return "EE1"
    elif marks >= 75:
        return "EE2"
    elif marks >= 58:
        return "ME1"
    elif marks >= 41:
        return "ME2"
    elif marks >= 31:
        return "AE1"
    elif marks >= 21:
        return "AE2"
    elif marks >= 11:
        return "BE1"
    else:
        return "BE2"


# ==========================================
# SINGLE PAGE CLASS ENTRY
# ==========================================
def class_entry(request):

    grades = Learner.objects.filter(
        school=request.user.school
    ).values_list(
        "grade",
        flat=True
    ).distinct().order_by("grade")

    subjects = Subject.objects.filter(
        school=request.user.school
    )

    exams = Exam.objects.filter(
        school=request.user.school
    )

    learners = []

    selected_grade = ""
    selected_subject = ""
    selected_exam = ""

    if request.method == "POST":

        action = request.POST.get("action")

        selected_grade = request.POST.get("grade")
        selected_subject = request.POST.get("subject")
        selected_exam = request.POST.get("exam")

        if (
            selected_grade
            and selected_subject
            and selected_exam
        ):

            learners = Learner.objects.filter(
                school=request.user.school,
                grade=selected_grade
            )

            # SAVE MARKS
            if action == "save":

                subject = get_object_or_404(
                    Subject,
                    id=selected_subject
                )

                exam = get_object_or_404(
                    Exam,
                    id=selected_exam
                )

                for learner in learners:

                    marks = request.POST.get(
                        f"marks_{learner.id}"
                    )

                    if marks not in ["", None]:

                        marks = int(marks)

                        if 0 <= marks <= 100:

                            Result.objects.update_or_create(
                                learner=learner,
                                subject=subject,
                                exam=exam,
                                defaults={
                                    "marks": marks,
                                    "grade": get_grade(marks)
                                }
                            )

                return redirect("class_entry")

            # LOAD EXISTING MARKS
            for learner in learners:

                result = Result.objects.filter(
                    learner=learner,
                    subject_id=selected_subject,
                    exam_id=selected_exam
                ).first()

                learner.saved_marks = (
                    result.marks if result else ""
                )

    context = {
        "subjects": subjects,
        "exams": exams,
        "grades": grades,
        "learners": learners,
        "selected_grade": selected_grade,
        "selected_subject": selected_subject,
        "selected_exam": selected_exam,
    }

    return render(
        request,
        "exams/class_entry.html",
        context
    )

# ==========================================
# TEACHER RESULTS
# ==========================================
def teacher_results(request):

    exams = Exam.objects.filter(
    school=request.user.school
    )

    grades = (
        Learner.objects
        .values_list("grade", flat=True)
        .distinct()
    )

    subjects = Subject.objects.filter(
        school=request.user.school
    )

    data = []

    selected_exam = None
    selected_grade = None

    if request.method == "POST":

        selected_exam = request.POST.get(
            "exam"
        )

        selected_grade = request.POST.get(
            "grade"
        )

        learners = Learner.objects.filter(
            school=request.user.school,
            grade=selected_grade
        )

        for learner in learners:

            learner_results = Result.objects.filter(
                learner=learner,
                exam_id=selected_exam
            )

            total = 0
            subject_scores = {}

            for subject in subjects:

                result = learner_results.filter(
                    subject=subject
                ).first()

                if result:
                    marks = result.marks
                    grade = result.grade
                else:
                    marks = 0
                    grade = "-"

                subject_scores[subject.name] = {
                    "marks": marks,
                    "grade": grade
                }

                total += marks

            data.append({
                "learner": learner,
                "subjects": subject_scores,
                "total": total
            })

    return render(
        request,
        "exams/teacher_results.html",
        {
            "exams": exams,
            "grades": grades,
            "subjects": subjects,
            "data": data,
            "selected_exam": selected_exam,
            "selected_grade": selected_grade,
        }
    )


# =========================
# MERIT LIST
# =========================
def merit_list(request, exam_id, grade):

    # merge streams of same grade
    # example:
    # 8 Blue
    # 8 Purple
    # 8 Green
    # becomes Grade 8

    grade_number = grade.split()[0]

    learners = Learner.objects.filter(
        school=request.user.school,
        grade__startswith=grade_number
    ).order_by("first_name")

    subjects = Subject.objects.all(
        school=request.user.school
    )

    data = []

    for learner in learners:

        results = Result.objects.filter(
            learner=learner,
            exam_id=exam_id
        )

        result_map = {
            r.subject_id: r
            for r in results
        }

        subject_scores = {}

        total_marks = 0
        subject_count = 0

        for subject in subjects:

            result = result_map.get(subject.id)

            if result:
                marks = result.marks
                grade_value = result.grade
            else:
                marks = 0
                grade_value = "BE2"

            subject_scores[subject.name] = {
                "marks": marks,
                "grade": grade_value
            }

            total_marks += marks
            subject_count += 1

        average_marks = (
            total_marks / subject_count
            if subject_count > 0
            else 0
        )

        overall_grade = get_grade(
            average_marks
        )

        data.append({
            "learner": learner,
            "stream": learner.grade,
            "subjects": subject_scores,
            "total": round(total_marks, 2),
            "total_grade": overall_grade,
            "average": round(
                average_marks, 2
            )
        })

    # rank by total
    data = sorted(
        data,
        key=lambda x: x["total"],
        reverse=True
    )

    for index, row in enumerate(
        data,
        start=1
    ):
        row["rank"] = index

    return render(
        request,
        "exams/merit_list.html",
        {
            "data": data,
            "subjects": subjects,
            "grade": grade_number,
            "exam_id": exam_id,
        }
    )
    from reportlab.lib.pagesizes import letter

def merit_pdf(request, exam_id, grade):
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.styles import getSampleStyleSheet

    grade_number = grade.split()[0]

    learners = Learner.objects.filter(
        school=request.user.school,
        grade__startswith=grade_number)
    subjects = list(Subject.objects.all())

    rows = []

    for learner in learners:
        results = Result.objects.filter(
            learner__school=request.user.school
    ).count()
        result_map = {r.subject_id: r for r in results}

        subject_marks = []
        total = 0

        for subject in subjects:
            result = result_map.get(subject.id)

            marks = result.marks if result else 0
            subject_marks.append(marks)
            total += marks

        avg = total / len(subjects) if subjects else 0

        rows.append([
            learner.assessment_no,
            f"{learner.first_name} {learner.last_name}",
            learner.grade,
            *subject_marks,
            round(total, 2),
            round(avg, 2),
            get_grade(avg)
        ])

    # sort by total (last numeric part before grade)
    rows.sort(key=lambda x: x[3 + len(subjects)], reverse=True)

    # add rank
    for i, row in enumerate(rows, start=1):
        row.insert(0, i)

    # =========================
    # TABLE HEADER
    # =========================
    header = ["Rank", "Assessment No", "Learner", "Class"]

    # rotate subject names using Paragraph + <br/> trick
    styles = getSampleStyleSheet()
    rotated_subjects = [
        Paragraph(f"<b>{s.name}</b>", styles["Normal"])
        for s in subjects
    ]

    header += rotated_subjects
    header += ["Total", "Average", "Grade"]

    table_data = [header] + rows

    # =========================
    # AUTO-FIT COLUMN WIDTHS
    # =========================

    # base widths for fixed columns
    col_widths = [
        30,   # Rank
        80,   # Assessment No
        140,  # Learner
        60    # Class
    ]

    # subject columns (narrow since vertical header)
    subject_width = 30
    col_widths += [subject_width] * len(subjects)

    # final columns
    col_widths += [60, 60, 50]  # Total, Avg, Grade

    # =========================
    # BUILD PDF
    # =========================

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Grade_{grade_number}_Merit_List.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(letter)
    )

    elements = []

    title = Paragraph(
        f"<b>GRADE {grade_number} MERIT LIST</b>",
        styles["Title"]
    )

    elements.append(title)
    elements.append(Spacer(1, 10))

    table = Table(table_data, repeatRows=1, colWidths=col_widths)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response
# ==========================================
# ANALYTICS
# ==========================================
def analytics_dashboard(request):

    return render(
        request,
        "exams/analytics_dashboard.html",
        {
            "total_learners":
                Learner.objects.count(),

            "total_results":
                Result.objects.count(),

            "subject_averages":
                Result.objects.values(
                    "subject__name"
                ).annotate(
                    avg_marks=Avg("marks")
                ),

            "grade_distribution":
                Result.objects.values(
                    "grade"
                ).annotate(
                    count=Count("id")
                ),

            "top_learners":
                Result.objects.values(
                    "learner__first_name",
                    "learner__last_name"
                ).annotate(
                    total=Sum("marks")
                ).order_by("-total")[:5],

            "weak_learners":
                Result.objects.values(
                    "learner__first_name",
                    "learner__last_name"
                ).annotate(
                    total=Sum("marks")
                ).order_by("total")[:5],
        }
    )


# ==========================================
# REPORT CARD PDF
# ==========================================
def report_card(request, learner_id, exam_id):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter  # PORTRAIT
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    learner = get_object_or_404(Learner, id=learner_id)
    subjects = Subject.objects.filter(
    school=learner.school
    )

    # =========================
    # ALL LEARNERS FOR RANKING
    # =========================
    all_learners = Learner.objects.filter(
        school=learner.school,
        grade=learner.grade)

    class_scores = []

    for l in all_learners:
        results = Result.objects.filter(learner=l, exam_id=exam_id)
        total = sum(r.marks for r in results)

        class_scores.append({
            "learner": l,
            "total": total
        })

    class_scores.sort(key=lambda x: x["total"], reverse=True)

    # assign ranks
    for i, item in enumerate(class_scores, start=1):
        item["rank"] = i

    learner_rank = next(
        item["rank"] for item in class_scores if item["learner"].id == learner.id
    )

    learner_total = next(
        item["total"] for item in class_scores if item["learner"].id == learner.id
    )

    # =========================
    # AUTO COMMENT SYSTEM
    # =========================
    avg = learner_total / len(subjects) if subjects else 0

    if avg >= 80:
        comment = "Excellent performance. Keep up the great work."
    elif avg >= 65:
        comment = "Good performance. You can improve further with more effort."
    elif avg >= 50:
        comment = "Fair performance. More revision is recommended."
    else:
        comment = "Weak performance. Immediate improvement is needed."

    # =========================
    # RESULTS MAP
    # =========================
    results = Result.objects.filter(learner=learner, exam_id=exam_id)
    result_map = {r.subject_id: r for r in results}

    # =========================
    # PDF SETUP (PORTRAIT)
    # =========================
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{learner.first_name}_report_card.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=letter  # PORTRAIT
    )

    elements = []
    styles = getSampleStyleSheet()

    # =========================
    # TITLE
    # =========================
    title = Paragraph(
        "<b>OFFICIAL SCHOOL REPORT CARD</b>",
        styles["Title"]
    )
    elements.append(title)
    elements.append(Spacer(1, 10))

    # =========================
    # STUDENT INFO
    # =========================
    info = Paragraph(
        f"""
        <b>Name:</b> {learner.first_name} {learner.last_name}<br/>
        <b>Assessment No:</b> {learner.assessment_no}<br/>
        <b>Class:</b> {learner.grade}<br/>
        <b>Rank in Class:</b> {learner_rank}
        """,
        styles["Normal"]
    )

    elements.append(info)
    elements.append(Spacer(1, 15))

    # =========================
    # SUBJECT TABLE
    # =========================
    table_data = [["Subject", "Marks", "Grade"]]

    total = 0

    for sub in subjects:
        result = result_map.get(sub.id)

        marks = result.marks if result else 0
        grade = get_grade(marks)

        total += marks

        table_data.append([sub.name, marks, grade])

    avg2 = total / len(subjects) if subjects else 0

    table_data.append(["TOTAL", total, ""])
    table_data.append(["AVERAGE", round(avg2, 2), ""])
    table_data.append(["OVERALL GRADE", get_grade(avg2), ""])

    table = Table(table_data, colWidths=[200, 80, 80])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    # =========================
    # TEACHER COMMENT
    # =========================
    comment_box = Paragraph(
        f"""
        <b>Teacher's Comment:</b><br/>
        {comment}
        """,
        styles["Normal"]
    )

    elements.append(comment_box)

    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)
    return response

def bulk_report_cards(request, exam_id):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Bulk_Report_Exam_{exam_id}.pdf"'
    )

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    subjects = Subject.objects.filter(
        school=request.user.school
    )
    learners = Learner.objects.filter(
        school=request.user.school
    )

    # =========================
    # CLASS RANKING
    # =========================
    class_scores = []

    for l in learners:
        results = Result.objects.filter(learner=l, exam_id=exam_id)
        total = sum(r.marks for r in results)

        class_scores.append({
            "learner": l,
            "total": total
        })

    class_scores.sort(key=lambda x: x["total"], reverse=True)

    for i, item in enumerate(class_scores, start=1):
        item["rank"] = i

    rank_map = {
        item["learner"].id: item["rank"]
        for item in class_scores
    }

    # =========================
    # EACH LEARNER REPORT CARD
    # =========================
    for item in class_scores:
        learner = item["learner"]

        results = Result.objects.filter(
            learner=learner,
            exam_id=exam_id
        )

        result_map = {r.subject_id: r for r in results}

        # TITLE
        elements.append(Paragraph(
            "<b>OFFICIAL REPORT CARD</b>",
            styles["Title"]
        ))
        elements.append(Spacer(1, 10))

        # STUDENT INFO
        info = Paragraph(
            f"""
            <b>Name:</b> {learner.first_name} {learner.last_name}<br/>
            <b>Assessment No:</b> {learner.assessment_no}<br/>
            <b>Class:</b> {learner.grade}<br/>
            <b>Rank:</b> {item['rank']}
            """,
            styles["Normal"]
        )
        elements.append(info)
        elements.append(Spacer(1, 10))

        # SUBJECT TABLE
        table_data = [["Subject", "Marks", "Grade"]]

        total = 0

        for sub in subjects:
            result = result_map.get(sub.id)

            marks = result.marks if result else 0
            grade = get_grade(marks)

            total += marks

            table_data.append([sub.name, marks, grade])

        avg = total / len(subjects) if subjects else 0

        table_data.append(["TOTAL", total, ""])
        table_data.append(["AVERAGE", round(avg, 2), ""])
        table_data.append(["OVERALL GRADE", get_grade(avg), ""])

        table = Table(table_data, colWidths=[200, 100, 100])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 10))

        # COMMENT SYSTEM
        if avg >= 80:
            comment = "Excellent performance."
        elif avg >= 65:
            comment = "Good performance."
        elif avg >= 50:
            comment = "Fair performance."
        else:
            comment = "Needs improvement."

        elements.append(Paragraph(
            f"<b>Teacher Comment:</b> {comment}",
            styles["Normal"]
        ))

        # PAGE BREAK
        elements.append(PageBreak())

    doc.build(elements)
    return response