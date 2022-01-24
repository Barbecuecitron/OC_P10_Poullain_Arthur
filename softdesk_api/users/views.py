from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
import jwt
import datetime
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from projets.validators import validate_input
# Create your views here.


class RegisterView(APIView):
    def post(self, request):
        validate_input(request.data, "registration")
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        validate_input(request.data, "login")
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("Utilisateur non trouvé")

        if not user.check_password(password):
            raise AuthenticationFailed("Mot de passe incorrect !")

        # 1hr expiration,
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow(),
        }
        #  create token from payload
        token = jwt.encode(payload, "secret", algorithm="HS256")

        response = Response()
        # create the cookie
        # httponly to not it sent to the frontend
        response.set_cookie(key="jwt", value=token, httponly=True)
        response.data = {
            "jwt": token,
        }

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Vous n'êtes pas connecté")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Vous avez été déconnecté")

        user = User.objects.filter(id=payload["id"]).first()

        serialized_user = UserSerializer(user)
        return Response(serialized_user.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "Vous vous êtes déconnecté de l'API"}
        return response
