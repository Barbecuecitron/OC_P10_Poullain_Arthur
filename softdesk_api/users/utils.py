from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from users.models import User
from rest_framework.exceptions import AuthenticationFailed, NotAcceptable
import jwt
from projets.models import Project, Contributors, Issues

# Prevents the execution of functions / assignation through () and =
char_whitelist = {" ", "_", ".", "@", "-", "!", "?"}


def secure_request(data):
    for key, string in data.items():
        if type(string) != str:
            raise NotAcceptable("One entry or more were not valid")

        for char in string:
            if not char.isalnum() and char not in char_whitelist:
                raise NotAcceptable("One entry or more were not valid")


def get_current_user(request):
    token = request.COOKIES.get("jwt")
    if not token:
        raise AuthenticationFailed("Vous n'êtes pas connecté")
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Vous avez été déconnecté")

    # Get User from PayLoad
    local_user = User.objects.filter(id=payload["id"]).first()
    return local_user


def is_contrib(arg_user_id, arg_project_id):
    try:
        contrib_object = Contributors.objects.get(
            project_id=arg_project_id, user_id=arg_user_id
        )
        return True
    except ObjectDoesNotExist:
        pass

    return False


def can_view_content(user, proj):
    if isinstance(proj, Project):
        if user.id == proj.author_user_id.id or is_contrib(user.id, proj):
            return True
    #     else:
    #         print(
    #             f"actual_user_id = {user.id}, auteur_projet={proj.author_user_id}, is_contrib={is_contrib(user.id, proj)}")
    raise PermissionDenied("Vous n'avez pas la permission nécessaire")


def check_modify_permission(user, obj):
    if obj.author_user_id is not None and obj.author_user_id == user.id:
        return True
    return False
