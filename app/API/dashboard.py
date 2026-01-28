from django.shortcuts import render
from django.http import JsonResponse

# websocket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# from project
from .. models import User,personal_details
from ..utils import check_authorization

# Create your views here.
@check_authorization(allowed_roles=["admin", "manager"])
def display_count(request):
    print(request.COOKIES)           # if using cookie
    print(request.headers.get("Authorization"))  # if using Authorization header
    try:
        users = User.objects.count()
        teachers = User.objects.filter(role = "teacher").count()
        students = User.objects.filter(role = "student").count()
        staff = User.objects.filter(role = "staff").count()
        placement_officer = User.objects.filter(role = "placement_officer").count()
        company = User.objects.filter(role = "company").count()

        return JsonResponse({
            "total_users": users,
            "total_teacher":teachers,
            "total_student": students,
            "total_staff": staff,
            "total_placement_officer": placement_officer,
            "total_company": company,
            },status=200)
    except Exception as e:
        return JsonResponse({"message": str(e)},status=500)