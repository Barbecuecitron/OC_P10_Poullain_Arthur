from wsgiref import validate
from rest_framework.views import APIView
from users.models import User
from users.utils import get_current_user
from projets.models import Issues, Project
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotFound, PermissionDenied
from ..serializers import IssuesSerializer
from django.core.exceptions import ObjectDoesNotExist
from ..validators import validate_input
import datetime


class ProjectIssuesManager(APIView):
    def post(self, request, url_project_id):
        # Get Token from cookie
        local_user = get_current_user(request)

        validate_input(request.data, "issues")
        rdata = request.data

        # Create project from Post data

        try:
            project_object = Project.objects.get(id=url_project_id)
        except ObjectDoesNotExist:
            # ERROR HANDLING TO BE DONE HERE
            raise NotFound(f"Aucun Projet n'existe à l'index {url_project_id}")

        new_issue = Issues(
            title=rdata["title"],
            description=rdata["description"],
            tag=rdata["tag"],
            priority=rdata["priority"],
            project_id=project_object,
            status=rdata["status"],
            author_user_id=local_user,
            assignee_user_id=local_user,
            created_time=datetime.datetime.now(),
        )
        new_issue.save()

        serialized_issue = IssuesSerializer(new_issue)
        return Response(serialized_issue.data)

        # Get method

    def get(self, request, url_project_id=None, url_issues_id=None):
        local_user = get_current_user(request)
        # We need a valid project to get issues from
        try:
            project_object = Project.objects.get(id=url_project_id)
        except ObjectDoesNotExist:
            # ERROR HANDLING TO BE DONE HERE
            raise NotFound(f"Aucun Projet n'existe à l'index {url_project_id}")

        # No issues_id in URL -> Get all issues
        if url_issues_id is None:
            serialized_issues = []
            project_related_issues = Issues.objects.filter(
                project_id=url_project_id
            ).all()
            for issue in project_related_issues:
                s_issue = IssuesSerializer(issue)
                serialized_issues.append(s_issue.data)
        else:
            try:
                url_targeted_issue = Issues.objects.get(id=url_issues_id)
                url_issues_serialized = IssuesSerializer(url_targeted_issue)
                serialized_issues = url_issues_serialized.data
            except ObjectDoesNotExist:
                # return Response(f"Aucun Projet n'existe à l'index {url_issues_id}")
                raise NotFound(f"Aucune Issue n'existe à l'index {url_issues_id}")

        return Response(serialized_issues)

        # Modify Issues

    def put(self, request, url_project_id=None, url_issues_id=None):
        local_user = get_current_user(request)

        validate_input(request.data, "issues")
        # Is project valid ?
        try:
            project_object = Project.objects.get(id=url_project_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun Projet n'existe à l'index {url_project_id}")
        # Is Issue valid ?
        try:
            issue_object = Issues.objects.get(id=url_issues_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucune Issue n'existe à l'index {url_issues_id}")

        rdata = request.data
        new_assigned = rdata["assignee_user_id"]
        # If new assignee doesn't exist, abort & don't apply changes
        try:
            assignee_user_object = User.objects.get(id=rdata["assignee_user_id"])
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun user n'existe à l'index {new_assigned}")

        issue_object.title = rdata["title"]
        issue_object.description = rdata["description"]
        issue_object.tag = rdata["tag"]
        issue_object.priority = rdata["priority"]
        issue_object.project_id = project_object
        issue_object.status = rdata["status"]
        issue_object.assignee_user_id = assignee_user_object

        issue_object.save()

        serializer = IssuesSerializer(issue_object)
        return Response(serializer.data)

    #  DELETE METHOD
    def delete(self, request, url_project_id, url_issues_id):
        local_user = get_current_user(request)
        # Is project valid
        try:
            project_object = Project.objects.get(id=url_project_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun Projet n'existe à l'index {url_project_id}")

        # Is issue valid
        try:
            issue_object = Issues.objects.get(id=url_issues_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucune Issue n'existe à l'index {url_issues_id}")

        if (
            issue_object.author_user_id.id != local_user.id
            and project_object.author_user_id.id != local_user.id
        ):
            raise PermissionDenied(
                "Seul l'auteur du projet ou de l'issue peuvent supprimer celle-ci"
            )

        issue_object.delete()

        return Response(
            f"L'issue n°{url_issues_id} du projet {url_project_id} a bien été supprimée"
        )
