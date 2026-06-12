from django.urls import path
from .views import (
    learner_list,
    add_learner,
    learner_detail,
    edit_learner,
    delete_learner
)
from .views import import_learners

urlpatterns = [
    path('', learner_list, name='learner_list'),

    path('add/',
         add_learner,
         name='add_learner'),

    path('detail/<int:pk>/',
         learner_detail,
         name='learner_detail'),

    path('edit/<int:pk>/',
         edit_learner,
         name='edit_learner'),

    path('delete/<int:pk>/',
         delete_learner,
         name='delete_learner'),

     path('import/',
          import_learners,
          name='import_learners'),
     
]