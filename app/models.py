import uuid
from django.db import models

# Create your models here.

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.TextField(blank=True,null=True)
    role = models.CharField(max_length=255)
    token = models.TextField()
    isverified = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False   # 🚫 No migrations
        db_table = 'users'


class personal_details(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50,null=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=50,null=True)
    dob = models.DateField(null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False   # 🚫 No migrations
        db_table = 'personal_details'


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    class_sections_id = models.UUIDField(null=True)
    roll_no = models.CharField(max_length=50,null=True)
    year = models.DateField(null=True)
    enrollment_number = models.CharField(null=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False   # 🚫 No migrations
        db_table = 'student'


class Class_Sections(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    class_name = models.CharField(null=False)

    class Meta:
        managed = False   # 🚫 No migrations
        db_table = 'class_sections'


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.UUIDField()
    user_role = models.CharField(max_length=50)

    action = models.CharField(max_length=100)

    entity_type = models.CharField(max_length=50, null=True, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)

    status = models.CharField(max_length=20, default="SUCCESS")

    ip_address = models.CharField(max_length=39,null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField()

    class Meta:
        managed = False          # IMPORTANT
        db_table = "audit_logs"
        ordering = ["-created_at"]