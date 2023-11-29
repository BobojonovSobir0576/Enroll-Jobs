from django.urls import path

from enrolls.views import (
    AppllyJobView,
    ApplyJobDetailsView,
    JobCategoriesView,
    JobCategoryCrudViews,
    JobVacanciesView,
    JobVacanciesAllView,
    ApplySearchView,
    JobVacanciesDetailsView,
)

urlpatterns = [
    path('job-categories/', JobCategoriesView.as_view()),
    path('job-category-crud-views/<int:pk>/', JobCategoryCrudViews.as_view()),
    path('job-vacancies-deleile/', JobVacanciesView.as_view()),
    path('job-vacancies-details-view/<int:pk>', JobVacanciesDetailsView.as_view()),
    path('jobs-vacancies', JobVacanciesAllView.as_view()),
    path('apply-job-user/', AppllyJobView.as_view()),
    path('apply-job-user-serach/', ApplySearchView.as_view()),
    path('apply-job-user-details/<int:id>/', ApplyJobDetailsView.as_view())

]
