from django.urls import path
from .views import interview_api
from .views import home, interview_api,personal_login,interview_dashboard,upload_file,interview_results

urlpatterns = [ 
    path("", home),
    path('personal_login/',personal_login, name='personal_login'),
    path("interview/", interview_api),
    path('interview_dashboard/', interview_dashboard, name='interview_dashboard'),
    path('upload/', upload_file, name='upload_file'),
    path("interview/results/", interview_results, name="interview_results"),
]

