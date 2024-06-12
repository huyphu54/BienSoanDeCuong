from django.contrib import admin
from django.urls import path, include
from . import views
from .admin import admin_site
from rest_framework import routers
from .views import UserViewSet, CategoryViewSet, CourseViewSet, CurriculumViewSet, SyllabusViewSet, \
    EvaluationCriterionViewSet, CommentViewSet, CurriculumEvaluationViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'curriculums', CurriculumViewSet, basename='curriculum')
router.register(r'syllabuses', SyllabusViewSet, basename='syllabus')
router.register(r'evaluationcriteria', EvaluationCriterionViewSet, basename='evaluationcriterion')
router.register(r'curriculum-evaluations', CurriculumEvaluationViewSet,  basename='curriculum-evaluations')
router.register(r'comments', CommentViewSet, basename='comment')


urlpatterns = [
    # path('', views.index, name="index"),
    path('admin/', admin_site.urls),
    path('', include(router.urls))

]
