# from curses.ascii import isalpha
from django.core.exceptions import BadRequest
from .models import Project, Contributors, Issues, Comments

# Check wether we have int or object-driven Foreign Key,
# Validate both cases


def is_valid_fk(fk_entry):
    valid_instances = [Project, Contributors, Issues, Comments]
    if str(fk_entry).isnumeric() or fk_entry in valid_instances:
        return
    raise BadRequest(
        "Something went wrong, be sure to respect the documentation to assign valid fields")


def is_string_safe(passed_string):
    if passed_string is None or not isinstance(passed_string, str) or passed_string == "":
        raise BadRequest(
            "Something went wrong, be sure to respect the documentation to assign valid fields")


def validate_input(obj, type):

    custom_validators = {
        "project": {
            "title": is_string_safe,
            "description": is_string_safe,
            "project_type": is_string_safe,
        },

        "contributors": {
            "project_id": is_valid_fk,
            "role": is_string_safe,
            "role": is_string_safe,
        },

        "registration": {
            "first_name": is_string_safe,
            "last_name": is_string_safe,
            "email": is_string_safe,
            "password": is_string_safe,
        },

        "login": {
            "email": is_string_safe,
            "password": is_string_safe,
        },

        "issues": {
            "title": is_string_safe,
            "description": is_string_safe,
            "tag": is_string_safe,
            "priority": is_string_safe,
            "project_id": is_valid_fk,
            "status": is_string_safe,
            "assignee_user_id": is_valid_fk
        },

        "comments": {
            "description": is_string_safe,
        }

    }
    # If input json keys have missing key compared to our custom_validators dicts
    for key in custom_validators[type].keys():
        if not key in obj.keys():
            raise BadRequest(
                "Something went wrong, a field is probably missing")

    for input_fields, input_value in obj.items():
        print(input_fields, input_value)
        if input_value is None or input_fields is None:
            raise BadRequest(
                "Something went wrong, be sure to respect the documentation to assign valid fields")

        try:
            custom_validators[type][input_fields](input_value)
        except KeyError:
            raise BadRequest(
                "Something went wrong, be sure to respect the documentation to assign valid fields")
