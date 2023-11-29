from django.urls import path

from enrolls.views import (
    AppllyJobView,
    ApplyJobDetailsView,
    JobCategoriesView,
    JobCategoriesDetailsView,
    JobVacanciesView,
    JobVacanciesDetailsView,
    JobVacanciesAllView,
    ApplySearchView,
    RejectAcceptsView
)

urlpatterns = [
    path('job-categories/', JobCategoriesView.as_view()),
    path('job-categories-details/<int:id>/', JobCategoriesDetailsView.as_view()),

    path('job-vacancies/', JobVacanciesView.as_view()),
    path('jobs-vacancies/', JobVacanciesAllView.as_view()),
    path('job-vacancies-details/<int:id>/', JobVacanciesDetailsView.as_view()),

    path('apply-job-user/', AppllyJobView.as_view()),
    path('apply-job-user-serach/', ApplySearchView.as_view()),
    path('apply-job-user-details/<int:id>/', ApplyJobDetailsView.as_view()),
    path('apply-job-reject-accept/<int:id>/<int:status_id>/', RejectAcceptsView.as_view())

]
