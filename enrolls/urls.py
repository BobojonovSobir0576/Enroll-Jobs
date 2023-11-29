from django.urls import path

from enrolls.views import (
    AppllyJobView,
    ApplyJobDetailsView,
    JobCategoriesView,
    JobVacanciesView,
    JobVacanciesAllView,
    ApplySearchView
)

urlpatterns = [
    path('job-categories/', JobCategoriesView.as_view()),
    path('job-vacancies/', JobVacanciesView.as_view()),
    path('jobs-vacancies/', JobVacanciesAllView.as_view()),
    path('apply-job-user/', AppllyJobView.as_view()),
    path('apply-job-user-serach/', ApplySearchView.as_view()),
    path('apply-job-user-details/<int:id>/', ApplyJobDetailsView.as_view())

]
