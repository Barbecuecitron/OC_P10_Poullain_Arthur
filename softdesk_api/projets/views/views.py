from rest_framework.views import APIView
from users import serializers
from users.models import User
from users.serializers import UserSerializer
from users.utils import get_current_user
from projets.models import Contributors, Project
from projets.validators import validate_input
from rest_framework.response import Response
from ..serializers import ContributorsSerializer, ProjectSerializer
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import NotAcceptable, NotFound

# Create your views here.

# Manage Project Core


class ProjectView(APIView):
    def post(self, request):
        validate_input(request.data, "project")
        # Get Token from cookie
        local_user = get_current_user(request)
        rdata = request.data
        # Create project from Post data
        project = Project(
            title=rdata["title"],
            description=rdata["description"],
            project_type=rdata["project_type"],
            author_user_id=local_user,
        )
        # project.save()

        serialized_project = ProjectSerializer(project)
        return Response(serialized_project.data)

    # Get method
    def get(self, request, project_id=None):
        local_user = get_current_user(request)
        # No project_id in URL -> Get all projects
        if project_id is None:
            user_related_projects = Project.objects.filter(
                author_user_id=local_user.id
            ).all()
            serialized_projects = []
            for project in user_related_projects:
                s_project = ProjectSerializer(project)
                serialized_projects.append(s_project.data)
            return Response(serialized_projects)

        # project_id in URL -> Get project infos
        else:
            try:
                project_object = Project.objects.get(id=project_id)
            except ObjectDoesNotExist:
                raise NotFound(f"Aucun Projet n'existe à l'index {project_id}")
            serializer = ProjectSerializer(project_object)
            return Response(serializer.data)

    # Modify Project
    def put(self, request, project_id=None):
        local_user = get_current_user(request)
        validate_input(request.data, "project")
        try:
            project_object = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun Projet n'existe à l'index {project_id}")

        rdata = request.data

        project_object.title = rdata["title"]
        project_object.description = rdata["description"]
        project_object.project_type = rdata["project_type"]
        project_object.author_user_id = local_user

        # project_object.save()

        serializer = ProjectSerializer(project_object)
        return Response(serializer.data)

    # Delete project
    def delete(self, request, project_id=None):
        local_user = get_current_user(request)
        try:
            project_object = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun Projet n'existe à l'index {project_id}")

        if project_object.author_user_id.id != local_user.id:
            raise PermissionDenied("Vous n'êtes pas autorisé à effectuer cette action.")
        project_object.delete()
        print(f"OBJECT AUTHOR USER ID {project_object.author_user_id.id}")
        print(f"CONNECTED_USER ID {local_user.id}")
        return Response(f"Vous avez supprimmé le projet {project_id}")


class ProjectContentView(APIView):
    # Get All contribs from project
    def get(self, request, url_project_id):
        # Get Token from cookie
        local_user = get_current_user(request)
        rdata = request.data
        # Catch or abort -> targeted Project
        try:
            project_object = Project.objects.get(id=url_project_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun Projet n'existe à l'index {url_project_id}")

        # Retrieve contributors' IDs
        contributors_objects = project_object.get_contributors()
        serialized_contributors = []
        for contributor in contributors_objects:
            serialized_contributors.append(ContributorsSerializer(contributor).data)
        return Response(serialized_contributors)

    # Add contrib to project
    def post(self, request, url_project_id):
        # Get Token from cookie
        local_user = get_current_user(request)
        rdata = request.data
        # Add a user through its id
        user_to_add_id = rdata["id"]
        if not rdata["id"].isnumeric():
            raise NotAcceptable("Saisie invalide, l'id utilisateur doit être un INT")
        # Catch or abort -> passed in user
        try:
            user_to_add_obj = User.objects.get(id=user_to_add_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun utilisateur trouvé avec l'email {user_to_add_id}")

        # Catch or abort -> targeted Project
        try:
            project_object = Project.objects.get(id=url_project_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun Projet n'existe à l'index {url_project_id}")

        # User already contributor of project | Abort or continue ?
        try:
            contrib_object = Contributors.objects.get(
                project_id=url_project_id, user_id=user_to_add_obj
            )
            return Response(
                f"L'utilisateur {user_to_add_id} ({user_to_add_obj.email}) est dèja contributaire du projet {url_project_id}"
            )
        except ObjectDoesNotExist:
            pass

        new_contrib = Contributors(
            user_id=user_to_add_obj, project_id=project_object, role="TestRole"
        )
        new_contrib.save()
        # return Response(serialized_project.data)
        return Response(
            f"Vous ajoutez l'utilisateur {user_to_add_id} ({user_to_add_obj.email}) au projet {url_project_id}"
        )


# REMOVE A CONTRIBUTOR FROM A PROJECT
class RemoveUserFromProjectView(APIView):
    def delete(self, request, url_project_id, user_to_delete_id):
        local_user = get_current_user(request)
        try:
            project_object = Project.objects.get(id=url_project_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun Projet n'existe à l'index {url_project_id}")

        try:
            user_to_delete = User.objects.get(id=user_to_delete_id)
        except ObjectDoesNotExist:
            raise NotFound(f"Aucun utilisateur trouvé avec l'email {user_to_delete_id}")

        if project_object.author_user_id.id != local_user.id:
            raise PermissionDenied(
                "Seul l'auteur du projet peut en supprimer les contributaires"
            )
        # Does this contribution even exist ?
        try:
            contrib_object = Contributors.objects.get(
                project_id=url_project_id, user_id=user_to_delete_id
            )
        except ObjectDoesNotExist:
            raise NotAcceptable(
                f"L'utilisateur {user_to_delete_id} ({user_to_delete.email}) n'est pas contributaire du {url_project_id}"
            )

        contrib_object.delete()
        return Response(
            f"La contribution de l'utilisateur {user_to_delete_id} ({user_to_delete.email}) au projet {url_project_id} a bien été supprimée"
        )
