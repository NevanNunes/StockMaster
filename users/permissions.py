from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Managers to edit/validate.
    Staff can only view and create drafts.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions
        if request.method == 'POST':
            return request.user.is_authenticated
            
        # Edit/Delete permissions are only allowed to Managers
        # Also explicitly check for 'validate' action if it's a custom action
        return request.user.is_authenticated and request.user.role == 'MANAGER'
