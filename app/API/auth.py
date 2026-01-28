
from ..models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.hashers import check_password
from ..utils import create_token

@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {"error": "Email and password are required"},
            status=400
        )

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid credentials"},
            status=401
        )

    if not check_password(password, user_obj.password):
        return Response({"error": "Invalid credentials"}, status=401)
    
    # Generate JWT
    access_token = create_token(user_obj)

    return Response({
        "access_token": access_token
    }, status=200)

    # token = create_token(user_obj)

    # return Response(
    #     {
    #         "message": "Login successful",
    #         "user_id": user_obj.id,
    #         "email": user_obj.email
    #     },
    #     status=200
    # )
