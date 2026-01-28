from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password,check_password

from .. models import User,personal_details,Student
from .. serializers import UserSerializer,personal_details_Serializer,Student_Serializer
from .. utils import auto_generate_username,send_email_with_signup_token,generate_activation_token

from django.utils import timezone

import json

from rest_framework.exceptions import ValidationError

# socket
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# ======================= Util Function  =================

def create_user_data(data):
    """
    Create user and return user instance + serialized data
    """

    # Validate required fields
    if not data.get('first_name') or not data.get('last_name'):
        raise ValidationError("First Name and Last Name are required")

    # Add timestamps
    data['created_at'] = timezone.now()
    data['updated_at'] = timezone.now()

    # Generate username
    username = auto_generate_username(data['first_name'], data['last_name'])
    data['username'] = username

    # Serialize & save
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()   # actual DB object
    return user, serializer.data


def create_personal_info(user, data):
    """
    Create personal info using user id
    """

    personal_data = {
        "user_id": user.id,
        "first_name" : data["first_name"],
        "last_name" : data["last_name"],
        "created_at" : data["created_at"],
        "updated_at" : data["updated_at"]
        # add more fields here
    }

    serializer = personal_details_Serializer(data=personal_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return serializer.data

def create_student(user, data):
    student_data = {
        "user_id": user.id,
        # "class_sections_id" : data["class_sections_id"],
        "enrollment_number" : data["enrollment_number"],
        "created_at" : data["created_at"],
        "updated_at" : data["updated_at"]
        # add more fields here
    }

    serializer = Student_Serializer(data=student_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return serializer.data


@api_view(["POST"])
def create_password(request):
    user_id = request.data.get('user_id')
    password = request.data.get('password')

    if not user_id or not password:
        return Response(
            {"error": "user_id and password are required"},
            status=400
        )
    
    try:
        data = User.objects.get(id = user_id)

        data.password = make_password(password)

        # to check password
        # if check_password(input_password, user.password):
            # pass
        # else:
            # pass
            

        data.isverified = True
        data.save()

        return Response(
            {"message": "Password added successfully", "user_id": user_id},
            status=200
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User Not Found"},status=400
        )
    except Exception as e:
        return Response(
            {"error": str(e)},status=400)


# ====================== Util Function End



# Create your views here.

# to Get All User List
@api_view(['GET'])
def view_all_users(request):
    try:
        data = User.objects.all()
        serializer = UserSerializer(data, many=True)
        return JsonResponse({"succuss":serializer.data}, status=200)
    except Exception as e:
            return JsonResponse({"exceptional": str(e)}, status=500)

# To Get Single User Detail List
@api_view(['GET'])
def view_user_details(request,id):

    try:
        user = User.objects.get(id=id)
        personal = personal_details.objects.filter(user_id=id).first()
        student = Student.objects.filter(user_id=id).first()

        response_data = {
                "user": UserSerializer(user).data,
                "personal_details": personal_details_Serializer(personal).data if personal else None,
                "student": Student_Serializer(student).data if student else None,
            }
        
        return JsonResponse({"success": response_data}, status=200)
    
    except User.DoesNotExist:
        return JsonResponse({"error": "User doesn't exist"}, status=404)

    except Exception as e:
        return JsonResponse({"exception": str(e)}, status=500)


@api_view(['POST'])
def add_user(request):

    student_data = {}

    try:

        data = request.data.copy()
        token = generate_activation_token()
        data["token"] = token
        

        # 1️⃣ Create user
        user, user_data = create_user_data(data)

        print(user.__dict__)

        # 2️⃣ Create personal info
        personal_info_data = create_personal_info(user, data)

        print(personal_info_data["first_name"])

        role = data.get('role')

        # 3️⃣ if student function
        if role == "student":
            student_data = create_student(user,data)

        total_users = User.objects.count()
        total_teacher = User.objects.filter(role="teacher").count()  
        total_students = User.objects.filter(role = "student").count()
        total_staff = User.objects.filter(role = "staff").count()
        total_placement_officer = User.objects.filter(role = "placement_officer").count()
        total_company = User.objects.filter(role = "company").count()

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
        "updates_group",
        {
            "type": "send_update",
            "user_count": total_users,
            "teacher_count": total_teacher,
            "student_count": total_students,
            "staff_count": total_staff,
            "placement_count": total_placement_officer,
            "company_count": total_company,
        }
    )
        
        




         # 🔔 Send Welcome Email
        send_email_with_signup_token(
            email=user.email,
            name=personal_info_data["first_name"],
            token = token
        )

        return JsonResponse(
            {
                "user": user_data,
                "personal_info": personal_info_data,
                "student_data":student_data
            },
            status=201
        )
    
    except ValidationError as e:
        print(f"validation error {e}")
        return JsonResponse(
            {"error": e.detail},
            status=400
        )
    
    except Exception as e:
        print(f"exception {e}")
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


    

@api_view(['DELETE'])
def delete_user(request,id):
    try:
        with transaction.atomic():
            # 1️⃣ Check if user exists
            data = User.objects.get(id = id)

            # 2️⃣ Delete related data safely (won't fail if not exists)
            personal_details.objects.filter(user_id=id).delete()
            Student.objects.filter(user_id=id).delete()

            # 3️⃣ Delete user
            data.delete()

            return JsonResponse({"succussfull":"User Delete Succussfull"}, status=200)
        
    except User.DoesNotExist:
        return JsonResponse({"error":"user dosn't exist"}, status=404)
    except Exception as e:
        return JsonResponse({"exceptional": str(e)}, status=500)
    
@api_view(['PATCH'])
def update_user(request,id):
    try:
        data = User.objects.get(id=id)
        serializer = UserSerializer(data, data=request.data, partial=True)  # partial=True allows PATCH
        if serializer.is_valid():
            serializer.save(updated_at=timezone.now())  # Update the timestamp
            return JsonResponse(serializer.data, status=200)
        else:
            # Validation failed, return errors
            return JsonResponse(serializer.errors, status=400)
    except User.DoesNotExist:
        return JsonResponse({"error":"user dosn't exist"}, status=404)
    except Exception as e:
        return JsonResponse({"exceptional": str(e)}, status=500)


def personal_detail_test(request):
    data = personal_details.objects.all()
    serializer = personal_details_Serializer(data, many=True) 
    return JsonResponse({"succuss":serializer.data}, status=200)