from django.urls import path

from . import views


app_name = "fmea_review"

urlpatterns = [
    path("", views.session_list, name="session_list"),
    path("upload/", views.upload_xlsx, name="upload_xlsx"),
    path("session/<str:stable_id>/", views.session_detail, name="session_detail"),
    path("row/<str:stable_id>/", views.row_group_detail, name="row_group_detail"),
    path("row/<str:stable_id>/accept/", views.accept_row_group, name="accept_row_group"),
    path("row/<str:stable_id>/reject/", views.reject_row_group, name="reject_row_group"),
    path("candidate/<str:stable_id>/", views.candidate_detail, name="candidate_detail"),
    path("candidate/<str:stable_id>/accept/", views.accept_candidate, name="accept_candidate"),
    path("candidate/<str:stable_id>/reject/", views.reject_candidate, name="reject_candidate"),
    path("candidate/<str:stable_id>/modify/", views.modify_candidate, name="modify_candidate"),
    path("candidate/<str:stable_id>/link-existing/", views.link_existing, name="link_existing"),
    path("candidate/<str:stable_id>/merge/", views.merge_candidate, name="merge_candidate"),
]
