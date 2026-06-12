from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count

import pandas as pd

from .forms import LearnerForm
from .models import Learner
from schools.models import School
# ===================================
# LEARNER LIST (CLASS CARDS)
# ===================================

def learner_list(request):

    school = request.user.school

    print("CURRENT USER:", request.user)
    print("SCHOOL:", school)
    print("SCHOOL ID:", school.id if school else None)
    
    class_cards = (
        Learner.objects
        .filter(school=school)
        .values("grade")
        .annotate(total=Count("id"))
        .order_by("grade")
    )

    total_learners = (
        Learner.objects
        .filter(school=school)
        .count()
    )

    learners = Learner.objects.none()

    selected_grade = request.GET.get("grade")

    if selected_grade:
        learners = (
            Learner.objects
            .filter(
                school=school,
                grade=selected_grade
            )
            .order_by(
                "first_name",
                "last_name"
            )
        )

    return render(
        request,
        "learners/learner_list.html",
        {
            "class_cards": class_cards,
            "learners": learners,
            "selected_grade": selected_grade,
            "total_learners": total_learners,
        }
    )

# ===================================
# LEARNER DETAIL
# ===================================
def learner_detail(request, pk):

    learner = get_object_or_404(
        Learner,
        pk=pk,
        school=request.user.school
    )

    return render(
        request,
        "learners/learner_detail.html",
        {
            "learner": learner
        }
    )


# ===================================
# ADD LEARNER
# ===================================
def add_learner(request):

    if request.method == "POST":

        form = LearnerForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            learner = form.save(commit=False)
            learner.school = request.user.school
            learner.save()

            return redirect(
                "learner_list"
            )

    else:

        form = LearnerForm()

    return render(
        request,
        "learners/learner_form.html",
        {
            "form": form
        }
    )


# ===================================
# EDIT LEARNER
# ===================================
def edit_learner(request, pk):

    learner = get_object_or_404(
        Learner,
        pk=pk,
        school=request.user.school
    )

    if request.method == "POST":

        form = LearnerForm(
            request.POST,
            request.FILES,
            instance=learner
        )

        if form.is_valid():

            form.save()

            return redirect(
                "learner_list"
            )

    else:

        form = LearnerForm(
            instance=learner
        )

    return render(
        request,
        "learners/learner_form.html",
        {
            "form": form
        }
    )


# ===================================
# DELETE LEARNER
# ===================================
def delete_learner(request, pk):

    learner = get_object_or_404(
        Learner,
        pk=pk,
        school=request.user.school
    )

    learner.delete()

    return redirect(
        "learner_list"
    )


# ===================================
# IMPORT LEARNERS FROM EXCEL
# ===================================
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd

from .models import Learner


def import_learners(request):

    if request.method == "POST":

        excel_file = request.FILES.get("file")

        if not excel_file:
            messages.error(request, "No file selected.")
            return redirect("import_learners")

        # ✅ Get school from user profile (correct architecture)
        try:
            school = request.user.userprofile.school
        except Exception:
            messages.error(request, "User is not linked to a school.")
            return redirect("import_learners")

        # ✅ Read Excel safely
        try:
            excel_data = pd.ExcelFile(excel_file)
        except Exception:
            messages.error(request, "Invalid Excel file.")
            return redirect("import_learners")

        total_imported = 0

        for sheet_name in excel_data.sheet_names:

            df = pd.read_excel(excel_data, sheet_name=sheet_name)

            # Normalize column names
            df.columns = (
                df.columns
                .str.strip()
                .str.upper()
                .str.replace(".", "", regex=False)
            )

            for _, row in df.iterrows():

                # ---------------------------
                # FLEXIBLE COLUMN HANDLING
                # ---------------------------
                assessment_no = None
                upi = ""
                full_name = ""

                for col in row.index:

                    col_clean = str(col).strip().upper()

                    if "ASSESSMENT" in col_clean:
                        assessment_no = row[col]

                    if "UPI" in col_clean:
                        upi = row[col]

                    if "NAME" in col_clean:
                        full_name = row[col]

                # Skip invalid rows
                if assessment_no is None or str(assessment_no).strip() == "":
                    continue

                assessment_no = str(assessment_no).replace("\xa0", "").strip()
                upi = str(upi).replace("\xa0", "").strip()
                full_name = str(full_name).replace("\xa0", "").strip()

                if not full_name or full_name.lower() == "nan":
                    continue

                # Clean name
                if "-" in full_name:
                    full_name = full_name.split("-", 1)[1].strip()

                names = full_name.split()
                first_name = names[0] if names else ""
                last_name = " ".join(names[1:]) if len(names) > 1 else ""

                # Save learner
                Learner.objects.update_or_create(
                    school=school,
                    assessment_no=assessment_no,
                    defaults={
                        "upi_number": upi,
                        "first_name": first_name,
                        "last_name": last_name,
                        "grade": sheet_name,
                    }
                )

                total_imported += 1

        messages.success(
            request,
            f"{total_imported} learners imported successfully!"
        )

        return redirect("learner_list")

    return render(request, "learners/import_learners.html")