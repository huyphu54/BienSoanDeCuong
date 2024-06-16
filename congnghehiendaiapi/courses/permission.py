from rest_framework import permissions


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        # Kiểm tra nếu user đã đăng nhập và là sinh viên
        return request.user.is_authenticated and request.user.is_student

    def has_object_permission(self, request, view, obj):
        # Cho phép chỉ cập nhật thông tin cá nhân của chính họ
        return request.user == obj
