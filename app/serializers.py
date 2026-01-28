from rest_framework import serializers
from .models import User,personal_details,Class_Sections,Student

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # fields = ['username','email','role','isverified','created_at','updated_at']


class personal_details_Serializer(serializers.ModelSerializer):
    class Meta:
        model = personal_details
        fields = '__all__'
        # fields = ['username','email','role','isverified','created_at','updated_at']

class class_sections_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Class_Sections
        fields = '__all__'

class Student_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
