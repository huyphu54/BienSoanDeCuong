from rest_framework.serializers import ModelSerializer
from .models import Course

from rest_framework import serializers
from .models import User, Category, Course, Curriculum, Syllabus, EvaluationCriterion, Comment, CurriculumEvaluation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name','email', 'birth_year', 'avatar', 'is_active', 'is_staff', 'is_superuser', 'is_teacher', 'is_student', 'HocVi', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            birth_year=validated_data.get('birth_year', None),
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False),
            is_superuser=validated_data.get('is_superuser', False),
            is_teacher=validated_data.get('is_teacher', False),
            is_student=validated_data.get('is_student', False),
            email=validated_data.get('email',False),
            HocVi=validated_data.get('HocVi', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'credits', 'created_at', 'updated_at', 'active']

class CurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'course', 'user', 'title', 'description', 'start_year', 'end_year', 'created_at', 'updated_at', 'active']

class SyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllabus
        fields = ['id', 'title', 'content', 'curriculum', 'file']

class EvaluationCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriterion
        fields = ['id', 'curriculum', 'name', 'weight', 'max_score', 'created_at', 'updated_at', 'active']


class CurriculumEvaluationSerializer(serializers.ModelSerializer):
    curriculum_title = serializers.CharField(source='curriculum.title', read_only=True)
    evaluation_criterion_name = serializers.CharField(source='evaluation_criterion.name', read_only=True)

    class Meta:
        model = CurriculumEvaluation
        fields = ['id', 'curriculum', 'curriculum_title', 'evaluation_criterion', 'evaluation_criterion_name', 'score', 'created_at', 'updated_at', 'active']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'curriculum', 'user', 'content', 'created_at', 'updated_at', 'active']
        read_only_fields = ['id', 'user']
