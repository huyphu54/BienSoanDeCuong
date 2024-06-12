from django.core.mail import send_mail
from django.http import FileResponse
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, parsers, generics,filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Category, Course, Curriculum, Syllabus, EvaluationCriterion, Comment
from .serializers import UserSerializer, CategorySerializer, CourseSerializer, CurriculumSerializer, SyllabusSerializer, \
    EvaluationCriterionSerializer, CommentSerializer, CurriculumEvaluation, CurriculumEvaluationSerializer
from courses import serializers, paginators


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser]


    def get_permissions(self):
        if self.action in ['create', 'register_student', 'register_teacher']:
            return [permissions.AllowAny()]
        if self.action in [ 'retrieve', 'approve_student', 'approve_teacher','list']:
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

    @action(detail=False, methods=['post'], url_path='register-teacher')
    def register_teacher(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False, is_teacher=True)
        # send_mail(
        #     'Teacher Registration Request',
        #     'A new teacher has registered. Please review and approve the account.',
        #     'admin@example.com',
        #     ['admin@example.com'],
        #     fail_silently=False,
        # )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    @action(detail=False, methods=['post'], url_path='register-student')
    def register_student(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False, is_student=True)
        # send_mail(
        #     'Student Registration Request',
        #     'A new student has registered. Please review and approve the account.',
        #     'admin@example.com',
        #     ['admin@example.com'],
        #     fail_silently=False,
        # )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['patch'], url_path='approve-teacher')
    def approve_teacher(self, request, pk=None):
        user = self.get_object()
        if not user.is_teacher or user.is_active:
            raise PermissionDenied("Invalid teacher account.")
        user.is_staff = True
        user.is_active = True
        user.save()
        # send_mail(
        #     'Account Approved',
        #     'Your account has been approved. Please update your password and upload an avatar.',
        #     'admin@example.com',
        #     [user.email],
        #     fail_silently=False,
        # )
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    @action(detail=True, methods=['patch'], url_path='approve-student')
    def approve_student(self, request, pk=None):
        user = self.get_object()
        if not user.is_student or user.is_active:
            raise PermissionDenied("Invalid student account.")
        user.is_active = True
        user.is_staff = True
        user.save()
        # send_mail(
        #     'Account Approved',
        #     'Your account has been approved. Please update your password and upload an avatar.',
        #     'admin@example.com',
        #     [user.email],
        #     fail_silently=False,
        # )
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


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
    queryset = Course.objects.filter(active=True)
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
        lessons = course.lesson_set.filter(active=True)
        return Response(serializers.LessonSerializer(lessons, many=True).data, status=status.HTTP_200_OK)


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
    search_fields = ['title', 'curriculums__course__name', 'curriculums__course__credits', 'curriculums__user__username', 'curriculums__start_year', 'curriculums__end_year']

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
            queryset = queryset.filter(curriculums__course__name__icontains=course_name)
        if course_credits:
            queryset = queryset.filter(curriculums__course__credits=course_credits)
        if user_username:
            queryset = queryset.filter(curriculums__user__username__icontains=user_username)
        if start_year:
            queryset = queryset.filter(curriculums__start_year=start_year)
        if end_year:
            queryset = queryset.filter(curriculums__end_year=end_year)

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