from django.urls import path

from . import views


app_name = "fmea"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("projects/create/", views.create_project, name="create_project"),
    path("fmeas/create/", views.create_fmea, name="create_fmea"),
    path("fmea/<str:stable_id>/", views.fmea_detail, name="fmea_detail"),
    path("fmea/<str:stable_id>/failure-modes/add/", views.add_failure_mode, name="add_failure_mode"),
    path(
        "process-characteristics/",
        views.process_characteristic_list,
        name="process_characteristic_list",
    ),
    path(
        "process-characteristics/new/",
        views.new_process_characteristic,
        name="new_process_characteristic",
    ),
    path(
        "process-characteristics/<str:stable_id>/",
        views.process_characteristic_detail,
        name="process_characteristic_detail",
    ),
    path(
        "processes/<str:stable_id>/flow/",
        views.process_flow,
        name="process_flow",
    ),
    path("cause-influences/", views.cause_influence_list, name="cause_influence_list"),
    path("cause-influences/new/", views.new_cause_influence, name="new_cause_influence"),
    path("cause-influences/create/", views.create_cause_influence_view, name="create_cause_influence"),
    path("cause-influences/<str:stable_id>/", views.cause_influence_detail, name="cause_influence_detail"),
    path(
        "cause-influences/<str:stable_id>/transition/",
        views.transition_cause_influence_view,
        name="transition_cause_influence",
    ),
    path(
        "failure-modes/<str:stable_id>/ishikawa-board/",
        views.ishikawa_board,
        name="ishikawa_board",
    ),
    path("failure-mode/<str:stable_id>/effects/add/", views.add_failure_effect, name="add_failure_effect"),
    path("failure-mode/<str:stable_id>/causes/add/", views.add_failure_cause, name="add_failure_cause"),
    path("failure-mode/<str:stable_id>/evaluate/", views.evaluate_failure, name="evaluate_failure"),
    path("cause/<str:stable_id>/prevention-controls/add/", views.add_prevention_control, name="add_prevention_control"),
    path("cause/<str:stable_id>/detection-controls/add/", views.add_detection_control, name="add_detection_control"),
]
