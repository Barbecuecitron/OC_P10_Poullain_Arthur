from sre_compile import isstring
import string
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.fields import DateTimeField
from django.utils.translation import gettext_lazy as lazy
from users.models import User
from django.conf import settings


def validate_project_type(value):
    valid_types = ("back-end", "front-end", "iOS", "Android")

    if not value in valid_types:
        raise ValidationError(
            lazy(f"{str(value)} is not valid. Pick one : {valid_types}"),
            params={"value": value},
        )

# Create your models here.


class Project(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=500, null=False)
    project_type = models.CharField(
        max_length=200, validators=[validate_project_type])
    author_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def get_contributors(self):
        contributors = Contributors.objects.filter(project_id=self.id).all()
        return contributors


class Contributors(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    # crud_permissions = pass,
    role = models.CharField(max_length=500, null=False)


class Issues(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=500, null=False)
    tag = models.CharField(max_length=500, null=False)
    priority = models.CharField(max_length=500, null=False)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, null=False)
    author_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author_user_id"
    )
    assignee_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assignee_user_id"
    )
    created_time = DateTimeField()


class Comments(models.Model):
    description = models.CharField(max_length=500, null=False)
    author_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_id = models.ForeignKey(Issues, on_delete=models.CASCADE)
    created_time = DateTimeField()
