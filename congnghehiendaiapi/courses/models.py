from django.core.validators import URLValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField
class User(AbstractUser):
    id = models.AutoField(primary_key=True)  # Trường ID tự động tăng, làm khóa chính
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30)  # Tên (first name)
    last_name = models.CharField(max_length=30)  # Họ (last name)
    birth_year = models.PositiveIntegerField(null=True, blank=True)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='images/avatar/%Y/%m/%d/', null=True, blank=True)
    degree = models.CharField(max_length=50, null=True, blank=True)  # Chỉ dành cho giáo viên
    email = models.EmailField(blank=True, null=True)
    def __str__(self):
        return self.username or ''


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-id']

class Course(BaseModel):
    name = models.CharField(max_length=255)
    credits = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE, default=1) # Added related_name

    def __str__(self):
        return self.name

class Curriculum(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='curriculums')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_year = models.IntegerField(default=2021)
    end_year = models.IntegerField(default=2025)

    class Meta:
        permissions = [
            ("can_add_curriculum", "Can add curriculum"),
            ("can_view_curriculum", "Can view curriculum"),
        ]

    def __str__(self):
        return f"{self.course.name} ({self.start_year}-{self.end_year})"

class Syllabus(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='syllabus/%Y/%m/%d/', null=True, blank=True)
    def __str__(self):
        return self.title

class EvaluationCriterion(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.course}) "
class CurriculumEvaluation(BaseModel):
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE,null=True)
    evaluation_criterion = models.ForeignKey(EvaluationCriterion, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.curriculum.title} - {self.evaluation_criterion.name}'

class Comment(BaseModel):
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()

    def __str__(self):
        return f'{self.user.username} - {self.curriculum.title}'
