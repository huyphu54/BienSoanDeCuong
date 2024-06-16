import string
from random import random

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import FileResponse
from django.shortcuts import render
from django.template.defaultfilters import slugify
from rest_framework import viewsets, permissions, status, parsers, generics,filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Category, Course, Curriculum, Syllabus, EvaluationCriterion, Comment
from .serializers import UserSerializer, CategorySerializer, CourseSerializer, CurriculumSerializer, SyllabusSerializer, \
    EvaluationCriterionSerializer, CommentSerializer, CurriculumEvaluation, CurriculumEvaluationSerializer
from courses import serializers, paginators
from django.contrib.auth.models import Group
from .permission import IsSuperuser, IsStudent

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser]


    def get_permissions(self):
        if self.action in ['create', 'register_student', 'register_teacher']:
            return [permissions.AllowAny()]
        if self.action in ['update_profile']:
            return [IsStudent()]
        if self.action in ['retrieve', 'approve_student', 'approve_teacher','list']:
            return [IsSuperuser()]
        return [permissions.IsAuthenticated()]

    # def perform_create(self, serializer):
    #     user = serializer.save()
    #     if user.is_teacher:
    #         user.is_active = False
    #         user.save()
    #         send_mail(
    #             'Account Registration',
    #             'Your account has been registered. Please upload an avatar and provide additional information.',
    #             'admin@example.com',
    #             [user.email],
    #             fail_silently=False,
    #         )

    #----------------Giảng Viên Đăng Ký-----------------

    @action(detail=False, methods=['post'], url_path='register-teacher')
    def register_teacher(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_email = 'huyphu2805@gmail.com'
        user = serializer.save(is_active=False, is_teacher=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='approve-teacher')
    def approve_teacher(self, request, pk=None):
        user = self.get_object()
        if not user.is_teacher or user.is_active:
            raise PermissionDenied("Invalid teacher account.")
        user.is_staff = True
        user.is_active = True
        group_name = 'Teacher'  # Replace with your group name
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        user.save()
        send_mail(
            'Account Approved',
            'Now you can use this account like an admin',
            'huyphu2805@gmail.com',
            [user.email],
            fail_silently=False,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


     #----------------Sinh Viên Đăng Ký-----------------
    @action(detail=False, methods=['post'], url_path='register-student')
    def register_student(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False, is_student=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['patch'], url_path='approve-student')
    def approve_student(self, request, pk=None):
        user = self.get_object()
        if not user.is_student or user.is_active:
            raise PermissionDenied("Invalid student account.")

        # Tạo username từ email
        username = user.email.split('@')[0]

        # Kiểm tra xem username đã tồn tại chưa
        if User.objects.filter(username=username).exists():
            # Nếu đã tồn tại, thêm một số ngẫu nhiên vào cuối
            username += ''.join(random.choices(string.digits, k=4))
        #Set mật khẩu mặc định là 123456
        user.set_password('123456')

        user.username = slugify(username)
        user.is_active = True
        user.is_staff = True
        group_name = 'Student'
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        user.save()

        send_mail(
            'Account Approved',
            'Your account has been approved. Please update your password and upload an avatar. '
            'username: your email name before @, password: 123456',
            'huyphu2805@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='update-profile-student')
    def update_profile_student(self, request, pk=None):
        student = self.get_object()

        password = request.data.get('password')
        avatar = request.data.get('avatar')

        if password:
            student.password = make_password(password)
        if avatar:
            student.avatar = avatar
        student.save()
        return Response({'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list']:
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [IsSuperuser()]
        return [permissions.IsAuthenticated()]


class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = paginators.CoursePaginator

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            queryset = queryset.filter(category_id=cate_id)
        return queryset

    @action(methods=['get'], url_path='lessons', detail=True)
    def get_lessons(self, request, pk=None):
        course = self.get_object()
        category = course.category
        if category.active:
            categories = [category]
        else:
            categories = []
        return Response(serializers.CategorySerializer(categories, many=True).data, status=status.HTTP_200_OK)
    @action(methods=['get'], url_path='category', detail=False)
    def get_courses_by_category(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({"detail": "Category ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        courses = Course.objects.filter(category=category)
        page = self.paginate_queryset(courses)
        if page is not None:
            return self.get_paginated_response(CourseSerializer(page, many=True).data)

        return Response(CourseSerializer(courses, many=True).data)

class CurriculumViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = Curriculum.objects.all()
    serializer_class = CurriculumSerializer

    def get_permissions(self):
        if self.action in ['list']:
            return [permissions.AllowAny()]
        elif self.action == ['create','retrieve', 'update']:
            return [IsSuperuser()]
        return [permissions.IsAuthenticated()]

class SyllabusViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = Syllabus.objects.all()
    serializer_class = SyllabusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'curriculum__course__name', 'curriculum__course__credits', 'curriculum__user__username', 'curriculum__start_year', 'curriculum__end_year']

    def get_queryset(self):
        queryset = Syllabus.objects.all()
        title = self.request.query_params.get('title', None)
        course_name = self.request.query_params.get('course_name', None)
        course_credits = self.request.query_params.get('course_credits', None)
        user_username = self.request.query_params.get('user_username', None)
        start_year = self.request.query_params.get('start_year', None)
        end_year = self.request.query_params.get('end_year', None)

        if title:
            queryset = queryset.filter(title__icontains=title)
        if course_name:
            queryset = queryset.filter(curriculum__course__name__icontains=course_name)
        if course_credits:
            queryset = queryset.filter(curriculum__course__credits=course_credits)
        if user_username:
            queryset = queryset.filter(curriculum__user__username__icontains=user_username)
        if start_year:
            queryset = queryset.filter(curriculum__start_year=start_year)
        if end_year:
            queryset = queryset.filter(curriculum__end_year=end_year)

        return queryset
    def get_permissions(self):
        if self.action in ['list']:
            return [permissions.AllowAny()]
        elif self.action in ['create', 'retrieve', 'update']:
            return [IsSuperuser()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'], url_path='download', permission_classes=[permissions.AllowAny])
    def download_syllabus(self, request, pk=None):
        syllabus = self.get_object()
        file_handle = syllabus.file.open()
        response = FileResponse(file_handle, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{syllabus.file.name}"'
        return response

class EvaluationCriterionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = EvaluationCriterion.objects.all()
    serializer_class = EvaluationCriterionSerializer

    def get_permissions(self):
        if self.action in ['list']:
            return [permissions.AllowAny()]
        elif self.action == ['create','retrieve', 'update']:
            return [IsSuperuser()]
        return [permissions.IsAuthenticated()]



class CurriculumEvaluationViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    queryset = CurriculumEvaluation.objects.all()
    serializer_class = CurriculumEvaluationSerializer

    def get_permissions(self):
        if self.action in ['list']:
            return [permissions.AllowAny()]
        elif self.action == ['create','retrieve']:
            return [IsSuperuser()]
        return [permissions.IsAuthenticated()]

class CommentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView, generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
