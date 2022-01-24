from django.contrib import admin
from django.urls import path
from .views.views import ProjectView, ProjectContentView, RemoveUserFromProjectView
from .views.issues import ProjectIssuesManager
from .views.comments import CommentManagerView

urlpatterns = [
    path("projects/", ProjectView.as_view()),
    path("projects/<int:project_id>/", ProjectView.as_view()),
    path("projects/<int:url_project_id>/users/", ProjectContentView.as_view()),
    path(
        "projects/<int:url_project_id>/users/<int:user_to_delete_id>/",
        RemoveUserFromProjectView.as_view(),
    ),
    path("projects/<int:url_project_id>/issues/",
         ProjectIssuesManager.as_view()),
    path(
        "projects/<int:url_project_id>/issues/<int:url_issues_id>/",
        ProjectIssuesManager.as_view(),
    ),
    path(
        "projects/<int:url_project_id>/issues/<int:url_issues_id>/comments/",
        CommentManagerView.as_view(),
    ),
    path(
        "projects/<int:url_project_id>/issues/<int:url_issues_id>/comments/<int:url_comment_id>/",
        CommentManagerView.as_view(),
    ),
]
