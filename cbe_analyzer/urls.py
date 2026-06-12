from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('schools.urls')),

    path('learners/', include('learners.urls')),

    path('exams/', include('exams.urls')),
]