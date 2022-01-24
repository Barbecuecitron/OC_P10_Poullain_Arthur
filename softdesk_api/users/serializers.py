from rest_framework import fields, serializers
from .models import User

# User Serializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "password"]
        extra_kwargs = {
            'password': {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        # Password will be hashed
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
