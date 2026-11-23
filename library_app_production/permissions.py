"""Authorization helpers shared by the route blueprints."""
from flask import flash
from flask_login import current_user


def is_admin():
    """Check whether the logged-in user is an admin.

    Returns:
        bool: True when the current user has the is_admin flag.
    """
    return current_user.is_authenticated and bool(current_user.is_admin)


def can_modify(owner_id):
    """Check whether the logged-in user may change a record.

    Args:
        owner_id (int): ID of the user who owns the record.

    Returns:
        bool: True for the record owner or an admin.
    """
    return current_user.is_authenticated and (
        current_user.id == owner_id or is_admin()
    )


def flash_form_errors(form):
    """Flash every validation error of a form.

    Args:
        form (FlaskForm): A form whose validation failed.
    """
    for field_name, errors in form.errors.items():
        label = getattr(form, field_name).label.text
        for error in errors:
            flash(f"Error in field '{label}': {error}", "error")
