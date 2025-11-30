from rest_framework import permissions

class IsAdminOrSuperadmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        if request.user.role:
            return request.user.role.name in ['Admin', 'Superadmin']
            
        return False

class IsOperatorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.user.role:
            return request.user.role.name in ['Operator', 'Admin', 'Superadmin']
            
        return False

class IsSuperadmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.user.role:
            return request.user.role.name == 'Superadmin'
            
        return False