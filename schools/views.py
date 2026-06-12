from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import School, UserProfile


# ====================================
# LOGIN
# ====================================
def school_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # LOGIN USER
            login(request, user)

            try:
                # GET USER PROFILE
                profile = UserProfile.objects.get(user=user)

                # SAVE SCHOOL ID IN SESSION
                request.session["school_id"] = profile.school.id

                print("SCHOOL SAVED:", profile.school.name)

            except UserProfile.DoesNotExist:

                messages.error(
                    request,
                    "No school assigned to this user."
                )

                return redirect("school_login")

            return redirect("school_dashboard")

        else:

            messages.error(
                request,
                "Invalid username or password"
            )

    return render(
        request,
        "schools/login.html"
    )


# ====================================
# DASHBOARD
# ====================================
@login_required
def school_dashboard(request):

    try:
        school = request.user.userprofile.school
    except UserProfile.DoesNotExist:
        school = None

    return render(request, "schools/schools_list.html", {
        "school": school
    })