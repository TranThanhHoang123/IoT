from rest_framework import permissions

class IsKhachHang(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super(IsKhachHang, self).has_permission(request, view) and
            (request.user.is_superuser or (request.user.role and request.user.role.name == "KHACHHANG"))
        )

class IsAdmin(permissions.IsAuthenticated):
    """
    Kiểm tra nếu người dùng là admin hoặc superuser.
    """
    def has_permission(self, request, view):
        return (
            super(IsAdmin, self).has_permission(request, view) and
            (request.user.is_superuser or (request.user.role and request.user.role.name == "ADMIN"))
        )

class IsNhanVien(permissions.IsAuthenticated):
    """
    Kiểm tra nếu người dùng là nhanvien hoặc superuser.
    """
    def has_permission(self, request, view):
        return (
            super(IsNhanVien, self).has_permission(request, view) and
            (request.user.is_superuser or (request.user.role and request.user.role.name == "NHANVIEN"))
        )
