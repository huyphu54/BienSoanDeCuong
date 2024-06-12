from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.admin import GroupAdmin
from .models import Course, Comment, Curriculum, EvaluationCriterion, User, Category, Syllabus,CurriculumEvaluation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# class UserAdmin(admin.ModelAdmin):
#     list_display = ['username', 'first_name', 'last_name', 'is_teacher', 'is_student', 'HocVi']
#     list_filter = ['is_teacher', 'is_student', 'HocVi', 'name']
#     search_fields = ['username', 'first_name', 'last_name']

class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'user', 'start_year', 'end_year', 'created_at', 'updated_at', 'active']
    search_fields = ['title', 'course__name', 'user__username', 'user__last_name']

class CurriculumEvaluationAdmin(admin.ModelAdmin):
    list_display = ['curriculum', 'evaluation_criterion', 'score', 'created_at', 'updated_at', 'active']
    search_fields = ['curriculum__title', 'evaluation_criterion__name']
class EvaluationCriterionAdmin(admin.ModelAdmin):
    list_display = ['name', 'curriculum', 'weight', 'max_score', 'created_at', 'updated_at', 'active']

    search_fields = ['name', 'curriculum__title']

class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'credits', 'category', 'created_at', 'updated_at', 'active']

    search_fields = ['name','credits']


class SyllabusAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'curriculums__title']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'curriculum', 'created_at', 'updated_at', 'active']

    search_fields = ['content', 'user__username', 'curriculum__title']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_year', 'is_teacher', 'is_student', 'avatar', 'HocVi')

class CustomUserAdmin(DefaultUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    fieldsets = DefaultUserAdmin.fieldsets + (
        (None, {'fields': ('birth_year', 'is_teacher', 'is_student', 'avatar', 'HocVi')}),
    )

    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        (None, {'fields': ('birth_year', 'is_teacher', 'is_student', 'avatar', 'HocVi')}),
    )

class CourseAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản lý đề cương'

    def get_urls(self):
        return [
            path('course-stats/', self.course_stats)
        ] + super().get_urls()

    def course_stats(self, request):
        courses_count = Course.objects.count()
        # stats = Course.objects.annotate()
        return TemplateResponse(request, 'admin/courses_stats.html',{
            'courses_count': courses_count
        })

admin_site = CourseAppAdminSite(name='Hệ thống quản lý đề cương')

# Register your models here.
admin_site.register(User, CustomUserAdmin)

admin_site.register(Category)
admin_site.register(Course,CourseAdmin)
admin_site.register(Curriculum, CurriculumAdmin)
admin_site.register(Syllabus, SyllabusAdmin)
admin_site.register(EvaluationCriterion,EvaluationCriterionAdmin)
admin_site.register(Comment, CommentAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Permission)
admin_site.register(CurriculumEvaluation, CurriculumEvaluationAdmin)
