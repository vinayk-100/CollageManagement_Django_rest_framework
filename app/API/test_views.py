from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from ..utils import check_authorization

@api_view(['GET'])
def verify_token(request):
    jwt_authenticator = JWTAuthentication()

    try:
        # Step 1: Get header
        header = jwt_authenticator.get_header(request)
        if header is None:
            return Response(
                {"error": "Authorization header missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Step 2: Get raw token
        raw_token = jwt_authenticator.get_raw_token(header)
        if raw_token is None:
            return Response(
                {"error": "Token missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Step 3: Validate token
        validated_token = jwt_authenticator.get_validated_token(raw_token)

        # Step 4: Read payload
        user_id = validated_token.get("user_id")
        role = validated_token.get("role")

        return Response({
            "valid": True,
            "user_id": user_id,
            "role": role
        })

    except (InvalidToken, TokenError) as e:
        return Response(
            {"valid": False, "error": str(e)},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@check_authorization(allowed_roles=["admin", "manager"])
def admin_dashboard(request):
    return Response({
        "message": "Welcome to admin dashboard",
        "user_id": request.user_id,
        "role": request.role
    })

@api_view(['GET'])
@check_authorization(allowed_roles=["user"])
def user_profile(request):
    return Response({
        "message": "User profile access granted",
        "user_id": request.user_id,
        "role": request.role
    })