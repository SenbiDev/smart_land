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

# --- BARU: Izin Read-Only untuk Viewer & Investor ---
class IsViewerOrInvestorReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Hanya izinkan method aman (GET, HEAD, OPTIONS)
        if request.method not in permissions.SAFE_METHODS:
            return False
            
        if request.user.role:
            return request.user.role.name in ['Viewer', 'Investor']
            
        return False