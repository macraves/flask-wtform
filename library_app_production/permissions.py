"""Authorization helpers shared by the route blueprints."""
from flask_login import current_user

# The first registered account (id 1) is treated as the admin
ADMIN_USER_ID = 1


def is_admin():
    """Check whether the logged-in user is the admin.

    Returns:
        bool: True when the current user is the admin account.
    """
    return current_user.is_authenticated and current_user.id == ADMIN_USER_ID


def can_modify(owner_id):
    """Check whether the logged-in user may change a record.

    Args:
        owner_id (int): ID of the user who owns the record.

    Returns:
        bool: True for the record owner or the admin.
    """
    return current_user.is_authenticated and (
        current_user.id == owner_id or is_admin()
    )
