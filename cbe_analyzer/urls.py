from django.contrib import admin
from django.urls import path, include
from learners import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('schools.urls')),
    
    path('', views.home, name='home'), 

    path('learners/', include('learners.urls')),

    path('exams/', include('exams.urls')),
]