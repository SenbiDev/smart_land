from rest_framework import permissions

class IsAdminOrSuperadmin(permissions.BasePermission):
    """
    Izin kustom yang hanya memperbolehkan Admin atau Superadmin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.role == 'Admin' or request.user.role == 'Superadmin')

class IsOpratorOrAdmin(permissions.BasePermission):
    """
    Izin kustom yang memperbolehkan Oprator, Admin, atau Superadmin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.role == 'Oprator' or \
                request.user.role == 'Admin' or \
                request.user.role == 'Superadmin')

class IsSuperadmin(permissions.BasePermission):
    """
    Izin kustom yang HANYA memperbolehkan Superadmin.
    Digunakan untuk User Management dan operasi sensitif lainnya.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.role == 'Superadmin'