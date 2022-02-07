from rest_framework.views import APIView
from users.models import User
from users.utils import get_current_user, can_view_content
from projets.models import Issues, Project, Comments
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from ..serializers import CommentsSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from ..validators import validate_input
import datetime


class CommentManagerView(APIView):
    #  POST METHOD
    def post(self, request, url_project_id, url_issues_id, url_comment_id=None):
        validate_input(request.data, "comments")
        # Get Token from cookie
        local_user = get_current_user(request)
        rdata = request.data
        # Is project valid ?

        project_object = get_object_or_404(Project, id=url_project_id)
        issues_object = get_object_or_404(Issues, id=url_issues_id)

        new_comment = Comments(
            description=rdata["description"],
            author_user_id=local_user,
            issue_id=issues_object,
            created_time=datetime.datetime.now(),
        )
        new_comment.save()

        serialized_comment = CommentsSerializer(new_comment)
        return Response(serialized_comment.data)

    def get(self, request, url_project_id, url_issues_id, url_comment_id=None):
        # GET METHOD
        local_user = get_current_user(request)
        rdata = request.data
        # Is project valid ?
        project_object = get_object_or_404(Project, id=url_project_id)
        can_view_content(local_user, project_object)
        issues_object = get_object_or_404(Issues, id=url_issues_id)
        # Do We get all comments of issues ?
        if url_comment_id is None:
            serialized_comments = []
            issue_related_comments = Comments.objects.filter(
                issue_id=url_issues_id
            ).all()
            for comment in issue_related_comments:
                s_comment = CommentsSerializer(comment)
                serialized_comments.append(s_comment.data)
        else:
            # We want a specify comment
            comment_object = get_object_or_404(Comments, id=url_comment_id)
            serialized_comments = CommentsSerializer(comment_object).data

        # serialized_comment = CommentsSerializer(new_comment)
        return Response(serialized_comments)

    #  MODIFY COMMENTS
    def put(
        self, request, url_project_id=None, url_issues_id=None, url_comment_id=None
    ):
        local_user = get_current_user(request)
        # Is project valid ?
        project_object = get_object_or_404(Project, id=url_project_id)
        # Is Issue valid ?
        issue_object = get_object_or_404(Issues, id=url_issues_id)
        # Is Comment Valid ?
        comment_object = Comments.objects.get(id=url_comment_id)

        if comment_object.author_user_id.id != local_user.id:
            raise PermissionDenied(
                "Seul l'auteur du projet ou de l'issue peuvent supprimer celle-ci"
            )

        rdata = request.data
        comment_object.description = rdata["description"]
        comment_object.save()

        serializer = CommentsSerializer(comment_object)
        return Response(serializer.data)

        #  DELETE METHOD

    def delete(self, request, url_project_id, url_issues_id, url_comment_id):
        local_user = get_current_user(request)
        # Is project valid
        project_object = get_object_or_404(Project, id=url_project_id)

        # Is issue valid
        issue_object = get_object_or_404(Issues, id=url_issues_id)
        # Is Comment Valid
        comment_object = Comments.objects.get(id=url_comment_id)
        comment_object = get_object_or_404(Comments, id=url_comment_id)
        comment_object.delete()

        return Response(
            f"Le commentaire n°{url_comment_id} de l'issue {url_issues_id} a bien été supprimé"
        )
