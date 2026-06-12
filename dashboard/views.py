from django.contrib.auth.decorators import login_required
from .models import School,render,redirect

@login_required
def school_dashboard(request):

    school_id = request.session.get("school_id")

    if not school_id:
        return redirect("school_login")

    school = School.objects.get(id=school_id)

    return render(request, "schools/dashboard.html", {
        "school": school
    })