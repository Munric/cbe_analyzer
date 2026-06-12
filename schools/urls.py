from django.urls import path
from . import views

urlpatterns = [

    # HOME / LOGIN
    path(
        "",
        views.school_login,
        name="home"
    ),

    # LOGIN
    path(
        "login/",
        views.school_login,
        name="school_login"
    ),

    # DASHBOARD
    path(
        "dashboard/",
        views.school_dashboard,
        name="school_dashboard"
    ),

]