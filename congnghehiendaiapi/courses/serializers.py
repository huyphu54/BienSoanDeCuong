from rest_framework.serializers import ModelSerializer
from .models import Course

from rest_framework import serializers
from .models import User, Category, Course, Curriculum, Syllabus, EvaluationCriterion, Comment, CurriculumEvaluation


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    birth_year = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name','email', 'birth_year', 'avatar', 'is_active', 'is_staff', 'is_superuser', 'is_teacher', 'is_student', 'degree', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        user = User(
            username=username,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            birth_year=validated_data.get('birth_year', None),
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False),
            is_superuser=validated_data.get('is_superuser', False),
            is_teacher=validated_data.get('is_teacher', False),
            is_student=validated_data.get('is_student', False),
            email=validated_data.get('email',False),
            degree=validated_data.get('degree', None)
        )
        if password:  # Kiểm tra xem password có trong validated_data không
            user.set_password(password)
        user.save()
        return user

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'birth_year', 'avatar', 'is_active', 'is_student', 'degree']
        # Loại bỏ trường 'username' và 'password'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'birth_year', 'avatar', 'is_active', 'is_teacher', 'degree']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','active']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'credits', 'created_at', 'updated_at', 'active','category']

    def validate(self, data):
        category = data.get('category')
        name = data['name']
        courses = Course.objects.all()

        if not category:
            raise serializers.ValidationError("Category is required.")
        if courses.filter(name=name).exists():
            raise serializers.ValidationError("A course with this name already exists.")
        return data
    def create(self, validated_data):
        category = validated_data.pop('category')
        validated_data['active'] = True
        course = Course.objects.create(category=category, **validated_data)

        return course
class CurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'course', 'title', 'description', 'start_year', 'end_year', 'created_at', 'updated_at', 'active']

    def validate(self, data):
        course = data.get('course')
        start_year = data.get('start_year')
        end_year = data.get('end_year')


        if Curriculum.objects.filter(course=course, start_year=start_year, end_year=end_year).exists():
            raise serializers.ValidationError("A curriculum with this course and time period already exists.")
        return data
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['active'] = True  # Đặt active thành True khi tạo mới
        course_id = validated_data.get('course')
        title = validated_data.get('title')
        description = validated_data.get('description')
        start_year = validated_data.get('start_year')
        end_year = validated_data.get('end_year')


        # Kiểm tra xem tất cả các trường dữ liệu có được cung cấp hay không
        if not course_id:
            raise serializers.ValidationError({'course': 'Course is required'})
        if not title:
            raise serializers.ValidationError({'title': 'Title is required'})
        if not description:
            raise serializers.ValidationError({'description': 'Description is required'})
        if not start_year:
            raise serializers.ValidationError({'start_year': 'Start year is required'})
        if not end_year:
            raise serializers.ValidationError({'end_year': 'End year is required'})

        # Tạo đối tượng Curriculum
        curriculum = Curriculum.objects.create(
            user=user,
            course=course_id,
            title=title,
            description=description,
            start_year=start_year,
            end_year=end_year
        )

        return curriculum
class SyllabusSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    curriculum = serializers.PrimaryKeyRelatedField(queryset=Curriculum.objects.all(), required=True)
    class Meta:
        model = Syllabus
        fields = ['id', 'title', 'content', 'curriculum', 'file']

    def validate(self, data):
        title = data['title']
        syllabus = Syllabus.objects.all()

        if syllabus.filter(title=title).exists():
            raise serializers.ValidationError("A syllabus with this name already exists.")
        return data

    def clean(self):
        # Check if the curriculum is within 2 consecutive years
        if self.curriculum:
            cur_start_year = self.curriculum.start_year
            cur_end_year = self.curriculum.end_year

            if not (cur_start_year <= self.curriculum.start_year <= cur_end_year <= self.curriculum.end_year):
                raise serializers.ValidationError('Syllabus can only be associated with up to 2 consecutive years of a curriculum.')


class EvaluationCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriterion
        fields = ['id', 'curriculum', 'name', 'weight', 'max_score', 'created_at', 'updated_at', 'active']

    def validate(self, data):
        curriculum = data.get('curriculum')
        name = data['name']

        if not curriculum:
            raise serializers.ValidationError("Curriculum is required.")


        # Lấy tất cả các tiêu chí đánh giá thuộc về cùng một khóa học
        criteria = EvaluationCriterion.objects.filter(curriculum=curriculum)

        # Kiểm tra trùng tên tiêu chí đánh giá trong cùng một khóa học
        if criteria.filter(name=name).exists():
            raise serializers.ValidationError("An evaluation criterion with this name already exists for this curriculum.")

        # Kiểm tra số lượng cột điểm đánh giá
        if self.instance is None and criteria.count() >= 5:
            raise serializers.ValidationError("A course cannot have more than 5 evaluation criteria.")

        # Kiểm tra tổng trọng số của các cột điểm đánh giá
        total_weight = sum(criterion.weight for criterion in criteria)
        if self.instance:
            total_weight -= self.instance.weight  # Loại trừ trọng số của tiêu chí hiện tại khi cập nhật

        if total_weight + data.get('weight', 0) > 1:
            raise serializers.ValidationError("Total weight of evaluation criteria cannot exceed 100%.")

        return data
    def create(self, validated_data):
        validated_data['active'] = True  # Đặt active thành True khi tạo mới

        return super().create(validated_data)



class CurriculumEvaluationSerializer(serializers.ModelSerializer):
    syllabus_title = serializers.CharField(source='syllabus.title', read_only=True)
    evaluation_criterion_name = serializers.CharField(source='evaluation_criterion.name', read_only=True)

    class Meta:
        model = CurriculumEvaluation
        fields = ['id', 'syllabus', 'syllabus_title', 'evaluation_criterion', 'evaluation_criterion_name', 'score', 'created_at', 'updated_at', 'active']

    def validate(self, data):
        syllabus = data['syllabus']
        evaluation_criterion = data['evaluation_criterion']

        # Kiểm tra xem evaluation_criterion thuộc về curriculum.course hay không
        if evaluation_criterion.curriculum != syllabus.curriculum:
            raise serializers.ValidationError("Evaluation criterion must belong to the corresponding course.")
        return data

    def create(self, validated_data):
        validated_data['active'] = True

        return super().create(validated_data)
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'syllabus', 'user', 'content', 'created_at', 'updated_at', 'active']
        read_only_fields = ['id', 'user']
