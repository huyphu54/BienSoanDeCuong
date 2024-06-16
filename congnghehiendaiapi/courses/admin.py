from django.contrib import admin
from django.shortcuts import render
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
    list_filter = ['title','start_year', 'end_year', 'course']
class CurriculumEvaluationAdmin(admin.ModelAdmin):
    list_display = ['curriculum', 'evaluation_criterion', 'score', 'created_at', 'updated_at', 'active']
    search_fields = ['curriculum__title', 'evaluation_criterion__name']
    list_filter = ['curriculum','score','evaluation_criterion__name']
class EvaluationCriterionAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'weight', 'max_score', 'created_at', 'updated_at', 'active']
    list_filter = ['course','name']
    search_fields = ['name','course']

class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'credits', 'category', 'created_at', 'updated_at', 'active']
    search_fields = ['name','credits']
    list_filter = ['category', 'credits']

class SyllabusAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'curriculums__title']
    list_filter = ['title','curriculum__course__name', 'curriculum__course__credits','curriculum__user__username','curriculum__start_year','curriculum__end_year']
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'curriculum', 'created_at', 'updated_at', 'active']
    list_filter = ['user', 'curriculum']
    search_fields = ['content', 'user__username', 'curriculum__title']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_year','is_student','is_teacher', 'avatar', 'degree')

class CustomUserAdmin(DefaultUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ['id', 'username', 'first_name','last_name','email','is_active']
    list_filter = ['is_teacher','is_student', 'is_staff','is_active']
    fieldsets = DefaultUserAdmin.fieldsets + (
        (None, {'fields': ('birth_year', 'avatar', 'degree','is_student','is_teacher')}),
    )

    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        (None, {'fields': ('birth_year', 'avatar', 'degree','is_student','is_teacher')}),
    )

class CourseAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản lý đề cương'
    site_title = 'Quản lý đề cương'
    index_title = 'Trang quản lý'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('courses-stats/', self.admin_view(self.statistics_view), name="statistics"),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        courses_count = Course.objects.count()

        course_stats = []
        for course in Course.objects.all():
            curriculums_count = Curriculum.objects.filter(course=course).count()
            syllabuses_count = Syllabus.objects.filter(curriculum__course=course).count()
            course_stats.append({
                'course': course.name,
                'curriculums_count': curriculums_count,
                'syllabuses_count': syllabuses_count
            })

        evaluation_stats = []
        for curriculum in Curriculum.objects.all():
            evaluations = CurriculumEvaluation.objects.filter(curriculum=curriculum)
            total_score = sum([evaluation.score for evaluation in evaluations])
            evaluation_stats.append({
                'curriculum': curriculum.title,
                'evaluations_count': evaluations.count(),
                'total_score': total_score
            })

        comment_stats = []
        for curriculum in Curriculum.objects.all():
            comments_count = Comment.objects.filter(curriculum=curriculum).count()
            comment_stats.append({
                'curriculum': curriculum.title,
                'comments_count': comments_count
            })

        context = {
            'courses_count': courses_count,
            'course_stats': course_stats,
            'evaluation_stats': evaluation_stats,
            'comment_stats': comment_stats
        }
        return render(request, 'admin/courses_stats.html', context)

# Instantiate the custom admin site
course_admin_site = CourseAppAdminSite(name='course_admin')
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

admin_site.register(CurriculumEvaluation, CurriculumEvaluationAdmin)
