from django.urls import include, path
from django.contrib.auth import views as auth_views
from _web import views

urlpatterns = [

    ##########################################
    ##########################################
    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="registration/logout.html"), name='logout'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="registration/logout.html"), name='logout'),
    path('update_semester/', views.change_semester, name='change_semester'),
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    ##########################################
    ##########################################

    path('measurement_section_reports/', views.measurement_section_reports, name='measurement_section_reports'),
    path('measurement_course_reports/', views.measurement_course_reports, name='measurement_course_reports'),
    path('measurement_department_reports/', views.measurement_department_reports,
         name='measurement_department_reports'),
    path('measurement__reviewers/', views.measurement__reviewers, name='measurement__reviewers'),
    path('measurement_export/', views.measurement_export, name='measurement_export'),

    path('generate_grades_excel_list/', views.generate_grades_excel_list, name='generate_grades_excel_list'),
    path('generate_zipped_measurement_reports_list/', views.generate_zipped_measurement_reports_list,
         name='generate_zipped_measurement_reports_list'),

    path('measurement_section_reports_admin/', views.measurement_section_reports_admin,
         name='measurement_section_reports_admin'),
    path('measurement_course_reports_admin/', views.measurement_course_reports_admin,
         name='measurement_course_reports_admin'),

    path('generate_section_report_list/', views.generate_section_report_list,
         name='generate_section_report_list'),
    path('generate_section_excel_list/', views.generate_section_excel_list,
         name='generate_section_excel_list'),
    path('generate_course_report_list/', views.generate_course_report_list,
         name='generate_course_report_list'),
    path('generate_department_excel_list/', views.generate_department_excel_list,
         name='generate_department_excel_list'),

    ##########################################
    ##########################################
    path('quality_mycfis/', views.quality_cfi_reports, name='quality_mycfis'),
    path('quality_mycfis_admin/', views.quality_mycfis_admin, name='quality_mycfis_admin'),
    path('quality_mycfis_reviewers/', views.quality_mycfis_reviewers, name='quality_mycfis_reviewers'),
    path('quality_export/', views.quality_export, name='quality_export'),
    path('generate_zipped_quality_reports_list/', views.generate_zipped_quality_reports_list,
         name='generate_zipped_quality_reports_list'),

    path('video/', views.video, name='video'),
]
