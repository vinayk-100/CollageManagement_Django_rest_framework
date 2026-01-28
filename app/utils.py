import random
import secrets
from django.http import JsonResponse


from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from functools import wraps

from .models import User




# Create your Uitls here.

# ======================== send email =============================

def send_email_with_signup_token(email, name, token):
    activation_link = f"http://localhost:5173/SetPassword?token={token}"

    subject = "Activate your account"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]

    text_body = f"""
    Hi {name},

    Click the link below to create your password:
    {activation_link}

    This link expires in 24 hours.
    """

    html_body = f"""
    <h3>Welcome!</h3>
    <p>Hi {name},</p>

    <p>Click the link below to create your password:</p>
    <a href="{activation_link}">Create Password</a>

    <p>This link expires in 24 hours.</p>
    """

    email_message = EmailMultiAlternatives(
        subject,
        text_body,
        from_email,
        to_email
    )

    email_message.attach_alternative(html_body, "text/html")
    email_message.send()

# =================== Send Email End ============================

# ==================== auto generation =============================

def auto_generate_username(fname,lname):

    if not fname or not lname:
        return None
    
    # Generate 4 random digits
    random_digits = random.randint(1000, 9999)

    # Create username
    generated_username = (
        fname.lower()
        + "_"
        + lname[0].lower()
        + str(random_digits)
    )

    return generated_username



def generate_activation_token():
    return secrets.token_urlsafe(32)

# ==================== auto generation end =============================
# ==================== Validation  =============================

@api_view(["POST"])
def validate_signup_token(request):
    token = request.data.get("token")
    if not token:
        print("===================== no token ===================")
        return Response({
            "status": "error",
            "message": "Token is required"
        }, status=400)

    try:
        user = User.objects.get(token=token)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Invalid token"
        }, status=400)
    
    expiry_time = user.updated_at + timedelta(days=5)

    if timezone.now() > expiry_time:
        return Response({
            "status": "expired",
            "message": "Token has expired"
        }, status=400)
    
    if user.isverified:
        return Response({
            "status": "verified",
            "message": "User already verified"
        }, status=200)
    
    return Response({
        "status": "valid",
        "message": "Token valid, allow password creation",
        "user_id": user.id
    }, status=200)




# ==================== Validation end  =============================

# ==================== JWT token  ================================

def create_token(user_obj):
    
    token = AccessToken()
    token["user_id"] = str(user_obj.id)  # ALWAYS store UUID as string
    token["role"] = user_obj.role

    return str(token)



# ==================== Jwt Token End  =============================

# ==================== Decorators   ===============================

def check_authorization(allowed_roles=[]):
    """
    Custom decorator for:
    - Authentication (JWT validation)
    - Authorization (role-based access)
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            jwt_authenticator = JWTAuthentication()

            try:
                # STEP 1: Get Authorization header
                header = jwt_authenticator.get_header(request)
                if header is None:
                    return JsonResponse(
                        {"error": "Authorization header missing"},
                        status=401
                    )

                # STEP 2: Extract token
                raw_token = jwt_authenticator.get_raw_token(header)
                if raw_token is None:
                    return JsonResponse(
                        {"error": "Token missing"},
                        status=401
                    )

                # STEP 3: Validate token
                validated_token = jwt_authenticator.get_validated_token(raw_token)

                # STEP 4: Extract payload
                user_id = validated_token.get("user_id")
                role = validated_token.get("role")

                if not user_id or not role:
                    return JsonResponse(
                        {"error": "Invalid token payload"},
                        status=401
                    )

                # STEP 5: Role-based authorization
                if allowed_roles and role not in allowed_roles:
                    return JsonResponse(
                        {
                            "error": "Permission denied",
                            "required_roles": allowed_roles,
                            "your_role": role
                        },
                        status=403
                    )

                # STEP 6: Attach data to request (VERY IMPORTANT)
                request.user_id = user_id   # UUID as string
                request.role = role

                return view_func(request, *args, **kwargs)

            except (InvalidToken, TokenError) as e:
                return JsonResponse(
                    {"error": "Invalid or expired token"},
                    status=401
                )

        return wrapped_view
    return decorator

# ==================== Decorators End  =============================
