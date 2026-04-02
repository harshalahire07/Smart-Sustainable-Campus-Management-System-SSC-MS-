from rest_framework import permissions

class IsAdminOrStaffReadOnlyCreate(permissions.BasePermission):
    """
    Custom permission for role-based access control:
    - User must be authenticated.
    - ADMIN can perform all actions (GET, POST, PUT, PATCH, DELETE).
    - STAFF can only read (GET, HEAD, OPTIONS) and create (POST).
    - STAFF cannot update or delete.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not bool(request.user and request.user.is_authenticated):
            return False

        # If user is ADMIN, they have full permission at the view level
        if request.user.role == 'ADMIN':
            return True

        # If user is STAFF, they can read and create (POST)
        if request.user.role == 'STAFF':
            if request.method in permissions.SAFE_METHODS or request.method == 'POST':
                return True

        return False

    def has_object_permission(self, request, view, obj):
        # Must be authenticated
        if not bool(request.user and request.user.is_authenticated):
            return False

        # If user is ADMIN, they have full permission at the object level
        if request.user.role == 'ADMIN':
            return True

        # If user is STAFF, they can only perform safe methods on existing objects (no updating/deleting)
        if request.user.role == 'STAFF':
            if request.method in permissions.SAFE_METHODS:
                return True

        return False
